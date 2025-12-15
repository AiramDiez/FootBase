import os
import re
import time
from neo4j import GraphDatabase

# ------------------------------
# 🧠 GROQ - LLM EN LA NUBE
# ------------------------------
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

groq_client = None
llm = None

try:
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print(f"✅ Modelo Groq configurado correctamente: {GROQ_MODEL}")
    else:
        print("⚠️ No se encontró GROQ_API_KEY. El LLM estará desactivado.")
except Exception as e:
    print(f"❌ Error inicializando Groq: {e}")
    groq_client = None

# Función simple de completado (igual que antes, pero usando Groq)
def groq_complete(prompt: str):
    if not groq_client:
        raise Exception("Groq no está configurado.")

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error Groq: {str(e)}"


# -----------------------------------------------------------
# 🧠 CONEXIÓN A NEO4J CON RETRY
# -----------------------------------------------------------

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://sibi-neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "recovery123")

driver = None
for attempt in range(5):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        with driver.session() as session:
            total = session.run("MATCH (n) RETURN count(n) AS total").single()["total"]
            print(f"✅ Conectado correctamente a Neo4j ({total} nodos detectados)")
        break
    except Exception as e:
        print(f"⏳ Intento {attempt + 1}/5: Error conectando con Neo4j: {e}")
        time.sleep(5)
else:
    print("❌ No se pudo conectar con Neo4j después de varios intentos.")


# -----------------------------------------------------------
# 📘 ESQUEMA DEL GRAFO
# -----------------------------------------------------------

GRAFO_SCHEMA = """
El grafo contiene nodos:
Player {player_id, name, age, nationality, team, league, position, specific_position, injured,
height_cm, weight_kg, stamina, matches_played, minutes_played, yellow_cards, red_cards,
goals, assists, shots_per_game, key_passes_per_game, dribbles_per_game,
tackles_per_game, interceptions_per_game, clearances_per_game,
aerial_duels_won_pct, fouls_per_game, pass_accuracy_pct, passes_per_game,
long_balls_per_game, crosses_per_game, saves_per_game, clean_sheets,
goals_conceded, penalty_save_pct}
Team {name}
League {name}
Country {name}

Relaciones:
(Player)-[:PLAYS_FOR]->(Team)
(Team)-[:PART_OF]->(League)
(Player)-[:REPRESENTS]->(Country)
(Player)-[:TEAMMATE_OF]->(Player)
"""


# -----------------------------------------------------------
# 🧩 IMPORTS DE MÓDULOS INTERNOS
# -----------------------------------------------------------

from app.selector_module import generar_convocatoria
from app.analysis_module import analizar_convocatoria
from app.context_memory import save_context, load_context, has_context
from app.sibi_agent import ajustar_convocatoria


# -----------------------------------------------------------
# 🔍 DETECCIÓN DE INTENCIÓN
# -----------------------------------------------------------

def detectar_intencion(pregunta: str, user_id: str) -> str:
    text = pregunta.lower()
    if has_context(user_id) and any(k in text for k in ["más", "menos", "cambia", "hazla", "modifica", "ajusta"]):
        return "ajuste"
    if any(k in text for k in ["convocatoria", "dame", "selecciona", "hazme", "elige", "mejor equipo", "llévame"]):
        return "convocatoria"
    return "consulta"


# -----------------------------------------------------------
# 🧩 EXTRACCIÓN DE PARÁMETROS (SIN CAMBIOS)
# -----------------------------------------------------------

