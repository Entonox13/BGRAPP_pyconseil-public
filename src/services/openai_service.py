#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service IA multi-fournisseurs pour l'application BGRAPP Pyconseil.
Gère le prétraitement et la génération d'appréciations via OpenAI (Responses API),
Anthropic (Messages API) et Google Gemini (google-genai).
"""

import logging
from typing import List, Dict, Optional, Tuple
import time
import re
from pathlib import Path

# Imports conditionnels pour les clients IA
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

try:
    from google import genai as google_genai
    from google.genai import types as google_genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    google_genai = None
    google_genai_types = None

# Import conditionnel pour la configuration IA
try:
    from .ai_config_service import AIProvider, get_ai_config_service, resolve_env_path
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ai_config_service import AIProvider, get_ai_config_service, resolve_env_path

# ==========================================
# CONFIGURATION RÉTROCOMPATIBILITÉ
# ==========================================
# Pour maintenir la rétrocompatibilité avec l'ancien code
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

# ==========================================
# CONFIGURATION ANONYMISATION RGPD
# ==========================================
ANONYMIZED_FIRST_NAME = "John"
ANONYMIZED_LAST_NAME = "DOE"

# Charger les variables d'environnement depuis le fichier .env
try:
    from dotenv import load_dotenv
    # Emplacement compatible mode source ET mode packagé (exe/AppImage)
    load_dotenv(resolve_env_path())
except ImportError:
    # Si python-dotenv n'est pas installé, continuer sans
    pass

# Import conditionnel
try:
    from ..models.bulletin import Bulletin
    from ..utils.semester import Period, Semester
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.bulletin import Bulletin
    from utils.semester import Period, Semester

# Import des prompts
try:
    from .prompts import get_preprocess_prompt, get_generate_general_prompt
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from prompts import get_preprocess_prompt, get_generate_general_prompt


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


class AIService:
    """Service de communication IA multi-fournisseurs avec anonymisation RGPD."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        enable_rgpd: bool = True,
        provider: Optional[AIProvider] = None,
        preprocess_model: Optional[str] = None,
        generation_model: Optional[str] = None,
    ):
        """
        Initialise le service IA.

        Args:
            api_key: Clé API (si non fournie, utilise la configuration)
            model: Modèle unique appliqué aux deux rôles (rétrocompatibilité).
                Si fourni, il prime sur preprocess_model/generation_model.
            enable_rgpd: Active/désactive l'anonymisation RGPD (défaut: True)
            provider: Fournisseur IA à utiliser (si non fourni, utilise le
                fournisseur actif de la configuration).
            preprocess_model: Modèle utilisé pour le prétraitement (balises HTML).
            generation_model: Modèle utilisé pour la génération d'appréciations.
        """
        self.config_service = get_ai_config_service()
        self.provider = provider if provider else self.config_service.get_enabled_provider()

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self.config_service.get_api_key(self.provider)
            if not self.api_key:
                raise ValueError(
                    f"Aucune clé API configurée pour {self.provider.value}. "
                    "Configurez votre clé API via l'interface de configuration."
                )

        # Deux modèles distincts : prétraitement et génération d'appréciations.
        if model:
            self.preprocess_model = model
            self.generation_model = model
        else:
            self.preprocess_model = preprocess_model or self.config_service.get_model(
                self.provider, role="preprocess"
            )
            self.generation_model = generation_model or self.config_service.get_model(
                self.provider, role="generation"
            )

        # Alias rétrocompatible (utilisé par le test de connexion et l'ancien code).
        self.model = self.generation_model

        self.logger = logging.getLogger(__name__)
        self.client = self._initialize_client()
        self.max_retries = 3
        self.retry_delay = 1

        self.enable_rgpd = enable_rgpd
        self.anonymizer = RGPDAnonymizer() if enable_rgpd else None

        rgpd_status = "activée" if enable_rgpd else "désactivée"
        self.logger.info(
            "Service IA initialisé avec %s, modèles [prétraitement: %s, appréciation: %s], "
            "Anonymisation RGPD: %s",
            self.provider.value,
            self.preprocess_model,
            self.generation_model,
            rgpd_status
        )

    def _initialize_client(self):
        """Initialise le client IA selon le fournisseur actif."""
        if self.provider == AIProvider.OPENAI:
            if not OPENAI_AVAILABLE:
                raise ImportError('Client OpenAI non installé. Exécutez: pip install "openai>=2.0"')
            return OpenAI(api_key=self.api_key)

        if self.provider == AIProvider.ANTHROPIC:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError('Client Anthropic non installé. Exécutez: pip install "anthropic>=0.69"')
            return anthropic.Anthropic(api_key=self.api_key)

        if self.provider == AIProvider.GEMINI:
            if not GEMINI_AVAILABLE:
                raise ImportError('Client Gemini non installé. Exécutez: pip install "google-genai>=2.0"')
            return google_genai.Client(api_key=self.api_key)

        raise ValueError(f"Fournisseur non supporté: {self.provider}")
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à l'API IA
        
        Returns:
            bool: True si la connexion fonctionne
        """
        try:
            # Utilise un minimum de tokens compatible avec l'API (>=16)
            test_response = self._make_api_call("test", max_tokens=16, model=self.generation_model)
            return bool(test_response)
        except Exception as e:
            self.logger.error(f"Erreur de connexion {self.provider.value}: {e}")
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
        
        # Récupérer le prompt depuis le module prompts
        prompt = get_preprocess_prompt()

        try:
            response = self._make_api_call(prompt + text_to_process, model=self.preprocess_model)
            
            # Désanonymisation RGPD si activée
            if self.enable_rgpd and self.anonymizer and student_nom and student_prenom:
                response = self.anonymizer.deanonymize_text(response, student_nom, student_prenom)
                self.logger.debug(f"Réponse désanonymisée après prétraitement: {student_nom} {student_prenom}")
            
            return response
        except Exception as e:
            self.logger.error(f"Erreur prétraitement: {e}")
            return text  # Retourne le texte original en cas d'erreur
    
    def generate_general_appreciation(self,
                                      appreciations_by_subject: Dict[str, str],
                                      student_nom: str = None,
                                      student_prenom: str = None,
                                      semester: Semester = Semester.S2) -> str:
        """
        Génère une appréciation générale à partir des appréciations par matière avec anonymisation RGPD
        
        Args:
            appreciations_by_subject: Dictionnaire {matière: appréciation}
            student_nom: Nom de l'élève (pour anonymisation RGPD)
            student_prenom: Prénom de l'élève (pour anonymisation RGPD)
            semester: Semestre ciblé pour la génération
            
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
        
        # Récupérer le prompt formaté depuis le module prompts
        semester_label = semester.label if isinstance(semester, Semester) else str(semester)
        prompt = get_generate_general_prompt(appreciations_text, semester_label=semester_label)

        try:
            response = self._make_api_call(prompt, model=self.generation_model)
            
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
        
        # Calculer le nombre total d'opérations (toutes périodes confondues)
        for bulletin in bulletins:
            for matiere in bulletin.matieres.values():
                for periode in matiere.periodes.values():
                    if periode.appreciation:
                        total_operations += 1
        
        current_operation = 0
        
        for bulletin in bulletins:
            for nom_matiere, matiere in bulletin.matieres.items():
                for code, periode in matiere.periodes.items():
                    if not periode.appreciation:
                        continue
                    try:
                        preprocessed = self.preprocess_appreciation(
                            periode.appreciation,
                            bulletin.eleve.nom,
                            bulletin.eleve.prenom
                        )
                        periode.appreciation = preprocessed
                        success_count += 1
                    except Exception as e:
                        self.logger.error(
                            f"Erreur prétraitement {code} {nom_matiere} pour {bulletin.eleve.nom}: {e}"
                        )
                        error_count += 1
                    
                    current_operation += 1
                    if progress_callback:
                        progress_callback(current_operation, total_operations)
        
        return success_count, error_count
    
    def generate_all_general_appreciations(self,
                                           bulletins: List[Bulletin],
                                           semester: Period = Period.S2,
                                           progress_callback=None) -> Tuple[int, int]:
        """
        Génère les appréciations générales de la période ciblée pour tous
        les bulletins.
        
        Args:
            bulletins: Liste des bulletins à traiter
            semester: Période ciblée pour la génération (S1/S2/T1/T2/T3)
            progress_callback: Fonction appelée avec (current, total) pour le suivi de progression
            
        Returns:
            Tuple[int, int]: (nombre de réussites, nombre d'erreurs)
        """
        success_count = 0
        error_count = 0
        total_bulletins = len(bulletins)
        period = semester if isinstance(semester, Period) else Period.from_code(str(semester)) or Period.S2
        code = period.value
        
        for i, bulletin in enumerate(bulletins):
            try:
                # Collecter les appréciations de la période ciblée par matière
                appreciations = {}
                
                for nom_matiere, matiere in bulletin.matieres.items():
                    periode = matiere.get_periode(code)
                    appreciation_value = periode.appreciation if periode else None
                    if appreciation_value and appreciation_value.strip():
                        appreciations[nom_matiere] = appreciation_value
                
                if appreciations:
                    general_appreciation = self.generate_general_appreciation(
                        appreciations, 
                        bulletin.eleve.nom, 
                        bulletin.eleve.prenom,
                        semester=period
                    )
                    bulletin.set_appreciation_generale(code, general_appreciation)
                    success_count += 1
                else:
                    self.logger.warning(
                        f"Aucune appréciation {code} trouvée pour {bulletin.eleve.nom}"
                    )
                    error_count += 1
                
            except Exception as e:
                self.logger.error(f"Erreur génération appréciation générale pour {bulletin.eleve.nom}: {e}")
                error_count += 1
            
            if progress_callback:
                progress_callback(i + 1, total_bulletins)
        
        return success_count, error_count
    
    def _make_api_call(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7,
                       model: Optional[str] = None) -> str:
        """
        Effectue un appel IA avec gestion des erreurs et retry, en dispatchant
        vers le fournisseur actif.
        
        Args:
            prompt: Prompt à envoyer à l'API
            max_tokens: Nombre maximum de tokens à générer
            temperature: Température pour la génération
            model: Modèle à utiliser (défaut: modèle de génération)
            
        Returns:
            str: Réponse de l'API
        """
        model = model or self.generation_model
        for attempt in range(self.max_retries):
            try:
                return self._dispatch_call(prompt, max_tokens, temperature, model)
                
            except Exception as e:
                is_rate_limit = self._is_rate_limit_error(e)
                
                if is_rate_limit and attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Rate limit atteint, attente {wait_time}s avant retry...")
                    time.sleep(wait_time)
                else:
                    if attempt < self.max_retries - 1 and not is_rate_limit:
                        self.logger.warning(f"Tentative {attempt + 1} échouée: {e}")
                        time.sleep(self.retry_delay)
                    else:
                        raise
    
    def _dispatch_call(self, prompt: str, max_tokens: int, temperature: float, model: str) -> str:
        """Dispatche l'appel vers le fournisseur actif."""
        if self.provider == AIProvider.OPENAI:
            return self._call_openai(prompt, max_tokens, temperature, model)
        if self.provider == AIProvider.ANTHROPIC:
            return self._call_anthropic(prompt, max_tokens, temperature, model)
        if self.provider == AIProvider.GEMINI:
            return self._call_gemini(prompt, max_tokens, temperature, model)
        raise ValueError(f"Fournisseur non supporté: {self.provider}")

    def _call_openai(self, prompt: str, max_tokens: int, temperature: float, model: str) -> str:
        """Appel OpenAI via l'API responses (standard unique).
        
        Certains modèles ne supportent pas le paramètre temperature. Pour
        maximiser la compatibilité, on ne le passe pas explicitement.
        """
        response = self.client.responses.create(
            model=model,
            input=prompt,
            max_output_tokens=max_tokens,
        )
        
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text.strip()
        
        # Fallback générique si output_text n'est pas exposé par le client
        parts = []
        for block in getattr(response, "output", []) or []:
            for content in getattr(block, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    parts.append(text)
        return "\n".join(parts).strip()

    def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float, model: str) -> str:
        """Appel Anthropic via l'API Messages."""
        message = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        parts = []
        for block in getattr(message, "content", []) or []:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts).strip()

    def _call_gemini(self, prompt: str, max_tokens: int, temperature: float, model: str) -> str:
        """Appel Google Gemini via google-genai."""
        config = None
        if google_genai_types is not None:
            config = google_genai_types.GenerateContentConfig(
                max_output_tokens=max_tokens,
            )

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        text = getattr(response, "text", None)
        if text:
            return text.strip()

        # Fallback générique sur les candidats / parts
        parts = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", None)
                if part_text:
                    parts.append(part_text)
        return "\n".join(parts).strip()

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Détecte si l'erreur est liée à un rate limit (tous fournisseurs)."""
        class_name = getattr(getattr(error, "__class__", None), "__name__", "").lower()
        status_code = getattr(error, "status_code", None)
        return "ratelimit" in class_name or status_code == 429


