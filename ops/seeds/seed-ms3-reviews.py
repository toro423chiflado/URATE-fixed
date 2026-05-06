"""
Seed de MongoDB para ms-reviews
Calificaciones coherentes — no random
Correr: python seed.py
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "reviews_db")

PROFESORES = [
    {"id": "00000000-0000-0000-0000-000000000001", "nombre": "Juan Pérez",  "perfil": "excelente"},
    {"id": "00000000-0000-0000-0000-000000000002", "nombre": "Ana Torres",  "perfil": "bueno"},
    {"id": "00000000-0000-0000-0000-000000000003", "nombre": "Pedro Ruiz",  "perfil": "regular"},
]

PERFILES = {
    "excelente": {
        "puntajes":    [5, 5, 5, 4.5, 5, 4.5, 5, 5, 4, 5],
        "comentarios": [
            "Excelente profesor, explica con mucha claridad y paciencia.",
            "Uno de los mejores que he tenido en UTEC. Muy recomendado.",
            "Siempre dispuesto a ayudar. Las clases son dinámicas.",
            "Domina el tema al 100%. Las evaluaciones son justas.",
            "Aprendí muchísimo. Sin duda el mejor del ciclo.",
            "Muy exigente pero justo. Se aprende de verdad.",
            "Sus ejemplos del mundo real hacen que todo tenga sentido.",
            "Llegaba puntual, respondía emails rápido. 10/10.",
            None, None,
        ]
    },
    "bueno": {
        "puntajes":    [4, 4, 3.5, 4, 4.5, 3, 4, 3.5, 4, 4.5],
        "comentarios": [
            "Buen profesor. Las clases son claras en general.",
            "Explica bien aunque a veces va muy rápido.",
            "Podría mejorar la retroalimentación de los exámenes.",
            "Buen manejo del tema. Las prácticas son útiles.",
            "Me gustó el enfoque práctico del curso.",
            "Aveces falta dinamismo pero el contenido es sólido.",
            None, None, None, None,
        ]
    },
    "regular": {
        "puntajes":    [3, 2.5, 3, 2, 3.5, 2, 3, 2.5, 3, 1.5],
        "comentarios": [
            "El curso es difícil pero el profesor no ayuda mucho.",
            "Llegaba tarde frecuentemente.",
            "Las evaluaciones no siempre coinciden con lo enseñado.",
            "Esperaba más retroalimentación en los trabajos.",
            "A veces es difícil seguir el ritmo de la clase.",
            None, None, None, None, None,
        ]
    }
}

SEMESTRES = ["2024-1", "2024-2", "2025-1"]
PC_IDS_POR_PROFESOR = {
    "00000000-0000-0000-0000-000000000001": [1, 4, 7, 10, 13],
    "00000000-0000-0000-0000-000000000002": [2, 5, 8, 11, 14],
    "00000000-0000-0000-0000-000000000003": [3, 6, 9, 12, 15],
}

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
    print("Limpiando coleccion...")
    await db.calificaciones.drop()
    docs = []
    estudiante_base = 5
    print("Generando calificaciones...")
    for prof in PROFESORES:
        perfil   = PERFILES[prof["perfil"]]
        pc_ids   = PC_IDS_POR_PROFESOR[prof["id"]]
        puntajes    = perfil["puntajes"]
        comentarios = perfil["comentarios"]
        for pc_id in pc_ids:
            for semestre in SEMESTRES:
                n = 100 if prof["perfil"] == "excelente" else (90 if prof["perfil"] == "bueno" else 80)
                for i in range(n):
                    anonimo    = i % 3 != 0
                    dias_atras = (SEMESTRES.index(semestre) * 180) + (i * 2)
                    docs.append({
                        "profesor_curso_id": pc_id,
                        "profesor_id_cache": prof["id"],
                        "estudiante_id":     None if anonimo else f"estudiante-{(estudiante_base+i)%5000}",
                        "puntaje":           puntajes[i % len(puntajes)],
                        "comentario":        comentarios[i % len(comentarios)],
                        "anonimo":           anonimo,
                        "semestre":          semestre,
                        "creado_en":         datetime.utcnow() - timedelta(days=dias_atras)
                    })
                estudiante_base += n
                if len(docs) >= 500:
                    await db.calificaciones.insert_many(docs)
                    docs = []
    if docs:
        await db.calificaciones.insert_many(docs)
    await db.calificaciones.create_index("profesor_curso_id")
    await db.calificaciones.create_index("profesor_id_cache")
    await db.calificaciones.create_index("semestre")
    total = await db.calificaciones.count_documents({})
    print(f"Seed completado: {total} calificaciones")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
