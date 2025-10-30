import numpy as np
import copy
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import FancyArrowPatch
from shapely.geometry import LineString
from sent_si import read_network_data





# read 
def in_neighbors(fn,node_id):
    in_bond,out_bond = read_network_data(fn)
    neigh = in_bond[node_id]
    neigh_ids = list(neigh.keys())
    neigh_ids = [int(x) for x in neigh_ids]
    return neigh_ids

def out_neighbors(fn,node_id):
    in_bond,out_bond = read_network_data(fn)
    neigh = out_bond[node_id]
    neigh_ids = list(neigh.keys())
    neigh_ids = [int(x) for x in neigh_ids]
    return neigh_ids


#   linking ranking and property df
def link_rank_prop_data(rank_df,prop_df):
    rank_df = rank_df.rename(columns={"sent":"PROPERTY_ID"})
    all_data = rank_df.merge(prop_df,on="PROPERTY_ID")
    return all_data



# use average of r_i and r_t metric to 
# break the tie
def break_tie(all_data,rank,top_id):
    best_val = 100000
    single_top = 0
    if rank == "R_F":
        rank_A = "R_I"
        rank_B = "R_T"
    if rank == "R_I":
        rank_A = "R_F"
        rank_B = "R_T"
    if rank == "R_T":
        rank_A = "R_I"
        rank_B = "R_F"
    for t in top_id:
        ri_val = int(set(all_data[all_data["PROPERTY_ID"] == t][rank_A]).pop())
        rt_val = int(set(all_data[all_data["PROPERTY_ID"] == t][rank_B]).pop())
        avg_val = (ri_val + rt_val) / 2
        if avg_val < best_val:
            best_val = avg_val
            single_top = t
    return str(single_top)
    

def get_subset(fn,filter_type,all_data,rank_type):

    in_bond,out_bond = read_network_data(fn)
    if filter_type == "top":
        top_id = str(list(all_data[all_data[rank_type] == 1.0]["PROPERTY_ID"])[0])
    else:
        rank_val = int(filter_type)
        top_id = (list(all_data[all_data[rank_type] == filter_type]["PROPERTY_ID"]))
        if len(top_id) == 1:
            top_id = str(top_id[0])
        else:
            top_id = break_tie(all_data,rank_type,top_id)

    in_neigh = set(in_neighbors(fn,top_id))
    out_neigh = set(out_neighbors(fn,top_id))

    in_comp,out_comp = set(),set()
#    in_comp = get_in_comp(in_bond)
#    out_comp = get_out_comp(out_bond)
    # go through top_id 
    # in-neighbors, to find 
    # neighbors that point into neighbors
#    for i in in_neigh:
#        in_reach = set(in_bond[i].keys())
#        in_reach = set([str(x) for x in in_reach])
#        in_comp.update(in_reach)
#
#    for i in out_neigh:
#        out_reach = set(out_bond[i].keys())
#        out_reach = set([str(x) for x in out_reach])
#        out_comp.update(out_reach)
    
    seeds = set(all_data["PROPERTY_ID"])
    top_set = set([int(top_id)])
    both_neigh = in_neigh.intersection(out_neigh)
    seeds = seeds.difference(top_set)
    seeds = seeds.difference(both_neigh)
    seeds = seeds.difference(out_neigh)
    seeds = seeds.difference(in_neigh)

    if int(top_id) in seeds:
        print("huh?")
    node_subsets = {"seeds":seeds,"both_neigh":both_neigh,"in_neigh":in_neigh,"out_neigh":out_neigh,"top_id":top_set}

    return node_subsets

def find_location(prop_data,node_id):
    spec_row = prop_data[prop_data["PROPERTY_ID"] == node_id]
    lat_val = float(list(spec_row["lat"])[0])
    long_val = float(list(spec_row["long"])[0])
    return (lat_val,long_val)


def get_latlong(all_data,node_types):


    arrow_locs = {}
    top_id = int(list(node_types["top_id"])[0])
    top_lat,top_long = find_location(all_data,top_id)
    for a in node_types:
        arrow_locs[a] = []
        if a == "in_neigh":
            for z in node_types[a]:
                if z in list(all_data["PROPERTY_ID"]):
                    (lat,long) = find_location(all_data,z)
                # leaving location to go to top
                    in_tup  = ((lat,long),(top_lat,top_long))
                    arrow_locs[a].append(in_tup)
        if a == "out_neigh":
            for z in node_types[a]:
                if z in list(all_data["PROPERTY_ID"]):
                    (lat,long) = find_location(all_data,z)
                    # going from location to go to top
                    out_tup  = ((top_lat,top_long),(lat,long))
                    arrow_locs[a].append(out_tup)

    return arrow_locs

        





def get_top_id(fn,all_data,rank_val,rank_type):
    in_bond,out_bond = read_network_data(fn)

    rank_val = int(rank_val)
    top_id = (list(all_data[all_data[rank_type] == rank_val]["PROPERTY_ID"]))
    if len(top_id) == 1:
        top_id = str(top_id[0])
    else:
        top_id = str(break_tie(all_data,rank_type,top_id))
    return top_id

