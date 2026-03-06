import pandas as pd
import numpy as np
import glob as glob
import copy
import os
import csv


"""
Return the id-values of all seeds associated with a sentinel
"""
def create_F_matrix(fn):
    all_ids = {}
    with open(fn, mode='r') as f:
       reader = csv.DictReader(f) # Reads row by row
       for row in reader:
           sent_id = int(row['sent'])
           seed_id = int(row['seed'])
           d_f = row["d_f"]
           if sent_id not in all_ids:
               all_ids[sent_id] = set()
           if d_f == 1:
               all_ids[sent_id].add(seed)
    return all_ids

"""
    Creates adjacency matrix via nested dicitonaries
    diciontary of seed_values (key:seed, value -> dictionary of sent_values)
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

def find_U(num_add,alpha,F_dict,I_dict):

    curr_set = set()
    counter = 0
    f_sav,i_sav,u_sav = [],[],[]
    max_u,max_id = 0,""
    temp_f,temp_i = 0,0
    f_set,i_set = set(),set()
    f_lab,i_lab = set(),set()
    temp_i,temp_f = 0,0

    f_lab = set()#F_dict[max_id]
    i_lab = set()#I_dict[max_id]
    nodes = set(F_dict.keys()).union(set(I_dict.keys()))
    while counter < num_add:
        max_u,max_id = 0,""
        temp_i,temp_f = 0,0
        for node_id in nodes:
            F_diff,I_diff = set(),set()
            F_val,I_val = 0,0
            if node_id not in curr_set:
                if(node_id in F_dict):
                    F_diff = F_dict[node_id].difference(f_lab)
                    F_val = len(F_diff)/(len(nodes))
                if(node_id in I_dict):
                    I_diff = I_dict[node_id].difference(i_lab)
                    I_val = len(I_diff)/(len(nodes))
                u_val = alpha*(F_val) + (1.0-alpha)*(I_val)
                if u_val > max_u:
                    max_u = u_val
                    max_id = node_id
                    temp_f = F_diff
                    temp_i = I_diff
        if max_id != "":
            f_lab = f_lab.union(temp_f)
            i_lab = i_lab.union(temp_i)
            curr_set.add(max_id)
            if max_id in node_ids:
                node_ids.remove(max_id)
            f_sav.append(len(temp_f))
            i_sav.append(len(temp_i))
            u_sav.append(max_u)
        else:
            break
        counter +=1 
    save_dict = {"u_set":list(curr_set),"F":f_sav,"I":i_sav,"U":u_sav}
    return save_dict



if __name__ == "__main__":
    year_fn = "data_y_real.csv"
    lab_folder= "data/y_lab/*.csv"
    num_add,alpha = 20,0
    alphas = [1,0,0.2,0.4,0.6,0.8]
    F_dict = create_F_matrix(year_fn)
    I_dict = create_I_matrix(lab_folder)
    for a in alphas:
        save_dict = find_U(num_add,a,F_dict,I_dict)
        dict_title = "best_U_"+str(a)+".csv"
        # now, lets just blind add best degree
        all_df = pd.DataFrame(save_dict)
        all_df.to_csv(dict_title)







