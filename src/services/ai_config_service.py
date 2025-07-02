#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de configuration multi-fournisseurs IA pour l'application BGRAPP Pyconseil
Gère la configuration des clés API et modèles pour OpenAI, Anthropic, et Google Gemini
"""

import os
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


class AIProvider(Enum):
    """Énumération des fournisseurs d'IA supportés"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    LOCAL = "local"


class AIConfigService:
    """Service de configuration pour les fournisseurs d'IA"""
    
    # Modèles disponibles pour chaque fournisseur
    AVAILABLE_MODELS = {
        AIProvider.OPENAI: [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4o-mini-2024-07-18",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "o3-mini-2025-01-31"
        ],
        AIProvider.ANTHROPIC: [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022", 
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        AIProvider.GEMINI: [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ],
        AIProvider.LOCAL: [
            "llama3.2",
            "llama3.1",
            "llama3",
            "qwen2.5",
            "codellama",
            "mistral",
            "phi3",
            "gemma2",
            "custom-model"
        ]
    }
    
    # Modèles par défaut pour chaque fournisseur
    DEFAULT_MODELS = {
        AIProvider.OPENAI: "gpt-4o-mini-2024-07-18",
        AIProvider.ANTHROPIC: "claude-3-5-haiku-20241022",
        AIProvider.GEMINI: "gemini-1.5-flash",
        AIProvider.LOCAL: "llama3.2"
    }
    
    # Variables d'environnement pour les clés API
    ENV_KEYS = {
        AIProvider.OPENAI: "OPENAI_API_KEY",
        AIProvider.ANTHROPIC: "ANTHROPIC_API_KEY", 
        AIProvider.GEMINI: "GOOGLE_API_KEY",
        AIProvider.LOCAL: "LOCAL_API_KEY"  # Optionnel pour certaines configs locales
    }
    
    # Variables d'environnement pour les modèles
    ENV_MODELS = {
        AIProvider.OPENAI: "OPENAI_MODEL",
        AIProvider.ANTHROPIC: "ANTHROPIC_MODEL",
        AIProvider.GEMINI: "GEMINI_MODEL",
        AIProvider.LOCAL: "LOCAL_MODEL"
    }
    
    # Variables d'environnement pour les URL de base (spécifique au LOCAL)
    ENV_BASE_URLS = {
        AIProvider.LOCAL: "LOCAL_BASE_URL"
    }
    
    # URL par défaut pour le provider LOCAL (Ollama par défaut)
    DEFAULT_BASE_URLS = {
        AIProvider.LOCAL: "http://localhost:11434"
    }
    
    def __init__(self):
        """Initialise le service de configuration"""
        self.logger = logging.getLogger(__name__)
        self.env_path = Path(__file__).parent.parent.parent / '.env'
        
        # Charger la configuration existante
        self._load_environment()
        
        # Configuration par défaut
        self._config = {
            'enabled_provider': AIProvider.OPENAI,  # Fournisseur actif par défaut
            'api_keys': {},
            'models': {},
            'base_urls': {}
        }
        
        # Charger la configuration depuis l'environnement
        self._load_config_from_env()
    
    def _load_environment(self):
        """Charge les variables d'environnement depuis le fichier .env"""
        if DOTENV_AVAILABLE and self.env_path.exists():
            load_dotenv(self.env_path)
            self.logger.info(f"Configuration chargée depuis {self.env_path}")
        else:
            if not self.env_path.exists():
                self.logger.warning(f"Fichier .env non trouvé: {self.env_path}")
            else:
                self.logger.warning("python-dotenv non disponible")
    
    def _load_config_from_env(self):
        """Charge la configuration depuis les variables d'environnement"""
        # Charger les clés API
        for provider, env_key in self.ENV_KEYS.items():
            api_key = os.getenv(env_key)
            if api_key and api_key.strip() and api_key != "your-api-key-here":
                self._config['api_keys'][provider] = api_key
                self.logger.debug(f"Clé API chargée pour {provider.value}")
        
        # Pour LOCAL, considérer qu'il est configuré même sans clé API
        if AIProvider.LOCAL not in self._config['api_keys']:
            self._config['api_keys'][AIProvider.LOCAL] = ""  # Clé vide pour LOCAL
        
        # Charger les URL de base (spécifique à LOCAL pour l'instant)
        for provider, env_key in self.ENV_BASE_URLS.items():
            base_url = os.getenv(env_key)
            if base_url and base_url.strip():
                self._config['base_urls'][provider] = base_url.strip()
            else:
                # Utiliser l'URL par défaut
                self._config['base_urls'][provider] = self.DEFAULT_BASE_URLS[provider]
        
        # Charger les modèles configurés
        for provider, env_key in self.ENV_MODELS.items():
            model = os.getenv(env_key)
            if model and model.strip():
                self._config['models'][provider] = model
            else:
                # Utiliser le modèle par défaut
                self._config['models'][provider] = self.DEFAULT_MODELS[provider]
        
        # Déterminer le fournisseur actif
        enabled_provider = os.getenv('AI_ENABLED_PROVIDER')
        if enabled_provider:
            try:
                provider_enum = AIProvider(enabled_provider.lower())
                if provider_enum in self._config['api_keys']:
                    self._config['enabled_provider'] = provider_enum
            except ValueError:
                self.logger.warning(f"Fournisseur inconnu dans AI_ENABLED_PROVIDER: {enabled_provider}")
    
    def get_api_key(self, provider: AIProvider) -> Optional[str]:
        """Récupère la clé API pour un fournisseur"""
        return self._config['api_keys'].get(provider)
    
    def set_api_key(self, provider: AIProvider, api_key: str):
        """Définit la clé API pour un fournisseur"""
        if api_key and api_key.strip():
            self._config['api_keys'][provider] = api_key.strip()
            self._save_to_env(self.ENV_KEYS[provider], api_key.strip())
            self.logger.info(f"Clé API mise à jour pour {provider.value}")
        else:
            # Supprimer la clé si vide
            self._config['api_keys'].pop(provider, None)
            self._save_to_env(self.ENV_KEYS[provider], "")
    
    def get_model(self, provider: AIProvider) -> str:
        """Récupère le modèle configuré pour un fournisseur"""
        return self._config['models'].get(provider, self.DEFAULT_MODELS[provider])
    
    def set_model(self, provider: AIProvider, model: str):
        """Définit le modèle pour un fournisseur"""
        if model in self.AVAILABLE_MODELS[provider]:
            self._config['models'][provider] = model
            self._save_to_env(self.ENV_MODELS[provider], model)
            self.logger.info(f"Modèle mis à jour pour {provider.value}: {model}")
        else:
            raise ValueError(f"Modèle {model} non supporté pour {provider.value}")
    
    def get_available_models(self, provider: AIProvider) -> List[str]:
        """Récupère la liste des modèles disponibles pour un fournisseur"""
        return self.AVAILABLE_MODELS[provider].copy()
    
    def get_base_url(self, provider: AIProvider) -> Optional[str]:
        """Récupère l'URL de base pour un fournisseur (utilisé pour LOCAL)"""
        return self._config['base_urls'].get(provider)
    
    def set_base_url(self, provider: AIProvider, base_url: str):
        """Définit l'URL de base pour un fournisseur"""
        if provider in self.ENV_BASE_URLS:
            self._config['base_urls'][provider] = base_url.strip() if base_url else self.DEFAULT_BASE_URLS[provider]
            self._save_to_env(self.ENV_BASE_URLS[provider], self._config['base_urls'][provider])
            self.logger.info(f"URL de base mise à jour pour {provider.value}: {self._config['base_urls'][provider]}")
        else:
            raise ValueError(f"URL de base non supportée pour {provider.value}")
    
    def get_enabled_provider(self) -> Optional[AIProvider]:
        """Récupère le fournisseur actuellement actif"""
        return self._config['enabled_provider']
    
    def set_enabled_provider(self, provider: AIProvider):
        """Définit le fournisseur actif"""
        # Pour LOCAL, pas besoin de clé API obligatoire
        if provider == AIProvider.LOCAL or provider in self._config['api_keys']:
            self._config['enabled_provider'] = provider
            self._save_to_env('AI_ENABLED_PROVIDER', provider.value)
            self.logger.info(f"Fournisseur actif changé vers: {provider.value}")
        else:
            raise ValueError(f"Aucune clé API configurée pour {provider.value}")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Valide la configuration actuelle"""
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'providers_with_keys': [],
            'enabled_provider': None
        }
        
        # Vérifier les clés API (LOCAL est toujours considéré comme configuré)
        for provider in AIProvider:
            if provider == AIProvider.LOCAL:
                result['providers_with_keys'].append(provider)  # LOCAL est toujours disponible
            elif provider in self._config['api_keys'] and self._config['api_keys'][provider]:
                result['providers_with_keys'].append(provider)
        
        # Vérifier qu'au moins un fournisseur est disponible
        if not result['providers_with_keys']:
            result['errors'].append("Aucun fournisseur IA configuré")
        else:
            result['valid'] = True
            
            # Vérifier le fournisseur activé
            enabled = self._config['enabled_provider']
            if enabled and (enabled == AIProvider.LOCAL or (enabled in self._config['api_keys'] and self._config['api_keys'][enabled])):
                result['enabled_provider'] = enabled
            else:
                result['warnings'].append("Aucun fournisseur actif configuré")
        
        return result
    
    def _save_to_env(self, key: str, value: str):
        """Sauvegarde une variable dans le fichier .env"""
        if not DOTENV_AVAILABLE:
            self.logger.warning(f"Impossible de sauvegarder {key}: python-dotenv non disponible")
            return
        
        try:
            # Créer le fichier .env s'il n'existe pas
            if not self.env_path.exists():
                self.env_path.touch()
            
            # Mettre à jour la variable
            set_key(str(self.env_path), key, value)
            self.logger.debug(f"Variable {key} sauvegardée dans .env")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de {key}: {e}")
    
    def get_current_config_summary(self) -> Dict[str, Any]:
        """Récupère un résumé de la configuration actuelle"""
        return {
            'enabled_provider': self._config['enabled_provider'],
            'providers_with_keys': list(self._config['api_keys'].keys()),
            'models': self._config['models'].copy(),
            'base_urls': self._config['base_urls'].copy(),
            'validation': self.validate_configuration()
        }


# Instance globale du service
_config_service = None

def get_ai_config_service() -> AIConfigService:
    """Factory function pour obtenir une instance du service de configuration"""
    global _config_service
    if _config_service is None:
        _config_service = AIConfigService()
    return _config_service 