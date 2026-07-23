# Arquitetura Serverless Final - Startup XYZ
# Fluxo real com pipeline de ingestão assíncrona, OCR e máquina de estados.
# Requer: pip install diagrams | Graphviz instalado no sistema.

import os
import shutil

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.general import User
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Textract
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3

# Garante que o Graphviz esteja disponível no PATH durante a execução
for graphviz_path in [
    r"C:\Program Files\Graphviz\bin",
    r"C:\Program Files (x86)\Graphviz\bin",
]:
    if os.path.isdir(graphviz_path) and graphviz_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] += os.pathsep + graphviz_path

if shutil.which("dot") is None:
    raise RuntimeError(
        "Graphviz não foi encontrado. Instale o Graphviz e reinicie o terminal."
    )

graph_attr = {
    "fontsize": "22",
    "fontname": "Arial Bold",
    "bgcolor": "transparent",
    "nodesep": "1.2",
    "ranksep": "2.5",
    "pad": "0.8",
    "fontcolor": "#232F3E",
    "splines": "ortho",
}

node_attr = {
    "fontsize": "13",
    "fontname": "Arial Bold",
    "fontcolor": "#232F3E",
    "labelloc": "b",
}

cluster_attr_main = {
    "fontsize": "16",
    "fontname": "Arial Bold",
    "fontcolor": "#FFFFFF",
    "bgcolor": "#232F3E",
    "margin": "40.0",
    "pencolor": "#FF9900",
    "penwidth": "2.0",
}

cluster_attr_ingestion = {
    "fontsize": "13",
    "fontname": "Arial Bold",
    "fontcolor": "#232F3E",
    "bgcolor": "#E8F5E9",
    "margin": "25.0",
    "pencolor": "#4CAF50",
    "penwidth": "1.5",
}

cluster_attr_ocr = {
    "fontsize": "13",
    "fontname": "Arial Bold",
    "fontcolor": "#232F3E",
    "bgcolor": "#FFF3E0",
    "margin": "25.0",
    "pencolor": "#FF9800",
    "penwidth": "1.5",
}

cluster_attr_observability = {
    "fontsize": "13",
    "fontname": "Arial Bold",
    "fontcolor": "#232F3E",
    "bgcolor": "#F3E5F5",
    "margin": "25.0",
    "pencolor": "#9C27B0",
    "penwidth": "1.5",
}

edge_primary = {"color": "#FF9900", "penwidth": "2.5", "fontsize": "11", "fontname": "Arial Bold", "fontcolor": "#e86200"}
edge_async = {"color": "#4CAF50", "penwidth": "2.0", "fontsize": "11", "fontname": "Arial Bold", "fontcolor": "#2E7D32", "style": "dashed"}
edge_error = {"color": "#F44336", "penwidth": "2.0", "fontsize": "11", "fontname": "Arial Bold", "fontcolor": "#C62828", "style": "dotted"}
edge_state = {"color": "#9C27B0", "penwidth": "2.0", "fontsize": "11", "fontname": "Arial Bold", "fontcolor": "#6A1B9A"}

with Diagram(
    "Arquitetura Serverless Final — Startup XYZ (MVP TCC)",
    direction="LR",
    show=False,
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
    filename="arquitetura_serverless_startup_xyz_final",
):
    cliente = User("Cliente\n(Aplicação/Script E2E)")

    with Cluster("AWS Cloud — Backend Serverless", graph_attr=cluster_attr_main):

        with Cluster("① Camada de Entrada", graph_attr=cluster_attr_ingestion):
            api_gw = APIGateway("API Gateway\n(HTTP API)")
            lambda_ingestion = Lambda("Lambda: Ingestão\n(Upload Handler)\nCold Start Optimized")

        s3 = S3("Amazon S3\n(Bucket Privado)\nVersioning + SSE + Lifecycle")

        with Cluster("② Processamento Assíncrono (OCR)", graph_attr=cluster_attr_ocr):
            lambda_ocr = Lambda("Lambda: OCR\n(OCR Handler)\ntimeout=30s | 256MB")
            textract = Textract("Amazon Textract\n(DetectDocumentText)\nus-east-1")

        with Cluster("③ Estado / Observabilidade", graph_attr=cluster_attr_observability):
            dynamodb = Dynamodb("DynamoDB\n(PAY_PER_REQUEST)\nMáquina de Estados")
            cloudwatch = Cloudwatch("CloudWatch Logs\n(Auditoria & Tracing)")

    # Fluxo principal: ingestão síncrona
    cliente >> Edge(label=" POST /upload", **edge_primary) >> api_gw
    api_gw >> Edge(label=" Aciona", **edge_primary) >> lambda_ingestion
    lambda_ingestion >> Edge(label=" Gera Presigned URL\n+ Salva PENDING_UPLOAD", **edge_primary) >> dynamodb
    lambda_ingestion >> Edge(label=" Retorna URL assinada", **edge_primary) >> cliente

    # Upload direto cliente → S3 (bypass Lambda)
    cliente >> Edge(label=" PUT Direto (Presigned URL)", **edge_async) >> s3

    # Trigger assíncrono: S3 Event Notification
    s3 >> Edge(label=" s3:ObjectCreated\n(Event Notification)", **edge_async) >> lambda_ocr

    # Pipeline OCR
    lambda_ocr >> Edge(label=" detect_document_text()", **edge_primary) >> textract
    textract >> Edge(label=" Texto Extraído", **edge_primary) >> lambda_ocr

    # Persistência de estado: sucesso e erro
    lambda_ocr >> Edge(label=" PROCESSED\nextracted_text", **edge_state) >> dynamodb
    lambda_ocr >> Edge(label=" FAILED_EXTERNAL\n_DEPENDENCY", **edge_error) >> dynamodb

    # Observabilidade
    lambda_ingestion >> Edge(label=" Logs", **edge_state) >> cloudwatch
    lambda_ocr >> Edge(label=" Logs + Tracebacks", **edge_state) >> cloudwatch
