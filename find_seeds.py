import networkx as nx
from sent_si import *
import random
import pandas as pd


def create_network(in_data,out_data):
    # go through dictioanries of in, out seeds
    random.seed()
    id_to_index = {}
    index_to_id = {}
    counter = 0
    for n in in_data:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1

    for n in out_data:
        if n not in id_to_index:
            id_to_index[n] = counter
            index_to_id[counter] = n
            counter += 1


    # convert id values to 0-vertex_amount
    mod_in_data = {}
    for d in in_data:
        x = in_data[d]
        new_d = id_to_index[d]
        mod_in_data[new_d] = {}
        for s in x:
            new_s = id_to_index[s]
            mod_in_data[new_d][new_s] = x[s]

    mod_out_data = {}
    for s in out_data:
        x = out_data[s]
        new_s = id_to_index[s]
        mod_out_data[new_s] = {}
        for d in x:
            new_d = id_to_index[d]
            mod_out_data[new_s][new_d] = x[d]
    # now, create graph
    G = nx.DiGraph()
    for d in mod_in_data:
        x = mod_in_data[d]
        for s in x:
            weight_val = mod_in_data[d][s]
#            G.add_edge(s,d,weight=weight_val))
    for s in mod_out_data:
        x = mod_out_data[s]
        for d in x:
            weight_val = mod_out_data[s][d]
            G.add_edge(s,d,weight=weight_val)
    # go through all the strongly connected components of graph
    # return the SCC


    gc = max(nx.strongly_connected_components(G), key=len)
    G = nx.DiGraph()
    for d in mod_in_data:
        x = {}
        if d in gc:
            x = mod_in_data[d]
        for s in x:
            if s in gc:
                weight_val = mod_in_data[d][s]
            G.add_edge(s,d,weight=weight_val)
    for s in mod_out_data:
        x = {}
        if s in gc:
            x = mod_out_data[s]
        for d in x:
            if d in gc:
                weight_val = mod_out_data[s][d]
                G.add_edge(s,d,weight=weight_val)
    

    return G



def find_conn_comp_calib_seeds(fp,seed_amount,in_data,out_data,save_fn=""):
    random.seed()
    id_to_index = {}
    index_to_id = {}
    counter = 0

    # go through dictioanries of in, out seeds
    for n in in_data:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1

    for n in out_data:
        if n not in id_to_index:
            id_to_index[n] = counter
            index_to_id[counter] = n
            counter += 1


    # convert id values to 0-vertex_amount
    mod_in_data = {}
    for d in in_data:
        x = in_data[d]
        new_d = id_to_index[d]
        mod_in_data[new_d] = {}
        for s in x:
            new_s = id_to_index[s]
            mod_in_data[new_d][new_s] = x[s]

    mod_out_data = {}
    for s in out_data:
        x = out_data[s]
        new_s = id_to_index[s]
        mod_out_data[new_s] = {}
        for d in x:
            new_d = id_to_index[d]
            mod_out_data[new_s][new_d] = x[d]
    # now, create graph
    G = nx.DiGraph()
    for d in mod_in_data:
        x = mod_in_data[d]
        for s in x:
            weight_val = mod_in_data[d][s]
#            G.add_edge(s,d,weight=weight_val))
    for s in mod_out_data:
        x = mod_out_data[s]
        for d in x:
            weight_val = mod_out_data[s][d]
            G.add_edge(s,d,weight=weight_val)


    # go through all the strongly connected components of graph
    comp_amount = 0
    for _ in nx.strongly_connected_components(G):
        comp_amount += 1
    largest = (max(nx.strongly_connected_components(G), key=len))
    id_largest = [x for x in largest]
    all_ids = [str(index_to_id[i]) for i in id_largest]
    prop_regions = read_property_data_regions(fp)
    proper_ids = []
    # now, match to region 2
    within_region = 0
    for p in all_ids:
        if p in prop_regions:
            r_id = prop_regions[p]
            if r_id == 2 and p in in_data and p in out_data:
                within_region += 1
                proper_ids.append(p)
    if seed_amount > len(proper_ids):
        seed_amount = len(proper_ids)
    seed_ids = random.sample(proper_ids,seed_amount)
    #print("total id amount of all nodes: ",len(all_ids))
    ## now, save these seed_ids to a filepath
    seed_dict = {'seed_ids':seed_ids}
    write_df = pd.DataFrame.from_dict(seed_dict)
    write_df.to_csv(save_fn)

    return seed_ids
    

