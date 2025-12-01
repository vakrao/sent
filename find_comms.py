from tkinter import N
import networkx as nx
from shapely import node
from shapely import Point
from sent_si import *
import random
import geopandas 
import pandas as pd
from find_seeds import *
from cent_funcs import *
from spatial import *





def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth 
    (specified in decimal degrees) using the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point in degrees.
        lon1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lon2 (float): Longitude of the second point in degrees.

    Returns:
        float: The distance between the two points in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance




def calc_moment(comm_dict,edge_dict):
    first_mom,unique_comms = {},{}
    node_counter = 0
    for node_comm in comm_dict:
        for node_id in comm_dict[node_comm]:
            node_id = str(node_id)
            node_edges = edge_dict.get(node_id, {})
            node_id = int(node_id)
            unique_comms[node_id] = 0
            u = set()
            for j, i_to_j in node_edges.items():
                j_comm = id_comm.get(j)
                if j_comm is None:
                    continue
                if j_comm != node_comm:
                    u.add(j_comm)
                    if node_id not in first_mom:
                        first_mom[node_id] = i_to_j
                    else:
                        first_mom[node_id] += i_to_j
            node_counter += 1
            unique_comms[node_id] = len(u)
            if node_id not in first_mom:
                first_mom[node_id] = 0 
                unique_comms[node_id] = 0

    return first_mom,unique_comms

def calc_deg_moment(comm_dict,edge_dict):
    first_mom,unique_comms = {},{}
    node_counter = 0
    for node_comm in comm_dict:
        for node_id in comm_dict[node_comm]:
            node_id = str(node_id)
            node_edges = edge_dict.get(node_id, {})
            node_id = int(node_id)
            unique_comms[node_id] = 0
            u = set()
            for j, i_to_j in node_edges.items():
                j_comm = id_comm.get(j)
                if j_comm is None:
                    continue
                if j_comm != node_comm:
                    u.add(j_comm)
                    if node_id not in first_mom:
                        first_mom[node_id] = 1
                    else:
                        first_mom[node_id] += 1
            node_counter += 1
            unique_comms[node_id] = len(u)
            if node_id not in first_mom:
                first_mom[node_id] = 0 
                unique_comms[node_id] = 0

    return first_mom,unique_comms

def calc_distance(comm_dict,edge_type,opt,prop_df,in_out):
    lat = list(prop_df["GPS_CENTRE_LATITUDE"])
    long = list(prop_df["GPS_CENTRE_LONGITUDE"])
    prop_id = list(prop_df["PROPERTY_ID"])
    comm_props = []

    latlong_dict = {}
    for i,p in enumerate(prop_id):
        latlong_dict[p] = (lat[i],long[i])

    all_dist = []
    for c in comm_dict:
        comm_ids = comm_dict[c]
        for node_vals in comm_ids:
            source_node = node_vals
            if str(node_vals) in edge_type:
                neighbors = edge_type[str(node_vals)]
                node_dist= []
                a_coords = latlong_dict[source_node]
                for n in neighbors:
                    b_coords = latlong_dict[int(n)]
                    dist_val = haversine_distance(a_coords[0],a_coords[1],b_coords[0],b_coords[1])
                    node_dist.append(dist_val)
            if opt == "MAX":
                dist_val = max(node_dist)
            if opt == "AVG":
                dist_val = np.mean(node_dist)
            all_dist.append(dist_val)
            comm_props.append(node_vals)

    dist_df = pd.DataFrame()
    dist_df['NODE_ID'] = comm_props
    title_string = opt+"_DIST_"+in_out
    if opt == "AVG":
        dist_df[title_string] = list(all_dist)
    if opt == "MAX":
        dist_df[title_string] = list(all_dist)

    return dist_df


                









# find first order moment for each node
# -> average weight of a node leaving its community
# find second order moment for each node 
# -> variance of weights of a node leaving its community
# -> calculate global weights of a node leaving its community
def moment_stats(in_bond,out_bond,comm_dict):
    out_first_mom,out_second_mom = {},{}
    unique_comms = {}


    out_first_mom,out_unique = calc_moment(comm_dict,out_bond)
    in_first_mom,in_unique = calc_moment(comm_dict,in_bond)


    all_nodes = []
    for c in comm_dict:
        for i in comm_dict[c]:
            all_nodes.append(i)
    temp_mom = pd.DataFrame()
    temp_mom['NODE_ID'] = list(all_nodes)
    temp_mom['FIRST_OUT_MOMENT'] = list(out_first_mom.values())
    temp_mom['FIRST_IN_MOMENT'] = list(in_first_mom.values())
    temp_mom["UNIQUE_OUT_COMMS"] = list(out_unique.values())
    temp_mom["UNIQUE_IN_COMMS"] = list(in_unique.values())

    return temp_mom

