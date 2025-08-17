import random
DIMENSIONS = ["R","I","A","S","E","C"]

def preguntar(pregs):
    print("\n--- TEST (20 preguntas) ---")
    print("Responde cada ítem del 1 al 5 (1 = nada, 5 = mucho).", flush=True)
    ans = {}
    for q in pregs:
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
        print(f"   Nota secuencia: {q.get('nota_secuencia','')}")
    return ans

def perfil_riasec(pregs, respuestas):
    agg = {k: [] for k in DIMENSIONS}
    for q in pregs:
        if q["id"] in respuestas:
            agg[q["dimension"]].append(respuestas[q["id"]])
    prom = {k: (sum(v)/len(v) if v else 0.0) for k,v in agg.items()}
    return {k: (max(0.0, min((v-1)/4, 1.0))) for k,v in prom.items()}

def avatar_por_perfil(p):
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

def medallas_por_perfil(p):
    medals = []
    if p["E"] >= 0.75: medals.append("🥇 Liderazgo")
    if p["I"] >= 0.75: medals.append("🧩 Resolución de Problemas")
    if p["A"] >= 0.70: medals.append("🎨 Mente Creativa")
    if p["S"] >= 0.70: medals.append("💬 Comunicación Empática")
    if p["C"] >= 0.70: medals.append("📚 Orden y Disciplina")
    if p["R"] >= 0.70: medals.append("🛠️ Manos a la Obra")
    if not medals: medals.append("⭐ Constancia")
    return medals

def jugar_escenarios(juego):
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