# ==========================================
# RÉTROCOMPATIBILITÉ
# ==========================================
# Alias pour maintenir la rétrocompatibilité avec l'ancien code
OpenAIService = AIService


def get_openai_service(model: Optional[str] = None, enable_rgpd: bool = True) -> Optional[AIService]:
    """
    Factory function pour obtenir une instance du service IA OpenAI (rétrocompatibilité)
    
    Args:
        model: Modèle à utiliser (optionnel, utilise la configuration par défaut)
        enable_rgpd: Active/désactive l'anonymisation RGPD (défaut: True)
    
    Returns:
        AIService ou None si la configuration échoue
    """
    return get_ai_service(provider=AIProvider.OPENAI, model=model, enable_rgpd=enable_rgpd)


def get_ai_service(provider: Optional[AIProvider] = None, model: Optional[str] = None,
                   enable_rgpd: bool = True,
                   preprocess_model: Optional[str] = None,
                   generation_model: Optional[str] = None) -> Optional[AIService]:
    """
    Factory function pour obtenir une instance du service IA.
    
    Args:
        provider: Fournisseur IA à utiliser (si None, utilise le fournisseur actif)
        model: Modèle unique appliqué aux deux rôles (rétrocompatibilité)
        enable_rgpd: Active/désactive l'anonymisation RGPD (défaut: True)
        preprocess_model: Modèle de prétraitement (optionnel, sinon configuration)
        generation_model: Modèle d'appréciation (optionnel, sinon configuration)
    
    Returns:
        AIService ou None si la configuration échoue
    """
    try:
        service = AIService(
            provider=provider,
            model=model,
            enable_rgpd=enable_rgpd,
            preprocess_model=preprocess_model,
            generation_model=generation_model,
        )
        if service.test_connection():
            return service
        else:
            return None
    except Exception as e:
        logging.error(f"Impossible d'initialiser le service IA: {e}")
        return None 