# find first order moment for each node
# -> average weight of a node leaving its community
# find second order moment for each node 
# -> variance of weights of a node leaving its community
# -> calculate global weights of a node leaving its community
def deg_stats(in_bond,out_bond,comm_dict):
    out_first_mom,out_second_mom = {},{}
    unique_comms = {}


    out_first_deg,out_unique = calc_deg_moment(comm_dict,out_bond)
    in_first_deg,in_unique = calc_deg_moment(comm_dict,in_bond)


    all_nodes = []
    for c in comm_dict:
        for i in comm_dict[c]:
            all_nodes.append(i)
    temp_deg = pd.DataFrame()
    temp_deg['NODE_ID'] = list(all_nodes)
    temp_deg['FIRST_OUT_DEG_MOMENT'] = list(out_first_deg.values())
    temp_deg['FIRST_IN_DEG_MOMENT'] = list(in_first_deg.values())
    temp_deg["UNIQUE_OUT_DEG_COMMS"] = list(out_unique.values())
    temp_deg["UNIQUE_IN_DEG_COMMS"] = list(in_unique.values())

    return temp_deg
net_fn = "params/hort365_NZ.csv"
prop_fn = "params/2024_prop_dat.csv"

## get in, out values

in_bond, out_bond = read_network_data(net_fn)
prop_size = read_property_data(prop_fn)





count_to_id = {}
counter = 0
for i in in_bond:
    count_to_id[counter] = i 
    counter += 1
last_vals = count_to_id.values()
for i in out_bond:
    if i not in list(last_vals):
        count_to_id[counter] = i 
        counter += 1

G,_,_ = create_network(in_bond, out_bond)

louv_comms = nx.community.louvain_communities(G,weight="weight",seed=123)



large_df = pd.DataFrame()
comm_ids = []
id_vals = []
comm_counter = 1
comm_dict = {}
id_comm = {}
# iterater through all communities
# convert graph ID to property ID
node_count = 0
for comm in (louv_comms):

    local_ids = []
    for i in comm:
        correct_id = int(count_to_id[i])
        id_comm[str(correct_id)] = comm_counter
        comm_ids.append(comm_counter)
        id_vals.append(correct_id)
        local_ids.append(correct_id)
        node_count += 1
    comm_dict[comm_counter] = local_ids
    comm_counter += 1 

comm_data = {"PROPERTY_ID":id_vals,"COMM_ID":comm_ids}
comm_df = pd.DataFrame(data=comm_data)


prop_data = pd.read_csv(prop_fn)

comm_df = comm_df.merge(prop_data)

comm_df.to_csv("results/louvain_data.csv")

fp = "params/regional-council-2025-clipped.shp"
comm_colors = comm_ids 


#scatter_communities(fp,seeds,comm_colors)
moment_df = moment_stats(in_bond,out_bond,comm_dict)
moment_df.to_csv("results/moments.csv")
degmom_df = deg_stats(in_bond,out_bond,comm_dict)
degmom_df.to_csv("results/deg_moments.csv")
moment_df = moment_df.merge(degmom_df)
in_max_dist_df =calc_distance(comm_dict,in_bond,"MAX",prop_data,"IN") 
in_avg_dist_df =calc_distance(comm_dict,in_bond,"AVG",prop_data,"IN") 
out_max_dist_df =calc_distance(comm_dict,out_bond,"MAX",prop_data,"OUT") 
out_avg_dist_df =calc_distance(comm_dict,out_bond,"AVG",prop_data,"OUT") 

cent_df = pd.read_csv("results/nz_hort_cent.csv")
moment_df = moment_df.merge(in_max_dist_df)
moment_df = moment_df.merge(in_avg_dist_df)
moment_df = moment_df.merge(out_avg_dist_df)
moment_df = moment_df.merge(out_max_dist_df)
cent_df = cent_df.rename(columns={"node_id":"NODE_ID"})
moment_df = moment_df.merge(cent_df)

#rank_fn = sys.argv[1]
rank_df = pd.read_csv("results/ranked_table.csv")
rank_df = rank_df.rename(columns={'sent':"NODE_ID"})
moment_df = moment_df.merge(rank_df)
moment_df.to_csv("results/all_stats.csv")


