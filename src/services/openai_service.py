#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service OpenAI pour l'application BGRAPP Pyconseil
Gère l'intégration avec l'API OpenAI pour le prétraitement et la génération d'appréciations
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
import openai
from openai import OpenAI
import time
import re
from pathlib import Path

# ==========================================
# CONFIGURATION DU MODÈLE OPENAI
# ==========================================
# Modifiez cette variable pour changer le modèle utilisé
DEFAULT_OPENAI_MODEL = "gpt-4o-mini-2024-07-18"

# Modèles disponibles (exemples) :
# - "gpt-3.5-turbo"           # Rapide et économique (recommandé pour la plupart des cas)
# - "gpt-3.5-turbo-16k"       # Version avec contexte étendu (16k tokens)
# - "gpt-4"                   # Plus puissant mais plus lent et coûteux
# - "gpt-4-turbo-preview"     # Version turbo de GPT-4
# - "o3-mini-2025-01-31"                  # Raisonnement
# - "gpt-4o-mini-2024-07-18"             # Version mini de GPT-4o (équilibré performance/coût)

# ==========================================
# CONFIGURATION ANONYMISATION RGPD
# ==========================================
ANONYMIZED_FIRST_NAME = "John"
ANONYMIZED_LAST_NAME = "DOE"

# Charger les variables d'environnement depuis le fichier .env
try:
    from dotenv import load_dotenv
    # Chercher le fichier .env dans le dossier racine du projet
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # Si python-dotenv n'est pas installé, continuer sans
    pass

# Import conditionnel
try:
    from ..models.bulletin import Bulletin
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.bulletin import Bulletin


class RGPDAnonymizer:
    """Gestionnaire d'anonymisation RGPD pour les données d'élèves"""
    
    def __init__(self):
        """Initialise l'anonymiseur RGPD"""
        self.name_mapping: Dict[str, Tuple[str, str]] = {}  # {anonymized_key: (original_nom, original_prenom)}
        self.reverse_mapping: Dict[str, str] = {}  # {original_nom_prenom: anonymized_key}
        self.logger = logging.getLogger(__name__)
    
    def register_student(self, nom: str, prenom: str) -> str:
        """
        Enregistre un élève et retourne sa clé anonymisée
        
        Args:
            nom: Nom de famille de l'élève
            prenom: Prénom de l'élève
            
        Returns:
            str: Clé anonymisée pour cet élève
        """
        # Normalisation pour la recherche
        nom_clean = nom.strip().upper()
        prenom_clean = prenom.strip().capitalize()
        
        # Clé de recherche basée sur le nom et prénom
        original_key = f"{nom_clean} {prenom_clean}"
        
        # Si déjà enregistré, retourner la clé existante
        if original_key in self.reverse_mapping:
            return self.reverse_mapping[original_key]
        
        # Créer une nouvelle clé anonymisée unique
        anonymized_key = f"{ANONYMIZED_FIRST_NAME}_{len(self.name_mapping) + 1:03d}"
        
        # Enregistrer les mappings bidirectionnels
        self.name_mapping[anonymized_key] = (nom_clean, prenom_clean)
        self.reverse_mapping[original_key] = anonymized_key
        
        self.logger.debug(f"Élève enregistré: {original_key} -> {anonymized_key}")
        return anonymized_key
    
    def anonymize_text(self, text: str, student_nom: str, student_prenom: str) -> str:
        """
        Anonymise un texte en remplaçant les noms/prénoms par des versions anonymisées
        
        Args:
            text: Texte à anonymiser
            student_nom: Nom de l'élève concerné
            student_prenom: Prénom de l'élève concerné
            
        Returns:
            str: Texte anonymisé
        """
        if not text or not text.strip():
            return text
        
        # Enregistrer l'élève et obtenir sa clé anonymisée
        anonymized_key = self.register_student(student_nom, student_prenom)
        
        # Créer le texte anonymisé en remplaçant les occurrences
        anonymized_text = text
        
        # Remplacer le prénom (recherche case-insensitive mais respecte la casse originale)
        prenom_pattern = re.compile(re.escape(student_prenom.strip()), re.IGNORECASE)
        anonymized_text = prenom_pattern.sub(ANONYMIZED_FIRST_NAME, anonymized_text)
        
        # Remplacer le nom de famille 
        nom_pattern = re.compile(re.escape(student_nom.strip()), re.IGNORECASE)
        anonymized_text = nom_pattern.sub(ANONYMIZED_LAST_NAME, anonymized_text)
        
        self.logger.debug(f"Texte anonymisé pour {student_nom} {student_prenom}")
        return anonymized_text
    
    def deanonymize_text(self, text: str, student_nom: str, student_prenom: str) -> str:
        """
        Désanonymise un texte en restaurant les vrais noms/prénoms
        
        Args:
            text: Texte anonymisé à restaurer
            student_nom: Nom original de l'élève
            student_prenom: Prénom original de l'élève
            
        Returns:
            str: Texte avec les vrais noms restaurés
        """
        if not text or not text.strip():
            return text
        
        # Restaurer le texte original
        deanonymized_text = text
        
        # Remplacer les noms anonymisés par les vrais noms
        # Note: On utilise word boundaries pour éviter les remplacements partiels
        john_pattern = re.compile(r'\b' + re.escape(ANONYMIZED_FIRST_NAME) + r'\b', re.IGNORECASE)
        deanonymized_text = john_pattern.sub(student_prenom.strip(), deanonymized_text)
        
        doe_pattern = re.compile(r'\b' + re.escape(ANONYMIZED_LAST_NAME) + r'\b', re.IGNORECASE)
        deanonymized_text = doe_pattern.sub(student_nom.strip(), deanonymized_text)
        
        self.logger.debug(f"Texte désanonymisé pour {student_nom} {student_prenom}")
        return deanonymized_text
    
    def clear_mappings(self):
        """Efface tous les mappings (utile pour les tests ou nouveau traitement)"""
        self.name_mapping.clear()
        self.reverse_mapping.clear()
        self.logger.debug("Mappings RGPD effacés")


