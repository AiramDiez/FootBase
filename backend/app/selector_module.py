# app/selector_module.py
import pandas as pd
import numpy as np
import random
from neo4j import GraphDatabase

# -----------------------------------------------------------
# 🔗 CONFIGURACIÓN DE CONEXIÓN NEO4J
# -----------------------------------------------------------
NEO4J_URI = "bolt://sibi-neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "recovery123"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# -----------------------------------------------------------
# ⚖️ PESOS POR POSICIÓN Y ESTILO (TODAS LAS ESTADÍSTICAS)
# -----------------------------------------------------------

WEIGHTS_BALANCEADO = {
    "POR": {
        "saves_per_game": 0.25, "clean_sheets": 0.25, "goals_conceded": 0.25, "penalty_save_pct": 0.25,
        "matches_played": 0.01, "minutes_played": 0.01, "yellow_cards": -0.01, "red_cards": -0.02,
        "pass_accuracy_pct": 0.03, "long_balls_per_game": 0.02,
        "height_cm": 0.01, "weight_kg": 0.01, "stamina": 0.01
    },
    "DF": {
        "tackles_per_game": 0.18, "interceptions_per_game": 0.15, "clearances_per_game": 0.12,
        "aerial_duels_won_pct": 0.1, "pass_accuracy_pct": 0.08, "fouls_per_game": -0.05,
        "yellow_cards": -0.03, "red_cards": -0.04, "goals": 0.05, "assists": 0.04,
        "passes_per_game": 0.05, "long_balls_per_game": 0.04, "crosses_per_game": 0.02,
        "matches_played": 0.02, "minutes_played": 0.02, "stamina": 0.02, "height_cm": 0.01
    },
    "MF": {
        "assists": 0.1, "key_passes_per_game": 0.1, "passes_per_game": 0.08,
        "pass_accuracy_pct": 0.08, "dribbles_per_game": 0.06, "tackles_per_game": 0.07,
        "interceptions_per_game": 0.06, "goals": 0.08, "shots_per_game": 0.05,
        "crosses_per_game": 0.04, "stamina": 0.03, "minutes_played": 0.03,
        "yellow_cards": -0.02, "red_cards": -0.02
    },
    "FW": {
        "goals": 0.3, "assists": 0.15, "shots_per_game": 0.15,
        "dribbles_per_game": 0.1, "key_passes_per_game": 0.08,
        "pass_accuracy_pct": 0.05, "fouls_per_game": -0.03,
        "stamina": 0.04, "matches_played": 0.02, "minutes_played": 0.02, "yellow_cards": -0.01
    }
}

WEIGHTS_DEFENSIVO = {
    "POR": {
        "clean_sheets": 0.35, "saves_per_game": 0.3, "goals_conceded": 0.2, "penalty_save_pct": 0.1,
        "pass_accuracy_pct": 0.03, "yellow_cards": -0.01, "red_cards": -0.02, "stamina": 0.02
    },
    "DF": {
        "tackles_per_game": 0.25, "interceptions_per_game": 0.2, "clearances_per_game": 0.15,
        "aerial_duels_won_pct": 0.1, "pass_accuracy_pct": 0.08, "passes_per_game": 0.05,
        "fouls_per_game": -0.05, "yellow_cards": -0.04, "red_cards": -0.04,
        "goals": 0.02, "assists": 0.02, "stamina": 0.02, "height_cm": 0.02
    },
    "MF": {
        "tackles_per_game": 0.2, "interceptions_per_game": 0.15, "passes_per_game": 0.1,
        "pass_accuracy_pct": 0.1, "stamina": 0.1, "fouls_per_game": -0.05,
        "assists": 0.07, "goals": 0.05, "yellow_cards": -0.03, "red_cards": -0.04,
        "key_passes_per_game": 0.05, "clearances_per_game": 0.03, "minutes_played": 0.02
    },
    "FW": {
        "assists": 0.15, "key_passes_per_game": 0.1,
        "tackles_per_game": 0.1, "pass_accuracy_pct": 0.1, "goals": 0.1,
        "shots_per_game": 0.05, "fouls_per_game": -0.05, "stamina": 0.05,
        "minutes_played": 0.05, "yellow_cards": -0.03, "red_cards": -0.02
    }
}

WEIGHTS_OFENSIVO = {
    "POR": {
        "pass_accuracy_pct": 0.25, "long_balls_per_game": 0.25, "saves_per_game": 0.25, "clean_sheets": 0.15,
        "goals_conceded": 0.05, "penalty_save_pct": 0.05
    },
    "DF": {
        "passes_per_game": 0.15, "pass_accuracy_pct": 0.15, "tackles_per_game": 0.1,
        "interceptions_per_game": 0.1, "assists": 0.08, "crosses_per_game": 0.08,
        "goals": 0.07, "dribbles_per_game": 0.05, "aerial_duels_won_pct": 0.05,
        "clearances_per_game": 0.05, "fouls_per_game": -0.03, "yellow_cards": -0.02,
        "stamina": 0.04
    },
    "MF": {
        "assists": 0.15, "key_passes_per_game": 0.15, "passes_per_game": 0.1,
        "pass_accuracy_pct": 0.1, "dribbles_per_game": 0.1, "goals": 0.1,
        "shots_per_game": 0.1, "crosses_per_game": 0.05, "stamina": 0.05,
        "fouls_per_game": -0.05, "yellow_cards": -0.02, "red_cards": -0.02
    },
    "FW": {
        "goals": 0.35, "shots_per_game": 0.2, "assists": 0.15,
        "dribbles_per_game": 0.1, "key_passes_per_game": 0.1,
        "pass_accuracy_pct": 0.05, "fouls_per_game": -0.03,
        "stamina": 0.05, "yellow_cards": -0.02, "red_cards": -0.02
    }
}

