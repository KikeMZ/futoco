from prompts import generar_preguntas_con_vectores, generar_juego_dinamico
from functions import preguntar, perfil_riasec, avatar_por_perfil, medallas_por_perfil, jugar_escenarios
from data_carreras import buscar_carreras_por_perfil

if __name__ == "__main__":
    print("=== TEST VOCACIONAL + VECTORES + RECOMENDACIÓN + MINI-JUEGO ===", flush=True)
    try:
        num_questions = 5
        data = generar_preguntas_con_vectores(num_questions)
        preguntas = data["preguntas"]
        print("\nExplicación rápida del modelo:", data.get("explicacion_corta",""))
        respuestas = preguntar(preguntas)
        perfil = perfil_riasec(preguntas, respuestas)
        avatar_name, avatar_desc = avatar_por_perfil(perfil)
        medals = medallas_por_perfil(perfil)
        xp = int(sum(v*100 for v in perfil.values()))
        level = min(5, max(1, xp // 120 + 1))
        cap = min(600, level*120)
        print("\n================= RESULTADOS =================")
        print("Perfil RIASEC (0..1):")
        for k in ["R","I","A","S","E","C"]: print(f"  {k}: {perfil[k]:.2f}")
        print("\nAvatar Vocacional:", avatar_name)
        print("Descripción      :", avatar_desc)
        print("Medallas         :", " | ".join(medals))
        print(f"Nivel            : {level}  (XP: {xp}/{cap})")
        print("\n=== TOP 5 carreras sugeridas ===")
        carreras = buscar_carreras_por_perfil(perfil, top_n=5)
        def vector_distance(c):
            return sum((perfil[k] - c['RIASEC'][k])**2 for k in perfil) ** 0.5
        for i, c in enumerate(carreras, 1):
            dist = vector_distance(c)
            print(f"  {i}. {c['nombre']}")
            print(f"     RIASEC: {c['RIASEC']}")
            print(f"     Distancia vectorial: {dist:.3f}")
        try:
            nombres_carreras = [c['nombre'] for c in carreras]
            juego = generar_juego_dinamico(nombres_carreras)
            jugar_escenarios(juego)
        except Exception as e:
            print("\n(No se pudo generar el mini-juego dinámico; detalle para depurar):")
            import traceback; traceback.print_exc()
    except Exception as e:
        import traceback
        print("\n❌ Ocurrió un error:\n")
        traceback.print_exc()
        input("\nPulsa Enter para cerrar...")