class OpenAIService:
    """Service de communication avec l'API OpenAI avec anonymisation RGPD"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, enable_rgpd: bool = True):
        """
        Initialise le service OpenAI
        
        Args:
            api_key: Clé API OpenAI (si non fournie, cherche dans les variables d'environnement)
            model: Modèle à utiliser (si non fourni, utilise DEFAULT_OPENAI_MODEL)
            enable_rgpd: Active/désactive l'anonymisation RGPD (défaut: True)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Clé API OpenAI non trouvée. Définissez OPENAI_API_KEY dans le fichier .env ou passez api_key")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Utiliser le modèle passé en paramètre ou celui configuré par défaut
        self.model = model or DEFAULT_OPENAI_MODEL
        
        self.max_retries = 3
        self.retry_delay = 1
        
        # Configuration RGPD
        self.enable_rgpd = enable_rgpd
        self.anonymizer = RGPDAnonymizer() if enable_rgpd else None
        
        # Configuration logging
        self.logger = logging.getLogger(__name__)
        
        # Log du modèle et configuration RGPD utilisés pour information
        rgpd_status = "activée" if enable_rgpd else "désactivée"
        self.logger.info(f"Service OpenAI initialisé avec le modèle: {self.model}, Anonymisation RGPD: {rgpd_status}")
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à l'API OpenAI
        
        Returns:
            bool: True si la connexion fonctionne
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            self.logger.error(f"Erreur de connexion OpenAI: {e}")
            return False
    
    def preprocess_appreciation(self, text: str, student_nom: str = None, student_prenom: str = None) -> str:
        """
        Prétraite une appréciation pour ajouter des balises HTML avec anonymisation RGPD
        
        Args:
            text: Texte de l'appréciation à prétraiter
            student_nom: Nom de l'élève (pour anonymisation RGPD)
            student_prenom: Prénom de l'élève (pour anonymisation RGPD)
            
        Returns:
            str: Texte avec balises HTML <span class="positif"> et <span class="negatif">
        """
        if not text or not text.strip():
            return text
        
        # Anonymisation RGPD si activée
        text_to_process = text
        if self.enable_rgpd and self.anonymizer and student_nom and student_prenom:
            text_to_process = self.anonymizer.anonymize_text(text, student_nom, student_prenom)
            self.logger.debug(f"Texte anonymisé pour prétraitement: {student_nom} {student_prenom}")
        
        prompt = """Tu es un expert en analyse de commentaires pédagogiques. 
Ta tâche est d'ajouter des balises HTML pour mettre en évidence les aspects positifs et négatifs.

Règles:
- Entoure les phrases/expressions POSITIVES avec <span class="positif">texte</span>
- Entoure les phrases/expressions NÉGATIVES avec <span class="negatif">texte</span>
- Ne modifie PAS le contenu du texte, ajoute seulement les balises
- Garde la ponctuation et la structure originale
- Ne balis que les parties vraiment positives ou négatives, pas les neutres

IMPORTANT: Réponds UNIQUEMENT par le texte traité avec les balises HTML, sans aucune explication, préambule ou formatage supplémentaire. Le texte sera inséré tel quel dans l'application.

Texte à traiter:
"""

        try:
            response = self._make_api_call(prompt + text_to_process)
            
            # Désanonymisation RGPD si activée
            if self.enable_rgpd and self.anonymizer and student_nom and student_prenom:
                response = self.anonymizer.deanonymize_text(response, student_nom, student_prenom)
                self.logger.debug(f"Réponse désanonymisée après prétraitement: {student_nom} {student_prenom}")
            
            return response
        except Exception as e:
            self.logger.error(f"Erreur prétraitement: {e}")
            return text  # Retourne le texte original en cas d'erreur
    
    def generate_general_appreciation(self, appreciations_by_subject: Dict[str, str], student_nom: str = None, student_prenom: str = None) -> str:
        """
        Génère une appréciation générale à partir des appréciations par matière avec anonymisation RGPD
        
        Args:
            appreciations_by_subject: Dictionnaire {matière: appréciation}
            student_nom: Nom de l'élève (pour anonymisation RGPD)
            student_prenom: Prénom de l'élève (pour anonymisation RGPD)
            
        Returns:
            str: Appréciation générale générée
        """
        if not appreciations_by_subject:
            return ""
        
        # Anonymisation RGPD des appréciations si activée
        anonymized_appreciations = {}
        for matiere, appreciation in appreciations_by_subject.items():
            if appreciation and appreciation.strip():
                if self.enable_rgpd and self.anonymizer and student_nom and student_prenom:
                    anonymized_appreciations[matiere] = self.anonymizer.anonymize_text(appreciation, student_nom, student_prenom)
                else:
                    anonymized_appreciations[matiere] = appreciation
        
        if self.enable_rgpd and student_nom and student_prenom:
            self.logger.debug(f"Appréciations anonymisées pour génération générale: {student_nom} {student_prenom}")
        
        # Construire le prompt avec les appréciations (anonymisées ou non)
        appreciations_text = "\n".join([
            f"- {matiere}: {appreciation}" 
            for matiere, appreciation in anonymized_appreciations.items()
        ])
        
        prompt = f"""Tu es un professeur principal rédigeant l'appréciation générale pour un conseil de classe.

À partir des appréciations suivantes par matière, rédige une appréciation générale synthétique:

{appreciations_text}

Consignes:
- Style formel de conseil de classe
- Maximum 255 caractères
- Synthèse globale des points forts et axes de progrès
- Encouragements constructifs
- Évite les répétitions
- Ton bienveillant mais objectif

IMPORTANT: Réponds UNIQUEMENT par l'appréciation générale rédigée, sans titre, préambule, explication ou formatage supplémentaire. Le texte sera inséré tel quel dans le bulletin.

Appréciation générale:"""

        try:
            response = self._make_api_call(prompt)
            
            # Désanonymisation RGPD si activée
            if self.enable_rgpd and self.anonymizer and student_nom and student_prenom:
                response = self.anonymizer.deanonymize_text(response, student_nom, student_prenom)
                self.logger.debug(f"Réponse désanonymisée après génération générale: {student_nom} {student_prenom}")
            
            return response
        except Exception as e:
            self.logger.error(f"Erreur génération appréciation: {e}")
            return ""
    
    def preprocess_all_bulletins(self, bulletins: List[Bulletin], progress_callback=None) -> Tuple[int, int]:
        """
        Prétraite toutes les appréciations de tous les bulletins
        
        Args:
            bulletins: Liste des bulletins à traiter
            progress_callback: Fonction appelée avec (current, total) pour le suivi de progression
            
        Returns:
            Tuple[int, int]: (nombre de réussites, nombre d'erreurs)
        """
        success_count = 0
        error_count = 0
        total_operations = 0
        
        # Calculer le nombre total d'opérations
        for bulletin in bulletins:
            for matiere in bulletin.matieres.values():
                if matiere.appreciation_s1:
                    total_operations += 1
                if matiere.appreciation_s2:
                    total_operations += 1
        
        current_operation = 0
        
        for bulletin in bulletins:
            for nom_matiere, matiere in bulletin.matieres.items():
                # Prétraitement S1
                if matiere.appreciation_s1:
                    try:
                        preprocessed = self.preprocess_appreciation(
                            matiere.appreciation_s1, 
                            bulletin.eleve.nom, 
                            bulletin.eleve.prenom
                        )
                        matiere.appreciation_s1 = preprocessed
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Erreur prétraitement S1 {nom_matiere} pour {bulletin.eleve.nom}: {e}")
                        error_count += 1
                    
                    current_operation += 1
                    if progress_callback:
                        progress_callback(current_operation, total_operations)
                
                # Prétraitement S2
                if matiere.appreciation_s2:
                    try:
                        preprocessed = self.preprocess_appreciation(
                            matiere.appreciation_s2, 
                            bulletin.eleve.nom, 
                            bulletin.eleve.prenom
                        )
                        matiere.appreciation_s2 = preprocessed
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Erreur prétraitement S2 {nom_matiere} pour {bulletin.eleve.nom}: {e}")
                        error_count += 1
                    
                    current_operation += 1
                    if progress_callback:
                        progress_callback(current_operation, total_operations)
        
        return success_count, error_count
    
    def generate_all_general_appreciations(self, bulletins: List[Bulletin], progress_callback=None) -> Tuple[int, int]:
        """
        Génère les appréciations générales S2 pour tous les bulletins
        
        Args:
            bulletins: Liste des bulletins à traiter
            progress_callback: Fonction appelée avec (current, total) pour le suivi de progression
            
        Returns:
            Tuple[int, int]: (nombre de réussites, nombre d'erreurs)
        """
        success_count = 0
        error_count = 0
        total_bulletins = len(bulletins)
        
        for i, bulletin in enumerate(bulletins):
            try:
                # Collecter les appréciations S2 par matière
                appreciations_s2 = {}
                for nom_matiere, matiere in bulletin.matieres.items():
                    if matiere.appreciation_s2 and matiere.appreciation_s2.strip():
                        appreciations_s2[nom_matiere] = matiere.appreciation_s2
                
                if appreciations_s2:
                    general_appreciation = self.generate_general_appreciation(
                        appreciations_s2, 
                        bulletin.eleve.nom, 
                        bulletin.eleve.prenom
                    )
                    bulletin.appreciation_generale_s2 = general_appreciation
                    success_count += 1
                else:
                    self.logger.warning(f"Aucune appréciation S2 trouvée pour {bulletin.eleve.nom}")
                    error_count += 1
                
            except Exception as e:
                self.logger.error(f"Erreur génération appréciation générale pour {bulletin.eleve.nom}: {e}")
                error_count += 1
            
            if progress_callback:
                progress_callback(i + 1, total_bulletins)
        
        return success_count, error_count
    
    def _make_api_call(self, prompt: str) -> str:
        """
        Effectue un appel API avec gestion des erreurs et retry
        
        Args:
            prompt: Prompt à envoyer à l'API
            
        Returns:
            str: Réponse de l'API
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
            except openai.RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Rate limit atteint, attente {wait_time}s avant retry...")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.logger.warning(f"Tentative {attempt + 1} échouée: {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise


def get_openai_service(model: Optional[str] = None, enable_rgpd: bool = True) -> Optional[OpenAIService]:
    """
    Factory function pour obtenir une instance du service OpenAI
    
    Args:
        model: Modèle à utiliser (optionnel, utilise DEFAULT_OPENAI_MODEL par défaut)
        enable_rgpd: Active/désactive l'anonymisation RGPD (défaut: True)
    
    Returns:
        OpenAIService ou None si la configuration échoue
    """
    try:
        service = OpenAIService(model=model, enable_rgpd=enable_rgpd)
        if service.test_connection():
            return service
        else:
            return None
    except Exception as e:
        logging.error(f"Impossible d'initialiser le service OpenAI: {e}")
        return None 