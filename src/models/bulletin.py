#!/usr/bin/env python3
"""
Modèles de données pour l'application de conseil de classe.
Définit les structures Eleve, AppreciationMatiere (par période) et Bulletin.

Les données sont stockées par période (S1/S2 en mode semestre,
T1/T2/T3 en mode trimestre) afin de supporter les deux organisations.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re


# Codes de période reconnus (ordre canonique pour la sérialisation/affichage)
PERIOD_CODES = ("S1", "S2", "T1", "T2", "T3")


@dataclass
class Eleve:
    """Représente un élève avec ses informations de base."""
    nom: str
    prenom: str
    classe: Optional[str] = None

    @classmethod
    def from_full_name(cls, full_name: str) -> 'Eleve':
        """
        Crée un élève à partir du nom complet format 'NOM Prenom'.

        Args:
            full_name: Nom complet de l'élève (ex: "DUPONT Alice")

        Returns:
            Instance d'Eleve avec nom et prénom séparés
        """
        # Diviser le nom complet en mots
        parts = full_name.strip().split()
        if len(parts) < 2:
            raise ValueError(f"Format de nom invalide: {full_name}")

        # Le nom est en majuscules, le prénom commence par une majuscule
        nom_parts = []
        prenom_parts = []

        for part in parts:
            if part.isupper():
                nom_parts.append(part)
            else:
                prenom_parts.append(part)

        # Si pas de séparation claire, prendre le premier mot comme nom
        if not nom_parts:
            nom_parts = [parts[0]]
            prenom_parts = parts[1:]

        nom = ' '.join(nom_parts)
        prenom = ' '.join(prenom_parts)

        return cls(nom=nom, prenom=prenom)

    def __str__(self) -> str:
        return f"{self.nom} {self.prenom}"


@dataclass
class PeriodeData:
    """Données d'une matière pour une période donnée."""
    heures_absence: Optional[str] = None
    retards: Optional[int] = None
    moyenne: Optional[float] = None
    moyenne_min: Optional[float] = None
    moyenne_max: Optional[float] = None
    appreciation: Optional[str] = None

    def is_empty(self) -> bool:
        """Indique si la période ne contient aucune donnée utile."""
        return (
            self.heures_absence is None
            and self.retards is None
            and self.moyenne is None
            and self.appreciation is None
        )


