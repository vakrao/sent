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
prop_size = read_property_data(prop_fn)





count_to_id = {}
counter = 0
for i in in_bond:
    count_to_id[counter] = i 
    counter += 1
for i in out_bond:
    if i not in list(count_to_id.values()):
        count_to_id[counter] = i 
        counter += 1

G = create_network(in_bond, out_bond)



## let us save all the relevant degree
## information

w,i_d,o_d,i_w,o_w,d,h = {},{},{},{},{},{},{}


## need to do prune in_bond,out_bond
## based on SCC

di_nodes = G.nodes

for n in di_nodes:
    in_deg= G.in_degree(n)
    out_deg= G.out_degree(n)
    all_in_w= G.in_edges(n,data=True)
    all_out_w= G.out_edges(n,data=True)
    
    in_w = 0
    out_w = 0

    for a in all_in_w:
        in_w = in_w + a[2]["weight"]
    for a in all_out_w:
        out_w = out_w + a[2]["weight"]
    
    ## assign to dictionaries

    i_d[n] = in_deg
    i_w[n] = in_w
    o_d[n] = out_deg
    o_w[n] = out_w
    w[n] = in_w + out_w
    d[n] = in_deg+out_deg
    h[n] = prop_size[count_to_id[n]]

## get network centrality measures
close = ret_closeness(G)
bc = ret_bc(G)
ev = ret_ev(G,1000)
harm = ret_harmonic(G)
clust = nx.clustering(G)

## need component size
x = {
    'h':h,
    'i_d':i_d,
    'o_d':o_d,
    'o_w':o_w,
    'i_w':i_w,
    'w':w,
    'd':d,
    'close':close,
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
    correct_ids = [count_to_id[i] for i in node_ids]
    all_vals = list(deg_type.values())
    new_df["node_id"] = correct_ids
    new_df[dt] = all_vals
    if i == 0:
        large_df = new_df
    else:
        large_df = large_df.merge(new_df, how="left")

large_df.to_csv("nz_hort_cent.csv")


## next, let's rank nodes...
ranked_data = pd.read_csv("../data/data_y_real.csv")
ranked_data['o_s'] = ranked_data['d_c'] + ranked_data['d_i']
outbreak_sizes = ranked_data.groupby(["seed"])["o_s"].agg("max")
new_df = pd.DataFrame()
new_df["seed"] = outbreak_sizes.index
# Get Full Outbreak Size
new_df["real_os"] = list(outbreak_sizes)
ranked_data = ranked_data.merge(new_df,left_on="seed",right_on="seed")
ranked_data = ranked_data[ranked_data["o_s"] > 0]
out_sizes = [ x for x in list(outbreak_sizes)  if x > 0 ]
# Count Number of times 
just_zero = ranked_data[ranked_data['o_s'] == 0].groupby(['seed']).size().rename('n_outbreaks')
zero_ids = list(just_zero.index)
seed_amount = len(set(ranked_data["seed"]))
## if an outbreak occurs - what is probability of detecting it for a given sentinel? 
g_zero = (ranked_data.groupby(["seed"])["real_os"].agg("max"))
ranked_data["norm_dt"] = ranked_data["d_t"] / 512
ranked_data["norm_di"] = ranked_data["d_i"] / ranked_data["real_os"]
ranked_data["norm_df"] = ((ranked_data["d_f"]) / seed_amount)











