import os
import csv
import logging
import webbrowser
from fastapi import FastAPI, HTTPException, Header, Request
from neo4j import GraphDatabase

# -----------------------------------------------------------
# 🧱 CONFIGURACIÓN BÁSICA
# -----------------------------------------------------------

app = FastAPI(
    title="SIBI Backend - Sistema Inteligente de Selección de Jugadores",
    version="1.0.0",
    description="Orquestador que conecta Neo4j, LlamaIndex y Ollama."
)

# Variables de entorno con valores por defecto
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://sibi-neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "recovery123")
API_KEY = os.getenv("API_KEY", "seleccionador123")

# Conexión con Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# Configuración de logging
logging.basicConfig(
    filename="agent_activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------------------------------------
# 🛡️ SEGURIDAD (API KEY)
# -----------------------------------------------------------

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Middleware para proteger rutas excepto las públicas."""
    public_paths = ["/health", "/docs", "/openapi.json", "/favicon.ico", "/api/query/public"]
    if any(request.url.path.startswith(p) for p in public_paths):
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")

    return await call_next(request)



# -----------------------------------------------------------
# 🩺 ENDPOINT DE SALUD
# -----------------------------------------------------------

@app.get("/health")
def health():
    status = {"status": "ok"}
    try:
        with driver.session() as s:
            result = s.run("RETURN 1 AS ok").single()
            status["neo4j"] = "connected" if result and result["ok"] == 1 else "no response"
    except Exception as e:
        status["neo4j"] = f"error: {type(e).__name__} - {str(e)}"
    return status

# -----------------------------------------------------------
# 🚀 ABRIR NAVEGADOR AL INICIAR SERVIDOR
# -----------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Abrir navegador automáticamente al arrancar el servidor."""
    try:
        webbrowser.open_new_tab("http://localhost:8000/health")
    except Exception as e:
        logging.warning(f"No se pudo abrir navegador automáticamente: {e}")

# -----------------------------------------------------------
# Resto de endpoints (igual que ya tienes)
# -----------------------------------------------------------
# ... tus endpoints /api/nodes/sample, /api/query, etc. ...

# -----------------------------------------------------------
# 🧩 CONSULTAS BÁSICAS A NEO4J
# -----------------------------------------------------------

@app.get("/api/nodes/sample")
def sample_nodes(limit: int = 5):
    """Devuelve una muestra de nodos para verificar contenido de la base."""
    try:
        with driver.session() as s:
            records = s.run(
                "MATCH (n) RETURN labels(n) AS labels, n.name AS name LIMIT $limit",
                limit=limit
            )
            nodes = [{"labels": r["labels"], "name": r["name"]} for r in records]
            return {"count": len(nodes), "nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/players/{nationality}")
def get_players_by_nationality(nationality: str):
    """Devuelve los jugadores de una nacionalidad específica."""
    try:
        with driver.session() as s:
            result = s.run("""
                MATCH (p:Player)
                WHERE p.nationality = $nationality
                RETURN p.name AS name,
                       p.team AS team,
                       p.position AS position,
                       p.specific_position AS specific_position,
                       p.injured AS injured
                LIMIT 100
            """, {"nationality": nationality})
            players = [record.data() for record in result]
            return {"nationality": nationality, "count": len(players), "players": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/check_neo4j")
def check_neo4j():
    """Comprueba conexión y cantidad total de nodos en Neo4j."""
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS total_nodes")
            total = result.single()["total_nodes"]
            return {"message": "Conexión con Neo4j exitosa", "total_nodes": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# -----------------------------------------------------------
# 📦 IMPORTACIÓN DE CSV (para pruebas administrativas)
# -----------------------------------------------------------


@app.post("/api/admin/import/players")
def import_players(path: str = "datasets/jugadores_futbol_realistas.csv"):
    """Carga los jugadores desde el CSV a la base de datos Neo4j."""
    full_path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {full_path}")

    rows = []
    with open(full_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Ahora capturamos TODAS las columnas del CSV
            rows.append({
                "player_id": row.get("player_id"),
                "name": row.get("name"),
                "age": row.get("age"),
                "nationality": row.get("nationality"),
                "team": row.get("team"),
                "league": row.get("league"),
                "position": row.get("position"),
                "specific_position": row.get("specific_position"),
                "injured": row.get("injured"),
                "height_cm": row.get("height_cm"),
                "weight_kg": row.get("weight_kg"),
                "stamina": row.get("stamina"),
                "matches_played": row.get("matches_played"),
                "minutes_played": row.get("minutes_played"),
                "yellow_cards": row.get("yellow_cards"),
                "red_cards": row.get("red_cards"),
                "goals": row.get("goals"),
                "assists": row.get("assists"),
                "shots_per_game": row.get("shots_per_game"),
                "key_passes_per_game": row.get("key_passes_per_game"),
                "dribbles_per_game": row.get("dribbles_per_game"),
                "tackles_per_game": row.get("tackles_per_game"),
                "interceptions_per_game": row.get("interceptions_per_game"),
                "clearances_per_game": row.get("clearances_per_game"),
                "aerial_duels_won_pct": row.get("aerial_duels_won_pct"),
                "fouls_per_game": row.get("fouls_per_game"),
                "pass_accuracy_pct": row.get("pass_accuracy_pct"),
                "passes_per_game": row.get("passes_per_game"),
                "long_balls_per_game": row.get("long_balls_per_game"),
                "crosses_per_game": row.get("crosses_per_game"),
                "saves_per_game": row.get("saves_per_game"),
                "clean_sheets": row.get("clean_sheets"),
                "goals_conceded": row.get("goals_conceded"),
                "penalty_save_pct": row.get("penalty_save_pct")
            })

    if not rows:
        return {"ok": True, "imported": 0}

    # Esta consulta Cypher ahora importa TODAS las propiedades
    # y las convierte al tipo de dato correcto (Integer, Float).
    cypher = """
    UNWIND $rows AS row
    MERGE (p:Player {player_id: row.player_id})
    SET
        p.name = row.name,
        p.age = toInteger(row.age),
        p.nationality = row.nationality,
        p.team = row.team,
        p.league = row.league,
        p.position = row.position,
        p.specific_position = row.specific_position,
        p.injured = row.injured,
        p.height_cm = toInteger(row.height_cm),
        p.weight_kg = toInteger(row.weight_kg),
        p.stamina = toInteger(row.stamina),
        
        // --- Estadísticas de Juego ---
        p.matches_played = toInteger(row.matches_played),
        p.minutes_played = toInteger(row.minutes_played),
        p.yellow_cards = toInteger(row.yellow_cards),
        p.red_cards = toInteger(row.red_cards),
        
        // --- Estadísticas Ofensivas ---
        p.goals = toInteger(row.goals),
        p.assists = toInteger(row.assists),
        p.shots_per_game = toFloat(row.shots_per_game),
        p.key_passes_per_game = toFloat(row.key_passes_per_game),
        p.dribbles_per_game = toFloat(row.dribbles_per_game),
        
        // --- Estadísticas Defensivas ---
        p.tackles_per_game = toFloat(row.tackles_per_game),
        p.interceptions_per_game = toFloat(row.interceptions_per_game),
        p.clearances_per_game = toFloat(row.clearances_per_game),
        p.aerial_duels_won_pct = toFloat(row.aerial_duels_won_pct),
        p.fouls_per_game = toFloat(row.fouls_per_game),
        
        // --- Estadísticas de Pases ---
        p.pass_accuracy_pct = toFloat(row.pass_accuracy_pct),
        p.passes_per_game = toFloat(row.passes_per_game),
        p.long_balls_per_game = toFloat(row.long_balls_per_game),
        p.crosses_per_game = toFloat(row.crosses_per_game),
        
        // --- Estadísticas de Portero ---
        p.saves_per_game = toFloat(row.saves_per_game),
        p.clean_sheets = toInteger(row.clean_sheets),
        p.goals_conceded = toInteger(row.goals_conceded),
        p.penalty_save_pct = toFloat(row.penalty_save_pct)
    """
    try:
        with driver.session() as s:
            s.run(cypher, rows=rows)
        logging.info(f"Importados {len(rows)} jugadores desde {path}")
        return {"ok": True, "imported": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/api/admin/create-graph")
def create_graph():
    """Construye toda la estructura del grafo (Teams, Leagues, Countries) y las relaciones entre jugadores."""
    try:
        with driver.session() as s:
            s.run("""
            MATCH (p:Player)
            MERGE (t:Team {name: p.team})
            MERGE (l:League {name: p.league})
            MERGE (c:Country {name: p.nationality})
            MERGE (p)-[:PLAYS_FOR]->(t)
            MERGE (t)-[:PART_OF]->(l)
            MERGE (p)-[:REPRESENTS]->(c)
            """)
            s.run("""
            MATCH (a:Player), (b:Player)
            WHERE a.team = b.team AND a <> b
            MERGE (a)-[:TEAMMATE_OF]->(b)
            """)
        return {"ok": True, "message": "Grafo creado correctamente con equipos, ligas, países y relaciones."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el grafo: {e}")


# -----------------------------------------------------------
# 💬 CONSULTA IA AL GRAFO (segura con API key)
# -----------------------------------------------------------

from app.llama_integration import query_grafo

@app.get("/api/query")
def ask_graph(pregunta: str, api_key: str = Header(None)):
    """Endpoint de preguntas naturales al grafo Neo4j (usa Ollama + LlamaIndex)."""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Acceso no autorizado")

    try:
        respuesta = query_grafo(pregunta)
        return {"ok": True, "pregunta": pregunta, "respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la pregunta: {e}")


# -----------------------------------------------------------
# 💬 CONSULTA PÚBLICA (sin API key, solo para desarrollo)
# -----------------------------------------------------------

@app.get("/api/query/public")
def ask_graph_public(pregunta: str):
    from app.llama_integration import query_grafo
    try:
        respuesta = query_grafo(pregunta)

        # 🟩 Caso: convocatoria o ajuste (texto normal)
        if isinstance(respuesta, dict) and "respuesta" in respuesta:
            return {
                "ok": True,
                "pregunta": pregunta,
                "respuesta": respuesta["respuesta"],
                "type": "convocatoria"
            }

        # 🟦 Caso: consulta limpia (solo lista de strings)
        if isinstance(respuesta, dict) and respuesta.get("type") == "consulta_limpia":
            valores = respuesta.get("data", [])

            # ---------------------------------------------------------
            # 🔥 DETECCIÓN INTELIGENTE DE TIPO PARA ELEGIR EMOJI
            # ---------------------------------------------------------

            def es_jugador(v):
                return isinstance(v, str) and len(v.split()) >= 2

            def es_liga(v):
                return v in ["LaLiga", "Ligue 1", "Premier", "Bundesliga", "Serie A"]

            def es_equipo(v):
                return any(x in v for x in ["FC", "United", "City", "Real", "RB", "Dortmund", "Milan", "Roma", "Atalanta", "Leverkusen"])

            # Jugadores (nombre + apellido)
            if all(es_jugador(v) for v in valores):
                emoji = "👤"

            # Ligas principales
            elif all(es_liga(v) for v in valores):
                emoji = "🏆"

            # Nacionalidades → regla lingüística fiable
            elif all(isinstance(v, str) and v.endswith(("a", "esa", "nesa", "ana", "ona", "ina", "eña", "iana")) for v in valores):
                emoji = "🌍"

            # Equipos → patrones típicos
            elif all(es_equipo(v) for v in valores):
                emoji = "🏟️"

            # Por defecto
            else:
                emoji = "⚽"

            # Construcción del texto final
            texto = "\n".join(f"{emoji} {v}" for v in valores)

            return {
                "ok": True,
                "pregunta": pregunta,
                "respuesta": texto,
                "type": "consulta_limpia"
            }

        # 🟧 Caso: consulta libre normal (JSON sin limpiar)
        if isinstance(respuesta, dict):
            return {
                "ok": True,
                "pregunta": pregunta,
                "respuesta": respuesta.get("data"),
                "type": respuesta.get("type", "consulta")
            }

        # 🟥 Caso: string crudo (errores o mensajes sueltos)
        return {
            "ok": True,
            "pregunta": pregunta,
            "respuesta": respuesta,
            "type": "raw"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la pregunta: {e}")


@app.on_event("shutdown")
def shutdown():
    """Cierra conexión a Neo4j al apagar el servidor."""
    driver.close()
    logging.info("Conexión a Neo4j cerrada correctamente.")
