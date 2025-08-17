import json

with open('data_carreras.json', encoding='utf-8') as f:
    CARRERAS = json.load(f)

def buscar_carreras_por_perfil(perfil, top_n=5):
    def distance(c):
        # Euclidean distance between perfil and carrera RIASEC
        return sum((perfil[k] - c['RIASEC'][k])**2 for k in perfil) ** 0.5
    carreras_ordenadas = sorted(CARRERAS, key=distance)
    return carreras_ordenadas[:top_n]
