from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib as mpl
from matplotlib import cm
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection

from find_seeds import create_network
from sent_si import read_network_data


def _build_id_index_maps(
    in_bond: Mapping[str, Mapping[str, float]],
    out_bond: Mapping[str, Mapping[str, float]],
) -> Mapping[int, str]:
    """
    Reconstruct the index -> property id mapping used inside ``create_network``.

    The helper mirrors the logic in :func:`find_seeds.create_network` so that
    nodes returned by the graph can be translated back to property identifiers.
    """
    count_to_id: dict[int, str] = {}
    counter = 0

    for node_id in in_bond:
        count_to_id[counter] = node_id
        counter += 1

    existing = set(count_to_id.values())
    for node_id in out_bond:
        if node_id not in existing:
            count_to_id[counter] = node_id
            counter += 1

    return count_to_id


def _community_layout(
    graph: nx.Graph, communities: Sequence[Iterable[int]], seed: int | None = None
) -> Mapping[int, Tuple[float, float]]:
    """
    Build a two-level layout that clusters communities together.

    Nodes inside a community are arranged via ``spring_layout`` centred on the
    community barycentre, while communities themselves are positioned using a
    spring layout on a super-graph of communities. This keeps intra-community
    nodes close and spreads communities apart for visual clarity.
    """
    rng = seed if seed is not None else 123

    community_graph = nx.Graph()
    community_graph.add_nodes_from(range(len(communities)))

    node_to_comm: dict[int, int] = {}
    for idx, nodes in enumerate(communities):
        community_graph.nodes[idx]["size"] = len(nodes)
        for node in nodes:
            node_to_comm[node] = idx

    for u, v in graph.edges():
        cu = node_to_comm.get(u)
        cv = node_to_comm.get(v)
        if cu is None or cv is None or cu == cv:
            continue
        # accumulate edge counts for weighting the community layout
        weight = community_graph.get_edge_data(cu, cv, {}).get("weight", 0) + 1
        community_graph.add_edge(cu, cv, weight=weight)

    comm_pos = nx.spring_layout(community_graph, weight="weight", seed=rng, scale=5.0)

    layout: dict[int, Tuple[float, float]] = {}
    for comm_idx, nodes in enumerate(communities):
        subgraph = graph.subgraph(nodes)
        centre = comm_pos.get(comm_idx, np.zeros(2))
        sub_pos = nx.spring_layout(subgraph, seed=rng, center=centre, scale=1.2)
        layout.update(sub_pos)

    # normalise layout to unit square for consistent plotting
    xs, ys = zip(*layout.values())
    xs_arr, ys_arr = np.array(xs), np.array(ys)
    xs_norm = (xs_arr - xs_arr.min()) / (xs_arr.max() - xs_arr.min() + 1e-9)
    ys_norm = (ys_arr - ys_arr.min()) / (ys_arr.max() - ys_arr.min() + 1e-9)
    for node, x, y in zip(layout.keys(), xs_norm, ys_norm):
        layout[node] = (float(x), float(y))

    return layout


def _region_colormap(region_ids: Sequence[int]) -> Mapping[int, str]:
    unique_regions = sorted({rid for rid in region_ids if pd.notna(rid)})
    cmap: ListedColormap = cm.get_cmap("tab20", max(len(unique_regions), 1))
    colours = cmap(np.linspace(0, 1, max(len(unique_regions), 1)))
    return {rid: cm.colors.rgb2hex(colours[idx]) for idx, rid in enumerate(unique_regions)}