class AppreciationMatiere:
    """Représente l'appréciation d'un élève dans une matière, par période."""

    def __init__(self, matiere: str,
                 periodes: Optional[Dict[str, PeriodeData]] = None,
                 *,
                 heures_absence_s1=None, heures_absence_s2=None,
                 moyenne_s1=None, moyenne_s2=None,
                 moyenne_s1_min=None, moyenne_s1_max=None,
                 moyenne_s2_min=None, moyenne_s2_max=None,
                 appreciation_s1=None, appreciation_s2=None):
        self.matiere = matiere
        self.periodes: Dict[str, PeriodeData] = periodes if periodes is not None else {}

        # Rétro-compatibilité : accepter les anciens champs S1/S2 au constructeur
        if heures_absence_s1 is not None:
            self.heures_absence_s1 = heures_absence_s1
        if heures_absence_s2 is not None:
            self.heures_absence_s2 = heures_absence_s2
        if moyenne_s1 is not None:
            self.moyenne_s1 = moyenne_s1
        if moyenne_s2 is not None:
            self.moyenne_s2 = moyenne_s2
        if moyenne_s1_min is not None:
            self.moyenne_s1_min = moyenne_s1_min
        if moyenne_s1_max is not None:
            self.moyenne_s1_max = moyenne_s1_max
        if moyenne_s2_min is not None:
            self.moyenne_s2_min = moyenne_s2_min
        if moyenne_s2_max is not None:
            self.moyenne_s2_max = moyenne_s2_max
        if appreciation_s1 is not None:
            self.appreciation_s1 = appreciation_s1
        if appreciation_s2 is not None:
            self.appreciation_s2 = appreciation_s2

    # ------------------------------------------------------------------
    # Accès aux périodes
    # ------------------------------------------------------------------
    def get_periode(self, code: str) -> Optional[PeriodeData]:
        """Récupère les données d'une période (ou None)."""
        return self.periodes.get(code)

    def ensure_periode(self, code: str) -> PeriodeData:
        """Récupère (en la créant si besoin) les données d'une période."""
        if code not in self.periodes:
            self.periodes[code] = PeriodeData()
        return self.periodes[code]

    # ------------------------------------------------------------------
    # Propriétés de rétro-compatibilité (ancien format S1/S2)
    # ------------------------------------------------------------------
    def _get_attr(self, code: str, attr: str):
        periode = self.periodes.get(code)
        return getattr(periode, attr) if periode else None

    def _set_attr(self, code: str, attr: str, value) -> None:
        if value is None and code not in self.periodes:
            return
        setattr(self.ensure_periode(code), attr, value)

    @property
    def heures_absence_s1(self):
        return self._get_attr("S1", "heures_absence")

    @heures_absence_s1.setter
    def heures_absence_s1(self, value):
        self._set_attr("S1", "heures_absence", value)

    @property
    def heures_absence_s2(self):
        return self._get_attr("S2", "heures_absence")

    @heures_absence_s2.setter
    def heures_absence_s2(self, value):
        self._set_attr("S2", "heures_absence", value)

    @property
    def moyenne_s1(self):
        return self._get_attr("S1", "moyenne")

    @moyenne_s1.setter
    def moyenne_s1(self, value):
        self._set_attr("S1", "moyenne", value)

    @property
    def moyenne_s2(self):
        return self._get_attr("S2", "moyenne")

    @moyenne_s2.setter
    def moyenne_s2(self, value):
        self._set_attr("S2", "moyenne", value)

    @property
    def moyenne_s1_min(self):
        return self._get_attr("S1", "moyenne_min")

    @moyenne_s1_min.setter
    def moyenne_s1_min(self, value):
        self._set_attr("S1", "moyenne_min", value)

    @property
    def moyenne_s1_max(self):
        return self._get_attr("S1", "moyenne_max")

    @moyenne_s1_max.setter
    def moyenne_s1_max(self, value):
        self._set_attr("S1", "moyenne_max", value)

    @property
    def moyenne_s2_min(self):
        return self._get_attr("S2", "moyenne_min")

    @moyenne_s2_min.setter
    def moyenne_s2_min(self, value):
        self._set_attr("S2", "moyenne_min", value)

    @property
    def moyenne_s2_max(self):
        return self._get_attr("S2", "moyenne_max")

    @moyenne_s2_max.setter
    def moyenne_s2_max(self, value):
        self._set_attr("S2", "moyenne_max", value)

    @property
    def appreciation_s1(self):
        return self._get_attr("S1", "appreciation")

    @appreciation_s1.setter
    def appreciation_s1(self, value):
        self._set_attr("S1", "appreciation", value)

    @property
    def appreciation_s2(self):
        return self._get_attr("S2", "appreciation")

    @appreciation_s2.setter
    def appreciation_s2(self, value):
        self._set_attr("S2", "appreciation", value)

    # ------------------------------------------------------------------
    # Sérialisation
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict:
        """Convertit l'appréciation en dictionnaire pour JSON (par période)."""
        result: Dict = {}

        ordered_codes = [c for c in PERIOD_CODES if c in self.periodes]
        for code in ordered_codes:
            periode = self.periodes[code]
            if periode.heures_absence is not None:
                result[f"HeuresAbsence{code}"] = periode.heures_absence
            if periode.retards is not None:
                result[f"Retards{code}"] = periode.retards
            if periode.moyenne is not None:
                result[f"Moyenne{code}"] = periode.moyenne
            if periode.moyenne_min is not None:
                result[f"Moyenne{code}Min"] = periode.moyenne_min
            if periode.moyenne_max is not None:
                result[f"Moyenne{code}Max"] = periode.moyenne_max
            if periode.appreciation:
                result[f"Appreciation{code}"] = periode.appreciation

        return result


