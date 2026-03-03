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
def create_seed_matrix(folder,sent_ids,seed_ids):
    all_filepaths = glob.glob(folder)
    seed_dict = {}
    for i in sent_ids:
        for j in seed_ids:
            seed_dict[(i,j)] = list()
    # go through all seeds,sent pairs
    for seed_path in all_filepaths:
        sent_data = pd.read_csv(seed_path)
        all_sents = sent_ids
        all_nodes = seed_ids
        x,y,z = list(sent_data["sent"]),list(sent_data["seed"]),list(sent_data["lab"])
        old_sent,old_seed = x[0],y[0]
        count_labs = list()
        for i in range(0,len(x)):
            sent_det,lab_prot = x[i],y[i]
            if old_sent == sent_det and old_seed == lab_prot: 
                count_labs.append(z[i])
            else:
                seed_dict[(old_sent,old_seed)] = copy.deepcopy(count_labs)
                count_labs = [z[i]]
            old_sent,old_seed = sent_det,lab_prot

    best_sent = {}
    # find every sentinels associated seeds
    for seed_val in seed_ids:
        max_val,max_id = 0,"hi"
        valid_sents = {}
        for sent_val in sent_ids:
            if((sent_val,seed_val) in seed_dict):
                num_saved = len(seed_dict[(sent_val,seed_val)]) 
                if num_saved > max_val:
                    max_val = num_saved
                    max_id = sent_val
                    if max_val in valid_sents:
                        valid_sents[max_val].append(max_id)
                    else:
                        valid_sents[max_val] = [max_id]

        if max_id != "hi":
            max_ids = valid_sents[max_val]
            for m in max_ids:
                if m in best_sent:
                    best_sent[m].add(seed_val)
                else:
                    best_sent[m] = set(seed_val)
    return best_sent
"""
Return the id-values of all seeds associated with a sentinel
"""
def greedy_I(best_sent,num_add,seed_ids):
    all_nodes = seed_ids
    # now, choose best-sentinel
    max_val,max_id = 0,"hi"
    for b in best_sent:
        most_vals = len(best_sent[b])
        if most_vals > max_val:
            max_val = most_vals
            max_id = b
    # pick sentinels that protect
    # most seeds
    greedy_set = best_sent[max_id]
    greedy_sents = set()
    greedy_sents.add(max_id)
    # now, need to find
    # sentinels that best cover other seeds 

    greedy_add = list()
    greedy_add.append(len(greedy_set))
    saved_labels = best_sent[max_id]
    counter = 1
    # find associated best-sentinel
    # value with each seed 
    # and count the increase  in 
    # seed-ids associated with each seed
    while counter < num_add:
        num_saved,max_saved = 0,0
        best_id = ""
        for s in best_sent:
            best_labs = best_sent[s]
            num_saved = best_labs.difference(saved_labs)
            if num_saved > max_saved:
                max_saved = num_saved
                best_id = s
        if best_id == "":
            break
        greedy_add.append(max_saved)
        greedy_sents.add(best_id)
        counter += 1
         
    return list(greedy_sents),greedy_add



            
def best_deg(year_cent,seed_dict,cent_type,num_add):

    cent_title = cent_type+"_I_add.csv"
    cent_df = pd.read_csv(year_cent)
    cent_df = cent_df.sort_values(by=[cent_type],ascending=False)

    top_vals = cent_df.head(num_add)
    top_ids = list(top_vals["node_id"])
    all_labs = set()
    all_unique,all_total = [],[]
    old_avg = 0
    counter = 0
    all_ids = []
    best_sent = {}

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
    year_fn= "data/y_cent.csv"
    year_dat = "data_y_real.csv"
    I_title = "best_I_greedy.csv"
    sent_data = set(pd.read_csv(year_dat)["sent"])
    seed_data = set(pd.read_csv(year_dat)["seed"])
    num_add = 20
    seed_dict = create_seed_matrix(lab_folder,sent_data,seed_data)
    sent_id,b_id,add_amount,total = [],[],[],[]
    greedy_sents,greedy_add = greedy_I(seed_dict,num_add)

    add_total = 0
    cent_type = "d"
    all_dict = {"sent_id":greedy_sents,"add_amount":greedy_add}
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(I_title)
    #add_deg_df = best_deg(year_fn,seed_dict,cent_type,num_add)
