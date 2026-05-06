# UTECRate — Estructura del proyecto y guía de clonado por MV

## Estructura completa (cómo debe quedar el repo)

```
URATE/
├── .gitignore                   ← usa GITIGNORE_root.txt
├── ms-users/                    (MS1 · Node.js · PostgreSQL)  ✓ OK
├── ms-academic/
│   ├── .gitignore               ← usa GITIGNORE_ms-academic.txt
│   ├── pom.xml                  ← agregar bloque de MS2_springdoc_dependency.xml
│   └── (NUNCA subir: target/)
├── ms-reviews/
│   └── src/
│       ├── models/calificacion.py   ← reemplazar con MS3_calificacion_model.py
│       └── routes/calificaciones.py ← reemplazar con MS3_calificaciones_route.py
├── ms-analytics/
│   ├── containers/
│   │   ├── ingest-content/
│   │   │   ├── src/main.py      ← reemplazar con INGESTA_ingest-content_main.py
│   │   │   └── requirements.txt ← reemplazar con INGESTA_ingest-content_requirements.txt
│   │   └── ingest-reviews/
│   │       ├── src/main.py      ← reemplazar con INGESTA_ingest-reviews_main.py
│   │       └── requirements.txt ← reemplazar con INGESTA_ingest-reviews_requirements.txt
│   └── aws/athena/
│       ├── queries.sql          ← reemplazar con ATHENA_queries.sql
│       └── views.sql            ← reemplazar con ATHENA_views.sql
├── web-frontend/
│   ├── .env.local.example       ← reemplazar con FRONTEND_env.local.example
│   └── src/services/api.js      ← reemplazar con FRONTEND_api.js
└── ops/                         ← docker-composes de producción por MV
```

---

## Dónde clonar en cada MV

### MV Base de Datos
```bash
git clone https://github.com/tu-org/URATE.git && cd URATE
cp ops/mv-database/docker-compose.yml ~/urate-db/
cp ms-academic/mysql-init/01-init.sql  ~/urate-db/mysql-init/
cd ~/urate-db && docker compose up -d
# fotos.sql (cuando MySQL esté healthy):
mysql -h 127.0.0.1 -P 3306 -uutec_user -putec_pass_2025 academic_db < fotos.sql
```

### MV1 — MS1 + MS2
```bash
git clone https://github.com/tu-org/URATE.git && cd URATE
docker build -t ms-users:latest    ./ms-users/
docker build -t ms-academic:latest ./ms-academic/
cp ops/mv1/.env.example ops/mv1/.env
nano ops/mv1/.env   # DB_HOST=<IP privada de MV-DB>
docker compose -f ops/mv1/docker-compose.yml --env-file ops/mv1/.env up -d
# seed.js corre automático vía entrypoint.sh cuando la BD está vacía
```

### MV2 — MS3 + MS4 + MS5
```bash
git clone https://github.com/tu-org/URATE.git && cd URATE
docker build -t ms-reviews:latest   ./ms-reviews/
docker build -t ms-content:latest   ./ms-content/
docker build -t ms-analytics:latest ./ms-analytics/
cp ops/mv2/.env.example ops/mv2/.env
nano ops/mv2/.env   # DB_HOST, MV1_HOST, AWS credentials
docker compose -f ops/mv2/docker-compose.yml --env-file ops/mv2/.env up -d
# Seed MongoDB una sola vez:
pip3 install motor
MONGO_URL=mongodb://<IP-MV-DB>:27017 MONGO_DB=reviews_db python3 ms-reviews/seed.py
```

### MV Ingesta
```bash
git clone https://github.com/tu-org/URATE.git
cd URATE/ms-analytics
# Editar .env de cada contenedor con IPs reales y creds AWS
docker compose -f docker-compose.ingesta.yml build
docker compose -f docker-compose.ingesta.yml up
```

### Frontend → AWS Amplify (no va en ninguna MV)
Conectar repo a Amplify y configurar en la consola:
VITE_MS1_URL … VITE_MS5_URL apuntando al API Gateway HTTPS
