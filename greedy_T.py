import pandas as pd
import numpy as np
import glob as glob
import copy
import os
import csv

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
def find_time_dict(fn):
    with open(fn) as csvfile:
        reader = csv.DictReader(csvfile) # Reads row by row
        all_ids = {}
        counter = 0
        for row in reader:
            sent_val = int(row["sent"])
            seed_val = int(row["seed"])
            dt_val = row["d_t"]
            dc_val = row["d_c"]
            if dc_val == 0 and dt_val == 0:
                continue
            if seed_val not in all_ids or dt_val < all_ids[seed_val][0]:
                all_ids[seed_val] = [dt_val,set()]
            if dt_val == all_ids[seed_val][0]:
                all_ids[seed_val][1].add(sent_val)
    best_ids = {}
    for s in all_ids:
        best_sents = all_ids[s][1]
        for b in best_sents:
            if b not in best_ids:
                best_ids[b] = set()
            best_ids[b].add(s)
    del all_ids
        
    return best_ids
"""
every seed has an associated
sentinel that detects it earliest
add tolerance band maybe - fastest x% 
"""
def greedy_T(seed_dict,num_add):
    pair_vals = list(seed_dict.keys())

    n = 0
    total = 0
    best_T,best_id = 0,""
    temp_total = total
    final_dict = {}
    curr_set,total_add = set(),list()
    for l in seed_dict:
        num_saved = len(seed_dict[l])
        if num_saved > best_T:
            best_T = num_saved
            best_id = l
    curr_set.add(best_id)
    saved_labs = seed_dict[best_id]
    total_add.append(best_T)
    n = 1
    while n < num_add:
        best_increase,best_add = 0,""
        for l in seed_dict:
            b = seed_dict[l]
            lab_saved = len(b.difference(saved_labs))
            if l not in curr_set and lab_saved > best_increase:
                best_increase=lab_saved
                best_add = l
        if best_increase == 0:
            break
        saved_labs = saved_labs.union(seed_dict[best_add])
        curr_set.add(best_add)
        total_add.append(best_increase)
    final_dict["sent_id"] = list(curr_set)
    final_dict["add_amount"] = total_add
    return final_dict



            
def best_deg(fn,seed_dict,cent_type,num_add):

    cent_title = cent_type+"_T_add.csv"
    cent_df = pd.read_csv(fn)
    cent_df = cent_df.sort_values(by=[cent_type],ascending=False)

    top_vals = cent_df.head(num_add)
    top_ids = list(top_vals["node_id"])

    greedy_labs = set()
    all_ids,all_unique,all_total= list(),list(),list()
    total = 0
    for t in top_ids:
        # how often are top-ids 
        # best sentinels? 
        prot_labs = (seed_dict[t])
        num_increase = len(prot_labs) - len(greedy_labs)
        greedy_labs = prot_labs.union(greedy_labs)
        total += num_increase
        all_unique.append(num_increase)
        all_ids.append(t)
        all_total.append(total)
    all_dict = {"sent_id":all_ids,"add_amount":all_unique,"old_T":all_total}
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(cent_title)
    return all_df

if __name__ == "__main__":
    fn = "data_y_real.csv"
    cent_fn = "data/y_cent.csv"
    num_add = 50
    time_dict = find_time_dict(fn)
    greedy_dict = greedy_T(time_dict,num_add)
    add_total = 0
    cent_type = "d"
    add_deg_df = best_deg(cent_fn,time_dict,cent_type,num_add)
    dict_title = "best_T_greedy.csv"
    greedy_df = pd.DataFrame(greedy_dict)
    greedy_df.to_csv(dict_title)







