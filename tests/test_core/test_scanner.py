"""Tests for project scanner."""

from pathlib import Path

from matoi.core.scanner import scan_project


def test_scan_current_project():
    """Scan the matoi project itself."""
    scan = scan_project(Path.cwd())
    assert scan.name != ""
    assert scan.total_files > 0
    assert "Python" in scan.languages


def test_scan_summary():
    scan = scan_project(Path.cwd())
    summary = scan.summary()
    assert scan.name in summary
    assert "Files:" in summary
