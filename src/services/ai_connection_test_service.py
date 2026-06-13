#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de test de connexion IA multi-fournisseurs (OpenAI, Anthropic, Gemini).
"""

import logging
import re
from typing import Dict, Any, Optional
import time

try:
    from .ai_config_service import AIProvider
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ai_config_service import AIProvider

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

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


class ConnectionTestResult:
    """Résultat d'un test de connexion."""

    def __init__(self, success: bool, message: str, details: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()


class AIConnectionTestService:
    """Service de test de connexion multi-fournisseurs."""

    # ==========================================
    # FILTRES DE COMPATIBILITÉ DES MODÈLES
    # ==========================================
    # On ne garde que les familles de modèles compatibles avec nos appels API
    # récents (OpenAI Responses API, Anthropic Messages API, Gemini generateContent).
    # Cela exclut les modèles legacy (gpt-3.5, gpt-4 d'origine, claude-2,
    # gemini 1.0, etc.) qui reposaient sur d'anciens formats d'appel.

    # OpenAI : familles compatibles Responses API
    _OPENAI_COMPATIBLE_PATTERN = re.compile(
        r"^(gpt-5|gpt-4\.1|gpt-4o|o3|o4)", re.IGNORECASE
    )
    # OpenAI : variantes non textuelles à exclure même si la famille correspond
    _OPENAI_EXCLUDE_TOKENS = (
        "audio", "realtime", "image", "tts", "embedding",
        "moderation", "transcribe", "search", "dall-e", "whisper",
    )

    # Anthropic : génération 3.5+ et 4+ (toutes via Messages API)
    _ANTHROPIC_COMPATIBLE_PATTERN = re.compile(
        r"claude-(3-[5-9]|3\.[5-9]|opus-4|sonnet-4|haiku-4|[4-9])",
        re.IGNORECASE,
    )

    # Gemini : versions 2.x et supérieures (generateContent moderne)
    _GEMINI_COMPATIBLE_PATTERN = re.compile(
        r"gemini-([2-9]|\d{2,})", re.IGNORECASE
    )
    _GEMINI_EXCLUDE_TOKENS = ("embedding", "aqa", "imagen")

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def test_connection(self, provider: AIProvider, api_key: str, model: str) -> ConnectionTestResult:
        """Teste la connexion avec le fournisseur demandé."""
        if not api_key or not api_key.strip():
            return ConnectionTestResult(
                success=False,
                message="Clé API manquante",
                details={"error_type": "missing_key"}
            )

        api_key = api_key.strip()

        if provider == AIProvider.OPENAI:
            return self._test_openai_connection(api_key, model)
        if provider == AIProvider.ANTHROPIC:
            return self._test_anthropic_connection(api_key, model)
        if provider == AIProvider.GEMINI:
            return self._test_gemini_connection(api_key, model)

        return ConnectionTestResult(
            success=False,
            message=f"Fournisseur non supporté: {provider}",
            details={"error_type": "unsupported_provider"}
        )

    def _test_openai_connection(self, api_key: str, model: str) -> ConnectionTestResult:
        """Teste la connexion OpenAI via l'API Responses."""
        if not OPENAI_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message='Client OpenAI non installé. Exécutez: pip install "openai>=2.0"',
                details={"error_type": "client_missing"}
            )

        try:
            client = openai.OpenAI(api_key=api_key)
            # Utiliser un minimum de tokens conformément aux contraintes OpenAI (>=16)
            # Certains modèles ne supportent pas le paramètre temperature → on ne le passe pas.
            response = client.responses.create(
                model=model,
                input="Test",
                max_output_tokens=16,
            )

            text_output = getattr(response, "output_text", None)
            has_output_blocks = bool(getattr(response, "output", None))
            if not text_output and not has_output_blocks:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide d'OpenAI (responses)",
                    details={"error_type": "invalid_response"}
                )

            usage = None
            usage_obj = getattr(response, "usage", None)
            if usage_obj:
                usage = {
                    "input_tokens": getattr(usage_obj, "input_tokens", None),
                    "output_tokens": getattr(usage_obj, "output_tokens", None),
                    "total_tokens": getattr(usage_obj, "total_tokens", None),
                }

            return ConnectionTestResult(
                success=True,
                message=f"✅ Connexion OpenAI réussie avec le modèle {model}",
                details={
                    "model_used": model,
                    "response_id": getattr(response, "id", None),
                    "usage": usage
                }
            )

        except openai.AuthenticationError:
            return ConnectionTestResult(
                success=False,
                message="❌ Clé API OpenAI invalide",
                details={"error_type": "invalid_key"}
            )
        except openai.PermissionDeniedError:
            return ConnectionTestResult(
                success=False,
                message="❌ Accès refusé - Vérifiez les permissions de votre clé API OpenAI",
                details={"error_type": "permission_denied"}
            )
        except openai.NotFoundError:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Modèle '{model}' non trouvé ou non accessible",
                details={"error_type": "model_not_found", "model": model}
            )
        except openai.RateLimitError:
            return ConnectionTestResult(
                success=False,
                message="❌ Limite de taux atteinte - Attendez quelques instants",
                details={"error_type": "rate_limit"}
            )
        except openai.APIConnectionError:
            return ConnectionTestResult(
                success=False,
                message="❌ Erreur de connexion à l'API OpenAI",
                details={"error_type": "connection_error"}
            )
        except Exception as e:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Erreur OpenAI: {str(e)}",
                details={"error_type": "openai_error", "exception": str(e)}
            )

    def _test_anthropic_connection(self, api_key: str, model: str) -> ConnectionTestResult:
        """Teste la connexion Anthropic via l'API Messages."""
        if not ANTHROPIC_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message='Client Anthropic non installé. Exécutez: pip install "anthropic>=0.69"',
                details={"error_type": "client_missing"}
            )

        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=16,
                messages=[{"role": "user", "content": "Test"}],
            )

            has_content = bool(getattr(message, "content", None))
            if not has_content:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide d'Anthropic (messages)",
                    details={"error_type": "invalid_response"}
                )

            usage = None
            usage_obj = getattr(message, "usage", None)
            if usage_obj:
                usage = {
                    "input_tokens": getattr(usage_obj, "input_tokens", None),
                    "output_tokens": getattr(usage_obj, "output_tokens", None),
                }

            return ConnectionTestResult(
                success=True,
                message=f"✅ Connexion Anthropic réussie avec le modèle {model}",
                details={
                    "model_used": model,
                    "response_id": getattr(message, "id", None),
                    "usage": usage
                }
            )

        except anthropic.AuthenticationError:
            return ConnectionTestResult(
                success=False,
                message="❌ Clé API Anthropic invalide",
                details={"error_type": "invalid_key"}
            )
        except anthropic.PermissionDeniedError:
            return ConnectionTestResult(
                success=False,
                message="❌ Accès refusé - Vérifiez les permissions de votre clé API Anthropic",
                details={"error_type": "permission_denied"}
            )
        except anthropic.NotFoundError:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Modèle '{model}' non trouvé ou non accessible",
                details={"error_type": "model_not_found", "model": model}
            )
        except anthropic.RateLimitError:
            return ConnectionTestResult(
                success=False,
                message="❌ Limite de taux atteinte - Attendez quelques instants",
                details={"error_type": "rate_limit"}
            )
        except anthropic.APIConnectionError:
            return ConnectionTestResult(
                success=False,
                message="❌ Erreur de connexion à l'API Anthropic",
                details={"error_type": "connection_error"}
            )
        except Exception as e:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Erreur Anthropic: {str(e)}",
                details={"error_type": "anthropic_error", "exception": str(e)}
            )

    def _test_gemini_connection(self, api_key: str, model: str) -> ConnectionTestResult:
        """Teste la connexion Google Gemini via google-genai."""
        if not GEMINI_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message='Client Gemini non installé. Exécutez: pip install "google-genai>=2.0"',
                details={"error_type": "client_missing"}
            )

        try:
            client = google_genai.Client(api_key=api_key)
            config = google_genai_types.GenerateContentConfig(max_output_tokens=16)
            response = client.models.generate_content(
                model=model,
                contents="Test",
                config=config,
            )

            has_text = bool(getattr(response, "text", None))
            has_candidates = bool(getattr(response, "candidates", None))
            if not has_text and not has_candidates:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide de Gemini",
                    details={"error_type": "invalid_response"}
                )

            usage = None
            usage_obj = getattr(response, "usage_metadata", None)
            if usage_obj:
                usage = {
                    "input_tokens": getattr(usage_obj, "prompt_token_count", None),
                    "output_tokens": getattr(usage_obj, "candidates_token_count", None),
                    "total_tokens": getattr(usage_obj, "total_token_count", None),
                }

            return ConnectionTestResult(
                success=True,
                message=f"✅ Connexion Gemini réussie avec le modèle {model}",
                details={
                    "model_used": model,
                    "usage": usage
                }
            )

        except Exception as e:
            message = str(e)
            lowered = message.lower()
            if "api key" in lowered or "api_key" in lowered or "permission" in lowered or "unauthenticated" in lowered:
                error_type = "invalid_key"
                display = "❌ Clé API Gemini invalide ou non autorisée"
            elif "not found" in lowered or "404" in lowered:
                error_type = "model_not_found"
                display = f"❌ Modèle '{model}' non trouvé ou non accessible"
            elif "quota" in lowered or "rate" in lowered or "429" in lowered:
                error_type = "rate_limit"
                display = "❌ Limite de taux/quota atteinte - Attendez quelques instants"
            else:
                error_type = "gemini_error"
                display = f"❌ Erreur Gemini: {message}"
            return ConnectionTestResult(
                success=False,
                message=display,
                details={"error_type": error_type, "exception": message}
            )

    def fetch_models(self, provider: AIProvider, api_key: str) -> Dict[str, Any]:
        """Récupère dynamiquement la liste des modèles disponibles via l'API.

        Returns:
            dict: {"success": bool, "models": List[str], "message": str}
        """
        if not api_key or not api_key.strip():
            return {"success": False, "models": [], "message": "Clé API manquante"}

        api_key = api_key.strip()

        try:
            if provider == AIProvider.OPENAI:
                return self._fetch_openai_models(api_key)
            if provider == AIProvider.ANTHROPIC:
                return self._fetch_anthropic_models(api_key)
            if provider == AIProvider.GEMINI:
                return self._fetch_gemini_models(api_key)
        except Exception as e:
            self.logger.error("Erreur récupération modèles %s: %s", getattr(provider, "value", provider), e)
            return {"success": False, "models": [], "message": f"❌ Erreur: {str(e)}"}

        return {"success": False, "models": [], "message": f"Fournisseur non supporté: {provider}"}

    def _fetch_openai_models(self, api_key: str) -> Dict[str, Any]:
        """Liste les modèles texte OpenAI pertinents."""
        if not OPENAI_AVAILABLE:
            return {"success": False, "models": [],
                    "message": 'Client OpenAI non installé. pip install "openai>=2.0"'}

        client = openai.OpenAI(api_key=api_key)
        page = client.models.list()

        models = []
        for model in page:
            model_id = getattr(model, "id", None)
            if not model_id:
                continue
            lowered = model_id.lower()
            if not self._OPENAI_COMPATIBLE_PATTERN.match(lowered):
                continue
            if any(token in lowered for token in self._OPENAI_EXCLUDE_TOKENS):
                continue
            models.append(model_id)

        models = sorted(set(models))
        if not models:
            return {"success": False, "models": [],
                    "message": "Aucun modèle compatible (Responses API) trouvé"}
        return {"success": True, "models": models,
                "message": f"{len(models)} modèles OpenAI compatibles récupérés"}

    def _fetch_anthropic_models(self, api_key: str) -> Dict[str, Any]:
        """Liste les modèles Anthropic disponibles."""
        if not ANTHROPIC_AVAILABLE:
            return {"success": False, "models": [],
                    "message": 'Client Anthropic non installé. pip install "anthropic>=0.69"'}

        client = anthropic.Anthropic(api_key=api_key)
        page = client.models.list()

        models = []
        data = getattr(page, "data", None) or page
        for model in data:
            model_id = getattr(model, "id", None)
            if model_id and self._ANTHROPIC_COMPATIBLE_PATTERN.search(model_id.lower()):
                models.append(model_id)

        models = sorted(set(models))
        if not models:
            return {"success": False, "models": [],
                    "message": "Aucun modèle compatible (Messages API) trouvé"}
        return {"success": True, "models": models,
                "message": f"{len(models)} modèles Anthropic compatibles récupérés"}

    def _fetch_gemini_models(self, api_key: str) -> Dict[str, Any]:
        """Liste les modèles Gemini supportant la génération de contenu."""
        if not GEMINI_AVAILABLE:
            return {"success": False, "models": [],
                    "message": 'Client Gemini non installé. pip install "google-genai>=2.0"'}

        client = google_genai.Client(api_key=api_key)

        models = []
        for model in client.models.list():
            actions = getattr(model, "supported_actions", None) or []
            if actions and "generateContent" not in actions:
                continue
            name = getattr(model, "name", None)
            if not name:
                continue
            # Les noms sont de la forme "models/gemini-2.5-flash"
            short_name = name.split("/", 1)[-1]
            lowered = short_name.lower()
            if not self._GEMINI_COMPATIBLE_PATTERN.search(lowered):
                continue
            if any(token in lowered for token in self._GEMINI_EXCLUDE_TOKENS):
                continue
            models.append(short_name)

        models = sorted(set(models))
        if not models:
            return {"success": False, "models": [],
                    "message": "Aucun modèle compatible (generateContent récent) trouvé"}
        return {"success": True, "models": models,
                "message": f"{len(models)} modèles Gemini compatibles récupérés"}

    def get_connection_requirements(self, provider: AIProvider) -> Dict[str, Any]:
        """Retourne les prérequis pour tester la connexion d'un fournisseur."""
        requirements = {
            AIProvider.OPENAI: {
                "client_available": OPENAI_AVAILABLE,
                "install_command": 'pip install "openai>=2.0"',
                "api_key_url": "https://platform.openai.com/api-keys"
            },
            AIProvider.ANTHROPIC: {
                "client_available": ANTHROPIC_AVAILABLE,
                "install_command": 'pip install "anthropic>=0.69"',
                "api_key_url": "https://console.anthropic.com/settings/keys"
            },
            AIProvider.GEMINI: {
                "client_available": GEMINI_AVAILABLE,
                "install_command": 'pip install "google-genai>=2.0"',
                "api_key_url": "https://aistudio.google.com/app/apikey"
            },
        }
        return requirements.get(provider, {})


_test_service = None


def get_ai_connection_test_service() -> AIConnectionTestService:
    """Retourne l'instance singleton du service de test de connexion."""
    global _test_service
    if _test_service is None:
        _test_service = AIConnectionTestService()
    return _test_service
