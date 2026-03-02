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
def find_time_dict(fn):
    sent_data = pd.read_csv(fn)
    sent_vals = list(sent_data["sent"])
    seed_vals = list(sent_data["seed"])
    seed_ids = set(sent_data["seed"])
    sent_ids = set(sent_data["sent"])
    dt_vals = list(sent_data["d_t"])
    all_ids = {}
    for id_val in seed_ids:
        all_ids[id_val] = {'d_t':float('inf'),'sent_id':set()}
    for i in range(0,len(sent_vals)):
        if float(dt_vals[i]) > 0) and (str(seed_vals[i]) != str(sent_vals[i])):
            if float(all_ids[seed_vals[i]]["d_t"]) > float(dt_vals[i]):
                all_ids[seed_vals[i]]['d_t'] = dt_vals[i]
    for i in range(0,len(sent_vals)):
        if float(dt_vals[i]) > 0) and (str(seed_vals[i]) != str(sent_vals[i])):
            if float(all_ids[seed_vals[i]]["d_t"]) == float(dt_vals[i]):
                # every seed has a best associated sentinel
                all_ids[seed_vals[i]]['d_t'] = float(dt_vals[i])
                all_ids[seed_vals[i]]['sent_id'].add(sent_vals[i])
    best_ids = {}
    for s in seed_ids:
        best_ids[s] = set()
    for s in seed_ids:
        best_sents = all_ids[s]['sent_id']
        for b in best_sents:
            best_ids[b].add(s)
        
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
    saved_labs = set(seed_dict[l])
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
        curr_set.add(best_add)
        total_add.append(best_increase)
    final_dict["best_ids"] = list(curr_set)
    final_dict["best_add"] = total_add
           
    return final_dict



            
def best_deg(fn,seed_dict,cent_type,num_add):

    cent_title = cent_type+"_T_add.csv"
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
    lab_folder= "data_y_real.csv"
    num_add = 20
    time_dict = find_time_dict(lab_folder)
    greedy_dict = greedy_T(time_dict,num_add)
    add_total = 0
    cent_type = "d"
#    add_deg_df = best_deg(year_fn,seed_dict,cent_type,num_add)
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
    dict_title = "best_T_greedy.csv"
    greedy_df = pd.DataFrame(greedy_dict)
    greedy_df.to_csv(dict_title)







