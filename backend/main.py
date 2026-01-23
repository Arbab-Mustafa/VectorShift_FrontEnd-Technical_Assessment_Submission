from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx

app = FastAPI()

# === VERY IMPORTANT: Add CORS middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://127.0.0.1:3000",      # sometimes browsers use 127.0.0.1
        "*"                           # temporary wildcard for testing (remove later)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
    expose_headers=["Content-Length"],
    max_age=600,                      # cache preflight for 10 minutes
)

@app.get("/")
def read_root():
    return {"Ping": "Pong"}

@app.post("/pipelines/parse")
def parse_pipeline(data: dict = Body(...)):
    try:
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("nodes and edges must be lists")

        # Extract node IDs (react-flow nodes have 'id')
        node_ids = [node["id"] for node in nodes if "id" in node]

        # Build directed graph
        G = nx.DiGraph()
        G.add_nodes_from(node_ids)

        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                G.add_edge(source, target)
            else:
                raise ValueError("Every edge must have 'source' and 'target'")

        num_nodes = len(nodes)
        num_edges = len(edges)
        is_dag = nx.is_directed_acyclic_graph(G)

        return {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "is_dag": is_dag
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))