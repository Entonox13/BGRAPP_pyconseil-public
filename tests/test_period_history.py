#!/usr/bin/env python3
"""
Tests unitaires pour la gestion de l'historique par période (period_history).
"""

import os
import json
import tempfile
from pathlib import Path

import pytest

from src.models.bulletin import Bulletin, Eleve, AppreciationMatiere, PeriodeData
from src.services.json_generator import save_output_json
from src.utils.semester import Period
from src.services.period_history import (
    read_payload,
    update_file_metadata,
    period_code_of_file,
    period_code_from_filename,
    suggested_period_code_for_link,
    default_period_filename,
    discover_sibling_period_files,
    resolve_period_links,
    add_period_link,
    remove_period_link,
    set_period_link_code,
    load_history_bulletins,
    build_display_bulletins,
    normalize_linked_bulletins,
    remap_bulletins_period_code,
)


def _make_bulletin(nom, prenom, code, matieres):
    """Construit un Bulletin avec une seule période `code`."""
    bulletin = Bulletin(Eleve(nom=nom, prenom=prenom))
    for mname, periode in matieres.items():
        appreciation = AppreciationMatiere(mname, periodes={code: periode})
        bulletin.add_matiere(appreciation)
    return bulletin


def _write_period_file(path, code, students, appreciation_generale=None):
    """Écrit un fichier JSON ne contenant qu'une période."""
    bulletins = []
    for nom, prenom, matieres in students:
        bulletin = _make_bulletin(nom, prenom, code, matieres)
        if appreciation_generale:
            bulletin.set_appreciation_generale(code, appreciation_generale)
        bulletins.append(bulletin)
    metadata = {
        "current_period": code,
        "period_system": Period[code].system.value,
    }
    save_output_json(bulletins, path, metadata=metadata)
    return path


class TestNaming:
    def test_default_period_filename(self):
        assert default_period_filename(None, "T3") == "output_T3.json"
        assert default_period_filename("/tmp", "s1") == "output_S1.json"
        assert default_period_filename(None, "", base="conseil") == "conseil.json"


