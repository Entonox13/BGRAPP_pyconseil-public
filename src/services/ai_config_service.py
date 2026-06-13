#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de configuration IA multi-fournisseurs pour l'application BGRAPP Pyconseil.
Gère les clés API, modèles et le fournisseur actif (OpenAI, Anthropic, Gemini).
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum

try:
    from dotenv import load_dotenv, set_key
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv non disponible. Configuration .env limitée.")


def resolve_env_path() -> Path:
    """Détermine l'emplacement du fichier .env, y compris en mode packagé.

    - AppImage : à côté du fichier .AppImage (variable d'environnement APPIMAGE)
    - Exécutable PyInstaller (Windows/Linux onefile) : à côté de l'exécutable
    - Mode source : à la racine du projet
    """
    appimage = os.environ.get("APPIMAGE")
    if appimage:
        return Path(appimage).resolve().parent / ".env"
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / ".env"
    return Path(__file__).resolve().parent.parent.parent / ".env"


class AIProvider(Enum):
    """Énumération des fournisseurs d'IA supportés."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class AIConfigService:
    """Service de configuration multi-fournisseurs (OpenAI, Anthropic, Gemini)."""

    # Rôles de modèle : un modèle distinct par étape de traitement.
    #   preprocess  -> ajout des balises HTML aux appréciations par matière
    #   generation  -> rédaction de l'appréciation générale
    MODEL_ROLES = ("preprocess", "generation")
    MODEL_ROLE_LABELS = {
        "preprocess": "Modèle de prétraitement",
        "generation": "Modèle d'appréciation",
    }
    DEFAULT_MODEL_ROLE = "generation"

    AVAILABLE_MODELS = {
        AIProvider.OPENAI: [
            "gpt-5.5",
            "gpt-5.4",
            "gpt-5.4-mini",
            "gpt-5.4-nano",
            "gpt-5",
            "gpt-5-mini",
        ],
        AIProvider.ANTHROPIC: [
            "claude-opus-4-8",
            "claude-sonnet-4-6",
            "claude-haiku-4-5",
        ],
        AIProvider.GEMINI: [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
        ],
    }

    DEFAULT_MODELS = {
        AIProvider.OPENAI: "gpt-5-mini",
        AIProvider.ANTHROPIC: "claude-sonnet-4-6",
        AIProvider.GEMINI: "gemini-2.5-flash",
    }

    ENV_KEYS = {
        AIProvider.OPENAI: "OPENAI_API_KEY",
        AIProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
        AIProvider.GEMINI: "GEMINI_API_KEY",
    }

    # Une variable d'environnement par fournisseur ET par rôle.
    ENV_MODELS = {
        AIProvider.OPENAI: {
            "preprocess": "OPENAI_MODEL_PREPROCESS",
            "generation": "OPENAI_MODEL_GENERATION",
        },
        AIProvider.ANTHROPIC: {
            "preprocess": "ANTHROPIC_MODEL_PREPROCESS",
            "generation": "ANTHROPIC_MODEL_GENERATION",
        },
        AIProvider.GEMINI: {
            "preprocess": "GEMINI_MODEL_PREPROCESS",
            "generation": "GEMINI_MODEL_GENERATION",
        },
    }

    # Ancienne variable unique (rétrocompatibilité des fichiers .env existants).
    LEGACY_ENV_MODELS = {
        AIProvider.OPENAI: "OPENAI_MODEL",
        AIProvider.ANTHROPIC: "ANTHROPIC_MODEL",
        AIProvider.GEMINI: "GEMINI_MODEL",
    }

    PLACEHOLDER_KEYS = {"your-api-key-here", "votre-cle-api", ""}

    def __init__(self):
        """Initialise le service de configuration."""
        self.logger = logging.getLogger(__name__)
        self.env_path = resolve_env_path()

        self._load_environment()

        self._config = {
            "enabled_provider": AIProvider.OPENAI,
            "api_keys": {},
            "models": {}
        }

        self._load_config_from_env()

    def _ensure_known_provider(self, provider: AIProvider):
        """Vérifie que le fournisseur fait bien partie de l'énumération supportée."""
        if not isinstance(provider, AIProvider):
            raise ValueError(f"Fournisseur non supporté: {provider}")

    def _is_valid_key(self, value: Optional[str]) -> bool:
        """Indique si une valeur de clé API est exploitable (non vide / non placeholder)."""
        return bool(value and value.strip() and value.strip() not in self.PLACEHOLDER_KEYS)

    def _load_environment(self):
        """Charge les variables d'environnement depuis le fichier .env."""
        if DOTENV_AVAILABLE and self.env_path.exists():
            load_dotenv(self.env_path)
            self.logger.info(f"Configuration chargée depuis {self.env_path}")
            return

        if not self.env_path.exists():
            self.logger.warning(f"Fichier .env non trouvé: {self.env_path}")
        else:
            self.logger.warning("python-dotenv non disponible")

    def _normalize_role(self, role: Optional[str]) -> str:
        """Retourne un rôle de modèle valide (fallback sur le rôle par défaut)."""
        return role if role in self.MODEL_ROLES else self.DEFAULT_MODEL_ROLE

    def _load_config_from_env(self):
        """Charge la configuration de tous les fournisseurs depuis l'environnement."""
        for provider in AIProvider:
            api_key = os.getenv(self.ENV_KEYS[provider])
            if self._is_valid_key(api_key):
                self._config["api_keys"][provider] = api_key.strip()
                self.logger.debug("Clé API %s chargée", provider.value)

            legacy_model = os.getenv(self.LEGACY_ENV_MODELS[provider])
            self._config["models"].setdefault(provider, {})
            for role in self.MODEL_ROLES:
                value = os.getenv(self.ENV_MODELS[provider][role])
                if value and value.strip():
                    self._config["models"][provider][role] = value.strip()
                elif legacy_model and legacy_model.strip():
                    self._config["models"][provider][role] = legacy_model.strip()
                else:
                    self._config["models"][provider][role] = self.DEFAULT_MODELS[provider]

        enabled_provider = os.getenv("AI_ENABLED_PROVIDER", "").strip().lower()
        if enabled_provider:
            try:
                self._config["enabled_provider"] = AIProvider(enabled_provider)
            except ValueError:
                self.logger.warning(
                    "AI_ENABLED_PROVIDER=%s inconnu, fallback sur openai",
                    enabled_provider
                )
                self._config["enabled_provider"] = AIProvider.OPENAI
        else:
            self._config["enabled_provider"] = AIProvider.OPENAI

    def get_api_key(self, provider: AIProvider) -> Optional[str]:
        """Récupère la clé API pour un fournisseur.

        Si aucune clé n'est présente dans la configuration interne, on tente de
        relire la variable d'environnement correspondante (robustesse).
        """
        self._ensure_known_provider(provider)
        key = self._config["api_keys"].get(provider)
        if not key:
            env_key_name = self.ENV_KEYS.get(provider)
            if env_key_name:
                env_value = os.getenv(env_key_name)
                if self._is_valid_key(env_value):
                    cleaned = env_value.strip()
                    self._config["api_keys"][provider] = cleaned
                    self.logger.info(
                        "Clé API %s chargée dynamiquement depuis l'environnement",
                        provider.value
                    )
                    return cleaned
        return key

    def set_api_key(self, provider: AIProvider, api_key: str):
        """Définit la clé API pour un fournisseur."""
        self._ensure_known_provider(provider)
        if api_key and api_key.strip():
            cleaned = api_key.strip()
            self._config["api_keys"][provider] = cleaned
            self._save_to_env(self.ENV_KEYS[provider], cleaned)
            self.logger.info("Clé API mise à jour pour %s", provider.value)
            return

        self._config["api_keys"].pop(provider, None)
        self._save_to_env(self.ENV_KEYS[provider], "")

    def get_model(self, provider: AIProvider, role: str = DEFAULT_MODEL_ROLE) -> str:
        """Récupère le modèle configuré pour un fournisseur et un rôle.

        Args:
            provider: Fournisseur IA.
            role: "preprocess" (prétraitement) ou "generation" (appréciation).
        """
        self._ensure_known_provider(provider)
        role = self._normalize_role(role)
        return self._config["models"].get(provider, {}).get(role, self.DEFAULT_MODELS[provider])

    def set_model(self, provider: AIProvider, model: str, role: str = DEFAULT_MODEL_ROLE):
        """Définit le modèle pour un fournisseur et un rôle donné."""
        self._ensure_known_provider(provider)
        role = self._normalize_role(role)
        if not model or not model.strip():
            raise ValueError("Le modèle ne peut pas être vide.")

        cleaned = model.strip()
        if cleaned not in self.AVAILABLE_MODELS[provider]:
            self.logger.warning(
                "Modèle %s non listé (%s), il sera tout de même enregistré",
                provider.value,
                cleaned
            )
        self._config["models"].setdefault(provider, {})[role] = cleaned
        self._save_to_env(self.ENV_MODELS[provider][role], cleaned)
        self.logger.info("Modèle (%s) mis à jour pour %s: %s", role, provider.value, cleaned)

    def get_available_models(self, provider: AIProvider) -> List[str]:
        """Récupère la liste des modèles disponibles pour un fournisseur."""
        self._ensure_known_provider(provider)
        return self.AVAILABLE_MODELS[provider].copy()

    def get_base_url(self, provider: AIProvider) -> Optional[str]:
        """Compatibilité API historique. Les fournisseurs publics n'utilisent
        pas d'URL personnalisée ici."""
        self._ensure_known_provider(provider)
        return None

    def set_base_url(self, provider: AIProvider, base_url: str):
        """Compatibilité API historique (ignoré pour les fournisseurs publics)."""
        self._ensure_known_provider(provider)
        if base_url and base_url.strip():
            self.logger.warning(
                "set_base_url ignoré pour %s (valeur reçue: %s)",
                provider.value,
                base_url.strip()
            )

    def get_enabled_provider(self) -> Optional[AIProvider]:
        """Récupère le fournisseur actuellement actif."""
        return self._config.get("enabled_provider", AIProvider.OPENAI)

    def set_enabled_provider(self, provider: AIProvider):
        """Définit le fournisseur actif."""
        self._ensure_known_provider(provider)
        self._config["enabled_provider"] = provider
        self._save_to_env("AI_ENABLED_PROVIDER", provider.value)
        self.logger.info("Fournisseur actif changé vers: %s", provider.value)

    def validate_configuration(self) -> Dict[str, Any]:
        """Valide la configuration actuelle."""
        enabled_provider = self.get_enabled_provider()
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "providers_with_keys": [],
            "enabled_provider": enabled_provider
        }

        for provider in AIProvider:
            if self.get_api_key(provider):
                result["providers_with_keys"].append(provider)

        if enabled_provider in result["providers_with_keys"]:
            result["valid"] = True
        else:
            result["errors"].append(
                f"Clé API manquante pour le fournisseur actif ({enabled_provider.value})"
            )

        return result

    def _save_to_env(self, key: str, value: str):
        """Sauvegarde une variable dans le fichier .env."""
        if not DOTENV_AVAILABLE:
            self.logger.warning(f"Impossible de sauvegarder {key}: python-dotenv non disponible")
            return

        try:
            if not self.env_path.exists():
                self.env_path.touch()

            set_key(str(self.env_path), key, value)
            self.logger.debug(f"Variable {key} sauvegardée dans .env")
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de {key}: {e}")

    def get_current_config_summary(self) -> Dict[str, Any]:
        """Récupère un résumé de la configuration actuelle."""
        return {
            "enabled_provider": self.get_enabled_provider(),
            "providers_with_keys": list(self._config["api_keys"].keys()),
            "models": {p: roles.copy() for p, roles in self._config["models"].items()},
            "base_urls": {},
            "validation": self.validate_configuration()
        }


_config_service = None


def get_ai_config_service() -> AIConfigService:
    """Factory function pour obtenir une instance du service de configuration."""
    global _config_service
    if _config_service is None:
        _config_service = AIConfigService()
    return _config_service


def requires_openai_responses_api(model: Optional[str]) -> bool:
    """L'application utilise systématiquement l'API Responses pour OpenAI."""
    return True
