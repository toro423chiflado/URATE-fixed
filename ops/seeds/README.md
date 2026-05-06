# Seeds de UTECRate

## Orden de ejecución (después de levantar MV-DB)

### Seed MS1 — PostgreSQL (25,000 usuarios)
Desde MV1, después de `docker compose up -d`:
```bash
# El entrypoint.sh de ms-users lo corre automáticamente si la BD está vacía.
# Para forzarlo manualmente:
docker exec utec_ms_users node prisma/seed.js
```

### Seed MS2 — MySQL (fotos de carreras y cursos)
El data.sql se aplica automático al arrancar MySQL.
Las fotos se aplican manualmente:
```bash
# Desde MV-DB o cualquier host con mysql-client:
mysql -h 127.0.0.1 -P 3306 -uutec_user -putec_pass_2025 academic_db < fotos-ms2.sql
```

### Seed MS3 — MongoDB (calificaciones coherentes)
Desde MV2 o MV-Ingesta:
```bash
pip3 install motor
MONGO_URL=mongodb://<IP-MV-DB>:27017 MONGO_DB=reviews_db python3 seed-ms3-reviews.py
```