class TestPayload:
    def test_read_payload_separates_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "output_T3.json")
            _write_period_file(path, "T3", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=14.0)}),
            ])
            metadata, data = read_payload(path)
            assert metadata.get("current_period") == "T3"
            assert len(data) == 1
            assert data[0]["Nom"] == "DUPONT"

    def test_period_code_of_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "x.json")
            _write_period_file(path, "T2", [
                ("MARTIN", "Bob", {"Maths": PeriodeData(moyenne=10.0)}),
            ])
            assert period_code_of_file(path) == "T2"

    def test_period_code_from_filename_over_metadata(self):
        """Un fichier output_T2.json mal etiquete S2 doit etre suggere en T2."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "output_T2.json")
            _write_period_file(path, "S2", [
                ("MARTIN", "Bob", {"Maths": PeriodeData(moyenne=10.0)}),
            ])
            assert period_code_of_file(path) == "S2"  # metadonnees d'abord
            assert period_code_from_filename(path) == "T2"
            assert suggested_period_code_for_link(path) == "T2"

    def test_update_file_metadata_preserves_bulletins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "output_T3.json")
            _write_period_file(path, "T3", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=14.0)}),
            ])
            metadata, _ = read_payload(path)
            metadata["period_links"] = {"T2": "output_T2.json"}
            update_file_metadata(path, metadata)
            new_meta, data = read_payload(path)
            assert new_meta["period_links"] == {"T2": "output_T2.json"}
            assert len(data) == 1
            assert data[0]["Nom"] == "DUPONT"


class TestDiscovery:
    def test_discover_sibling_period_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t1 = os.path.join(tmp, "output_T1.json")
            t2 = os.path.join(tmp, "output_T2.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(t1, "T1", students)
            _write_period_file(t2, "T2", students)

            found = discover_sibling_period_files(cur, "T3")
            assert set(found.keys()) == {"T1", "T2"}
            assert os.path.abspath(found["T1"]) == os.path.abspath(t1)
            # Le fichier courant ne doit pas apparaître
            assert "T3" not in found

    def test_resolve_links_auto(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t1 = os.path.join(tmp, "output_T1.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(t1, "T1", students)

            links = resolve_period_links(cur, {}, "T3")
            assert set(links.keys()) == {"T1"}

    def test_resolve_links_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t1 = os.path.join(tmp, "output_T1.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(t1, "T1", students)

            metadata = {"period_links_excluded": ["T1"]}
            links = resolve_period_links(cur, metadata, "T3")
            assert links == {}

    def test_add_and_remove_manual_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            other = os.path.join(tmp, "ancien_T1.json")  # nom hors convention
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(other, "T1", students)

            metadata = {}
            code = add_period_link(metadata, cur, other)
            assert code == "T1"
            assert "period_links" in metadata
            links = resolve_period_links(cur, metadata, "T3")
            assert "T1" in links

            remove_period_link(metadata, cur, "T1", "T3")
            links = resolve_period_links(cur, metadata, "T3")
            assert "T1" not in links

    def test_remove_auto_link_adds_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t1 = os.path.join(tmp, "output_T1.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(t1, "T1", students)

            metadata = {}
            remove_period_link(metadata, cur, "T1", "T3")
            assert "T1" in metadata.get("period_links_excluded", [])
            links = resolve_period_links(cur, metadata, "T3")
            assert "T1" not in links

    def test_add_link_with_manual_period_code(self):
        """Un JSON etiquete S2 peut etre lie manuellement en T2."""
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t2 = os.path.join(tmp, "output_T2.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(t2, "S2", students)

            metadata = {}
            code = add_period_link(metadata, cur, t2, period_code="T2")
            assert code == "T2"
            assert metadata["period_link_overrides"][os.path.basename(t2)] == "T2"
            links = resolve_period_links(cur, metadata, "T3")
            assert links.get("T2") == os.path.abspath(t2)
            assert "S2" not in links

    def test_set_period_link_code_corrects_auto_discovery(self):
        """Corriger une auto-decouverte S2 -> T2 via surcharge."""
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t2 = os.path.join(tmp, "output_T2.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0)})]
            _write_period_file(cur, "T3", students)
            _write_period_file(t2, "S2", students)

            metadata = {}
            found = discover_sibling_period_files(cur, "T3", metadata)
            assert "S2" in found

            set_period_link_code(metadata, cur, t2, "T2", "T3")
            links = resolve_period_links(cur, metadata, "T3")
            assert "T2" in links
            assert "S2" not in links


class TestLinkedPeriodNormalization:
    def test_remap_s2_content_linked_as_t2(self):
        """Fichier T2/output.json avec donnees S2 : fusion sous cle T2."""
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t2 = os.path.join(tmp, "output_T2.json")
            students = [("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=12.0, appreciation="s2")})]
            _write_period_file(cur, "T3", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=14.0, appreciation="t3")}),
            ])
            # Contenu S2 dans un fichier nomme T2 (cas reel utilisateur)
            _write_period_file(t2, "S2", students)

            metadata = {}
            add_period_link(metadata, cur, t2, period_code="T2")
            links = resolve_period_links(cur, metadata, "T3")
            history = load_history_bulletins(links)
            assert "T2" in history
            maths = history["T2"][0].get_matiere("Maths")
            assert "T2" in maths.periodes
            assert maths.get_periode("T2").moyenne == 12.0
            assert "S2" not in maths.periodes

            current = [Bulletin.from_dict(d) for d in read_payload(cur)[1]]
            display = build_display_bulletins(current, history, "T3")
            merged = display[0].get_matiere("Maths")
            assert merged.get_periode("T3").moyenne == 14.0
            assert merged.get_periode("T2").moyenne == 12.0

    def test_merge_matches_matiere_name_variants(self):
        """Fusionne malgré des libellés différents (espaces / abréviations)."""
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t2 = os.path.join(tmp, "output_T2.json")
            _write_period_file(cur, "T3", [
                ("DUPONT", "Alice", {
                    "AnglaisLV1": PeriodeData(moyenne=14.0),
                    "EducationPhysiqueSportive": PeriodeData(moyenne=16.0),
                }),
            ])
            other = _make_bulletin(
                "DUPONT", "Alice", "S2",
                {"Anglais LV1": PeriodeData(moyenne=11.0), "EPS": PeriodeData(moyenne=15.0)},
            )
            save_output_json([other], t2)

            metadata = {}
            add_period_link(metadata, cur, t2, period_code="T2")
            links = resolve_period_links(cur, metadata, "T3")
            history = load_history_bulletins(links)
            current = [Bulletin.from_dict(d) for d in read_payload(cur)[1]]
            display = build_display_bulletins(current, history, "T3")
            bulletin = display[0]
            assert bulletin.get_matiere("AnglaisLV1").get_periode("T2").moyenne == 11.0
            assert bulletin.get_matiere("EducationPhysiqueSportive").get_periode("T2").moyenne == 15.0

    def test_build_display_merges_other_periods(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t1 = os.path.join(tmp, "output_T1.json")
            _write_period_file(cur, "T3", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=14.0, appreciation="T3 maths")}),
            ])
            _write_period_file(t1, "T1", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=10.0, appreciation="T1 maths")}),
            ])

            _meta, data = read_payload(cur)
            current = [Bulletin.from_dict(d) for d in data]
            links = resolve_period_links(cur, {}, "T3")
            history = load_history_bulletins(links)
            display = build_display_bulletins(current, history, "T3")

            assert len(display) == 1
            maths = display[0].get_matiere("Maths")
            # La période courante est préservée
            assert maths.get_periode("T3").moyenne == 14.0
            # La période liée est fusionnée
            assert maths.get_periode("T1").moyenne == 10.0

    def test_build_display_does_not_overwrite_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            other = os.path.join(tmp, "output_T1.json")
            _write_period_file(cur, "T3", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=14.0)}),
            ])
            # Fichier lié qui contient (à tort) aussi T3 : ne doit pas écraser
            other_b = _make_bulletin("DUPONT", "Alice", "T1", {"Maths": PeriodeData(moyenne=5.0)})
            other_b.matieres["Maths"].periodes["T3"] = PeriodeData(moyenne=99.0)
            save_output_json([other_b], other, metadata={"current_period": "T1"})

            _meta, data = read_payload(cur)
            current = [Bulletin.from_dict(d) for d in data]
            history = load_history_bulletins({"T1": other})
            display = build_display_bulletins(current, history, "T3")

            maths = display[0].get_matiere("Maths")
            assert maths.get_periode("T3").moyenne == 14.0  # inchangé
            assert maths.get_periode("T1").moyenne == 5.0

    def test_build_display_does_not_mutate_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            cur = os.path.join(tmp, "output_T3.json")
            t1 = os.path.join(tmp, "output_T1.json")
            _write_period_file(cur, "T3", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=14.0)}),
            ])
            _write_period_file(t1, "T1", [
                ("DUPONT", "Alice", {"Maths": PeriodeData(moyenne=10.0)}),
            ])
            _meta, data = read_payload(cur)
            current = [Bulletin.from_dict(d) for d in data]
            history = load_history_bulletins({"T1": t1})
            _display = build_display_bulletins(current, history, "T3")

            # self.bulletins (current) ne doit contenir que la période courante
            maths = current[0].get_matiere("Maths")
            assert maths.get_periode("T1") is None
            assert maths.get_periode("T3").moyenne == 14.0


EXEMPLES_DIR = Path("exemples")
HAS_EXAMPLES = (EXEMPLES_DIR / "source.xlsx").exists() and any(EXEMPLES_DIR.glob("*.csv"))


@pytest.mark.skipif(not HAS_EXAMPLES, reason="Données d'exemple non disponibles")
class TestProcessorSinglePeriod:
    def test_generated_json_contains_single_period(self):
        from src.services.main_processor import process_directory_to_json

        with tempfile.TemporaryDirectory() as tmp:
            output = os.path.join(tmp, "output.json")
            # 1er traitement imposant T1
            process_directory_to_json("exemples", output, period_override=Period.T1)
            # 2e traitement imposant T2 dans le MÊME fichier : pas d'accumulation
            process_directory_to_json("exemples", output, period_override=Period.T2)

            _meta, data = read_payload(output)
            present = set()
            for item in data:
                for key in item.keys():
                    for code in ("S1", "S2", "T1", "T2", "T3"):
                        if key.endswith(code) or f"{code}" in key:
                            pass
                matieres = item.get("Matieres", {})
                for app in matieres.values():
                    for k in app.keys():
                        for code in ("T1", "T2", "T3", "S1", "S2"):
                            if code in k:
                                present.add(code)
            # Le fichier ne doit refléter que la dernière période traitée (T2)
            assert "T1" not in present


class TestEditionWindowFilePeriod:
    """Régression : le sélecteur d'affichage ne doit pas altérer la période du fichier."""

    def test_metadata_save_uses_file_period_not_view_period(self):
        from src.gui.edition_window import EditionWindow
        from src.utils.semester import Period

        window = EditionWindow.__new__(EditionWindow)
        window.metadata = {"current_period": "T3", "period_system": "TRIMESTRE"}
        window._file_period = Period.T3
        window.period = Period.T1  # période affichée basculée vers une période liée

        meta = EditionWindow._metadata_for_save(window)
        assert meta["current_period"] == "T3"
        assert meta["period_system"] == "TRIMESTRE"

    def test_period_selector_does_not_change_editable_codes(self):
        from unittest.mock import Mock
        from src.gui.edition_window import EditionWindow
        from src.utils.semester import Period

        window = EditionWindow.__new__(EditionWindow)
        window._file_period = Period.T3
        window.period = Period.T3
        window.editable_codes = ["T3"]
        window._period_choice_codes = ["T1", "T3"]
        window.period_combo = Mock()
        window.period_combo.current.return_value = 0  # T1
        window._update_display = Mock()
        window._refresh_period_selector = Mock()

        EditionWindow._on_period_selected(window)

        assert window.period == Period.T1
        assert window._file_period == Period.T3
        assert window.editable_codes == ["T3"]
        window._update_display.assert_called_once()
