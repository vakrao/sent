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
from matplotlib import pyplot as plt





def comm_dict(df):
    c = list(df["COMM_ID"])
    i  = list(df["PROPERTY_ID"])

    comm_ids = dict(zip(i,c))
    
    return comm_ids

def comm_density(node_comm_dict,in_bond,out_bond):


    N_comms,w = {},{}
    for i in node_comm_dict:
        c = node_comm_dict[i]
        if c not in N_comms:
            N_comms[c] = 1
        else:
            N_comms[c] += 1

    for a in N_comms:
        for b in N_comms:
            w[(a,b)] = 0

    # count community density
    for i in node_comm_dict:
        r = node_comm_dict[i]
        for j in node_comm_dict:
            if i != j:
                s = node_comm_dict[j]
                a_ij = 0
                if str(i) in out_bond:
                    if str(j) in out_bond[str(i)]:
                        a_ij = out_bond[str(i)][str(j)]
                x = 0
                if r != s:
                    x = a_ij/(N_comms[r]*N_comms[s])
                if r == s:
                    x = a_ij/((N_comms[r]-1)*N_comms[s])
                w[(r,s)] += x


    class_types = []
    combos = set()
    for r in N_comms:
        for s in N_comms:
            if (r,s) not in combos:
            if max(w[(r,s)],w[(s,r)]) < min(w[(r,r)],w[(s,s)]):
                class_types.append("Assortative")
            if max(w[(r,r)],w[(r,s)]) > max(w[(s,r)],w[(s,s)]):
                class_types.append("Core-periphery")
            if min(w[(r,s)],w[(s,r)]) > max(w[(r,r)],w[(s,s)]):
                class_types.append("Disassortative")
            if min(w[(r,r)],w[(s,r)]) > max(w[(r,s)],w[(s,s)]):
                class_types.append("Source-basin")

    return class_types


network_stats = "params/hort365_NZ.csv"
all_stats = pd.read_csv("results/louvain_data.csv")
comm_ids = comm_dict(all_stats)
in_bond,out_bond = read_network_data(network_stats)
class_types = comm_density(comm_ids,in_bond,out_bond)
plt.hist(class_types)
plt.savefig("class_types.png")





