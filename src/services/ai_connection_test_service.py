#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service de test de connexion pour les fournisseurs IA
"""

import logging
from typing import Dict, Any, Optional
import time

try:
    from .ai_config_service import AIProvider
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ai_config_service import AIProvider

# Imports conditionnels pour les clients IA
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
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    genai = None


class ConnectionTestResult:
    """Résultat d'un test de connexion"""
    
    def __init__(self, success: bool, message: str, details: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.details = details or {}
        self.timestamp = time.time()


class AIConnectionTestService:
    """Service de test de connexion pour les fournisseurs IA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self, provider: AIProvider, api_key: str, model: str) -> ConnectionTestResult:
        """Teste la connexion avec un fournisseur IA"""
        # Pour LOCAL, la validation est différente (pas de clé API obligatoire)
        if provider != AIProvider.LOCAL and (not api_key or not api_key.strip()):
            return ConnectionTestResult(
                success=False,
                message="Clé API manquante",
                details={"error_type": "missing_key"}
            )
        
        try:
            if provider == AIProvider.OPENAI:
                return self._test_openai_connection(api_key, model)
            elif provider == AIProvider.ANTHROPIC:
                return self._test_anthropic_connection(api_key, model)
            elif provider == AIProvider.GEMINI:
                return self._test_gemini_connection(api_key, model)
            elif provider == AIProvider.LOCAL:
                return self._test_local_connection(api_key, model)  # api_key contient l'URL pour LOCAL
            else:
                return ConnectionTestResult(
                    success=False,
                    message=f"Fournisseur non supporté: {provider.value}",
                    details={"error_type": "unsupported_provider"}
                )
        
        except Exception as e:
            self.logger.error(f"Erreur lors du test de connexion {provider.value}: {e}")
            return ConnectionTestResult(
                success=False,
                message=f"Erreur inattendue: {str(e)}",
                details={"error_type": "unexpected_error", "exception": str(e)}
            )
    
    def _test_openai_connection(self, api_key: str, model: str) -> ConnectionTestResult:
        """Teste la connexion OpenAI"""
        if not OPENAI_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message="Client OpenAI non installé. Exécutez: pip install openai>=1.0.0",
                details={"error_type": "client_missing"}
            )
        
        try:
            # Créer le client OpenAI
            client = openai.OpenAI(api_key=api_key)
            
            # Test simple avec une requête minimale
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                temperature=0
            )
            
            # Vérifier que la réponse est valide
            if response and response.choices:
                return ConnectionTestResult(
                    success=True,
                    message=f"✅ Connexion OpenAI réussie avec le modèle {model}",
                    details={
                        "model_used": model,
                        "response_id": response.id,
                        "usage": response.usage.dict() if response.usage else None
                    }
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide d'OpenAI",
                    details={"error_type": "invalid_response"}
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
        """Teste la connexion Anthropic"""
        if not ANTHROPIC_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message="Client Anthropic non installé. Exécutez: pip install anthropic>=0.21.0",
                details={"error_type": "client_missing"}
            )
        
        try:
            # Créer le client Anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Test simple avec une requête minimale
            response = client.messages.create(
                model=model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Test"}]
            )
            
            # Vérifier que la réponse est valide
            if response and response.content:
                return ConnectionTestResult(
                    success=True,
                    message=f"✅ Connexion Anthropic réussie avec le modèle {model}",
                    details={
                        "model_used": model,
                        "response_id": response.id,
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens
                        } if response.usage else None
                    }
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide d'Anthropic",
                    details={"error_type": "invalid_response"}
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
        """Teste la connexion Google Gemini"""
        if not GOOGLE_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message="Client Google Generative AI non installé. Exécutez: pip install google-generativeai>=0.3.0",
                details={"error_type": "client_missing"}
            )
        
        try:
            # Configurer l'API Google
            genai.configure(api_key=api_key)
            
            # Créer le modèle
            gen_model = genai.GenerativeModel(model)
            
            # Test simple avec une requête minimale
            response = gen_model.generate_content(
                "Test",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1,
                    temperature=0
                )
            )
            
            # Vérifier que la réponse est valide
            if response and hasattr(response, 'text'):
                return ConnectionTestResult(
                    success=True,
                    message=f"✅ Connexion Google Gemini réussie avec le modèle {model}",
                    details={
                        "model_used": model,
                        "usage": {
                            "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', None),
                            "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', None)
                        } if hasattr(response, 'usage_metadata') and response.usage_metadata else None
                    }
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide de Google Gemini",
                    details={"error_type": "invalid_response"}
                )
        
        except Exception as e:
            error_msg = str(e).lower()
            
            if "api_key" in error_msg or "invalid" in error_msg:
                return ConnectionTestResult(
                    success=False,
                    message="❌ Clé API Google invalide",
                    details={"error_type": "invalid_key"}
                )
            
            elif "not found" in error_msg or "model" in error_msg:
                return ConnectionTestResult(
                    success=False,
                    message=f"❌ Modèle '{model}' non trouvé ou non accessible",
                    details={"error_type": "model_not_found", "model": model}
                )
            
            elif "quota" in error_msg or "limit" in error_msg:
                return ConnectionTestResult(
                    success=False,
                    message="❌ Limite de quota atteinte - Vérifiez votre usage Google",
                    details={"error_type": "quota_exceeded"}
                )
            
            elif "permission" in error_msg or "denied" in error_msg:
                return ConnectionTestResult(
                    success=False,
                    message="❌ Accès refusé - Vérifiez les permissions de votre clé API Google",
                    details={"error_type": "permission_denied"}
                )
            
            else:
                return ConnectionTestResult(
                    success=False,
                    message=f"❌ Erreur Google Gemini: {str(e)}",
                    details={"error_type": "gemini_error", "exception": str(e)}
                )
    
    def _test_local_connection(self, base_url: str, model: str) -> ConnectionTestResult:
        """Teste la connexion vers un serveur LLM local"""
        if not OPENAI_AVAILABLE:
            return ConnectionTestResult(
                success=False,
                message="Client OpenAI requis pour les connexions locales. Exécutez: pip install openai>=1.0.0",
                details={"error_type": "client_missing"}
            )
        
        if not base_url or not base_url.strip():
            return ConnectionTestResult(
                success=False,
                message="URL du serveur local manquante",
                details={"error_type": "missing_url"}
            )
        
        try:
            # Préparer l'URL pour l'API
            clean_url = base_url.strip()
            
            # Convertir l'URL Ollama vers le format OpenAI si nécessaire
            if "localhost:11434" in clean_url and not clean_url.endswith("/v1"):
                clean_url = clean_url.rstrip("/") + "/v1"
            elif not clean_url.endswith("/v1") and "localhost:1234" not in clean_url:
                # Pour d'autres serveurs locaux, tenter d'ajouter /v1 si pas déjà présent
                if not any(x in clean_url for x in ["/v1", "/api", "/chat"]):
                    clean_url = clean_url.rstrip("/") + "/v1"
            
            # Créer le client OpenAI avec l'URL locale
            client = openai.OpenAI(
                api_key="local-api-key",  # Clé factice pour les serveurs locaux
                base_url=clean_url
            )
            
            # Test de connexion simple
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                temperature=0
            )
            
            # Vérifier que la réponse est valide
            if response and response.choices:
                return ConnectionTestResult(
                    success=True,
                    message=f"✅ Connexion au serveur local réussie avec le modèle {model}",
                    details={
                        "base_url": clean_url,
                        "model_used": model,
                        "response_id": getattr(response, 'id', 'N/A'),
                        "usage": response.usage.dict() if response.usage else None
                    }
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    message="Réponse invalide du serveur local",
                    details={"error_type": "invalid_response", "base_url": clean_url}
                )
        
        except openai.NotFoundError:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Modèle '{model}' non trouvé sur le serveur local. Vérifiez que le modèle est installé.",
                details={"error_type": "model_not_found", "model": model, "base_url": clean_url}
            )
        
        except openai.APIConnectionError as e:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Impossible de se connecter au serveur local {clean_url}. Vérifiez que le serveur est démarré.",
                details={"error_type": "connection_error", "base_url": clean_url, "exception": str(e)}
            )
        
        except openai.BadRequestError as e:
            return ConnectionTestResult(
                success=False,
                message=f"❌ Requête invalide vers le serveur local. Vérifiez l'URL et le modèle.",
                details={"error_type": "bad_request", "base_url": clean_url, "exception": str(e)}
            )
        
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "timeout" in error_msg:
                return ConnectionTestResult(
                    success=False,
                    message=f"❌ Erreur de connexion au serveur local {clean_url}. Vérifiez que le serveur est accessible.",
                    details={"error_type": "connection_error", "base_url": clean_url, "exception": str(e)}
                )
            else:
                return ConnectionTestResult(
                    success=False,
                    message=f"❌ Erreur serveur local: {str(e)}",
                    details={"error_type": "local_error", "base_url": clean_url, "exception": str(e)}
                )
    
    def get_connection_requirements(self, provider: AIProvider) -> Dict[str, Any]:
        """Retourne les prérequis pour tester la connexion avec un fournisseur"""
        requirements = {
            AIProvider.OPENAI: {
                "client_available": OPENAI_AVAILABLE,
                "install_command": "pip install openai>=1.0.0",
                "api_key_url": "https://platform.openai.com/api-keys"
            },
            AIProvider.ANTHROPIC: {
                "client_available": ANTHROPIC_AVAILABLE,
                "install_command": "pip install anthropic>=0.21.0",
                "api_key_url": "https://console.anthropic.com/"
            },
            AIProvider.GEMINI: {
                "client_available": GOOGLE_AVAILABLE,
                "install_command": "pip install google-generativeai>=0.3.0",
                "api_key_url": "https://makersuite.google.com/app/apikey"
            },
            AIProvider.LOCAL: {
                "client_available": OPENAI_AVAILABLE,  # Utilise le client OpenAI
                "install_command": "pip install openai>=1.0.0",
                "setup_guide": "Démarrez votre serveur local (Ollama, LM Studio, etc.) et assurez-vous qu'il expose une API compatible OpenAI",
                "common_urls": {
                    "Ollama": "http://localhost:11434",
                    "LM Studio": "http://localhost:1234",
                    "Text Generation WebUI": "http://localhost:5000"
                }
            }
        }
        
        return requirements.get(provider, {})


# Instance singleton
_test_service = None

def get_ai_connection_test_service() -> AIConnectionTestService:
    """Retourne l'instance singleton du service de test de connexion"""
    global _test_service
    if _test_service is None:
        _test_service = AIConnectionTestService()
    return _test_service
