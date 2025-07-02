#!/usr/bin/env python3
"""
Modèles de données pour l'application de conseil de classe.
Définit les structures Eleve, Appreciation et Bulletin.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import re


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
class AppreciationMatiere:
    """Représente l'appréciation d'un élève dans une matière donnée."""
    matiere: str
    heures_absence_s1: Optional[int] = None
    heures_absence_s2: Optional[int] = None
    moyenne_s1: Optional[float] = None
    moyenne_s2: Optional[float] = None
    moyenne_s1_max: Optional[float] = None
    moyenne_s1_min: Optional[float] = None
    moyenne_s2_max: Optional[float] = None  
    moyenne_s2_min: Optional[float] = None
    appreciation_s1: Optional[str] = None
    appreciation_s2: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convertit l'appréciation en dictionnaire pour JSON."""
        result = {}
        
        # Heures d'absence
        if self.heures_absence_s1 is not None:
            result["HeuresAbsenceS1"] = self.heures_absence_s1
        if self.heures_absence_s2 is not None:
            result["HeuresAbsenceS2"] = self.heures_absence_s2
            
        # Moyennes
        if self.moyenne_s1 is not None:
            result["MoyenneS1"] = self.moyenne_s1
        if self.moyenne_s2 is not None:
            result["MoyenneS2"] = self.moyenne_s2
            
        # Moyennes min/max
        if self.moyenne_s1_max is not None:
            result["MoyenneS1Max"] = self.moyenne_s1_max
        if self.moyenne_s1_min is not None:
            result["MoyenneS1Min"] = self.moyenne_s1_min
        if self.moyenne_s2_max is not None:
            result["MoyenneS2Max"] = self.moyenne_s2_max
        if self.moyenne_s2_min is not None:
            result["MoyenneS2Min"] = self.moyenne_s2_min
            
        # Appréciations
        if self.appreciation_s1:
            result["AppreciationS1"] = self.appreciation_s1
        if self.appreciation_s2:
            result["AppreciationS2"] = self.appreciation_s2
            
        return result


@dataclass
class Bulletin:
    """Représente le bulletin complet d'un élève."""
    eleve: Eleve
    appreciation_generale_s1: Optional[str] = None
    appreciation_generale_s2: Optional[str] = None
    matieres: Dict[str, AppreciationMatiere] = field(default_factory=dict)
    
    def add_matiere(self, appreciation: AppreciationMatiere) -> None:
        """Ajoute une appréciation de matière au bulletin."""
        self.matieres[appreciation.matiere] = appreciation
    
    def get_matiere(self, nom_matiere: str) -> Optional[AppreciationMatiere]:
        """Récupère l'appréciation d'une matière donnée."""
        return self.matieres.get(nom_matiere)
    
    def to_dict(self) -> Dict:
        """Convertit le bulletin en dictionnaire pour JSON."""
        result = {
            "Nom": self.eleve.nom,
            "Prenom": self.eleve.prenom,
        }
        
        # Appréciations générales
        if self.appreciation_generale_s1:
            result["AppreciationGeneraleS1"] = self.appreciation_generale_s1
        if self.appreciation_generale_s2:
            result["AppreciationGeneraleS2"] = self.appreciation_generale_s2
            
        # Matières
        if self.matieres:
            result["Matieres"] = {}
            for nom_matiere, appreciation in self.matieres.items():
                result["Matieres"][nom_matiere] = appreciation.to_dict()
                
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Bulletin':
        """Crée un bulletin à partir d'un dictionnaire."""
        eleve = Eleve(
            nom=data["Nom"],
            prenom=data["Prenom"]
        )
        
        bulletin = cls(
            eleve=eleve,
            appreciation_generale_s1=data.get("AppreciationGeneraleS1"),
            appreciation_generale_s2=data.get("AppreciationGeneraleS2")
        )
        
        # Charger les matières
        if "Matieres" in data:
            for nom_matiere, matiere_data in data["Matieres"].items():
                appreciation = AppreciationMatiere(matiere=nom_matiere)
                
                # Charger les données de la matière
                if "HeuresAbsenceS1" in matiere_data:
                    appreciation.heures_absence_s1 = matiere_data["HeuresAbsenceS1"]
                if "HeuresAbsenceS2" in matiere_data:
                    appreciation.heures_absence_s2 = matiere_data["HeuresAbsenceS2"]
                    
                if "MoyenneS1" in matiere_data:
                    appreciation.moyenne_s1 = matiere_data["MoyenneS1"]
                if "MoyenneS2" in matiere_data:
                    appreciation.moyenne_s2 = matiere_data["MoyenneS2"]
                    
                if "MoyenneS1Max" in matiere_data:
                    appreciation.moyenne_s1_max = matiere_data["MoyenneS1Max"]
                if "MoyenneS1Min" in matiere_data:
                    appreciation.moyenne_s1_min = matiere_data["MoyenneS1Min"]
                if "MoyenneS2Max" in matiere_data:
                    appreciation.moyenne_s2_max = matiere_data["MoyenneS2Max"]
                if "MoyenneS2Min" in matiere_data:
                    appreciation.moyenne_s2_min = matiere_data["MoyenneS2Min"]
                    
                if "AppreciationS1" in matiere_data:
                    appreciation.appreciation_s1 = matiere_data["AppreciationS1"]
                if "AppreciationS2" in matiere_data:
                    appreciation.appreciation_s2 = matiere_data["AppreciationS2"]
                
                bulletin.add_matiere(appreciation)
        
        return bulletin
    
    def __str__(self) -> str:
        return f"Bulletin de {self.eleve} ({len(self.matieres)} matières)"


def parse_heures_absence(heures_str: str) -> Optional[int]:
    """
    Parse une chaîne d'heures d'absence (ex: "3h00", "1h30") en nombre d'heures.
    
    Args:
        heures_str: Chaîne représentant les heures d'absence
        
    Returns:
        Nombre d'heures ou None si non parsable
    """
    if not heures_str or heures_str.strip() == "":
        return None
        
    # Rechercher pattern comme "3h00", "1h30", etc.
    match = re.search(r'(\d+)h', heures_str)
    if match:
        return int(match.group(1))
    
    # Si c'est juste un nombre
    try:
        return int(float(heures_str))
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
    if not moyenne_str or moyenne_str.strip() == "" or moyenne_str == "N.Not":
        return None
        
    # Remplacer virgule par point pour conversion
    try:
        return float(moyenne_str.replace(',', '.'))
    except (ValueError, TypeError):
        return None 