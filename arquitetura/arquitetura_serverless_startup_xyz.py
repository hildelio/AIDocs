# Arquitetura Serverless - Startup XYZ
# Requer Python 3.7+ e Graphviz instalado no sistema.

import os
import shutil

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.general import User
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
    "fontname": "Arial bold",
    "bgcolor": "transparent",
    "nodesep": "1.8",
    "ranksep": "3.5",
    "pad": "0.5",
    "fontcolor": "#232F3E",
}

node_attr = {
    "fontsize": "13",
    "fontname": "Arial bold",
    "fontcolor": "#232F3E",
    "labelloc": "b",
}

cluster_attr = {
    "fontsize": "15",
    "fontname": "Arial bold",
    "fontcolor": "#232F3E",
    "bgcolor": "#F2F8FD",
    "margin": "45.0",
    "pencolor": "#8c949e",
}

edge_attr = {
    "fontsize": "12",
    "fontname": "Arial bold",
    "fontcolor": "#e86200",
    "color": "#e86200",
    "penwidth": "2.5",
}

# Cria o diagrama com o nome solicitado
with Diagram(
    "Arquitetura Serverless - Startup XYZ",
    direction="LR",
    show=False,
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename="arquitetura_serverless_startup_xyz_v4",
) as diag:

    # Usuário
    cliente = User("Cliente\n(Envia PDF e ID)")

    # Cluster visual para destacar a infraestrutura AWS
    with Cluster("AWS Cloud - Backend Serverless", graph_attr=cluster_attr):
        api_gateway = APIGateway("API Gateway\n(Porta de Entrada)")
        lambda_func = Lambda("AWS Lambda\n(Validação e Presigned URL)")
        s3 = S3("Amazon S3\n(Lifecycle de 365 dias)")

    # Fluxo da arquitetura com rótulos explicativos
    cliente >> Edge(label=" Requisição\ncom PDF e ID ") >> api_gateway
    api_gateway >> Edge(label=" Aciona\nFunção ") >> lambda_func
    lambda_func >> Edge(label=" Salva / Busca\nArquivo ") >> s3