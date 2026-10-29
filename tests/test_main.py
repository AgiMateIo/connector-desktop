"""Tests for the application entry point."""

import sys
import types
from unittest.mock import MagicMock

import main


def _fake_appkit():
    module = types.ModuleType("AppKit")
    module.NSApplication = MagicMock()
    module.NSApplicationActivationPolicyAccessory = 1
    return module


def test_hide_from_dock_sets_accessory_policy_on_macos(monkeypatch):
    """A source run has no Info.plist, so the policy is set at runtime."""
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delattr(sys, "frozen", raising=False)
    appkit = _fake_appkit()
    monkeypatch.setitem(sys.modules, "AppKit", appkit)

    main._hide_from_dock()

    app = appkit.NSApplication.sharedApplication.return_value
    app.setActivationPolicy_.assert_called_once_with(1)


def test_hide_from_dock_is_noop_off_macos(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delattr(sys, "frozen", raising=False)
    appkit = _fake_appkit()
    monkeypatch.setitem(sys.modules, "AppKit", appkit)

    main._hide_from_dock()

    appkit.NSApplication.sharedApplication.assert_not_called()


def test_hide_from_dock_skips_bundled_app(monkeypatch):
    """The bundle already carries LSUIElement in its Info.plist."""
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    appkit = _fake_appkit()
    monkeypatch.setitem(sys.modules, "AppKit", appkit)

    main._hide_from_dock()

    appkit.NSApplication.sharedApplication.assert_not_called()
