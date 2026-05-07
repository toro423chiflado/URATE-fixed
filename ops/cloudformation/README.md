# UTECRate — CloudFormation

## Qué crea este stack

| Recurso | Cantidad | Detalle |
|---|---|---|
| VPC | 1 | 10.0.0.0/16 con subredes pública y privada |
| Security Groups | 5 | sg-db, sg-mv1, sg-mv2, sg-alb, sg-ingesta |
| Instancias EC2 | 4 | MV-DB, MV1, MV2, MV-Ingesta |
| Application Load Balancer | 1 | Interno, con 5 Target Groups |
| Target Groups | 5 | Uno por microservicio, con health checks |
| Listener Rules | 5 | Path-based routing por /api/xxx |
| API Gateway HTTP | 1 | Con VPC Link al ALB — URL HTTPS pública |
| S3 Bucket | 1 | Para analytics (privado) |
| Glue Database | 1 | Catálogo `utecrate` |
| IAM Managed Policy | 1 | S3 + Athena + Glue |
| IAM Role | 1 | Para Glue Crawler |

## Prerrequisito único: subir las imágenes a Docker Hub

El CloudFormation asume que las imágenes ya existen en Docker Hub.
**Antes de ejecutar el stack**, asegúrate de que el workflow de GitHub Actions
haya corrido y que estas imágenes existan:

```
TU_USUARIO/urate-ms-users:latest
TU_USUARIO/urate-ms-academic:latest
TU_USUARIO/urate-ms-reviews:latest
TU_USUARIO/urate-ms-content:latest
TU_USUARIO/urate-ms-analytics:latest
TU_USUARIO/urate-ingest-users:latest
TU_USUARIO/urate-ingest-content:latest
TU_USUARIO/urate-ingest-reviews:latest
```

## Pasos para desplegar

### Paso 1 — Editar la URL del repo en el stack

Buscar `TU_ORG` en `urate-stack.yaml` y reemplazarlo con tu usuario/organización de GitHub:

```bash
# En Linux/Mac:
sed -i 's/TU_ORG/tu-usuario-github/g' urate-stack.yaml
```

### Paso 2 — Crear el stack en AWS CloudFormation

**Opción A — Consola AWS (recomendado para el curso):**

1. AWS Console → CloudFormation → Create Stack → With new resources
2. Template source: Upload a template file → subir `urate-stack.yaml`
3. Stack name: `urate-stack`
4. Completar los parámetros:
   - `KeyPairName`: nombre del key pair existente en tu cuenta
   - `DockerHubUsername`: tu usuario de Docker Hub
   - `JwtSecret`: dejar el default o cambiar
   - `AwsAccessKeyId` y `AwsSecretKey`: credenciales IAM con acceso a S3/Athena
   - `S3BucketName`: nombre único globalmente (ej: `utecrate-analytics-ARA2025`)
5. Next → Next → Create Stack
6. Esperar ~15-20 minutos (los EC2 instalan Docker y hacen docker pull)

**Opción B — AWS CLI:**

```bash
aws cloudformation create-stack \
  --stack-name urate-stack \
  --template-body file://urate-stack.yaml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=tu-key-pair \
    ParameterKey=DockerHubUsername,ParameterValue=tu_dockerhub_user \
    ParameterKey=AwsAccessKeyId,ParameterValue=TU_KEY \
    ParameterKey=AwsSecretKey,ParameterValue=TU_SECRET \
    ParameterKey=S3BucketName,ParameterValue=utecrate-analytics-tuusuario \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Paso 3 — Ver los outputs (URLs e IPs)

```bash
# Con AWS CLI:
aws cloudformation describe-stacks \
  --stack-name urate-stack \
  --query "Stacks[0].Outputs" \
  --output table

# O en la consola: CloudFormation → urate-stack → Outputs
```

El output `FrontendEnvVars` te da exactamente las 5 variables que necesitas
pegar en AWS Amplify.

### Paso 4 — Correr la ingesta manualmente

Después de que todo esté up (verificar que los Target Groups estén healthy):

```bash
# SSH a MV-Ingesta (IP del output IpMVIngesta)
ssh -i tu-clave.pem ubuntu@<IpMVIngesta>

cd ~/app/ops/mv-ingesta
docker compose -f docker-compose.prod.yml --env-file .env up
```

### Paso 5 — Configurar Glue Crawler y Athena

1. AWS Glue → Crawlers → Create Crawler
   - Data source: `s3://TU_BUCKET/raw/`
   - IAM Role: usar el ARN del output `GlueRoleArn`
   - Database: `utecrate`
2. Correr el crawler
3. AWS Athena → Query Editor → Database: `utecrate`
4. Pegar y ejecutar las queries de `ms-analytics/aws/athena/queries.sql`

### Paso 6 — Conectar Amplify

1. AWS Amplify → New App → GitHub → repo URATE
2. Root dir: `web-frontend`
3. Environment variables: pegar las 5 líneas del output `FrontendEnvVars`

## Para eliminar todo

```bash
# Consola: CloudFormation → urate-stack → Delete
# O CLI:
aws cloudformation delete-stack --stack-name urate-stack
```

⚠️ El bucket S3 NO se elimina automáticamente si tiene objetos.
Vaciarlo primero: S3 → tu-bucket → Empty → Delete.
