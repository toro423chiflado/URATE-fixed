"""
ingest-content — extrae tablas de MySQL (MS2 ms-academic) y las sube a S3 como CSV.

FIX respecto al original:
- Cambiado driver de postgresql+psycopg2 → mysql+pymysql
- Tablas reales de academic_db: carrera, curso, profesor_curso
"""
import io
import os
from datetime import datetime, timezone

import boto3
import pandas as pd
from sqlalchemy import create_engine, text


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise ValueError(f"Missing env var: {name}")
    return value


def load_table(engine, table_name: str) -> pd.DataFrame:
    return pd.read_sql(text(f"SELECT * FROM {table_name}"), engine)


def main() -> None:
    # FIX: mysql+pymysql en lugar de postgresql+psycopg2
    source_db_url  = env("SOURCE_DB_URL")   # mysql+pymysql://utec_user:utec_pass_2025@DB_HOST:3306/academic_db
    tables_raw     = env("TABLES", "carrera,curso,profesor_curso")
    bucket         = env("S3_BUCKET")
    region         = env("AWS_REGION", "us-east-1")
    s3_prefix      = env("S3_PREFIX", "raw")
    output_format  = env("OUTPUT_FORMAT", "csv").lower()
    service_name   = env("SERVICE_NAME", "content")

    tables = [t.strip() for t in tables_raw.split(",") if t.strip()]

    engine     = create_engine(source_db_url)
    s3_client  = boto3.client("s3", region_name=region)
    ingestion_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for table_name in tables:
        df = load_table(engine, table_name)
        buffer = io.BytesIO()

        if output_format == "json":
            payload = df.to_json(orient="records", date_format="iso", force_ascii=False)
            buffer.write(payload.encode("utf-8"))
            extension = "json"
        else:
            buffer.write(df.to_csv(index=False).encode("utf-8"))
            extension = "csv"

        key = f"{s3_prefix}/{service_name}/{table_name}/ingestion_ts={ingestion_ts}/{table_name}.{extension}"
        buffer.seek(0)
        s3_client.upload_fileobj(buffer, bucket, key)
        print(f"Uploaded: s3://{bucket}/{key}  rows={len(df)}")


if __name__ == "__main__":
    main()
