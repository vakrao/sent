from tkinter import N
import networkx as nx
from shapely import node
from sent_si import *
import random
import pandas as pd
from find_seeds import *
from cent_funcs import *
from spatial import *


# find first order moment for each node
# -> average weight of a node leaving its community
# find second order moment for each node 
# -> variance of weights of a node leaving its community
# -> calculate global weights of a node leaving its community
def moment_stats(in_bond,out_bond,comm_dict,id_comm):
    out_first_mom,out_second_mom = {},{}
    unique_comms = {}

    # for each node 
    # -> comm_id
    # -> movements out of community
    for i in in_bond:
        out_first_mom[i] = 0
        out_second_mom[i] = 0
        unique_comms[i] = 0
    for i in out_bond:
        out_first_mom[i] = 0
        out_second_mom[i] = 0
        unique_comms[i] = 0

    # first moement is mean of all movements
    # out of a nodes commmunity
    for comm in comm_dict:
        for node_id in comm_dict[comm]:
            node_id = str(node_id)
            node_out_edges = out_bond.get(node_id, {})
            unique_comms[node_id] = 0
            u = set()
            for j, i_to_j in node_out_edges.items():
                j_comm = id_comm.get(j)
                if j_comm is None:
                    continue
                if j_comm != comm:
                    u.add(j_comm)
                    out_first_mom[node_id] += i_to_j
            unique_comms[node_id] = len(u)

    mean_first_mom = [out_first_mom[x] for x in out_first_mom] 
    mean_first_mom = sum(mean_first_mom)/len(mean_first_mom)

    ## now, lets calculate the second moment
    for comm in comm_dict:
        for node_id in comm_dict[comm]:
            node_id = str(node_id)
            if node_id not in out_second_mom:
                out_second_mom[node_id] = 0

    comm_df = pd.DataFrame()
    comm_df['NODE_ID'] = list(out_first_mom.keys())
    comm_df['FIRST_MOMENT'] = list(out_first_mom.values())
    comm_df['SECOND_MOMENT'] = list(out_second_mom.values())    
    comm_df["UNIQUE_COMMS"] = list(unique_comms.values())

    return comm_df

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

G = create_network(in_bond, out_bond)

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

print("toal nodes:",node_count)
comm_data = {"PROPERTY_ID":id_vals,"COMM_ID":comm_ids}
comm_df = pd.DataFrame(data=comm_data)

prop_data = pd.read_csv(prop_fn)

comm_df = comm_df.merge(prop_data)

comm_df.to_csv("results/louvain_data.csv")

fp = "params/regional-council-2025-clipped.shp"
comm_colors = comm_ids 

seeds = comm_df 
seeds = seeds.rename(columns={"GPS_CENTRE_LONGITUDE":"long","GPS_CENTRE_LATITUDE":"lat"})

#scatter_communities(fp,seeds,comm_colors)
comm_df = moment_stats(in_bond,out_bond,comm_dict,id_comm)

comm_df.to_csv("results/moments.csv")


