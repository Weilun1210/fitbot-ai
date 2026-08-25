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
            "Choose what you want to find. FitBox will prepare a question for you.",
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

    def test_chat_stays_centered_when_guide_opens(self) -> None:
        self.assertIn("margin-inline: auto", SOURCE)
        self.assertIn(".drawer {\n            position: absolute;", SOURCE)
        self.assertNotIn(
            ".workspace.drawer-open .drawer {\n            width: var(--drawer-width);",
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
        ):
            self.assertIn(selector, SOURCE)

    def test_script_block_is_present_once(self) -> None:
        self.assertEqual(len(re.findall(r"<script>", SOURCE)), 1)
        self.assertEqual(len(re.findall(r"</script>", SOURCE)), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