def plot_NZ_nodes_arrows(fp,rank_type,rank_val,subsets_df,latlong_data,neighbors,colors,alpha_vals,node_sizes,node_zorder):

    arrow_types = get_latlong(subsets_df,neighbors)

    nz_regions = gpd.read_file(fp)
    fig,axs = plt.subplots(figsize=(7,9))
    
    nz_regions.plot(ax=axs,color="#fbfbfb", edgecolor="#606060",alpha=0.2,markersize=6,zorder=1)
    

    lon_bounds = (166.0, 179.0)
    lat_bounds = (-47.5, -33.5)
    # convert dictionaries to arrays
    #node_colors = [colors[x] for x in list(subsets_df["node_type"])]
    #node_sizes= [node_sizes[x] for x in list(subsets_df["node_type"])]
    #node_shapes = ["o" if x != "top_id" else "x" for x in list(subsets_df["node_type"])]
    #node_zorder = [node_zorder[x] for x in list(subsets_df["node_type"])]
    #node_alpha = [alpha_vals[x] for x in list(subsets_df["node_type"])]
    rank = rank_type
    new_fn = "../params/hort365_NZ.csv"
    top_id = int(get_top_id(new_fn,subsets_df,rank_val,rank))
    print("top-id: ",top_id)

    both_nodes = set(neighbors.get("both_neigh", []))
    in_nodes = set(neighbors.get("in_neigh", []))
    out_nodes = set(neighbors.get("out_neigh", []))
    seed_nodes = set(neighbors.get("seeds", []))

    in_only_nodes = in_nodes.difference(both_nodes)
    out_only_nodes = out_nodes.difference(both_nodes)

    def select_nodes(node_ids):
        if not node_ids:
            return latlong_data.iloc[0:0]
        subset = latlong_data[latlong_data["PROPERTY_ID"].isin(node_ids)]
        return subset.drop_duplicates(subset="PROPERTY_ID")

    just_top = select_nodes({top_id})
    just_both = select_nodes(both_nodes)
    just_seeds = select_nodes(seed_nodes)
    just_in = select_nodes(in_only_nodes)
    just_out = select_nodes(out_only_nodes)

    in_label = f"In-Neigh ({len(in_only_nodes)})"
    out_label = f"Out-Neigh ({len(out_only_nodes)})"
    both_label = f"Both-Neigh ({len(both_nodes)})"

    if not just_seeds.empty:
        axs.scatter(just_seeds["lat"],just_seeds["long"],c=colors["seeds"],s=node_sizes["seeds"],alpha=alpha_vals["seeds"],zorder=1,label="Seeds")
    if not just_out.empty:
        axs.scatter(just_out["lat"],just_out["long"],c=colors["out_neigh"],s=node_sizes["out_neigh"],alpha=alpha_vals["out_neigh"],zorder=3,label=out_label)
    else:
        axs.scatter([],[],c=colors["out_neigh"],s=node_sizes["out_neigh"],alpha=alpha_vals["out_neigh"],label=out_label)
    if not just_in.empty:
        axs.scatter(just_in["lat"],just_in["long"],c=colors["in_neigh"],s=node_sizes["in_neigh"],alpha=alpha_vals["in_neigh"],zorder=3,label=in_label)
    else:
        axs.scatter([],[],c=colors["in_neigh"],s=node_sizes["in_neigh"],alpha=alpha_vals["in_neigh"],label=in_label)
    if not just_top.empty:
        axs.scatter(just_top["lat"],just_top["long"],c=colors["top_id"],marker="X",s=node_sizes["top_id"],zorder=4,alpha=alpha_vals["top_id"],label="Top Node")
    if not just_both.empty:
        axs.scatter(just_both["lat"],just_both["long"],c=colors["both_neigh"],s=node_sizes["both_neigh"],alpha=alpha_vals["both_neigh"],label=both_label,zorder=3)
    else:
        axs.scatter([],[],c=colors["both_neigh"],s=node_sizes["both_neigh"],alpha=alpha_vals["both_neigh"],label=both_label)
    axs.legend(loc="upper left",frameon=True)
    axs.set_xlim(lon_bounds)
    axs.set_ylim(lat_bounds)
    axs.set_aspect("equal", adjustable="box")
    ## now, let's plot the arrow between neighbors
    for neigh_type in arrow_types:
        arrow_color = colors[neigh_type]
        for ar in arrow_types[neigh_type]:
            arrow = FancyArrowPatch(posA = (ar[0][0],ar[0][1]), posB = (ar[1][0],ar[1][1]), arrowstyle='simple',color=arrow_color,mutation_scale =10,zorder=3)
            #axs.annotate("", xy = (ar[1][0],ar[1][1]), textcoords = "data", xytext=(ar[0][0],ar[0][1]), arrowprops= dict(arrowstyle="-|>",connectionstyle="arc3"),)
            axs.add_patch(arrow)

    return 
    
def scatter_communities(fp,seeds,comm_colors):
    nz_regions = gpd.read_file(fp)
    fig,axs = plt.subplots(figsize=(7,9))
    nz_regions.plot(ax=axs,color="#fbfbfb", edgecolor="#606060",alpha=0.2,markersize=6,zorder=1)
    axs.scatter(seeds["lat"],seeds["long"],colormap="rainbow",c=comm_colors,alpha=0.4)
