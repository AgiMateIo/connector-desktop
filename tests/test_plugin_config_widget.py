"""Tests for the plugin configuration card on the Plugins tab.

The JSON editor is an advanced surface: collapsed, the card is one row, and
the editor only gets a real height when it is asked for. The bug this guards
against is the opposite — an always-visible editor squeezed by the scroll
layout down to a single line, which read as an empty config.
"""

import json
import os
import sys

import pytest


@pytest.fixture(scope="module")
def qt_app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def config_path(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"enabled": True, "answer": 42}, indent=2), encoding="utf-8"
    )
    return path


@pytest.fixture
def card(qt_app, config_path):
    from ui.settings import PluginConfigWidget

    widget = PluginConfigWidget("file_watcher", "File Watcher", config_path)
    yield widget
    widget.deleteLater()


class TestCollapsedCard:
    """The list is for scanning; the JSON is asked for."""

    def test_the_config_starts_hidden(self, card):
        assert card.config_edit.isHidden()
        assert card.configure_btn.text() == "Configure"

    def test_the_summary_names_the_config_size(self, card):
        # Pretty-printed: "{" + two entries + "}".
        assert card.summary_label.text() == "Configuration · 4 lines"

    def test_the_summary_follows_edits(self, card):
        card.config_edit.setPlainText('{\n  "answer": 43\n}')

        assert card.summary_label.text() == "Configuration · 3 lines"

    def test_an_empty_config_says_so(self, card):
        card.config_edit.setPlainText("")

        assert card.summary_label.text() == "No configuration yet"


class TestExpandedCard:
    """The editor gets a height the scroll layout cannot squeeze away."""

    def test_expanding_shows_the_editor(self, card):
        card.configure_btn.click()

        assert not card.config_edit.isHidden()
        assert card.configure_btn.text() == "Hide"

    def test_the_editor_is_marked_for_its_height_rule(self, card):
        # QSS min-height overrides setMinimumHeight, so the height lives in
        # the sheet keyed by this role — the widget's job is to carry it.
        assert card.config_edit.property("role") == "config"

    def test_collapsing_hides_the_editor_again(self, card):
        card.configure_btn.click()
        card.configure_btn.click()

        assert card.config_edit.isHidden()
        assert card.configure_btn.text() == "Configure"


class TestSaving:
    def test_a_collapsed_card_still_saves_its_edits(self, card, config_path):
        card.config_edit.setPlainText('{"enabled": true, "answer": 43}')

        card.save_config()

        assert json.loads(config_path.read_text(encoding="utf-8"))["answer"] == 43
