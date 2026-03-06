import pandas as pd
import numpy as np
import glob as glob
import copy
import csv
import os

"""
    Creates adjacency matrix via nested dictionaries 
    d_values (key:seed, value -> dictionary of sent_values)
        dict of sent_values (key:sent: value -> 1/0)
        1 -> sentinel protects 
    returns dict{(sent,seed)} = set(protected_labels)
"""
def create_I_matrix(folder):
    all_filepaths = glob.glob(folder)
    fp_name = 0
    max_sent_for_seed = {}
    for seed_path in all_filepaths:
        seed_dict = {}
        with open(seed_path, mode='r') as f:
           reader = csv.DictReader(f) # Reads row by row
           for row in reader:
               key = (int(row['sent']),int(row['seed']))
               label = int(row["lab"])
               if key not in seed_dict:
                   seed_dict[key] = set()
               seed_dict[key].add(label)
        # now, immediately find best sentinel
        # for a seed
        for (sent_val,seed_val) in seed_dict:
            tup_val = (sent_val,seed_val)
            num_saved = len(seed_dict[tup_val])
            if seed_val not in max_sent_for_seed or num_saved > max_sent_for_seed[seed_val][0]:
                max_sent_for_seed[seed_val] = (num_saved,[sent_val])
            elif num_saved ==  max_sent_for_seed[seed_val][0]:
                max_sent_for_seed[seed_val][1].append(sent_val)
        seed_dict.clear()
        del seed_dict
        fp_name += 1
        print(fp_name)

    print("read all values!")

    best_sent = {}

    for seed_val in max_sent_for_seed:
        max_ids = max_sent_for_seed[seed_val][1]
        for m in max_ids:
            if m not in best_sent:
                best_sent[m] = set()
            best_sent[m].add(seed_val)
    del max_sent_for_seed
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
            if s not in greedy_sents:
                sent_labels =  best_sent[s]
                num_saved = len(sent_labels.difference(saved_labels))
                if num_saved > max_saved:
                    max_saved = num_saved
                    best_id = s
        saved_labels = saved_labels.union(best_sent[best_id])
        if best_id == "":
            break
        greedy_add.append(max_saved)
        greedy_sents.add(best_id)
        counter += 1
         
    return list(greedy_sents),greedy_add



            
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
    lab_folder= "data/y_lab/*.csv"
    year_fn= "data/y_cent.csv"
    year_dat = "data_y_real.csv"
    I_title = "best_I_greedy.csv"
    seed_data,sent_data = set(),set()
#    with open(year_dat,mode='r') as file:
#        csvFile = csv.DictReader(file)
#        for lines in csvFile:
#           sent_data.add(lines["sent"]) 
#           seed_data.add(lines["seed"]) 
#    sent_data = set(pd.read_csv(year_dat)["sent"])
#    seed_data = set(pd.read_csv(year_dat)["seed"])
    num_add = 50
    seed_dict = create_I_matrix(lab_folder)
    sent_id,b_id,add_amount,total = [],[],[],[]
    greedy_sents,greedy_add = greedy_I(seed_dict,num_add,seed_data)
    all_dict = {"sent_id":greedy_sents,"add_amount":greedy_add}
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(I_title)

    add_total = 0
    cent_types = ["d","w"]
    for c in cat_types:
        best_deg(year_fn,seed_dict,c,num_add)