STYLE_WEIGHTS = {
    "balanceado": WEIGHTS_BALANCEADO,
    "defensivo": WEIGHTS_DEFENSIVO,
    "ofensivo": WEIGHTS_OFENSIVO
}

# -----------------------------------------------------------
# 🧮 PARÁMETROS GLOBALES
# -----------------------------------------------------------
ALPHA = 0.8  # Peso del rendimiento
BETA = 0.2   # Peso de la química


# -----------------------------------------------------------
# 🧠 FUNCIÓN PRINCIPAL (con búsqueda automática de mejor estilo)
# -----------------------------------------------------------

def generar_convocatoria(
    nationality: str,
    num_players: int = 23,
    style: str = "balanceado",
    injured_allowed: bool = False,
    specific_positions_config: dict = None,
    fixed_players: list = None,
    max_iterations: int = 300
):
    """
    Genera la mejor convocatoria según rendimiento + química (club + liga).
    Si no se especifica estilo (balanceado por defecto), prueba todos los estilos
    y devuelve el de mayor total_score.
    """
    # Si el usuario no especifica estilo (o usa "balanceado"), probamos los tres
    if style == "balanceado":
        styles_to_try = ["ofensivo", "defensivo", "balanceado"]
        best_result = None
        best_score = -1
        best_style = "balanceado"
        for candidate_style in styles_to_try:
            result = generar_convocatoria_interna(
                nationality, num_players, candidate_style,
                injured_allowed, specific_positions_config, fixed_players, max_iterations
            )
            if result["total_score"] > best_score:
                best_result = result
                best_score = result["total_score"]
                best_style = candidate_style
        best_result["style"] = best_style
        return best_result
    else:
        # Si ya se especificó estilo, usamos ese directamente
        return generar_convocatoria_interna(
            nationality, num_players, style,
            injured_allowed, specific_positions_config, fixed_players, max_iterations
        )


# -----------------------------------------------------------
# 🔧 FUNCIÓN INTERNA PARA UN ESTILO ESPECÍFICO
# -----------------------------------------------------------

