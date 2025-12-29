# ⚽ SIBI – Seleccionador Inteligente de Fútbol

SIBI es un **sistema inteligente de recomendación de convocatorias de fútbol**, diseñado para simular el trabajo de un seleccionador nacional real.  
El proyecto combina **bases de datos orientadas a grafos**, **algoritmos de optimización** e **inteligencia artificial conversacional** para generar convocatorias óptimas basadas en rendimiento y química entre jugadores.

---

## 🎯 Objetivo del proyecto

El objetivo de SIBI no es sustituir al entrenador, sino **apoyar la toma de decisiones**, ofreciendo recomendaciones objetivas, reproducibles y adaptables a distintos estilos de juego.

El sistema busca:
- maximizar el **rendimiento individual** de los jugadores,
- sin descuidar la **cohesión y química colectiva** del equipo.

---

## 🧠 ¿Cómo funciona?

1. El usuario interactúa mediante un **chat en lenguaje natural**.
2. La **IA conversacional** interpreta la intención (generar, ajustar o consultar).
3. El sistema consulta un **grafo de datos** con jugadores y relaciones.
4. Un **algoritmo de selección** calcula la mejor convocatoria posible.
5. El resultado se devuelve explicado y estructurado.

👉 La IA **no decide la convocatoria**, solo interpreta la consulta.  
👉 La decisión final la toma el **algoritmo del backend**.

---

## 🗂️ Modelo de datos (Neo4j)

El sistema utiliza una base de datos orientada a grafos con:
- nodos de tipo `Player`, `Team`, `League` y `Country`
- relaciones como:
  - `PLAYS_FOR`
  - `REPRESENTS`
  - `TEAMMATE_OF`

Este modelo permite calcular de forma natural la **química entre jugadores**.

Los datos utilizados son **sintéticos**, generados mediante scripts en Python, lo que garantiza un entorno seguro y controlado.

---

## ⚙️ Algoritmo de selección

El algoritmo:
- calcula un **score individual** por jugador según su posición y estilo de juego,
- evalúa la **química del equipo** (club y liga compartidos),
- combina ambos factores mediante una función objetivo:


La solución se mejora mediante un proceso **iterativo heurístico**, buscando el mejor equilibrio entre calidad y coste computacional.

---

## 💬 IA conversacional y memoria de contexto

SIBI incorpora una capa de IA conversacional que permite:
- realizar consultas en lenguaje natural,
- generar convocatorias,
- modificar convocatorias previas gracias a **memoria de contexto**.


---

## 🖥️ Interfaz de usuario

La interfaz está desarrollada con **Streamlit** y presenta:
- un chatbot sencillo e intuitivo,
- respuestas explicadas y estructuradas,
- tiempos de respuesta reducidos.

---

## 🔐 Seguridad

- Todo el sistema se ejecuta **en local**.
- Los datos son **propios y sintéticos**.
- Las consultas generadas por la IA se validan antes de ejecutarse.
- Se valoró el uso de **API Key en headers** para control de acceso, descartado por tratarse de un proyecto académico, pero fácilmente integrable en producción.

---

## 🛠️ Tecnologías utilizadas

- **Python**
- **Neo4j** (base de datos orientada a grafos)
- **Ollama** (ejecución local de modelos de lenguaje)
- **Groq** (inferencia de modelos de gran tamaño)
- **Streamlit** (interfaz web)
- **FastAPI** (backend)

---

## 🚀 Líneas de futuro

- Uso de **datos reales y actualizados**
- Mejora del modelo de química
- Algoritmos más avanzados (multiobjetivo, genéticos)
- Explicaciones más detalladas de las recomendaciones
- Despliegue en entorno productivo multiusuario

---

## 👤 Autor

**Airam Diez Flecha**

- GitHub: https://github.com/AiramDiez
- LinkedIn: https://www.linkedin.com/in/airam-diez-flecha-a356081b0/
- Email: adiezf07@estudiantes.unileon.es

---

## 📌 Nota

Este proyecto ha sido desarrollado con fines **académicos y experimentales**.
