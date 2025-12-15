# app/sibi_agent.py
from app.context_memory import load_context, save_context
from app.selector_module import generar_convocatoria

def ajustar_convocatoria(user_id: str, instruccion: str):
    """
    Ajusta la última convocatoria guardada según una nueva instrucción del usuario.
    Devuelve un resumen textual del cambio y el nuevo resultado.
    """
    context = load_context(user_id)
    if not context:
        return "❌ No hay ninguna convocatoria previa para ajustar.", None

    params = context["params"].copy()
    cambios = []
    t = instruccion.lower()

    # 🔹 Cambios de estilo
    if "ofensiv" in t:
        if params.get("style") != "ofensivo":
            params["style"] = "ofensivo"
            cambios.append("estilo cambiado a ofensivo")
    elif "defensiv" in t:
        if params.get("style") != "defensivo":
            params["style"] = "defensivo"
            cambios.append("estilo cambiado a defensivo")
    elif "balancead" in t:
        if params.get("style") != "balanceado":
            params["style"] = "balanceado"
            cambios.append("estilo cambiado a balanceado")

    # 🔹 Cambios en número de jugadores por posición
    spec = params.get("specific_positions_config", {})

    if any(k in t for k in ["más delanter", "añade un delantero", "añade otro delantero", "un atacante más"]):
        spec["DC"] = spec.get("DC", 2) + 1
        cambios.append("añadido un delantero")

    if any(k in t for k in ["menos defens", "quita un defensa", "reduce defensas"]):
        spec["DFC"] = max(1, spec.get("DFC", 4) - 1)
        cambios.append("quitado un defensa")

    if any(k in t for k in ["más mediocentros", "añade un mediocentro", "un medio más"]):
        spec["MC"] = spec.get("MC", 4) + 1
        cambios.append("añadido un mediocentro")

    if any(k in t for k in ["menos delanter", "quita un delantero"]):
        spec["DC"] = max(1, spec.get("DC", 2) - 1)
        cambios.append("quitado un delantero")

    params["specific_positions_config"] = spec

    # 🔹 Regenerar convocatoria con los nuevos parámetros
    new_result = generar_convocatoria(**params)
    save_context(user_id, {"params": params, "result": new_result})

    resumen = "🔁 Ajuste aplicado:\n" + ("\n".join(f" - {c}" for c in cambios) if cambios else " - sin cambios detectados")
    return resumen, new_result
