"""Tests for GSProject's use of base_app's project-file format.

Covers gzip compression, app-compatibility checking, and the
schema-migration route.
"""

import gzip
import sys
from pathlib import Path

import jsonpickle
import pytest

APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

from base_app.ProjectFile import (  # noqa: E402
    IncompatibleProjectFileError,
    decode_project,
    encode_project,
)
from GSProject import GSProject  # noqa: E402

APP_ID = "GroupSelect"
APP_VERSION = "v2.0.0"


def test_round_trip_is_gzip_compressed():
    """A saved project file round-trips and is actually gzip-compressed."""
    project = GSProject()
    raw = encode_project(project, APP_ID, APP_VERSION)

    # Not raising here is the actual assertion: gzip.decompress() rejects
    # anything that isn't gzip-compressed.
    gzip.decompress(raw)

    restored = decode_project(raw, GSProject, APP_ID)
    assert isinstance(restored, GSProject)
    assert restored.settings == project.settings


def test_project_state_survives_round_trip():
    """Non-default project state survives a save/reopen cycle unchanged."""
    project = GSProject()
    project.terms = {1: [["M", "Male"], ["F", "Female"]]}
    project.manuals = {3: 0}
    project.settings["n_part_per_group"] = 12

    raw = encode_project(project, APP_ID, APP_VERSION)
    restored = decode_project(raw, GSProject, APP_ID)

    assert restored.terms == project.terms
    assert restored.manuals == project.manuals
    assert restored.settings["n_part_per_group"] == 12


def test_rejects_file_from_a_different_app():
    """A project file saved by a different app is rejected cleanly."""
    project = GSProject()
    raw = encode_project(project, "SomeOtherApp", "v1.0")

    with pytest.raises(IncompatibleProjectFileError):
        decode_project(raw, GSProject, APP_ID)


def test_rejects_garbage_file():
    """A file that isn't a project file at all is rejected cleanly."""
    with pytest.raises(IncompatibleProjectFileError):
        decode_project(b"not a project file", GSProject, APP_ID)


def test_legacy_uncompressed_file_still_opens():
    """A pre-envelope, uncompressed `.gspr` file still opens today."""
    project = GSProject()
    legacy_raw = jsonpickle.encode(project, keys=True).encode("utf-8")

    restored = decode_project(legacy_raw, GSProject, APP_ID)
    assert isinstance(restored, GSProject)


def test_migrations_hook_is_applied_on_load(monkeypatch):
    """A registered migration step runs when opening an older file.

    This proves out the migration route for future use even though
    GSProject has no real migration to register yet.
    """

    def _v1_to_v2(data):
        data["migrated_marker"] = True
        return data

    monkeypatch.setattr(GSProject, "SCHEMA_VERSION", 2)
    monkeypatch.setattr(
        GSProject, "migrations", classmethod(lambda cls: {1: _v1_to_v2})
    )

    project = GSProject()  # encoded at (implicit) schema version 1
    raw = jsonpickle.encode(project, keys=True).encode("utf-8")

    restored = decode_project(raw, GSProject, APP_ID)
    assert restored.migrated_marker is True
