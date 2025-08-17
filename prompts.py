import os, json, re
from dotenv import load_dotenv, dotenv_values
from openai import AzureOpenAI
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV_PATH = HERE / ".env"
vals = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
load_dotenv(dotenv_path=ENV_PATH, override=True)
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
client = AzureOpenAI(api_key=API_KEY, azure_endpoint=ENDPOINT, api_version=API_VERSION)

DIMENSIONS = ["R","I","A","S","E","C"]

QUESTIONS_WITH_VECTOR_SCHEMA = {
  "type": "json_schema",
  "json_schema": {
    "name": "riasec_adaptativo_20",
    "schema": {
      "type": "object",
      "properties": {
        "explicacion_corta": {"type":"string"},
        "preguntas": {
          "type": "array",
          "minItems": 5, "maxItems": 5,
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "integer"},
              "texto": {"type": "string"},
              "dimension": {"type": "string", "enum": DIMENSIONS},
              "prob_vector": {
                "type": "object",
                "properties": {d:{"type":"number","minimum":0,"maximum":1} for d in DIMENSIONS},
                "required": DIMENSIONS
              },
              "nota_secuencia": {"type":"string"}
            },
            "required": ["id","texto","dimension","prob_vector","nota_secuencia"]
          }
        }
      },
      "required": ["explicacion_corta","preguntas"]
    }
  }
}

CAREER_SCHEMA = {
  "type": "json_schema",
  "json_schema": {
    "name": "recomendacion_carreras",
    "schema": {
      "type": "object",
      "properties": {
        "resumen": {"type":"string"},
        "carreras": {
          "type": "array",
          "minItems": 5, "maxItems": 5,
          "items": {
            "type":"object",
            "properties":{
              "id_slug":{"type":"string"},
              "nombre":{"type":"string"},
              "razon":{"type":"string","maxLength":260},
              "confianza":{"type":"number","minimum":0,"maximum":1}
            },
            "required":["id_slug","nombre","razon","confianza"]
          }
        }
      },
      "required": ["resumen","carreras"]
    }
  }
}

GAME_SCHEMA = {
  "type": "json_schema",
  "json_schema": {
    "name": "mini_juego_vocacional",
    "schema": {
      "type": "object",
      "properties": {
        "juego": {
          "type": "object",
          "properties": {
            "introduccion": {"type":"string"},
            "escenarios": {
              "type":"array",
              "minItems": 2, "maxItems": 3,
              "items": {
                "type":"object",
                "properties": {
                  "carrera": {"type":"string"},
                  "situacion": {"type":"string"},
                  "opciones": {
                    "type":"array",
                    "minItems": 2, "maxItems": 2,
                    "items": {
                      "type":"object",
                      "properties": {
                        "accion": {"type":"string"},
                        "resultado_bueno": {"type":"string"},
                        "resultado_neutro": {"type":"string"},
                        "resultado_malo": {"type":"string"}
                      },
                      "required": ["accion","resultado_bueno","resultado_neutro","resultado_malo"]
                    }
                  }
                },
                "required": ["carrera","situacion","opciones"]
              }
            }
          },
          "required": ["introduccion","escenarios"]
        }
      },
      "required": ["juego"]
    }
  }
}

def coerce_json(txt: str) -> dict:
    txt = (txt or "").strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.IGNORECASE|re.DOTALL)
    s, e = txt.find("{"), txt.rfind("}")
    if s != -1 and e != -1 and e > s:
        txt = txt[s:e+1]
    return json.loads(txt)

def generar_preguntas_con_vectores(num_questions=5):
    system = (
        "Eres orientador vocacional. Responde SIEMPRE en JSON válido que cumpla el esquema. "
        "No devuelvas texto fuera del JSON."
    )
    user = (
        f"Genera EXACTAMENTE {num_questions} preguntas cortas (10–14 palabras) para un test vocacional RIASEC. "
        "Cada pregunta pertenece a UNA dimensión (R,I,A,S,E,C). Lenguaje claro de bachillerato, "
        "neutral en género y sin tecnicismos. Campos por pregunta: id(1..5), texto, dimension, prob_vector. "
        "Al crear la PRIMERA pregunta, genera un prob_vector (R,I,A,S,E,C) con probabilidad inicial 0 en todas las entradas. "
        "La SIGUIENTE pregunta debe elegirse EN BASE a ese prob_vector (dimensión con mayor probabilidad o muestreo razonable). "
        "Después de cada pregunta, actualiza el prob_vector y vuelve a elegir la siguiente, repite hasta la ultima. "
        "Incluye en cada objeto 'nota_secuencia' una frase breve que explique cómo el vector influyó en la siguiente elección. "
        "Devuelve también 'explicacion_corta' al inicio (1–2 frases) sobre cómo funciona la adaptación."
    )
    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":user}
        ],
        response_format=QUESTIONS_WITH_VECTOR_SCHEMA,
        temperature=0.0,
        max_tokens=2000
    )
    data = coerce_json(resp.choices[0].message.content)
    preguntas = data["preguntas"]
    for i, q in enumerate(preguntas, start=1):
        q["id"] = i
    return data

def recomendar_carreras_con_ia(pregs, respuestas):
    payload = {
        "instrucciones": (
            "Con base en las 5 preguntas RIASEC y sus respuestas (1–5), recomienda EXACTAMENTE 5 carreras "
            "para un/una estudiante de bachillerato en México. Usa nombres comunes "
            "Devuelve SOLO JSON del esquema, con breve razón y confianza (0–1). Evita estereotipos."
        ),
        "preguntas": pregs,
        "respuestas": respuestas
    }
    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role":"system","content":"Eres orientador vocacional. Respondes exclusivamente en JSON válido del esquema."},
            {"role":"user","content": json.dumps(payload, ensure_ascii=False)}
        ],
        response_format=CAREER_SCHEMA,
        temperature=0.2,
        max_tokens=1200
    )
    return coerce_json(resp.choices[0].message.content)

def generar_juego_dinamico(carreras):
    payload = {
        "instrucciones": (
            "Crea un mini-juego de texto que simule decisiones en las carreras listadas. "
            "Cada escenario debe tener: carrera, situación, y 2 opciones (accion) con 3 posibles "
            "resultados (bueno, neutro, malo). Lenguaje motivador, claro, para bachillerato. Evita estereotipos."
        ),
        "carreras": carreras[:3]
    }
    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role":"system","content":"Eres diseñador(a) de juegos educativos. Devuelve SOLO JSON del esquema."},
            {"role":"user","content": json.dumps(payload, ensure_ascii=False)}
        ],
        response_format=GAME_SCHEMA,
        temperature=0.3,
        max_tokens=1200
    )
    return coerce_json(resp.choices[0].message.content)
