"""
Service d'analyse LLM — PROFILER by DORIA
Lot 1 : classification profil comportemental client
Lot 2 : extraction clusters/sous-clusters + sentiment + score satisfaction
"""
import json
import httpx
from app.config import settings


def _call_claude(prompt: str, system: str = "") -> str:
    """Appel direct à l'API Anthropic (claude-haiku-4-5, rapide et économique)."""
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=body,
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def classify_profile(transcription_text: str, profiles: list[dict]) -> dict:
    """
    Lot 1 — Classifie le client parmi les profils du projet.

    profiles: [{"id": "uuid", "name": "conquête", "description": "...", "is_neutral": false}]
    Retourne: {"profile_id": "uuid", "confidence": 0.85, "reasoning": "..."}
    """
    profiles_desc = "\n".join(
        f"- Profil {i+1} [{p['name']}] (id={p['id']}): {p['description']}"
        for i, p in enumerate(profiles)
    )

    prompt = f"""Tu es un expert en analyse comportementale client pour des call centers.

Analyse la conversation suivante entre un CLIENT et un OPÉRATEUR.
Ton objectif : identifier le profil comportemental du CLIENT (pas de l'opérateur) parmi les profils définis ci-dessous.

PROFILS DISPONIBLES :
{profiles_desc}

CONVERSATION :
{transcription_text}

INSTRUCTIONS :
- Analyse uniquement le comportement et les propos du CLIENT.
- Choisis le profil qui correspond le mieux à son attitude et ses intentions d'achat.
- Si aucun profil ne correspond clairement, choisis le profil "Non catégorisé" (is_neutral=true).
- Réponds UNIQUEMENT en JSON valide, sans texte avant ou après.

FORMAT DE RÉPONSE :
{{
  "profile_id": "<uuid du profil choisi>",
  "confidence": <0.0 à 1.0>,
  "reasoning": "<explication courte en français, 1-3 phrases>"
}}"""

    raw = _call_claude(prompt)
    # Nettoyer les balises markdown si présentes
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def extract_clusters(transcription_text: str) -> dict:
    """
    Lot 2 — Extrait les thèmes (clusters/sous-clusters), sentiment et score satisfaction.

    Retourne: {
        "clusters": [{"name": "Prix", "sentiment": "+", "sub_clusters": [...]}],
        "satisfaction_score": 7.5,
        "satisfaction_reasoning": "..."
    }
    """
    prompt = f"""Tu es un expert en analyse de conversations de call center.

Analyse la conversation suivante entre un CLIENT et un OPÉRATEUR.
Identifie les thèmes évoqués UNIQUEMENT dans les propos du CLIENT.

CONVERSATION :
{transcription_text}

INSTRUCTIONS :
1. Détecte les clusters (thèmes principaux) et sous-clusters (thèmes spécifiques) dans les propos du client.
2. Pour chaque cluster et sous-cluster, définis le sentiment : "+" (positif), "neutre", ou "-" (négatif).
3. Génère un score de satisfaction global du client de 0 à 10 (0 = très insatisfait, 10 = très satisfait).
4. Réponds UNIQUEMENT en JSON valide, sans texte avant ou après.

FORMAT DE RÉPONSE :
{{
  "clusters": [
    {{
      "name": "<nom du thème principal>",
      "sentiment": "<+|neutre|->",
      "sub_clusters": [
        {{
          "name": "<nom du sous-thème>",
          "sentiment": "<+|neutre|->"
        }}
      ]
    }}
  ],
  "satisfaction_score": <0.0 à 10.0>,
  "satisfaction_reasoning": "<explication courte en français, 1-2 phrases>"
}}"""

    raw = _call_claude(prompt)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def run_full_analysis(transcription_text: str, profiles: list[dict]) -> dict:
    """
    Lance Lot 1 + Lot 2 en séquence.
    Retourne un dict avec profile + clusters + satisfaction.
    """
    result = {}

    # Lot 1 : Profil
    try:
        profile_result = classify_profile(transcription_text, profiles)
        result.update(profile_result)
    except Exception as e:
        result["profile_error"] = str(e)

    # Lot 2 : Clusters & satisfaction
    try:
        clusters_result = extract_clusters(transcription_text)
        result.update(clusters_result)
    except Exception as e:
        result["clusters_error"] = str(e)

    return result