def generar_convocatoria_interna(
    nationality: str,
    num_players: int,
    style: str,
    injured_allowed: bool,
    specific_positions_config: dict,
    fixed_players: list,
    max_iterations: int
):
    # 1) Obtener jugadores desde Neo4j
    with driver.session() as s:
        q = f"""
        MATCH (p:Player)
        WHERE p.nationality = $nation
        {'AND (p.injured IS NULL OR p.injured = "No")' if not injured_allowed else ''}
        RETURN p.player_id AS player_id, p.name AS name, p.age AS age, p.nationality AS nationality,
               p.team AS team, p.league AS league, p.position AS position,
               p.specific_position AS specific_position, p.injured AS injured,
               p.height_cm AS height_cm, p.weight_kg AS weight_kg, p.stamina AS stamina,
               p.matches_played AS matches_played, p.minutes_played AS minutes_played,
               p.yellow_cards AS yellow_cards, p.red_cards AS red_cards,
               p.goals AS goals, p.assists AS assists, p.shots_per_game AS shots_per_game,
               p.key_passes_per_game AS key_passes_per_game, p.dribbles_per_game AS dribbles_per_game,
               p.tackles_per_game AS tackles_per_game, p.interceptions_per_game AS interceptions_per_game,
               p.clearances_per_game AS clearances_per_game, p.aerial_duels_won_pct AS aerial_duels_won_pct,
               p.fouls_per_game AS fouls_per_game, p.pass_accuracy_pct AS pass_accuracy_pct,
               p.passes_per_game AS passes_per_game, p.long_balls_per_game AS long_balls_per_game,
               p.crosses_per_game AS crosses_per_game, p.saves_per_game AS saves_per_game,
               p.clean_sheets AS clean_sheets, p.goals_conceded AS goals_conceded,
               p.penalty_save_pct AS penalty_save_pct
        """
        df = pd.DataFrame([r.data() for r in s.run(q, nation=nationality)])
            # ✅ Guardar la edad original antes de normalizar (para mostrarla correctamente)
        df["age_raw"] = pd.to_numeric(df["age"], errors="coerce")

    if df.empty:
        return {"error": f"No se encontraron jugadores de {nationality}"}

    # Normalizar columnas numéricas
    exclude_cols = ["player_id", "name", "position", "specific_position", "team", "league", "nationality", "injured"]
    numeric_cols = [c for c in df.columns if c not in exclude_cols]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        if df[col].max() > df[col].min():
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # Score individual (normalizado por estilo)
    def calc_score(row):
        weights = STYLE_WEIGHTS.get(style, STYLE_WEIGHTS["balanceado"]).get(
            row.get("position"), STYLE_WEIGHTS["balanceado"]["MF"]
        )
        s = sum(float(row.get(stat, 0)) * w for stat, w in weights.items())
        # Normalizamos por estilo para evitar inflar scores
        style_multiplier = {"ofensivo": 0.97, "defensivo": 0.98, "balanceado": 1.0}[style]
        return s * style_multiplier

    df["score_individual"] = df.apply(calc_score, axis=1)

    # Matriz de química
    chem = {}
    ids = df["player_id"].tolist()
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            c = 1.0 if df.at[i, "team"] == df.at[j, "team"] else 0.5 if df.at[i, "league"] == df.at[j, "league"] else 0.0
            chem[(df.at[i, "player_id"], df.at[j, "player_id"])] = c

    # Default structure
    fixed_players = fixed_players or []
    selected = df[
        (df["name"].isin(fixed_players)) &
     (df["nationality"] == nationality)
    ].copy()


    # Estructura por defecto si no viene personalizada
    if not specific_positions_config:
        specific_positions_config = {
            "POR": 3, "DFC": 4, "LD": 2, "LI": 2,
            "MC": 4, "MCD": 2, "MCO": 2, "EI": 2, "ED": 2, "DC": 2
        }

    # --- Restar plazas en función de los jugadores fijos ---
    for _, row in selected.iterrows():
        pos = row.get("specific_position")
        if pos in specific_positions_config:
            specific_positions_config[pos] = max(0, specific_positions_config[pos] - 1)

    # Rellenar posiciones
    for pos, qty in specific_positions_config.items():
        already = selected[selected["specific_position"] == pos]
        needed = max(0, qty - len(already))
        if needed <= 0:
            continue
        pool = df[(df["specific_position"] == pos) & (~df["name"].isin(selected["name"]))]
        if pool.empty:
            general = "DF" if pos in ["DFC", "LD", "LI"] else "MF" if pos in ["MC", "MCD", "MCO"] else "FW" if pos in ["EI", "ED", "DC"] else "POR"
            pool = df[(df["position"] == general) & (~df["name"].isin(selected["name"]))]
        selected = pd.concat([selected, pool.sort_values("score_individual", ascending=False).head(needed)])

    if len(selected) < num_players:
        pool = df[~df["name"].isin(selected["name"])]
        selected = pd.concat([selected, pool.sort_values("score_individual", ascending=False).head(num_players - len(selected))])

    selected = selected.drop_duplicates(subset=["name"]).head(num_players)

    # Score del equipo
    def team_score(team_df):
        mean_ind = float(team_df["score_individual"].mean()) if not team_df.empty else 0.0
        pid_list = team_df["player_id"].tolist()
        chem_sum, count = 0.0, 0
        for i in range(len(pid_list)):
            for j in range(i + 1, len(pid_list)):
                chem_sum += chem.get((pid_list[i], pid_list[j]), chem.get((pid_list[j], pid_list[i]), 0.0))
                count += 1
        mean_chem = (chem_sum / count) if count > 0 else 0.0
        return ALPHA * mean_ind + BETA * mean_chem, mean_ind, mean_chem

    best_score, _, _ = team_score(selected)

    # Mejora iterativa
    for _ in range(max_iterations):
        improved = False
        for out_idx in list(selected.index):
            out_pos = selected.at[out_idx, "specific_position"]
            pool = df[df["specific_position"] == out_pos]
            if pool.empty:
                pool = df[df["position"] == selected.at[out_idx, "position"]]
            for _, cand in pool.sort_values("score_individual", ascending=False).iterrows():
                if cand["name"] in selected["name"].values:
                    continue
                new_team = pd.concat([selected.drop(out_idx), pd.DataFrame([cand])]).drop_duplicates(subset=["name"]).head(num_players)
                new_score, _, _ = team_score(new_team)
                if new_score > best_score + 1e-9:
                    selected = new_team.reset_index(drop=True)
                    best_score = new_score
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break

    total, mean_ind, mean_chem = team_score(selected)
    players_selected = [{
        "player_id": r.get("player_id"),
        "name": r.get("name"),
        # ✅ Usamos la edad original guardada en age_raw, no la columna normalizada 'age'
        "age": int(r.get("age_raw")) if pd.notna(r.get("age_raw")) else None,
        "team": r.get("team"),
        "league": r.get("league"),
        "position": r.get("position"),
        "specific_position": r.get("specific_position"),
        "injured": r.get("injured"),
        "score_individual": float(r.get("score_individual"))
    } for _, r in selected.iterrows()]


    return {
        "nationality": nationality,
        "style": style,
        "total_score": round(total, 4),
        "rendimiento_medio": round(mean_ind, 4),
        "quimica_media": round(mean_chem, 4),
        "players_selected": players_selected
    }