def plot_community_network(
    network_path: str | Path,
    property_path: str | Path,
    seed: int = 123,
    save_path: str | Path | None = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Draw the strongly-connected movement network, coloured by community and clustered by layout.

    Parameters
    ----------
    network_path:
        CSV file describing the directed movement network (passed to ``read_network_data``).
    property_path:
        CSV file with property metadata (must include ``PROPERTY_ID`` and ``REGION_ID``).
    seed:
        Random seed for reproducible layouts and Louvain community detection.
    save_path:
        Optional path to save the generated figure. When provided, the figure is stored as
        a PNG with tight bounding boxes.

    Returns
    -------
    (figure, axes):
        The matplotlib figure and axes objects for further tweaking in notebooks.
    """
    network_path = Path(network_path)
    property_path = Path(property_path)

    in_bond, out_bond = read_network_data(str(network_path))
    prop_data = pd.read_csv(property_path)
    prop_data["PROPERTY_ID"] = prop_data["PROPERTY_ID"].astype(int)

    base_graph = create_network(in_bond, out_bond)
    graph = base_graph.to_undirected()
    if graph.number_of_nodes() == 0:
        raise ValueError("The constructed movement graph is empty; nothing to visualise.")

    id_lookup = _build_id_index_maps(in_bond, out_bond)
    property_id_map: dict[int, int] = {}
    for node in graph.nodes:
        raw_id = id_lookup.get(node)
        if raw_id is None:
            continue
        try:
            property_id_map[node] = int(raw_id)
        except (TypeError, ValueError):
            continue
    nx.set_node_attributes(graph, property_id_map, name="property_id")

    region_lookup = dict(zip(prop_data["PROPERTY_ID"], prop_data["REGION_ID"]))
    node_regions = {
        node: region_lookup.get(prop_id)
        for node, prop_id in property_id_map.items()
    }
    nx.set_node_attributes(graph, node_regions, name="region_id")

    # Note: CSV columns store longitude in `GPS_CENTRE_LATITUDE` and latitude in
    # `GPS_CENTRE_LONGITUDE` (they are flipped compared to their names), so we
    # swap when building the lookup.
    coord_lookup = {}
    for _, row in prop_data.iterrows():
        lat_val = row.get("GPS_CENTRE_LONGITUDE")
        lon_val = row.get("GPS_CENTRE_LATITUDE")
        if pd.isna(lat_val) or pd.isna(lon_val):
            continue
        coord_lookup[int(row["PROPERTY_ID"])] = (float(lat_val), float(lon_val))

    # Use the directed graph for Louvain so the community count matches analytical scripts.
    communities = list(
        nx.community.louvain_communities(base_graph, seed=seed, weight="weight")
    )
    node_to_comm = {
        node: comm_idx for comm_idx, nodes in enumerate(communities) for node in nodes
    }
    nx.set_node_attributes(graph, node_to_comm, name="community_id")

    fallback_layout = _community_layout(graph, communities, seed=seed)
    layout: dict[int, Tuple[float, float]] = dict(fallback_layout)

    lat_lon_positions: dict[int, Tuple[float, float]] = {}
    for node, prop_id in property_id_map.items():
        coords = coord_lookup.get(prop_id)
        if coords is None:
            continue
        lon, lat = coords[1], coords[0]
        lat_lon_positions[node] = (lon, lat)

    if lat_lon_positions:
        positions_arr = np.array(list(lat_lon_positions.values()))
        lon_vals, lat_vals = positions_arr[:, 0], positions_arr[:, 1]
        lon_norm = (lon_vals - lon_vals.min()) / (lon_vals.max() - lon_vals.min() + 1e-9)
        lat_norm = (lat_vals - lat_vals.min()) / (lat_vals.max() - lat_vals.min() + 1e-9)
        rng_geo = np.random.default_rng(seed)
        jitter = rng_geo.normal(scale=0.012, size=(len(lat_lon_positions), 2))
        for idx, node in enumerate(lat_lon_positions):
            layout[node] = (
                float(lon_norm[idx] + jitter[idx, 0]),
                float(lat_norm[idx] + jitter[idx, 1]),
            )

    degrees = dict(graph.degree(weight="weight"))
    max_deg = max(degrees.values()) if degrees else 1.0

    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius = 6371.0
        phi1, phi2 = np.radians([lat1, lat2])
        d_phi = np.radians(lat2 - lat1)
        d_lambda = np.radians(lon2 - lon1)
        a = (
            np.sin(d_phi / 2.0) ** 2
            + np.cos(phi1) * np.cos(phi2) * np.sin(d_lambda / 2.0) ** 2
        )
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return float(radius * c)

    distance_bins = {
        "0–5 km": {"edges": [], "color": "#000000"},
        "5–20 km": {"edges": [], "color": "#1565C0"},
        "20+ km": {"edges": [], "color": "#C62828"},
    }

    weight_lookup: dict[Tuple[int, int], float] = {}
    for u, v, data in base_graph.edges(data=True):
        key = (min(u, v), max(u, v))
        weight_lookup[key] = weight_lookup.get(key, 0.0) + float(data.get("weight", 1.0))

    for u, v in graph.edges():
        prop_u = property_id_map.get(u)
        prop_v = property_id_map.get(v)
        coords_u = coord_lookup.get(prop_u)
        coords_v = coord_lookup.get(prop_v)
        if (
            coords_u is None
            or coords_v is None
            or u not in layout
            or v not in layout
        ):
            continue
        distance = haversine_km(coords_u[0], coords_u[1], coords_v[0], coords_v[1])
        weight = weight_lookup.get((min(u, v), max(u, v)), 1.0)
        if distance < 5:
            bucket = "0–5 km"
        elif distance < 20:
            bucket = "5–20 km"
        else:
            bucket = "20+ km"
        segment = (layout[u], layout[v], weight)
        distance_bins[bucket]["edges"].append(segment)

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_axis_off()

    for label, meta in distance_bins.items():
        if not meta["edges"]:
            continue
        segments = [seg[:2] for seg in meta["edges"]]
        weights = np.array([seg[2] for seg in meta["edges"]], dtype=float)
        if weights.size == 0:
            continue
        w_min = weights.min()
        w_max = weights.max()
        if np.isclose(w_min, w_max):
            alphas = np.full(weights.shape, 0.35)
            widths = np.full(weights.shape, 1.4)
        else:
            norm = (weights - w_min) / ((w_max - w_min) + 1e-9)
            alphas = 0.18 + 0.42 * norm
            widths = 0.6 + 2.2 * norm
        base_rgba = np.tile(
            mpl.colors.to_rgba(meta["color"]), (len(weights), 1)
        )
        base_rgba[:, 3] = np.clip(alphas, 0.1, 0.85)
        collection = LineCollection(
            segments,
            colors=base_rgba,
            linewidths=widths,
        )
        ax.add_collection(collection)

    node_scaler = 160 / (max_deg + 1e-6)
    handles = []
    labels = []
    shapes = ["o", "s", "^", "D", "P", "X", "*", "h", "v", "<", ">"]

    community_cmap = cm.get_cmap("tab20", max(len(communities), 1))
    community_colours = list(getattr(community_cmap, "colors", community_cmap(np.linspace(0, 1, max(len(communities), 1)))))
    community_palette = {
        comm_idx: cm.colors.rgb2hex(community_colours[comm_idx % len(community_colours)])
        for comm_idx in range(len(communities))
    }

    for comm_idx, nodes in enumerate(communities):
        shape = shapes[comm_idx % len(shapes)]
        coords = np.array([layout[n] for n in nodes])
        colour = community_palette.get(comm_idx, "#bcbcbc")
        colours = [colour] * len(nodes)
        sizes = [(degrees.get(node, 0.0) + 1) * node_scaler for node in nodes]
        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            s=sizes,
            c=colours,
            marker=shape,
            edgecolors="#1f1f1f",
            linewidths=0.35,
            alpha=0.9,
        )
        handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=colour,
                markeredgecolor="#1f1f1f",
                markersize=7,
            )
        )
        labels.append(f"C{comm_idx + 1}")

    for comm_idx, nodes in enumerate(communities):
        coords = np.array([layout[node] for node in nodes])
        centroid = coords.mean(axis=0)
        ax.text(
            centroid[0],
            centroid[1],
            f"C{comm_idx + 1}",
            fontsize=9,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.25",
                facecolor="#ffffff",
                edgecolor="#424242",
                linewidth=0.8,
                alpha=0.85,
            ),
        )

    ax.set_title(
        "Louvain Community Structure Coloured by Community",
        fontsize=14,
        pad=12,
    )

    edge_legend_handles = []
    for label, meta in distance_bins.items():
        if not meta["edges"]:
            continue
        edge_legend_handles.append(
            plt.Line2D(
                [0],
                [0],
                color=meta["color"],
                linewidth=2.0,
                alpha=0.7,
                label=label,
            )
        )
    if edge_legend_handles:
        handles.extend(edge_legend_handles)
        labels.extend([h.get_label() for h in edge_legend_handles])

    legend = ax.legend(
        handles,
        labels,
        loc="upper right",
        frameon=True,
        framealpha=0.9,
        title="Community / Edge Distance",
    )
    if legend:
        legend.get_frame().set_linewidth(0.6)

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    community_stats = _compute_region_alignment(communities, node_regions)

    return fig, ax, community_stats


def _compute_region_alignment(
    communities: Sequence[Iterable[int]],
    node_regions: Mapping[int, int | float | None],
) -> pd.DataFrame:
    """
    Compute, for each community, the probability that two randomly chosen nodes share the same region.

    This equals one when the community is homogeneous and decreases as regional diversity increases.
    """
    records = []
    for idx, nodes in enumerate(communities):
        region_counts = Counter(
            node_regions.get(node) for node in nodes if node_regions.get(node) is not None
        )
        size = sum(region_counts.values())
        if size <= 1:
            probability = 1.0
        else:
            numerator = sum(count * (count - 1) for count in region_counts.values())
            probability = numerator / (size * (size - 1))
        records.append(
            {
                "community_id": idx + 1,
                "size": size,
                "same_region_probability": probability,
            }
        )

    return pd.DataFrame.from_records(records)


__all__ = ["plot_community_network"]
