# app/analysis_module.py
import pandas as pd

# app/context_memory.py
"""
Módulo de memoria de contexto (simple en memoria).
Guarda el estado de convocatorias previas por usuario.
"""

# Diccionario global en memoria
_context_store = {}

def save_context(user_id: str, context: dict):
    """Guarda el contexto del usuario."""
    _context_store[user_id] = context

def load_context(user_id: str) -> dict:
    """Devuelve el contexto guardado (si existe)."""
    return _context_store.get(user_id, None)

def has_context(user_id: str) -> bool:
    """Indica si el usuario tiene contexto previo."""
    return user_id in _context_store


def analizar_convocatoria(convocatoria: dict):
    """
    Analiza los datos de una convocatoria generada por selector_module.
    Devuelve (texto_resumen, resumen_dict).
    """
    jugadores = convocatoria.get("players_selected", [])
    if not jugadores:
        return "❌ No hay datos de jugadores en la convocatoria.", {}

    df = pd.DataFrame(jugadores)

    resumen = {}
    resumen["total_jugadores"] = len(df)
    resumen["edad_media"] = round(df["age"].dropna().astype(float).mean(), 1) if "age" in df and not df["age"].isnull().all() else None
    resumen["ligas_representadas"] = int(df["league"].nunique()) if "league" in df else 0
    resumen["clubes_representados"] = int(df["team"].nunique()) if "team" in df else 0

    top_clubes = df["team"].value_counts().head(5).to_dict() if "team" in df else {}
    distrib_pos = df["specific_position"].value_counts().to_dict() if "specific_position" in df else {}
    rend_por_pos = df.groupby("position")["score_individual"].mean().round(3).to_dict() if "position" in df and "score_individual" in df else {}

    texto = (
        f"📊 Análisis de la convocatoria\n"
        f"- Total jugadores: {resumen['total_jugadores']}\n"
        f"- Edad media: {resumen['edad_media']} años\n"
        f"- Ligas representadas: {resumen['ligas_representadas']}\n"
        f"- Clubes representados: {resumen['clubes_representados']}\n\n"
        f"🏟️ Clubes más representados:\n"
        + ("\n".join([f"  • {club}: {num}" for club, num in top_clubes.items()]) if top_clubes else "  • -") + "\n\n"
        f"⚙️ Distribución por posición específica:\n"
        + ("\n".join([f"  • {pos}: {num}" for pos, num in distrib_pos.items()]) if distrib_pos else "  • -") + "\n\n"
        f"💪 Rendimiento medio por rol:\n"
        + ("\n".join([f"  • {pos}: {val}" for pos, val in rend_por_pos.items()]) if rend_por_pos else "  • -")
    )

    return texto, resumen
