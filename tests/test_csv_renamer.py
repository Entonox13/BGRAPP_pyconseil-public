#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from src.services.csv_renamer import (
    CsvRenamerError,
    display_name_without_extension,
    normalize_csv_filename,
    plan_csv_renames,
    rename_csv_files,
)


def test_display_name_without_extension():
    assert display_name_without_extension("mathematiques.csv") == "mathematiques"
    assert display_name_without_extension("Export CSV(10).csv") == "Export CSV(10)"


def test_normalize_csv_filename_adds_extension():
    assert normalize_csv_filename("mathematiques") == "mathematiques.csv"
    assert normalize_csv_filename(" francais.csv ") == "francais.csv"
    assert normalize_csv_filename("Anglais LV1") == "Anglais LV1.csv"


def test_plan_csv_renames_skips_unchanged_names(tmp_path):
    (tmp_path / "Export CSV(1).csv").write_text("a,b\n", encoding="utf-8")
    pairs, errors = plan_csv_renames(
        str(tmp_path),
        {"Export CSV(1).csv": "Export CSV(1).csv"},
    )
    assert errors == []
    assert pairs == []


def test_rename_csv_files_success(tmp_path):
    source = tmp_path / "Export CSV(10).csv"
    source.write_text("eleve,note\n", encoding="utf-8")

    count = rename_csv_files(
        str(tmp_path),
        {"Export CSV(10).csv": "mathematiques"},
    )

    assert count == 1
    assert not source.exists()
    assert (tmp_path / "mathematiques.csv").exists()


def test_rename_csv_files_rejects_duplicate_targets(tmp_path):
    (tmp_path / "a.csv").write_text("1\n", encoding="utf-8")
    (tmp_path / "b.csv").write_text("2\n", encoding="utf-8")

    with pytest.raises(CsvRenamerError) as exc:
        rename_csv_files(
            str(tmp_path),
            {
                "a.csv": "mathematiques.csv",
                "b.csv": "mathematiques.csv",
            },
        )

    assert "double" in str(exc.value).lower()


def test_rename_csv_files_rejects_existing_target(tmp_path):
    (tmp_path / "a.csv").write_text("1\n", encoding="utf-8")
    (tmp_path / "mathematiques.csv").write_text("2\n", encoding="utf-8")

    with pytest.raises(CsvRenamerError):
        rename_csv_files(str(tmp_path), {"a.csv": "mathematiques.csv"})
