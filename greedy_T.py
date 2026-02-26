import pandas as pd
import numpy as np
import glob as glob
import copy
import os

"""
    Creates adjacency matrix via nested dicitonaries
    diciontary of seed_values (key:seed, value -> dictionary of sent_values)
        dict of sent_values (key:sent: value -> 1/0)
        1 -> sentinel protects 
    returns dict{(sent,seed)} = set(protected_labels)
"""

"""
Return the id-values of all seeds associated with a sentinel
"""
def choose_metric(fn,m):
    metrics = {"I":"d_c","F":"d_f","T":"d_t"}
    sent_data = pd.read_csv(fn)
    sent_vals = list(sent_data["sent"])
    seed_vals = list(sent_data["seed"])
    seed_ids = set(sent_data["seed"])
    sent_ids = set(sent_data["sent"])
    dt_vals = list(sent_data[metrics[m]])
    all_ids = {}
    for id_val in sent_ids:
        all_ids[id_val] = {'d_T':float('inf'),'sent_id':1}
    for i in range(0,len(sent_vals)):
        if (dt_vals[i] > 0 and (seed_vals[i] != sent_vals[i])):
            if all_ids[seed_vals[i]] > dt_vals[i]:
                all_ids[seed_vals[i]] = {'d_T':dt_vals[i],'sent_id':sent_vals[i]}
    return all_ids
"""
Return the id-values of all seeds associated with a sentinel
"""
def greedy_T(seed_dict,num_add):
    pair_vals = list(seed_dict.keys())
    all_sents,all_nodes = set(),set()
    for p in pair_vals:
        all_sents.add(p[0])
        all_nodes.add(p[1])

    best_sent = {}

    for seed_val in seed_dict:
        best_sent[seed_dict[seed_val]['sent_id']] = set()
    
    best_sent = {}
    for seed_val in seed_dict:
        max_val,max_id = 0,"hi"
        min_pair = seed_dict[seed_val]
        best_sent[min_pair['sent_id']].append(seed_val)

    # now, choose best-sentinel
    max_val,max_id = 0,"hi"
    for b in best_sent:
        most_vals = len(best_sent[b])
        if most_vals > max_val:
            max_val = most_vals
            max_id = b
    # pick sentinles that protect
    # most seeds
    greedy_set = best_sent[max_id]
    nodes_left = all_nodes - greedy_set
    greedy_sents = set()
    greedy_sents.add(max_id)
    # now, need to find
    # sentinels that best cover other seeds 

    greedy_add = list()
    greedy_add.append(len(greedy_set))
    counter = 1
    # find associated best-sentinel
    # value with each seed 
    # and count the increase  in 
    # seed-ids associated with each seed
    while counter < num_add:
        best_sent = {}
        for seed_val in nodes_left:
            max_val,max_id = 0,"hi"
            for sent_val in all_sents:
                if( (sent_val,seed_val) in seed_dict):
                    if len(seed_dict[(sent_val,seed_val)]) > max_val:
                        max_val = len(seed_dict[(sent_val,seed_val)])
                        max_id = sent_val
            if max_id != "hi":
                if max_id not in best_sent:
                    best_sent[max_id] = set()
                best_sent[max_id].add(seed_val)

        max_val,max_id = 0,"hi"
        for b in best_sent:
            most_vals = len(best_sent[b])
            if most_vals > max_val:
                max_val = most_vals
                max_id = b
        greedy_set = greedy_set.union(best_sent[max_id])
        
        greedy_sents.add(max_id)
        nodes_old = len(nodes_left)
        # seed nodes left to protect
        # are ones that greedy set still
        # does not cover
        nodes_left = all_nodes-greedy_set
        nodes_add = nodes_old - len(nodes_left)
        greedy_add.append(nodes_add)
        counter += 1
         
    return greedy_sents,greedy_add



            
def best_deg(fn,seed_dict,cent_type,num_add):

    cent_title = cent_type+"_I_add.csv"
    I_dict = avg_infec(fn)
    cent_df = pd.read_csv(year_cent)
    cent_df = cent_df.sort_values(by=[cent_type],ascending=False)

    top_vals = cent_df.head(num_add)
    top_ids = list(top_vals["node_id"])
    all_labs = set()
    all_unique,all_total = [],[]
    old_avg = 0
    counter = 0
    all_ids = []
    sent_

    pair_vals = list(seed_dict.keys())
    all_sents,all_nodes = set(),set()
    for p in pair_vals:
        all_sents.add(p[0])
        all_nodes.add(p[1])

    for y in all_sents:
        best_sent[y] = set()
    
    for seed_val in all_nodes:
        max_val,max_id = 0,"hi"
        for sent_val in all_sents:
            if((sent_val,seed_val) in seed_dict):
                if len(seed_dict[(sent_val,seed_val)]) > max_val:
                    max_val = len(seed_dict[(sent_val,seed_val)])
                    max_id = sent_val
        if max_id != "hi":
            best_sent[max_id].add(seed_val)

    greedy_labs = set()
    all_ids,all_unique,all_total= list(),list(),list()
    total = 0
    for t in top_ids:
        # how often are top-ids 
        # best sentinels? 
        prot_labs = best_sent[t]
        num_increase = len(prot_labs - greedy_labs)
        greedy_labs = prot_labs.union(greedy_labs)
        total += num_increase
        all_unique.append(num_increase)
        all_ids.append(t)
        all_total.append(total)
    print(len(all_ids))
    print(len(all_ids))
    print(len(all_total))
    all_dict = {"sent_id":all_ids,"add_amount":all_unique,"old_T":all_total}
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(cent_title)
    return all_df

if __name__ == "__main__":
    lab_folder= "data/y_lab/*.csv"
    num_add = 20
    seed_dict = create_seed_matrix(lab_folder)
    sent_id,b_id,add_amount,total = [],[],[],[]
#    greedy_sents,greedy_add = greedy_I(seed_dict,num_add)
    add_total = 0
    cent_type = "d"
    year_fn= "data/y_cent.csv"
    add_deg_df = best_deg(year_fn,seed_dict,cent_type,num_add)
    #for num in add_dict:
    #    add_id = add_dict[num][0]
    #    add_val = add_dict[num][1]
    #    sent_id.append(add_id)
    #    add_amount.append(add_val)
    #    add_total += add_val
    #    print(num)
    #    total.append(add_total)
    ## create dictionary
#    all_dict = {"sent_id":list(greedy_sents),"add_amount":list(greedy_add)}
#    dict_title = "best_I_greedy.csv"
    # now, lets just blind add best degree
#    all_df = pd.DataFrame(all_dict)
#    all_df.to_csv(dict_title)







