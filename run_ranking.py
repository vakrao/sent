import pandas as pd
import multiprocessing as mp
import sys
import yaml
from tqdm import tqdm
from sent_si import *
#from helpers import *
from find_seeds import *
from rank_nodes import *
from decimal import *
from concurrent.futures import ProcessPoolExecutor, as_completed





net_fn = "params/hort365_NZ.csv"
prop_fn = "params/2024_prop_dat.csv"

## get in, out values

in_bond, out_bond = read_network_data(net_fn)

G = create_network(in_bond, out_bond)

## let us save all the relevant degree
## information

w,i_d,o_d,i_w,o_w = {},{},{},{},{}


## need to do prune in_bond,out_bond
## based on SCC



for i in in_bond:
    i_d[i] = ret_in_deg(i,in_bond,out_bond)
    i_w[i] = ret_in_w(i,in_bond,out_bond)
    w[i] = ret_total_w(i,in_bond,out_bond)

for i in out_bond:
    o_d[i] = ret_out_deg(i,in_bond,out_bond)
    o_w[i] = ret_out_w(i,in_bond,out_bond)

## get network centrality measures
close = ret_closeness(G)
bc = ret_bc(G)
ev = ret_ev(G,1000)
harm = ret_harmonic(G)
clust = nx.clustering(G)
## need component size

x = {'close':close,
     'bc':bc,
     'ev':ev,
     'harm':harm,
     'clust':clust}
#     'katz':katz}

## okay, now lets save the degree values

large_df = pd.DataFrame()
for i,dt in enumerate(x):
    new_df = pd.DataFrame()
    deg_type = x[dt]
    node_ids = list(deg_type.keys())
    all_vals = list(deg_type.values())
    new_df["node_id"] = node_ids
    new_df[dt] = all_vals
    if i == 0:
        large_df = new_df
    else:
        large_df = large_df.merge(new_df, how="left")

large_df.to_csv("nz_hort_cent.csv")











