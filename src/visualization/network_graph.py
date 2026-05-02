from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd
import networkx as nx
import numpy as np
import plotly.graph_objects as go


def _normalize_name(name: str) -> str:
    if name is None:
        return ""
    return str(name).strip()


def build_actor_graph(
    dataframe: pd.DataFrame,
    actor1_col: str = "Actor1Name",
    actor2_col: str = "Actor2Name",
    min_edge_weight: int = 1,
) -> nx.Graph:
    """Build an undirected actor interaction graph from two actor columns.

    Edges are aggregated as counts of co-occurrence between actor1 and actor2.

    Returns a networkx.Graph with edge attribute `weight` (int).
    """
    if actor1_col not in dataframe.columns or actor2_col not in dataframe.columns:
        raise ValueError(f"Expected columns {actor1_col} and {actor2_col} in dataframe")

    df = dataframe[[actor1_col, actor2_col]].copy()
    df[actor1_col] = df[actor1_col].astype(str).map(_normalize_name)
    df[actor2_col] = df[actor2_col].astype(str).map(_normalize_name)

    df = df[(df[actor1_col] != "") & (df[actor2_col] != "")]
    if df.empty:
        return nx.Graph()

    # Use sorted tuple so (A,B) == (B,A)
    pairs = df.apply(lambda r: tuple(sorted((r[actor1_col], r[actor2_col]))), axis=1)
    edge_counts = pairs.value_counts()

    G = nx.Graph()
    # add nodes
    unique_nodes = set(edge_counts.index.tolist())
    for a, b in unique_nodes:
        G.add_node(a)
        G.add_node(b)

    for (a, b), count in edge_counts.items():
        if count >= min_edge_weight and a != b:
            G.add_edge(a, b, weight=int(count))

    # compute degree/strength attributes
    if len(G):
        degrees = dict(G.degree())
        nx.set_node_attributes(G, degrees, "degree")

    return G


def graph_to_plotly(
    G: nx.Graph,
    title: str = "Actor Interaction Network",
    seed: int = 42,
    node_size_scale: float = 6.0,
    edge_width_scale: float = 1.5,
    max_nodes: int = 200,
) -> go.Figure:
    """Convert a networkx.Graph to an interactive Plotly figure.

    - Limits to `max_nodes` by taking highest-degree nodes if graph is large.
    - Node size proportional to degree. Edge width proportional to `weight`.
    """
    if G is None or G.number_of_nodes() == 0:
        fig = go.Figure()
        fig.update_layout(title=title)
        return fig

    # If graph is large, take subgraph of top-degree nodes
    if G.number_of_nodes() > max_nodes:
        top_nodes = sorted(G.nodes(data=True), key=lambda x: x[1].get("degree", 0), reverse=True)[:max_nodes]
        selected = {n for n, _ in top_nodes}
        G = G.subgraph(selected).copy()

    pos = nx.spring_layout(G, seed=seed)

    edge_x = []
    edge_y = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        weight = data.get("weight", 1)
        edge_widths.append(weight)

    # map weight to a width for each segment (repeat per edge)
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    node_x = []
    node_y = []
    node_text: List[str] = []
    node_size: List[float] = []
    for n, data in G.nodes(data=True):
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        deg = data.get("degree", 0)
        node_text.append(f"{n}<br>degree: {deg}")
        node_size.append(max(4.0, deg * node_size_scale))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            color=[data.get("degree", 0) for _, data in G.nodes(data=True)],
            size=node_size,
            colorbar=dict(title="Degree"),
            line_width=1,
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=title,
        showlegend=False,
        margin=dict(b=20, l=5, r=5, t=40),
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    return fig


if __name__ == "__main__":
    # tiny smoke test when run directly
    import pandas as pd

    demo = pd.DataFrame(
        {
            "Actor1Name": ["A", "A", "B", "C", "D", "A"],
            "Actor2Name": ["B", "C", "C", "D", "A", "D"],
        }
    )
    G = build_actor_graph(demo)
    print("nodes", G.number_of_nodes(), "edges", G.number_of_edges())