def read_property_data_regions (filename):

    prop_size = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        for row in rows:
            if first_row > 0:
                #print (row[0], row[3])
                i = row[0]
                r_id = -10
                s = 1.0
                if len(row[6])>0:
                    r_id = int(row[6])
                
                prop_size[i] = r_id
            first_row = 1

    return prop_size
# USE OUTSIDE OF CALIBRATION
# PICKING SEEDS OUTSIDE OF BAY OF PLENTY
def find_real_seeds(fp,seed_amount,in_data,out_data,save_fn):
    random.seed()


    id_to_index = {}
    index_to_id = {}
    counter = 0

    for n in in_data:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1

    for n in out_data:
        if n not in id_to_index:
            id_to_index[n] = counter
            index_to_id[counter] = n
            counter += 1


    # convet id values to 0-vertex_amount
    mod_in_data = {}
    for d in in_data:
        x = in_data[d]
        new_d = id_to_index[d]
        mod_in_data[new_d] = {}
        for s in x:
            new_s = id_to_index[s]
            mod_in_data[new_d][new_s] = x[s]

    mod_out_data = {}
    for s in out_data:
        x = out_data[s]
        new_s = id_to_index[s]
        mod_out_data[new_s] = {}
        for d in x:
            new_d = id_to_index[d]
            mod_out_data[new_s][new_d] = x[d]
    weights = []
    # now, create graph
    for d in mod_in_data:
        x = mod_in_data[d]
        for s in x:
            weight_val = mod_in_data[d][s]
    G = nx.DiGraph()
    # now, create graph
    for s in mod_out_data:
        x = mod_out_data[s]
        for d in x:
            weight_val = mod_out_data[s][d]
            G.add_edge(s,d,weight=weight_val)


    #G.add_nodes_from(counter)
    comp_amount = 0
    for component in nx.strongly_connected_components(G):
        comp_amount += 1
    largest = (max(nx.strongly_connected_components(G), key=len))
    id_largest = [x for x in largest]
    
    
    print("seeds in scc :",len(largest))
    all_ids = [str(index_to_id[i]) for i in id_largest]
    seed_amount_max = len(all_ids)
    print("seed amount: ",seed_amount_max)
    if seed_amount > seed_amount_max:
        seed_amount = seed_amount_max
    # now, match to region 2
    within_region = 0
    seed_ids = random.sample(all_ids,seed_amount)
    print("total id amount of all nodes: ",len(all_ids))
    ## now, save these seed_ids to a filepath
    seed_dict = {'seed_ids':seed_ids}
    write_df = pd.DataFrame.from_dict(seed_dict)
    write_df.to_csv(save_fn)


    return seed_ids
    

def seed_in_scc(in_data,out_data):
    random.seed()
    id_to_index = {}
    index_to_id = {}
    counter = 0

    # go through dictioanries of in, out seeds
    for n in in_data:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1

    for n in out_data:
        if n not in id_to_index:
            id_to_index[n] = counter
            index_to_id[counter] = n
            counter += 1


    # convert id values to 0-vertex_amount
    mod_in_data = {}
    for d in in_data:
        x = in_data[d]
        new_d = id_to_index[d]
        mod_in_data[new_d] = {}
        for s in x:
            new_s = id_to_index[s]
            mod_in_data[new_d][new_s] = x[s]

    mod_out_data = {}
    for s in out_data:
        x = out_data[s]
        new_s = id_to_index[s]
        mod_out_data[new_s] = {}
        for d in x:
            new_d = id_to_index[d]
            mod_out_data[new_s][new_d] = x[d]
    # now, create graph
    G = nx.DiGraph()
    for d in mod_in_data:
        x = mod_in_data[d]
        for s in x:
            weight_val = mod_in_data[d][s]

    for s in mod_out_data:
        x = mod_out_data[s]
        for d in x:
            weight_val = mod_out_data[s][d]
            G.add_edge(s,d,weight=weight_val)


    # go through all the strongly connected components of graph
    comp_amount = 0
    for _ in nx.strongly_connected_components(G):
        comp_amount += 1
    largest = (max(nx.strongly_connected_components(G), key=len))
    id_largest = [x for x in largest]
    all_ids = [str(index_to_id[i]) for i in id_largest]

    return all_ids
