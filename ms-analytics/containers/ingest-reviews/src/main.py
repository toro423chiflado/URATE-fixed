"""
ingest-reviews — extrae calificaciones de MongoDB (MS3) y las sube a S3 como JSON.

FIX respecto al original:
- Eliminado psycopg2-binary (era driver de PostgreSQL, no sirve para Mongo)
- Eliminado SQLAlchemy
- Usa pymongo directamente para leer la colección 'calificaciones'
- Sube JSON (no CSV) porque los docs de Mongo tienen estructura anidada
"""
import io
import os
import json
from datetime import datetime, timezone

import boto3
from pymongo import MongoClient


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise ValueError(f"Missing env var: {name}")
    return value


def main() -> None:
    mongo_url  = env("SOURCE_DB_URL")           # mongodb://user:pass@host:27017
    mongo_db   = env("MONGO_DB", "reviews_db")
    collection = env("COLLECTION", "calificaciones")
    bucket     = env("S3_BUCKET")
    region     = env("AWS_REGION", "us-east-1")
    s3_prefix  = env("S3_PREFIX", "raw")

    # ── Leer desde MongoDB ────────────────────────────────────────
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=10000)
    db     = client[mongo_db]
    col    = db[collection]

    docs = list(col.find({}, {"_id": 0}))   # excluir _id de Mongo (no serializable)
    print(f"Leídos {len(docs)} documentos de {mongo_db}.{collection}")
    client.close()

    # ── Serializar a JSON ─────────────────────────────────────────
    # datetime → iso string para que Athena lo pueda leer
    payload = json.dumps(docs, default=str, ensure_ascii=False)
    buffer  = io.BytesIO(payload.encode("utf-8"))

    # ── Subir a S3 ────────────────────────────────────────────────
    ingestion_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"{s3_prefix}/reviews/{collection}/ingestion_ts={ingestion_ts}/{collection}.json"

    s3 = boto3.client("s3", region_name=region)
    buffer.seek(0)
    s3.upload_fileobj(buffer, bucket, key, ExtraArgs={"ContentType": "application/json"})
    print(f"Uploaded: s3://{bucket}/{key}  docs={len(docs)}")


if __name__ == "__main__":
    main()
