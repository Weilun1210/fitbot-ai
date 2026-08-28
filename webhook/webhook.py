"""FitBot Dialogflow ES exercise webhook (v5.9).

The webhook answers only from ``FitBot_cleaned_dataset.csv``. It supports strict
recommendations, named-exercise details, and ordinal follow-ups referring to
the most recent recommendation list. Search helpers are dependency-free.
"""

from __future__ import annotations

import csv
import difflib
import os
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote


HERE = Path(__file__).resolve().parent
DEFAULT_DATASET_CANDIDATES = (
    HERE / "FitBot_cleaned_dataset.csv",
    HERE.parents[2] / "02 data" / "processed" / "FitBot_cleaned_dataset.csv",
)

# Canonical values are the exact values present in FitBot_cleaned_dataset.csv.
BODY_PART_VALUES = (
    "Abdominals", "Abductors", "Adductors", "Biceps", "Calves", "Chest",
    "Forearms", "Glutes", "Hamstrings", "Lats", "Lower Back", "Middle Back",
    "Neck", "Quadriceps", "Shoulders", "Traps", "Triceps",
)
EQUIPMENT_VALUES = (
    "Bands", "Barbell", "Body Only", "Cable", "Dumbbell", "E-Z Curl Bar",
    "Exercise Ball", "Foam Roll", "Kettlebells", "Machine", "Medicine Ball",
    "None", "Other",
)
LEVEL_VALUES = ("Beginner", "Expert", "Intermediate")
TYPE_VALUES = (
    "Cardio", "Olympic Weightlifting", "Plyometrics", "Powerlifting",
    "Strength", "Stretching", "Strongman",
)

BACK_PARTS = ("Lats", "Lower Back", "Middle Back", "Traps")
LEG_PARTS = (
    "Abductors", "Adductors", "Calves", "Glutes", "Hamstrings", "Quadriceps",
)
NO_EQUIPMENT = ("Body Only", "None")


def _aliases(values: Iterable[str]) -> dict[str, tuple[str, ...]]:
    return {value.casefold(): (value,) for value in values}


BODY_PART_MAP = _aliases(BODY_PART_VALUES)
BODY_PART_MAP.update({
    "abs": ("Abdominals",), "abdominal": ("Abdominals",),
    "core": ("Abdominals",), "back": BACK_PARTS, "leg": LEG_PARTS,
    "legs": LEG_PARTS, "quad": ("Quadriceps",), "quads": ("Quadriceps",),
    "shoulder": ("Shoulders",), "trap": ("Traps",),
})

EQUIPMENT_MAP = _aliases(EQUIPMENT_VALUES)
EQUIPMENT_MAP.update({
    "band": ("Bands",), "resistance band": ("Bands",),
    "resistance bands": ("Bands",), "bodyweight": NO_EQUIPMENT,
    "body weight": NO_EQUIPMENT, "body only": NO_EQUIPMENT,
    "no equipment": NO_EQUIPMENT, "without equipment": NO_EQUIPMENT,
    "none": NO_EQUIPMENT, "cable machine": ("Cable",),
    "e-z curl bar": ("E-Z Curl Bar",), "ez curl bar": ("E-Z Curl Bar",),
    "exercise balls": ("Exercise Ball",), "foam roller": ("Foam Roll",),
    "foam rollers": ("Foam Roll",), "kettlebell": ("Kettlebells",),
    "medicine balls": ("Medicine Ball",), "barbells": ("Barbell",),
    "cables": ("Cable",), "dumbbells": ("Dumbbell",),
    "machines": ("Machine",),
})

LEVEL_MAP = _aliases(LEVEL_VALUES)
LEVEL_MAP.update({
    "advanced": ("Expert",), "new": ("Beginner",), "novice": ("Beginner",),
})

