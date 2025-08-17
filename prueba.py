# Ejecuta con:  py -u vocacional_ia_vector.py
import os, sys, json, re, random
from typing import List, Dict, Tuple
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from openai import AzureOpenAI

# ================
# Setup + diagnóstico
# ================
HERE = Path(__file__).resolve().parent
ENV_PATH = HERE / ".env"

print("== INICIO ==", flush=True)
print("Script dir:", HERE, flush=True)
print(".env existe?", ENV_PATH.exists(), flush=True)
vals = dotenv_values(ENV_PATH) if ENV_PATH.exists() else {}
print("Claves en .env:", list(vals.keys()), flush=True)

load_dotenv(dotenv_path=ENV_PATH, override=True)
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
print("Tiene KEY? ", bool(API_KEY), flush=True)
print("Endpoint  :", ENDPOINT, flush=True)
print("Deployment:", DEPLOYMENT, flush=True)
print("== FIN SETUP ==\n", flush=True)
if not API_KEY or not ENDPOINT:
    print("❌ Falta AZURE_OPENAI_API_KEY o AZURE_OPENAI_ENDPOINT en .env")
    sys.exit(1)

client = AzureOpenAI(api_key=API_KEY, azure_endpoint=ENDPOINT, api_version=API_VERSION)

DIMENSIONS = ["R","I","A","S","E","C"]  # Realista, Investigativo, Artístico, Social, Emprendedor, Convencional

# ================
# Util: parseo JSON robusto
# ================
def coerce_json(txt: str) -> dict:
    txt = (txt or "").strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.IGNORECASE|re.DOTALL)
    s, e = txt.find("{"), txt.rfind("}")
    if s != -1 and e != -1 and e > s:
        txt = txt[s:e+1]
    return json.loads(txt)

