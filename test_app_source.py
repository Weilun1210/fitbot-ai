"""Static regression checks for the FitBox Streamlit integration shell."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SOURCE = Path(__file__).with_name("app.py").read_text(encoding="utf-8")


class FitBoxStreamlitV41Tests(unittest.TestCase):
    def test_visible_copy_is_natural(self) -> None:
        self.assertIn("Personalised exercise discovery", SOURCE)
        self.assertIn(
            "Choose a supported question. FitBox will prepare the exact wording for you.",
            SOURCE,
        )
        self.assertNotIn("Dataset-based exercise discovery", SOURCE)
        self.assertNotIn("find in the exercise dataset", SOURCE)

    def test_chat_panel_is_contained_in_stage(self) -> None:
        self.assertIn(
            'panel.style.setProperty("position", "absolute", "important")',
            SOURCE,
        )
        self.assertIn(
            'panel.style.setProperty("inset", "0", "important")',
            SOURCE,
        )
        self.assertNotIn("stageRect", SOURCE)
        self.assertNotIn(
            'panel.style.setProperty("position", "fixed", "important")',
            SOURCE,
        )

    def test_desktop_guide_pushes_chat_and_mobile_guide_overlays(self) -> None:
        self.assertIn("flex: 0 0 0;", SOURCE)
        self.assertIn("flex-basis: var(--drawer-width);", SOURCE)
        self.assertIn("width: var(--drawer-width);", SOURCE)
        self.assertIn(".backdrop { display: block; }", SOURCE)
        self.assertNotIn(
            ".workspace.drawer-open .backdrop { opacity: .18",
            SOURCE,
        )

    def test_user_messages_align_to_the_right(self) -> None:
        self.assertIn("width: fit-content !important", SOURCE)
        self.assertIn("margin-left: auto !important", SOURCE)
        self.assertIn("margin-right: 8px !important", SOURCE)

    def test_chat_uses_the_full_browser_page(self) -> None:
        self.assertIn("max-width: none", SOURCE)
        self.assertIn("height: 100vh", SOURCE)
        self.assertIn('chat.style.setProperty("inset", "0", "important")', SOURCE)
        self.assertIn('openButton.style.setProperty("display", "none", "important")', SOURCE)
        self.assertNotIn('chat.style.setProperty("inset", "12px", "important")', SOURCE)

    def test_extra_large_ui_remains_viewport_based(self) -> None:
        self.assertIn("--drawer-width: 430px", SOURCE)
        self.assertIn("padding: 15px 28px;", SOURCE)
        self.assertIn('font: 800 26px/1.2 "Manrope"', SOURCE)
        self.assertIn("font-size: 18px !important;", SOURCE)
        self.assertIn("min-height: 66px !important;", SOURCE)
        self.assertIn("fitbox-input-theme", SOURCE)

    def test_question_guide_matches_dialogflow_training(self) -> None:
        for phrase in (
            "Recommend exercises",
            "Show me beginner exercises",
            "Show me exercises using dumbbells",
            "Show me strength exercises",
            "Recommend beginner chest exercises using dumbbells",
            "Show me expert barbell strength exercises",
            "Find intermediate stretching exercises for lower back",
            "Tell me about Partner plank band row",
        ):
            self.assertIn(phrase, SOURCE)
        self.assertIn('id="tested-combination"', SOURCE)
        self.assertIn('id="exercise-name"', SOURCE)
        self.assertNotIn('id="personalised-flow"', SOURCE)
        self.assertNotIn('id="exercise-name" type="text"', SOURCE)
        self.assertNotIn("buildPersonalisedPrompt", SOURCE)

    def test_streamlit_wrappers_cannot_create_vertical_whitespace(self) -> None:
        self.assertIn('[data-testid="stMain"]', SOURCE)
        self.assertIn("overflow: hidden !important;", SOURCE)
        self.assertIn('[data-testid="stVerticalBlock"]', SOURCE)
        self.assertIn("gap: 0 !important;", SOURCE)
        self.assertIn(
            '[data-testid="stElementContainer"]:has(iframe[title="st.iframe"])',
            SOURCE,
        )
        self.assertIn("flex: 0 0 100vh !important;", SOURCE)

    def test_message_list_scroll_and_events_are_wired(self) -> None:
        for text in (
            "function findMessageList()",
            "function scrollToLatest(delay = 0)",
            "new MutationObserver",
            'messenger.addEventListener("df-user-input-entered"',
            'messenger.addEventListener("df-response-received"',
            "list.scrollTop = list.scrollHeight",
            "scrollbar-gutter: stable",
            'panel.style.setProperty("display", "flex", "important")',
            'panel.style.setProperty("flex-direction", "column", "important")',
            'inputShell.style.setProperty("flex", "0 0 auto", "important")',
            "if (shell) shell.scrollTop = 0",
            'panel.dataset.fitboxScrollPinned !== "true"',
            "if (panel.scrollTop !== 0) panel.scrollTop = 0",
        ):
            self.assertIn(text, SOURCE)

    def test_rich_cards_receive_fitbox_theme(self) -> None:
        for selector in (
            'nestedRoot.host?.localName === "df-card"',
            'nestedRoot.host?.localName === "df-description"',
            'nestedRoot.host?.localName === "df-accordion"',
            "border-left: 4px solid #b8f22e",
            "fitbox-card-theme",
            "white-space: pre-line !important",
            "border-left: 4px solid #b8f22e !important",
            "line-height: 1.85 !important",
            'nestedRoot.host?.localName === "df-button"',
            "fitbox-detail-button-theme",
            "background: #b8f22e !important",
        ):
            self.assertIn(selector, SOURCE)

    def test_view_details_button_sends_a_normal_ai_question(self) -> None:
        for text in (
            "function findSendControl()",
            "function sendPrompt(value)",
            'messenger.addEventListener("df-button-clicked"',
            'eventName !== "FITBOX_VIEW_DETAILS"',
            "event.preventDefault()",
            "parameters.exercise_name",
            "sendPrompt(query)",
            "detailSendLockedUntil = Date.now() + 1000",
        ):
            self.assertIn(text, SOURCE)

    def test_script_block_is_present_once(self) -> None:
        self.assertEqual(len(re.findall(r"<script>", SOURCE)), 1)
        self.assertEqual(len(re.findall(r"</script>", SOURCE)), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