TYPE_MAP = _aliases(TYPE_VALUES)
TYPE_MAP.update({
    "endurance": ("Cardio",), "weight loss": ("Cardio",),
    "fat loss": ("Cardio",), "flexibility": ("Stretching",),
    "mobility": ("Stretching",), "muscle gain": ("Strength",),
    "toning": ("Strength",), "olympic": ("Olympic Weightlifting",),
})

# Public compatibility alias for older imports/tests.
GOAL_TYPE_MAP = TYPE_MAP

RECOMMENDATION_ACTIONS = {
    "exercise.recommendation", "exercise.by_body_part", "exercise.by_equipment",
    "exercise.by_level", "workout.recommendation",
}
DETAIL_ACTIONS = {"exercise.details"}
SCOPE_MESSAGE = (
    "I’m not sure I understood that. Try asking for an exercise by level, "
    "body part, equipment, or training type, or ask about a specific exercise."
)
RECOMMENDATION_HEADING = "Here are the best matches for your request."
MORE_RECOMMENDATION_HEADING = "Here are three more exercises."
MISSING_DESCRIPTION = "Exercise instructions have not been added yet."


def dataset_path() -> Path:
    """Return the configured dataset path or the first existing default."""
    configured = os.getenv("FITBOT_DATASET_PATH")
    if configured:
        path = Path(configured).expanduser().resolve()
        if path.is_file():
            return path
        raise FileNotFoundError(f"FITBOT_DATASET_PATH does not exist: {path}")
    for candidate in DEFAULT_DATASET_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("FitBot_cleaned_dataset.csv was not found")


def load_exercises(path: Path | None = None) -> list[dict[str, str]]:
    """Load all usable rows while preserving the team-cleaned CSV unchanged.

    The shared cleaned file represents missing equipment with an empty field.
    At runtime that value is mapped to ``None`` so no valid exercise is lost
    and existing no-equipment filters remain compatible.
    """
    source = path or dataset_path()
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        exercises: list[dict[str, str]] = []
        for source_row in reader:
            row = {
                str(key or "").strip(): str(value or "").strip()
                for key, value in source_row.items()
            }
            if not row.get("Equipment"):
                row["Equipment"] = "None"
            if (row.get("Title") and row.get("BodyPart") and
                    row.get("Level") and row.get("Type")):
                exercises.append(row)
        return exercises


def scalar(value: Any) -> str:
    """Normalize a Dialogflow scalar/list parameter to lowercase text."""
    if isinstance(value, list):
        value = value[0] if value else ""
    if isinstance(value, dict):
        value = next((item for item in value.values() if item), "")
    return str(value or "").strip().casefold()


def display_scalar(value: Any) -> str:
    """Normalize a parameter while preserving case for exercise names."""
    if isinstance(value, list):
        value = value[0] if value else ""
    if isinstance(value, dict):
        value = next((item for item in value.values() if item), "")
    return str(value or "").strip()


