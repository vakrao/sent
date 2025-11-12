import pandas as pd
import multiprocessing as mp
import sys
import yaml
from tqdm import tqdm
from sent_si import *
#from helpers import *
from find_seeds import *
from cent_funcs import *
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

G,_,_ = create_network(in_bond, out_bond)



## let us save all the relevant degree
## information

w,i_d,o_d,i_w,o_w,d,h = {},{},{},{},{},{},{}


## need to do prune in_bond,out_bond
## based on SCC

di_nodes = G.nodes
all_ids = []

for n in di_nodes:
    convt_id = count_to_id[int(n)]
    all_ids.append(convt_id)
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

    i_d[convt_id] = in_deg
    i_w[convt_id] = in_w
    o_d[convt_id] = out_deg
    o_w[convt_id] = out_w
    w[convt_id] = in_w + out_w
    d[convt_id] = in_deg+out_deg
    h[convt_id] = prop_size[convt_id]
    if convt_id == "31568":
        print("in-bond degree:",in_bond[convt_id])
        print("in-degree: ",i_d[convt_id])
        print("in-weight: ",i_w[convt_id])
        print("out-degree: ",o_d[convt_id])
        print("out-weight: ",o_w[convt_id])
        print("total w: ",w[convt_id])

## get network centrality measures
close = ret_closeness(G)
bc = ret_bc(G)
ev = ret_ev(G,1000)
harm = ret_harmonic(G)
clust = nx.clustering(G)

## need component size
x = {
    'node_id':all_ids,
    'h':h.values(),
    'i_d':i_d.values(),
    'o_d':o_d.values(),
    'o_w':o_w.values(),
    'i_w':i_w.values(),
    'w':w.values(),
    'd':d.values(),
    'close':close.values(),
    'bc':bc.values(),
    'ev':ev.values(),
    'harm':harm.values(),
    'clust':clust.values()}

## okay, now lets save the degree values

large_df = pd.DataFrame.from_dict(x)
"""
for i,dt in enumerate(x):
    new_df = pd.DataFrame()
    deg_type = x[dt]
    node_ids = list(deg_type.keys())
    correct_ids = [k for k in node_ids]
    all_vals = list(deg_type.values())
    new_df["node_id"] = correct_ids
    new_df[dt] = all_vals
    if i == 0:
        large_df = new_df
    else:
        large_df = large_df.join(new_df)
"""
large_df.to_csv("results/nz_hort_cent.csv")


## next, let's rank nodes...
ranked_data = pd.read_csv("data/data_y_real.csv")
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

# now, we rank
agg = ranked_data.groupby("sent", as_index=True).agg(
    dF_sum=("norm_df", "sum"),     # total detections (higher better)
    dI_mean=("norm_di", "mean"),   # mean infections at detection (lower better)
    dT_mean=("norm_dt", "mean"),   # mean time to detection (lower better)
)
agg["dF_sum"] = 1- agg["dF_sum"]
# ----------------------------------------------------
# Compute ranks (1 = best)
# ----------------------------------------------------
agg["R_F"] = agg["dF_sum"].rank(ascending=True, method="min")
agg["R_I"] = agg["dI_mean"].rank(ascending=True,  method="min")
agg["R_T"] = agg["dT_mean"].rank(ascending=True,  method="min")
agg.to_csv("results/ranked_table.csv")