def extraer_parametros(pregunta: str):
    text = pregunta.lower()

    nationality_map = {
        "españa": "Española", "español": "Española", "españoles": "Española",

        # 🇮🇹 Italia
        "italia": "Italiana", "italiano": "Italiana", "italianos": "Italiana",

        # 🇫🇷 Francia
        "francia": "Francesa", "francés": "Francesa", "franceses": "Francesa",

        # 🇵🇹 Portugal
        "portugal": "Portuguesa", "portugués": "Portuguesa", "portugueses": "Portuguesa",

        # 🇦🇷 Argentina
        "argentina": "Argentina", "argentino": "Argentina", "argentinos": "Argentina",

        # 🇩🇪 Alemania
        "alemania": "Alemana", "alemán": "Alemana", "alemanes": "Alemana",

        # 🏴 Inglaterra
        "inglaterra": "Inglesa", "inglés": "Inglesa", "ingleses": "Inglesa",

        # 🇧🇷 Brasil
        "brasil": "Brasileña", "brasileño": "Brasileña", "brasileños": "Brasileña",

        # 🇳🇱 Países Bajos
        "países bajos": "Neerlandesa", "holanda": "Neerlandesa",
        "neerlandés": "Neerlandesa", "neerlandeses": "Neerlandesa",

        # 🇺🇾 Uruguay
        "uruguay": "Uruguaya", "uruguayo": "Uruguaya", "uruguayos": "Uruguaya"
    }

    nationality = "Española"
    for k, v in nationality_map.items():
        if k in text:
            nationality = v
            break

    style = (
        "ofensivo" if "ofensiv" in text else
        "defensivo" if "defensiv" in text else
        "balanceado"
    )

    injured_allowed = not ("sin lesionados" in text or "no lesionados" in text)

    num_match = re.search(r"(\d+)\s+jugadores", text)
    num_players = int(num_match.group(1)) if num_match else 23

    fixed_players = []
    patterns = [
        r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\s+(?:es|sea)\s+fijo",
        r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\s+(?:son|sean)\s+fijos",
        r"fijos?\s*:\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)",
    ]

    for patt in patterns:
        matches = re.findall(patt, pregunta)
        fixed_players.extend([m.strip() for m in matches])

    fixed_players = list(set(fixed_players))

    specific_positions_config = {}
    matches = re.findall(r"(\d+)\s*(POR|DFC|LD|LI|MC|MCD|MCO|EI|ED|DC)", text)
    for num, pos in matches:
        specific_positions_config[pos.upper()] = int(num)

    if not specific_positions_config:
        specific_positions_config = None

    return {
        "nationality": nationality,
        "num_players": num_players,
        "style": style,
        "injured_allowed": injured_allowed,
        "fixed_players": fixed_players,
        "specific_positions_config": specific_positions_config,
    }


# -----------------------------------------------------------
# 💬 FORMATEO DE CONVOCATORIA (SIN CAMBIOS)
# -----------------------------------------------------------

def formatear_convocatoria(resultado):
    if not resultado or "error" in resultado:
        return f"❌ {resultado.get('error', 'Error desconocido')}"

    flag = {
        "Española": "🇪🇸", "Italiana": "🇮🇹", "Francesa": "🇫🇷", "Portuguesa": "🇵🇹",
        "Argentina": "🇦🇷", "Alemana": "🇩🇪", "Inglesa": "🏴",
        "Brasileña": "🇧🇷", "Neerlandesa": "🇳🇱", "Uruguaya": "🇺🇾"
    }.get(resultado["nationality"], "🌍")

    resumen = (
        f"{flag} Convocatoria {resultado['style']} ({resultado['nationality']})\n"
        f"🎯 Total: {resultado['total_score']} | 💪 Rendimiento: {resultado['rendimiento_medio']} | 🤝 Química: {resultado['quimica_media']}\n\n"
    )

    jugadores = resultado["players_selected"]
    by_pos = {}

    for p in jugadores:
        pos = p.get("specific_position") or p.get("position")
        by_pos.setdefault(pos, []).append(p)

    for pos, lst in by_pos.items():
        resumen += f"🧩 {pos}:\n"
        for pl in lst:
            resumen += f" - {pl['name']} ({pl['team']}) — score:{round(pl['score_individual'], 3)}\n"
        resumen += "\n"

    return resumen.strip()


# -----------------------------------------------------------
# 🧠 FUNCIÓN PRINCIPAL DE CONSULTA USANDO GROQ
# -----------------------------------------------------------

