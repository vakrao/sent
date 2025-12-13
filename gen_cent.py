import pandas as pd
import multiprocessing as mp
import sys
import yaml
import os
from tqdm import tqdm
from sent_si import *
#from helpers import *
from find_seeds import *
from cent_funcs import *
from decimal import *
from concurrent.futures import ProcessPoolExecutor, as_completed



"""
inputs:
    season_var: season directory to read from
    prop_data: file-name for property-data 
outputs:
    pandas dataframe of all centrlaity data 
"""
def find_node_stats(season_var,prop_fn):
    num_networks =  0
    net_type = "year"
    if season_var == "s":
        net_type = "season"
    if season_var == "m":
        net_type = "month"
    param_directory = "params/new_"+net_type+"_tau/"
    contents = os.listdir(param_directory)


    
    for net_fn in contents:
        ## get in, out values
    

        num_networks += 1
        net_path = param_directory+net_fn
        in_bond, out_bond = read_network_data(net_path)
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
        
            if convt_id not in i_d:
                i_d[convt_id] = in_deg
                i_w[convt_id] = in_w
                o_d[convt_id] = out_deg
                o_w[convt_id] = out_w
                w[convt_id] = in_w + out_w
                d[convt_id] = in_deg+out_deg
                h[convt_id] = prop_size[convt_id]
        
            else:
                i_d[convt_id] += in_deg
                i_w[convt_id] += in_w
                o_d[convt_id] += out_deg
                o_w[convt_id] += out_w
                w[convt_id] += in_w + out_w
                d[convt_id] += in_deg+out_deg
    
        ## get network centrality measures
        all_close,all_bc,all_ev,all_harm,all_clust = {},{},{},{},{}
        close = ret_closeness(G)
        bc = ret_bc(G)
        ev = ret_ev(G,1000)
        harm = ret_harmonic(G)
        clust = nx.clustering(G)
        for x in close:
    
            if x in all_close:
                all_close[x] += close[x]
                all_bc[x] += bc[x]
                all_harm[x] += harm[x]
                all_clust[x] += clust[x]
                all_ev[x] += ev[x]
    
            else:
                all_close[x] = close[x]
                all_bc[x] = bc[x]
                all_harm[x] = harm[x]
                all_clust[x] = clust[x]
                all_ev[x] = ev[x]
    
    all_dicts = [i_d,i_w,o_d,o_w,w,d,all_close,all_bc,all_harm,all_ev]
    for a in all_dicts:
        for node_id in a:
            a[node_id] = a[node_id] / num_networks
    
    
    
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
         'close':all_close.values(),
         'bc':all_bc.values(),
         'ev':all_ev.values(),
         'harm':all_harm.values(),
         'clust':all_clust.values()
        }
    
    large_df = pd.DataFrame.from_dict(x)
    return large_df

## pipeline to run sentinel experiments
## 1. run S_runner based on chosen inputs
## pipeline to create sentinle files
## 1. create ranking .csv
## 2. create centrality .csv
## 3. avg distance/avg first moment
## 4. combine all into one .csv
## input: network-save-file to use 
## pipeline for basic plots-so-far
## -> compare d_F, d_I,d_T
## -> compare d_{f,i,t} to centrality
## greedy pipeline needed I think as well?
## 1) okay - need to store n
if __name__ == "__main__":
    season_var = sys.argv[1]
    prop_data = sys.argv[2]
    save_name = sys.argv[3]
    df = find_node_stats(season_var,prop_data)
    df.to_csv(save_name)