# ==========================================
# 1) 20 preguntas adaptativas + vector por paso
# ==========================================
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
          "minItems": 20, "maxItems": 20,
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "integer"},
              "texto": {"type": "string"},
              "dimension": {"type": "string", "enum": DIMENSIONS},
              "prob_vector": {
                "type": "object",
                "properties": {
                  "R":{"type":"number","minimum":0,"maximum":1},
                  "I":{"type":"number","minimum":0,"maximum":1},
                  "A":{"type":"number","minimum":0,"maximum":1},
                  "S":{"type":"number","minimum":0,"maximum":1},
                  "E":{"type":"number","minimum":0,"maximum":1},
                  "C":{"type":"number","minimum":0,"maximum":1}
                },
                "required":["R","I","A","S","E","C"]
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

def generar_preguntas_con_vectores() -> List[Dict]:
    """
    Pide al modelo que:
      - Genere EXACTAMENTE 20 preguntas RIASEC (10–14 palabras)
      - Para CADA pregunta devuelva un prob_vector R,I,A,S,E,C (suma ≈ 1.0)
      - Use ese vector para decidir la dimensión de la SIGUIENTE pregunta (secuencia adaptativa)
      - Incluya 'nota_secuencia' explicando cómo el vector influyó en la siguiente elección
    """
    system = (
        "Eres orientador vocacional. Responde SIEMPRE en JSON válido que cumpla el esquema. "
        "No devuelvas texto fuera del JSON."
    )
    # Pedimos que explicite el vector y lo use para decidir la siguiente pregunta.
    user = (
        "Genera EXACTAMENTE 5 preguntas cortas (10–14 palabras) para un test vocacional RIASEC. "
        "Cada pregunta pertenece a UNA dimensión (R,I,A,S,E,C). Lenguaje claro de bachillerato, "
        "neutral en género y sin tecnicismos. Campos por pregunta: id(1..5), texto, dimension, prob_vector. "
        "Al crear la PRIMERA pregunta, genera un prob_vector (R,I,A,S,E,C) con suma ~1.0. "
        "La SIGUIENTE pregunta debe elegirse EN BASE a ese prob_vector (dimensión con mayor probabilidad o muestreo razonable). "
        "Después de cada pregunta, actualiza el prob_vector y vuelve a elegir la siguiente, repite hasta la 20. "
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
    # fuerza ids 1..20 por seguridad
    for i, q in enumerate(preguntas, start=1):
        q["id"] = i
    return data

# ==============================
# 2) Captura respuestas 1–5
# ==============================
def preguntar(pregs: List[Dict]) -> Dict[int,int]:
    print("\n--- TEST (20 preguntas) ---")
    print("Responde cada ítem del 1 al 5 (1 = nada, 5 = mucho).", flush=True)
    ans = {}
    for q in pregs:
        # Mostrar vector antes de preguntar
        pv = q["prob_vector"]
        vec_txt = f"[R:{pv['R']:.2f} I:{pv['I']:.2f} A:{pv['A']:.2f} S:{pv['S']:.2f} E:{pv['E']:.2f} C:{pv['C']:.2f}]"
        print(f"\nVector previo a la P{q['id']}: {vec_txt}")
        print(f"{q['id']:02d}. {q['texto']}  (dimensión objetivo: {q['dimension']})")
        while True:
            try:
                val = int(input("   Respuesta [1-5]: ").strip())
                if 1 <= val <= 5:
                    ans[q["id"]] = val
                    break
            except ValueError:
                pass
            print("  → Ingresa un número del 1 al 5.")
        # Mostrar nota de cómo el vector afectó la secuencia
        print(f"   Nota secuencia: {q.get('nota_secuencia','')}")
    return ans

# ==============================
# 3) IA: 5 carreras sugeridas
# ==============================
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

def recomendar_carreras_con_ia(pregs: List[Dict], respuestas: Dict[int,int]) -> Dict:
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

# ==============================
# Gamificación
# ==============================
def perfil_riasec(pregs: List[Dict], respuestas: Dict[int,int]) -> Dict[str, float]:
    agg = {k: [] for k in DIMENSIONS}
    for q in pregs:
        if q["id"] in respuestas:
            agg[q["dimension"]].append(respuestas[q["id"]])
    prom = {k: (sum(v)/len(v) if v else 0.0) for k,v in agg.items()}
    return {k: (max(0.0, min((v-1)/4, 1.0))) for k,v in prom.items()}  # 1..5 → 0..1

def avatar_por_perfil(p: Dict[str, float]) -> Tuple[str,str]:
    top2 = sorted(p.items(), key=lambda kv: kv[1], reverse=True)[:2]
    key = "".join([d for d,_ in top2])
    mapping = {
        "RI": ("🔧🧠 Exploradora Analítica", "Afinidad por ingeniería, lógica y ciencias aplicadas."),
        "IR": ("🧠🔧 Analista Constructora", "Ciencia con orientación práctica y tangible."),
        "IA": ("🧠🎨 Científica Creativa", "Curiosidad científica con impulso artístico."),
        "SI": ("🤝🧠 Mentora Investigativa", "Empatía social con análisis riguroso."),
        "SE": ("🤝🚀 Lideresa Social", "Vocación de impacto con liderazgo."),
        "AE": ("🎨🚀 Creativa Emprendedora", "Innovación con impulso para lanzar proyectos."),
        "AS": ("🎨🤝 Diseñadora Humana", "Creatividad enfocada en personas y experiencias."),
        "EC": ("🚀📊 Estratega Ejecutiva", "Liderazgo con orden y procesos."),
        "CE": ("📊🚀 Gestora Dinámica", "Ejecución con visión de negocio."),
        "RC": ("🔧📊 Técnica Metódica", "Orientación práctica con alto orden."),
        "CR": ("📊🔧 Gestora Técnica", "Procesos con base técnica."),
        "AR": ("🎨🔧 Arquitecta Artesana", "Creatividad con construcción concreta.")
    }
    return mapping.get(key, ("🌟 Exploradora en Desarrollo", "Perfil balanceado en varias áreas."))

def medallas_por_perfil(p: Dict[str, float]) -> List[str]:
    medals = []
    if p["E"] >= 0.75: medals.append("🥇 Liderazgo")
    if p["I"] >= 0.75: medals.append("🧩 Resolución de Problemas")
    if p["A"] >= 0.70: medals.append("🎨 Mente Creativa")
    if p["S"] >= 0.70: medals.append("💬 Comunicación Empática")
    if p["C"] >= 0.70: medals.append("📚 Orden y Disciplina")
    if p["R"] >= 0.70: medals.append("🛠️ Manos a la Obra")
    if not medals: medals.append("⭐ Constancia")
    return medals

# ==============================
# Mini-juego dinámico por IA
# ==============================
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

def generar_juego_dinamico(carreras: List[str]) -> Dict:
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

def jugar_escenarios(juego: Dict):
    print("\n================= MINI-JUEGO VOCACIONAL (IA) =================")
    print(juego["juego"]["introduccion"])
    score = {"satisfaccion": 5, "estres": 3, "crecimiento": 3}
    for i, esc in enumerate(juego["juego"]["escenarios"], 1):
        print(f"\n{i}. Carrera: {esc['carrera']}")
        print(f"   Situación: {esc['situacion']}")
        for idx, op in enumerate(esc["opciones"], 1):
            print(f"     {idx}) {op['accion']}")
        sel = input("   Elige [1/2]: ").strip()
        idx = 0 if sel == "1" else 1
        op = esc["opciones"][idx] if idx in (0,1) else esc["opciones"][0]
        outcome_key = random.choices(
            ["resultado_bueno","resultado_neutro","resultado_malo"], weights=[0.45, 0.35, 0.20]
        )[0]
        print(f"   → {op[outcome_key]}")
        if outcome_key == "resultado_bueno":
            score["satisfaccion"] = min(10, score["satisfaccion"] + 2)
            score["crecimiento"]  = min(10, score["crecimiento"]  + 2)
        elif outcome_key == "resultado_neutro":
            score["crecimiento"]  = min(10, score["crecimiento"]  + 1)
        else:
            score["estres"]       = min(10, score["estres"] + 2)
        print(f"   Estado → Satisfacción {score['satisfaccion']} | Estrés {score['estres']} | Crecimiento {score['crecimiento']}")
    balance = score["satisfaccion"] + score["crecimiento"] - score["estres"]
    mood = "👍 Positivo" if balance >= 6 else ("⚖️ Mixto" if balance >= 2 else "👀 Retador")
    print(f"\n🏁 Resultado del juego: {mood} (balance={balance})\n")

# ==============
# Main
# ==============
def main():
    print("=== TEST VOCACIONAL (20) + VECTORES + RECOMENDACIÓN + MINI-JUEGO ===", flush=True)

    # 1) Preguntas con vector por paso
    data = generar_preguntas_con_vectores()
    preguntas = data["preguntas"]
    print("\nExplicación rápida del modelo:", data.get("explicacion_corta",""))

    # 2) Responder mostrando el vector previo a cada pregunta
    respuestas = preguntar(preguntas)

    # 3) Recomendación IA
    print("\nGenerando recomendaciones de carreras con IA...", flush=True)
    rec = recomendar_carreras_con_ia(preguntas, respuestas)

    # 4) Gamificación breve
    perfil = perfil_riasec(preguntas, respuestas)
    avatar_name, avatar_desc = avatar_por_perfil(perfil)
    medals = medallas_por_perfil(perfil)
    xp = int(sum(v*100 for v in perfil.values()))
    level = min(5, max(1, xp // 120 + 1))
    cap = min(600, level*120)

    print("\n================= RESULTADOS =================")
    print("Perfil RIASEC (0..1):")
    for k in DIMENSIONS: print(f"  {k}: {perfil[k]:.2f}")
    print("\nAvatar Vocacional:", avatar_name)
    print("Descripción      :", avatar_desc)
    print("Medallas         :", " | ".join(medals))
    print(f"Nivel            : {level}  (XP: {xp}/{cap})")

    print("\n=== TOP 5 carreras sugeridas por IA ===")
    print("Resumen:", rec.get("resumen",""))
    carreras = []
    for i, c in enumerate(rec["carreras"], 1):
        print(f"  {i}. {c['nombre']}  (confianza: {c['confianza']:.2f})")
        print(f"     Razón: {c['razon']}")
        carreras.append(c["nombre"])

    # 5) Mini-juego IA
    try:
        juego = generar_juego_dinamico(carreras)
        jugar_escenarios(juego)
    except Exception as e:
        print("\n(No se pudo generar el mini-juego dinámico; detalle para depurar):")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("\n❌ Ocurrió un error:\n")
        traceback.print_exc()
        input("\nPulsa Enter para cerrar...")