class Bulletin:
    """Représente le bulletin complet d'un élève."""

    def __init__(self, eleve: Eleve,
                 appreciations_generales: Optional[Dict[str, str]] = None,
                 matieres: Optional[Dict[str, AppreciationMatiere]] = None,
                 *,
                 appreciation_generale_s1: Optional[str] = None,
                 appreciation_generale_s2: Optional[str] = None):
        self.eleve = eleve
        self.appreciations_generales: Dict[str, str] = (
            appreciations_generales if appreciations_generales is not None else {}
        )
        self.matieres: Dict[str, AppreciationMatiere] = (
            matieres if matieres is not None else {}
        )

        # Rétro-compatibilité : anciens champs au constructeur
        if appreciation_generale_s1:
            self.appreciations_generales["S1"] = appreciation_generale_s1
        if appreciation_generale_s2:
            self.appreciations_generales["S2"] = appreciation_generale_s2

    # ------------------------------------------------------------------
    # Propriétés de rétro-compatibilité (appréciation générale S1/S2)
    # ------------------------------------------------------------------
    @property
    def appreciation_generale_s1(self) -> Optional[str]:
        return self.appreciations_generales.get("S1")

    @appreciation_generale_s1.setter
    def appreciation_generale_s1(self, value: Optional[str]) -> None:
        if value is None:
            self.appreciations_generales.pop("S1", None)
        else:
            self.appreciations_generales["S1"] = value

    @property
    def appreciation_generale_s2(self) -> Optional[str]:
        return self.appreciations_generales.get("S2")

    @appreciation_generale_s2.setter
    def appreciation_generale_s2(self, value: Optional[str]) -> None:
        if value is None:
            self.appreciations_generales.pop("S2", None)
        else:
            self.appreciations_generales["S2"] = value

    def get_appreciation_generale(self, code: str) -> Optional[str]:
        """Récupère l'appréciation générale d'une période."""
        return self.appreciations_generales.get(code)

    def set_appreciation_generale(self, code: str, value: Optional[str]) -> None:
        """Définit l'appréciation générale d'une période."""
        if value is None:
            self.appreciations_generales.pop(code, None)
        else:
            self.appreciations_generales[code] = value

    # ------------------------------------------------------------------
    # Matières
    # ------------------------------------------------------------------
    def add_matiere(self, appreciation: AppreciationMatiere) -> None:
        """Ajoute une appréciation de matière au bulletin."""
        self.matieres[appreciation.matiere] = appreciation

    def get_matiere(self, nom_matiere: str) -> Optional[AppreciationMatiere]:
        """Récupère l'appréciation d'une matière donnée."""
        return self.matieres.get(nom_matiere)

    # ------------------------------------------------------------------
    # Sérialisation
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict:
        """Convertit le bulletin en dictionnaire pour JSON."""
        result: Dict = {
            "Nom": self.eleve.nom,
            "Prenom": self.eleve.prenom,
        }

        # Appréciations générales par période
        for code in PERIOD_CODES:
            texte = self.appreciations_generales.get(code)
            if texte:
                result[f"AppreciationGenerale{code}"] = texte

        # Matières
        if self.matieres:
            result["Matieres"] = {}
            for nom_matiere, appreciation in self.matieres.items():
                result["Matieres"][nom_matiere] = appreciation.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'Bulletin':
        """Crée un bulletin à partir d'un dictionnaire (formats ancien et nouveau)."""
        eleve = Eleve(
            nom=data["Nom"],
            prenom=data["Prenom"]
        )

        bulletin = cls(eleve=eleve)

        # Appréciations générales par période
        for code in PERIOD_CODES:
            texte = data.get(f"AppreciationGenerale{code}")
            if texte:
                bulletin.appreciations_generales[code] = texte

        # Charger les matières
        if "Matieres" in data:
            for nom_matiere, matiere_data in data["Matieres"].items():
                appreciation = _appreciation_from_dict(nom_matiere, matiere_data)
                bulletin.add_matiere(appreciation)

        return bulletin

    def __str__(self) -> str:
        return f"Bulletin de {self.eleve} ({len(self.matieres)} matières)"


# Motif des clés sérialisées par période, ex: "MoyenneT3Max", "HeuresAbsenceS1"
_FIELD_KEY_PATTERN = re.compile(
    r"^(HeuresAbsence|Retards|Moyenne|Appreciation)(S1|S2|T1|T2|T3)(Min|Max)?$"
)