def _targets(value: str, aliases: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    """Resolve one entity value to one or more exact dataset values."""
    normalized = str(value or "").strip().casefold()
    if not normalized:
        return ()
    return aliases.get(normalized, (str(value).strip(),))


def _rating(row: dict[str, str]) -> tuple[bool, float]:
    raw = row.get("Rating", "").strip()
    if not raw:
        return False, 0.0
    try:
        return True, float(raw)
    except ValueError:
        return True, 0.0


def _result_sort_key(row: dict[str, str]) -> tuple[Any, ...]:
    has_rating, rating = _rating(row)
    return (
        -int(has_rating), -rating, -int(bool(row.get("Desc", "").strip())),
        row.get("Title", "").casefold(), row.get("BodyPart", "").casefold(),
        row.get("Equipment", "").casefold(),
    )


def select_exercises(
    exercises: list[dict[str, str]], *, body_part: str = "",
    equipment: str = "", level: str = "", exercise_type: str = "",
    goal: str = "", limit: int = 3, offset: int = 0,
) -> list[dict[str, str]]:
    """Return strict, deterministic, de-duplicated dataset matches.

    Every supplied filter is intersected. Aggregate query terms expand only
    within their own field; filters are never silently removed.
    """
    if limit <= 0 or offset < 0:
        return []
    filters = (
        ("Level", _targets(level, LEVEL_MAP)),
        ("BodyPart", _targets(body_part, BODY_PART_MAP)),
        ("Equipment", _targets(equipment, EQUIPMENT_MAP)),
        ("Type", _targets(exercise_type or goal, TYPE_MAP)),
    )
    active = [
        (field, {item.casefold() for item in values})
        for field, values in filters if values
    ]
    matches = [
        row for row in exercises
        if all(row.get(field, "").casefold() in allowed for field, allowed in active)
    ]
    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in sorted(matches, key=_result_sort_key):
        key = row["Title"].casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique[offset:offset + limit]


def _filter_summary(*, body_part: str, equipment: str, level: str,
                    exercise_type: str) -> str:
    values = (level, body_part, equipment, exercise_type)
    return " · ".join(value.strip().title() for value in values if value.strip())


def _rating_label(row: dict[str, str]) -> str:
    """Return a reader-friendly rating without presenting zero as a score."""
    raw = row.get("Rating", "").strip()
    try:
        return f"{raw} / 10" if raw and float(raw) > 0 else "Not rated"
    except ValueError:
        return "Not rated"


def _plain_field_lines(row: dict[str, str]) -> list[str]:
    return [
        f"Body part: {row['BodyPart']}",
        f"Equipment: {row['Equipment']}",
        f"Level: {row['Level']}",
        f"Type: {row['Type']}",
        f"Rating: {_rating_label(row)}",
    ]


def _card_field_lines(row: dict[str, str]) -> list[str]:
    return [
        f"💪 Body part · {row['BodyPart']}",
        f"🏋️ Equipment · {row['Equipment']}",
        f"📈 Level · {row['Level']}",
        f"⚡ Type · {row['Type']}",
        f"⭐ Rating · {_rating_label(row)}",
    ]


def format_exercises(
    results: list[dict[str, str]], *, start_number: int = 1,
    heading: str = RECOMMENDATION_HEADING,
) -> str:
    """Create a field-complete recommendation response."""
    if not results:
        return (
            "No exact match was found for those choices. Try changing one option."
        )
    lines = [heading]
    for number, row in enumerate(results, start=start_number):
        lines.extend(("", f"{number}. {row['Title']}", *_plain_field_lines(row)))
    return "\n".join(lines)


def recommendation_rich_messages(
    results: list[dict[str, str]], *, start_number: int = 1,
    local_pager: bool = False, heading: str = RECOMMENDATION_HEADING,
) -> list[dict[str, Any]]:
    """Create recommendation cards and optional client-side page controls."""
    cards = [
        [{
            "type": "accordion",
            "title": f"{number}. {row['Title']}",
            "subtitle": (
                f"{row['BodyPart']} · {row['Equipment']} · {row['Level']}"
            ),
            "text": "\n".join(_card_field_lines(row)),
        }, _details_button(row["Title"])]
        for number, row in enumerate(results, start=start_number)
    ]
    if local_pager:
        cards.append([{
            "type": "button",
            "icon": {"type": "expand_more", "color": "#6F930D"},
            "text": "Show more exercises",
            "link": "#fitbot-recommendation-page=2",
        }])
        cards.append([{
            "type": "button",
            "icon": {"type": "arrow_back", "color": "#6F930D"},
            "text": "Previous page",
            "link": "#fitbot-recommendation-page=1",
        }, {
            "type": "button",
            "icon": {"type": "arrow_forward", "color": "#6F930D"},
            "text": "Next page",
            "link": "#fitbot-recommendation-page=2",
        }])
    return [
        {"text": {"text": [heading]}},
        {"payload": {"richContent": cards}},
    ]


def _context_names(payload: dict[str, Any]) -> list[str]:
    query_result = payload.get("queryResult") or {}
    for context in query_result.get("outputContexts") or []:
        if str(context.get("name", "")).casefold().endswith(
            "/contexts/last_recommendations"
        ):
            parameters = context.get("parameters") or {}
            names = parameters.get("exercise_names") or parameters.get(
                "exercise_names.original"
            )
            if isinstance(names, list):
                return [str(name).strip() for name in names if str(name).strip()]
            recovered = []
            for number in range(1, 7):
                value = parameters.get(f"recommendation_{number}")
                if value:
                    recovered.append(str(value).strip())
            return recovered
    return []


def _ordinal_index(value: Any) -> int | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        number = int(value)
        return number - 1 if value == number and 1 <= number <= 6 else None
    if isinstance(value, list) and value:
        return _ordinal_index(value[0])
    text = scalar(value)
    if not text:
        return None
    words = {
        "first": 0, "one": 0, "second": 1, "two": 1,
        "third": 2, "three": 2, "fourth": 3, "four": 3,
        "fifth": 4, "five": 4, "sixth": 5, "six": 5,
    }
    for word, index in words.items():
        if re.search(rf"\b{word}\b", text):
            return index
    match = re.search(r"\b([1-6])(?:st|nd|rd|th)?\b", text)
    return int(match.group(1)) - 1 if match else None


def _details_button(title: str) -> dict[str, Any]:
    """Build a marker link that the Streamlit chat shell sends as normal text."""
    return {
        "type": "button",
        "icon": {"type": "info", "color": "#6F930D"},
        "text": "View details",
        "link": f"#fitbot-view-details={quote(title, safe='')}",
    }


def _unique_title_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    unique: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["Title"].casefold()
        current = unique.get(key)
        if current is None or _result_sort_key(row) < _result_sort_key(current):
            unique[key] = row
    return list(unique.values())


def _candidate_sort_key(row: dict[str, str], wanted: str) -> tuple[Any, ...]:
    title = row["Title"].casefold()
    prefix_rank = 0 if title.startswith(wanted) else 1
    neutral_variant_rank = 0 if title == f"{wanted} - medium grip" else 1
    similarity = difflib.SequenceMatcher(None, wanted, title).ratio()
    return (
        prefix_rank, neutral_variant_rank, -similarity,
        len(title), _result_sort_key(row),
    )


def resolve_exercise(
    exercises: list[dict[str, str]], query: str,
) -> tuple[dict[str, str] | None, str, list[dict[str, str]]]:
    """Resolve an exercise as exact, unique partial, ambiguous, or fuzzy."""
    wanted = query.strip().casefold()
    if not wanted:
        return None, "none", []
    exact = [row for row in exercises if row["Title"].casefold() == wanted]
    if exact:
        return sorted(exact, key=_result_sort_key)[0], "exact", []
    substring = _unique_title_rows(
        row for row in exercises if wanted in row["Title"].casefold()
    )
    if len(substring) == 1:
        return substring[0], "substring", []
    if len(substring) > 1:
        substring.sort(key=lambda row: _candidate_sort_key(row, wanted))
        return None, "ambiguous", substring[:3]
    title_by_key: dict[str, str] = {}
    for row in exercises:
        title_by_key.setdefault(row["Title"].casefold(), row["Title"])
    # Keep fuzzy matching useful for small spelling errors without treating a
    # largely unrelated name as a real dataset exercise.
    close = difflib.get_close_matches(wanted, list(title_by_key), n=1, cutoff=0.72)
    if not close:
        return None, "none", []
    fuzzy_rows = [row for row in exercises if row["Title"].casefold() == close[0]]
    return sorted(fuzzy_rows, key=_result_sort_key)[0], "fuzzy", []


def _find_exercise(exercises: list[dict[str, str]], query: str
                   ) -> tuple[dict[str, str] | None, str]:
    """Compatibility wrapper for exact, unique partial, and fuzzy lookups."""
    row, mode, _ = resolve_exercise(exercises, query)
    return row, mode


def ambiguous_rich_messages(candidates: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Offer up to three exact dataset titles as direct-query buttons."""
    heading = (
        "I found several exercises with similar names. "
        "Which one would you like to view?"
    )
    buttons = []
    for row in candidates[:3]:
        button = _details_button(row["Title"])
        button["text"] = row["Title"]
        buttons.append(button)
    return [
        {"text": {"text": [heading]}},
        {"payload": {"richContent": [buttons]}},
    ]


def format_ambiguous(candidates: list[dict[str, str]]) -> str:
    heading = (
        "I found several exercises with similar names. "
        "Which one would you like to view?"
    )
    return "\n".join((heading, *(f"- {row['Title']}" for row in candidates[:3])))


def _query_exercise_name(query_text: str) -> str:
    """Recover the requested name when Dialogflow did not fill the entity."""
    text = query_text.strip().rstrip("?.!").strip()
    patterns = (
        r"(?:tell me (?:more )?about|details? (?:for|about)|describe|explain)\s+(.+)$",
        r"(?:give me details about|show information for|how do i do)\s+(.+)$",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text


def format_exercise_details(row: dict[str, str], *, query: str = "",
                            match_mode: str = "exact") -> str:
    """Format only details that are actually present in the CSV row."""
    if match_mode == "fuzzy":
        heading = f"Closest match: {row['Title']} (searched for '{query}')"
    else:
        heading = row["Title"]
    description = row.get("Desc", "").strip()
    description_line = (
        f"Description: {description}" if description else
        f"Description: {MISSING_DESCRIPTION}"
    )
    return "\n".join((heading, *_plain_field_lines(row), "", description_line))


def details_rich_messages(
    row: dict[str, str], *, query: str = "", match_mode: str = "exact",
) -> list[dict[str, Any]]:
    """Create a compact metadata card with a collapsed instruction accordion."""
    title = (
        f"Closest match: {row['Title']}"
        if match_mode == "fuzzy" else row["Title"]
    )
    description = row.get("Desc", "").strip() or MISSING_DESCRIPTION
    card: list[dict[str, Any]] = [{
        "type": "description",
        "title": title,
        "text": _card_field_lines(row),
    }, {
        "type": "accordion",
        "title": "How to perform",
        "subtitle": "Tap to view instructions",
        "text": description,
    }]
    if match_mode == "fuzzy" and query:
        card.insert(1, {
            "type": "description",
            "title": "Search note",
            "text": [f"You searched for · {query}"],
        })
    # Keep a short standard text message first so the Dialogflow ES test console
    # has a readable response while Messenger renders the richer card below it.
    return [
        {"text": {"text": ["Here are the exercise details."]}},
        {"payload": {"richContent": [card]}},
    ]


def _recommendation_context(
    payload: dict[str, Any], results: list[dict[str, str]], *,
    body_part: str = "", equipment: str = "", level: str = "",
    exercise_type: str = "", page: int = 1,
) -> list[dict[str, Any]]:
    if not results:
        return []
    session = str(payload.get("session") or "").rstrip("/")
    if not session:
        return []
    names = [row["Title"] for row in results]
    parameters: dict[str, Any] = {
        "exercise_names": names,
        "filter_body_part": body_part,
        "filter_equipment": equipment,
        "filter_level": level,
        "filter_exercise_type": exercise_type,
        "recommendation_page": page,
    }
    parameters.update({
        f"recommendation_{index}": name
        for index, name in enumerate(names, start=1)
    })
    return [{
        "name": f"{session}/contexts/last_recommendations",
        "lifespanCount": 5,
        "parameters": parameters,
    }]


def _recommendation_filters(payload: dict[str, Any]) -> dict[str, Any]:
    """Recover the first-page filters used by a Show more request."""
    query_result = payload.get("queryResult") or {}
    for context in query_result.get("outputContexts") or []:
        if str(context.get("name", "")).casefold().endswith(
            "/contexts/last_recommendations"
        ):
            parameters = context.get("parameters") or {}
            page_value = parameters.get("recommendation_page", 1)
            try:
                page = int(float(page_value))
            except (TypeError, ValueError):
                page = 1
            return {
                "body_part": scalar(parameters.get("filter_body_part")),
                "equipment": scalar(parameters.get("filter_equipment")),
                "level": scalar(parameters.get("filter_level")),
                "exercise_type": scalar(parameters.get("filter_exercise_type")),
                "page": page,
            }
    return {}


def _query_aware_aggregates(query_text: str, body_part: str,
                            equipment: str) -> tuple[str, str]:
    """Recover aggregate words that Dialogflow may canonicalize to one value."""
    text = query_text.casefold()
    if re.search(r"\blegs?\b", text):
        body_part = "legs"
    elif body_part.casefold() in {"lats", "back"} and re.search(r"\bback\b", text):
        body_part = "back"
    if re.search(r"\b(body\s*weight|no equipment|without equipment)\b", text):
        equipment = "no equipment"
    return body_part, equipment


def handle_dialogflow(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle one Dialogflow ES webhook request body."""
    query_result = payload.get("queryResult") or {}
    action = str(query_result.get("action") or "").strip()
    parameters = query_result.get("parameters") or {}
    exercises = load_exercises()

    if action in RECOMMENDATION_ACTIONS:
        query_text = str(query_result.get("queryText") or "").strip()
        body_part = scalar(parameters.get("body_part"))
        equipment = scalar(parameters.get("equipment"))
        level = scalar(parameters.get("fitness_level") or parameters.get("level"))
        exercise_type = scalar(parameters.get("exercise_type") or parameters.get("goal"))
        body_part, equipment = _query_aware_aggregates(
            query_text, body_part, equipment
        )
        if action == "exercise.by_body_part" and not body_part:
            return {"fulfillmentText": "Which body part would you like to train?"}
        if action == "exercise.by_equipment" and not equipment:
            return {"fulfillmentText": "Which equipment would you like to use?"}
        if action == "exercise.by_level" and not level:
            return {"fulfillmentText": (
                "What is your fitness level: Beginner, Intermediate, or Expert?"
            )}
        if not any((body_part, equipment, level, exercise_type)):
            return {"fulfillmentText": (
                "Tell me at least one fitness level, body part, equipment, or "
                "training type."
            )}
        available = select_exercises(
            exercises, body_part=body_part, equipment=equipment, level=level,
            exercise_type=exercise_type, limit=6,
        )
        results = available
        response: dict[str, Any] = {"fulfillmentText": format_exercises(results)}
        contexts = _recommendation_context(
            payload, results, body_part=body_part, equipment=equipment,
            level=level, exercise_type=exercise_type, page=1,
        )
        if contexts:
            response["outputContexts"] = contexts
        if not results:
            summary = _filter_summary(
                body_part=body_part, equipment=equipment, level=level,
                exercise_type=exercise_type,
            )
            if summary:
                response["fulfillmentText"] = (
                    f"No exact match was found for {summary}. Try changing one option."
                )
        else:
            response["fulfillmentMessages"] = recommendation_rich_messages(
                results, local_pager=len(results) > 3,
            )
        return response

    if action in DETAIL_ACTIONS:
        exercise_name = display_scalar(parameters.get("exercise_name"))
        query_text = str(query_result.get("queryText") or "").strip()
        index = _ordinal_index(parameters.get("result_index"))
        if not exercise_name and index is not None:
            names = _context_names(payload)
            if index >= len(names):
                return {"fulfillmentText": (
                    "That number is outside the current recommendation list. "
                    "Ask for a new exercise recommendation first."
                )}
            exercise_name = names[index]
        if not exercise_name and query_text and index is None:
            exercise_name = _query_exercise_name(query_text)
        if not exercise_name:
            return {"fulfillmentText": (
                "Which exercise would you like details about? Please give its name, "
                "or ask about the first through sixth recent recommendation."
            )}
        row, mode, candidates = resolve_exercise(exercises, exercise_name)
        if mode == "ambiguous":
            return {
                "fulfillmentText": format_ambiguous(candidates),
                "fulfillmentMessages": ambiguous_rich_messages(candidates),
            }
        if row is None:
            return {"fulfillmentText": (
                "That exercise name was not recognised. Check the spelling or ask "
                "for a recommendation first."
            )}
        return {
            "fulfillmentText": format_exercise_details(
                row, query=exercise_name, match_mode=mode
            ),
            "fulfillmentMessages": details_rich_messages(
                row, query=exercise_name, match_mode=mode
            ),
        }

    return {"fulfillmentText": SCOPE_MESSAGE}


def _find_term(text: str, options: dict[str, tuple[str, ...]]) -> str:
    for term in sorted(options, key=len, reverse=True):
        if re.search(rf"\b{re.escape(term)}\b", text):
            targets = options[term]
            # Preserve aggregate aliases, but normalize one-to-one aliases to
            # the canonical dataset value Dialogflow would normally return.
            return targets[0].casefold() if len(targets) == 1 else term
    return ""


def website_chat_payload(message: str) -> dict[str, Any]:
    """Convert a simple website question into the Dialogflow webhook shape."""
    original = message.strip()
    text = original.casefold()
    ordinal = next((
        word for word in ("first", "second", "third", "1st", "2nd", "3rd")
        if re.search(rf"\b{word}\b", text)
    ), "")
    details_match = re.search(
        r"(?:tell me (?:more )?about|details? (?:for|about)|describe)\s+(.+)$", text
    )
    exact_titles = {row["Title"].casefold() for row in load_exercises()}
    bare_detail = text in exact_titles or text == "barbell bench press"
    if details_match or bare_detail or (ordinal and "recommend" in text):
        return {"queryResult": {
            "action": "exercise.details", "queryText": original,
            "parameters": {
                "exercise_name": (
                    details_match.group(1).strip() if details_match and not ordinal
                    else original if bare_detail else ""
                ),
                "result_index": ordinal,
            },
        }}
    parameters = {
        "body_part": _find_term(text, BODY_PART_MAP),
        "equipment": _find_term(text, EQUIPMENT_MAP),
        "fitness_level": _find_term(text, LEVEL_MAP),
        "exercise_type": _find_term(text, TYPE_MAP),
    }
    return {"queryResult": {
        "action": "exercise.recommendation", "queryText": original,
        "parameters": parameters,
    }}


try:
    from flask import Flask, jsonify, request

    app = Flask(__name__)

    @app.get("/")
    def website() -> tuple[dict[str, str], int]:
        return {"status": "FitBot webhook is running"}, 200

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "FitBot webhook is running"}, 200

    @app.post("/webhook")
    def webhook():
        return jsonify(handle_dialogflow(request.get_json(silent=True) or {}))

    @app.post("/website-chat")
    def website_chat():
        body = request.get_json(silent=True) or {}
        message = str(body.get("message", "")).strip()
        if not message:
            return jsonify({"answer": "Please enter an exercise question."}), 400
        payload = website_chat_payload(message)
        if body.get("outputContexts"):
            payload["queryResult"]["outputContexts"] = body["outputContexts"]
        result = handle_dialogflow(payload)
        response: dict[str, Any] = {"answer": result["fulfillmentText"]}
        if result.get("outputContexts"):
            response["outputContexts"] = result["outputContexts"]
        return jsonify(response)

except ImportError:
    app = None


if __name__ == "__main__":
    if app is None:
        raise SystemExit("Install dependencies first: pip install -r requirements.txt")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
