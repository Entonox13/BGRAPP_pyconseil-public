#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module contenant les prompts utilisés pour les appels API IA
Permet de modifier facilement les prompts sans toucher à la logique métier
"""

# ==========================================
# PROMPT DE PRÉTRAITEMENT DES APPRÉCIATIONS
# ==========================================
# Utilisé pour ajouter des balises HTML aux appréciations par matière
PROMPT_PREPROCESS_APPRECIATION = """Tu es un expert en analyse de commentaires pédagogiques. 
Ta tâche est d'ajouter des balises HTML pour mettre en évidence les aspects positifs et négatifs.

Règles:
- Entoure les phrases/expressions POSITIVES avec <span class="positif">texte</span>
- Entoure les phrases/expressions NÉGATIVES avec <span class="negatif">texte</span>
- Ne modifie PAS le contenu du texte, ajoute seulement les balises
- Garde la ponctuation et la structure originale
- Ne balise que les parties vraiment positives ou négatives, pas les neutres

IMPORTANT: Réponds UNIQUEMENT par le texte traité avec les balises HTML, sans aucune explication, préambule ou formatage supplémentaire. Le texte sera inséré tel quel dans l'application.

Texte à traiter:
"""

# ==========================================
# PROMPT DE GÉNÉRATION D'APPRÉCIATION GÉNÉRALE
# ==========================================
# Utilisé pour générer l'appréciation générale S2 à partir des appréciations par matière
# Note: Ce prompt est un template qui sera formaté avec les appréciations par matière
PROMPT_GENERATE_GENERAL_APPRECIATION_TEMPLATE = """Tu es un professeur principal rédigeant l'appréciation générale pour un conseil de classe ({semester_label}).

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


def get_preprocess_prompt() -> str:
    """
    Retourne le prompt pour le prétraitement des appréciations
    
    Returns:
        str: Prompt de prétraitement
    """
    return PROMPT_PREPROCESS_APPRECIATION


def get_generate_general_prompt(appreciations_text: str,
                                semester_label: str = "Semestre 2") -> str:
    """
    Retourne le prompt formaté pour la génération d'appréciation générale
    
    Args:
        appreciations_text: Texte formaté contenant les appréciations par matière
        
    Returns:
        str: Prompt formaté pour la génération
    """
    return PROMPT_GENERATE_GENERAL_APPRECIATION_TEMPLATE.format(
        appreciations_text=appreciations_text,
        semester_label=semester_label
    )