def query_grafo(pregunta: str, user_id: str = "user"):

    intencion = detectar_intencion(pregunta, user_id)

    # AJUSTE
    if intencion == "ajuste":
        msg, result = ajustar_convocatoria(user_id, pregunta)
        if result:
            texto_conv = formatear_convocatoria(result)
            texto_analisis, _ = analizar_convocatoria(result)
            return {"respuesta": texto_conv + "\n\n" + texto_analisis, "result": result}
        return msg

    # NUEVA CONVOCATORIA
    if intencion == "convocatoria":
        params = extraer_parametros(pregunta)
        result = generar_convocatoria(**params)
        save_context(user_id, {"params": params, "result": result})
        texto_conv = formatear_convocatoria(result)
        texto_analisis, _ = analizar_convocatoria(result)
        return {"respuesta": texto_conv + "\n\n" + texto_analisis, "result": result}

    # -----------------------------------------------------------
     # -----------------------------------------------------------
    # CONSULTA LIBRE CON GROQ (Cypher Only)
    # -----------------------------------------------------------

    import re
    m = re.search(r"\b(\d+)\b", pregunta)
    numero_detectado = int(m.group(1)) if m else 5

    prompt = f"""
Eres un generador estricto de consultas Cypher para Neo4j.

REGLAS OBLIGATORIAS:
- Devuelve SOLO la consulta Cypher.
- La consulta DEBE empezar por MATCH.
- NO devuelvas RETURN p, RETURN t, RETURN l → usa SIEMPRE una propiedad.
- SIEMPRE incluye ORDER BY rand().
- SIEMPRE incluye LIMIT {numero_detectado}.
- NO generes CREATE, DELETE, SET, MERGE, DROP.
- NO devuelvas nodos completos.

CUANDO EL USUARIO PIDE:
- Jugadores → MATCH (p:Player) RETURN p.name ORDER BY rand() LIMIT {numero_detectado}
- Equipos → MATCH (t:Team) RETURN t.name ORDER BY rand() LIMIT {numero_detectado}
- Ligas → MATCH (l:League) RETURN l.name ORDER BY rand() LIMIT {numero_detectado}
- Nacionalidades → MATCH (p:Player) RETURN DISTINCT p.nationality ORDER BY rand() LIMIT {numero_detectado}

Esquema del grafo:
{GRAFO_SCHEMA}

Pregunta del usuario:
{pregunta}

Devuelve SOLO la consulta Cypher válida:
"""

    cypher_raw = groq_complete(prompt)
    if not cypher_raw:
        return "❌ Error generando Cypher."

    cypher = cypher_raw.strip().replace("```", "").strip()
    cypher = cypher.split("\n")[0].strip()

    print("🧠 Cypher generado por Groq:", cypher)

    forbidden = ["delete", "create", "merge", "set", "drop"]
    if not cypher.lower().startswith("match") or any(f in cypher.lower() for f in forbidden):
        return f"🤖 Consulta no segura:\n{cypher}"

    try:
        with driver.session() as s:
            recs = [r.data() for r in s.run(cypher)]

        # -------------------------------------------------------
        # 🔥 LIMPIEZA AVANZADA DEFINITIVA
        # -------------------------------------------------------

        if recs:

            # A) Caso simple: solo una key → p.name, t.name...
            if all(len(r.keys()) == 1 for r in recs):
                key = list(recs[0].keys())[0]
                valores = []

                for r in recs:
                    val = r[key]

                    # Nodo completo → extraer solo name
                    if isinstance(val, dict):
                        valores.append(val.get("name", str(val)))
                    else:
                        valores.append(val)

                # Asegurar tamaño correcto
                valores = valores[:numero_detectado]
                return {"type": "consulta_limpia", "data": valores}

            # B) Caso múltiple: Groq devolvió varias columnas → extraer SOLO nombre
            valores = []
            for r in recs:
                encontrado = False

                for k, v in r.items():
                    k_lower = k.lower()

                    # 1) p.name
                    if "name" in k_lower:
                        valores.append(v)
                        encontrado = True
                        break

                    # 2) alias tipo "jugador" → si es nombre completo
                    if isinstance(v, str) and len(v.split()) >= 2:
                        valores.append(v)
                        encontrado = True
                        break

                    # 3) nodo Player → extraemos name
                    if isinstance(v, dict) and "name" in v:
                        valores.append(v["name"])
                        encontrado = True
                        break

                if not encontrado:
                    valores.append(str(r))

            valores = valores[:numero_detectado]
            return {"type": "consulta_limpia", "data": valores}

        return {"type": "consulta", "data": recs}

    except Exception as e:
        return {"type": "error", "data": str(e)}