def _appreciation_from_dict(nom_matiere: str, matiere_data: Dict) -> AppreciationMatiere:
    """Reconstruit une AppreciationMatiere depuis sa représentation JSON."""
    appreciation = AppreciationMatiere(matiere=nom_matiere)

    if not isinstance(matiere_data, dict):
        return appreciation

    for key, value in matiere_data.items():
        match = _FIELD_KEY_PATTERN.match(str(key))
        if not match:
            continue
        field_name, code, suffix = match.group(1), match.group(2), match.group(3)
        periode = appreciation.ensure_periode(code)

        if field_name == "HeuresAbsence":
            periode.heures_absence = normalize_absence(value)
        elif field_name == "Retards":
            periode.retards = parse_retards(value)
        elif field_name == "Appreciation":
            periode.appreciation = value
        elif field_name == "Moyenne":
            parsed = parse_moyenne(str(value)) if value is not None else None
            if suffix == "Min":
                periode.moyenne_min = parsed
            elif suffix == "Max":
                periode.moyenne_max = parsed
            else:
                periode.moyenne = parsed

    return appreciation


def parse_heures_absence(heures_str: str) -> Optional[int]:
    """
    Parse une chaîne d'heures d'absence (ex: "3h00", "1h30") en nombre d'heures.

    Note: conservé pour compatibilité ; ne garde que la partie heures.
    Pour un stockage fidèle, utiliser `normalize_absence`.

    Args:
        heures_str: Chaîne représentant les heures d'absence

    Returns:
        Nombre d'heures ou None si non parsable
    """
    if heures_str is None:
        return None
    heures_str = str(heures_str)
    if heures_str.strip() == "":
        return None

    # Rechercher pattern comme "3h00", "1h30", etc.
    match = re.search(r'(\d+)h', heures_str)
    if match:
        return int(match.group(1))

    # Si c'est juste un nombre
    try:
        return int(float(heures_str.replace(',', '.')))
    except (ValueError, TypeError):
        return None


def normalize_absence(value) -> Optional[str]:
    """
    Normalise une valeur d'absence en chaîne fidèle au format PRONOTE.

    Conserve les minutes (ex: "0h30", "1h30", "10h00") contrairement à
    `parse_heures_absence` qui ne garde que les heures.

    Args:
        value: Valeur brute (str, int, float...)

    Returns:
        Chaîne normalisée "XhMM" ou None si vide.
    """
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None

    # Déjà au format "XhMM" / "Xh"
    match = re.match(r'^(\d+)\s*h\s*(\d{0,2})$', text)
    if match:
        heures = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return f"{heures}h{minutes:02d}"

    # Valeur numérique (heures décimales)
    try:
        total = float(text.replace(',', '.'))
        heures = int(total)
        minutes = int(round((total - heures) * 60))
        if minutes == 60:
            heures += 1
            minutes = 0
        return f"{heures}h{minutes:02d}"
    except (ValueError, TypeError):
        return text


def absence_to_hours(value) -> Optional[float]:
    """Convertit une absence ("XhMM") en nombre d'heures décimal."""
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    match = re.match(r'^(\d+)\s*h\s*(\d{0,2})$', text)
    if match:
        heures = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return heures + minutes / 60.0
    try:
        return float(text.replace(',', '.'))
    except (ValueError, TypeError):
        return None


def parse_retards(value) -> Optional[int]:
    """
    Parse une valeur de retards (ex: "1.0", "3", 2) en entier.

    Args:
        value: Valeur brute du nombre de retards

    Returns:
        Nombre de retards ou None si non parsable/vide
    """
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    try:
        return int(float(text.replace(',', '.')))
    except (ValueError, TypeError):
        return None


def parse_moyenne(moyenne_str: str) -> Optional[float]:
    """
    Parse une chaîne de moyenne (ex: "14,50", "N.Not") en nombre flottant.

    Args:
        moyenne_str: Chaîne représentant la moyenne

    Returns:
        Moyenne ou None si non parsable
    """
    if moyenne_str is None:
        return None
    moyenne_str = str(moyenne_str)
    if moyenne_str.strip() == "" or moyenne_str == "N.Not":
        return None

    # Remplacer virgule par point pour conversion
    try:
        return float(moyenne_str.replace(',', '.'))
    except (ValueError, TypeError):
        return None
