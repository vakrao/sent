import pandas as pd
import numpy as np
import glob as glob
import copy
import os


"""
Return the id-values of all seeds associated with a sentinel
"""
def create_F_matrix(fn):
    sent_data = pd.read_csv(fn)
    sent_vals = list(sent_data["sent"])
    seed_vals = list(sent_data["seed"])
    df_vals = list(sent_data["d_f"])
    all_ids = {}
    for i in range(0,len(sent_vals)):
        sentinel = sent_vals[i]
        all_ids[sentinel] = set()
    for i in range(0,len(sent_vals)):
        sentinel = sent_vals[i]
        seed = seed_vals[i]
        d_f = df_vals[i]
        if d_f == 1:
            all_ids[sentinel].add(seed)
    
    return all_ids

"""
    Creates adjacency matrix via nested dicitonaries
    diciontary of seed_values (key:seed, value -> dictionary of sent_values)
        dict of sent_values (key:sent: value -> 1/0)
        1 -> sentinel protects 
    returns dict{(sent,seed)} = set(protected_labels)
"""
def create_I_matrix(folder):
    folder = folder+"*.csv"
    all_filepaths = glob.glob(folder)
    seed_dict = {}
    for seed_path in all_filepaths:
        sent_data = pd.read_csv(seed_path)
        # for each seed, 2-d matrix of sent-label values
        all_sents = set(sent_data["sent"])
        all_nodes = set(sent_data["seed"])
        for i in all_sents:
            for j in all_nodes:
                seed_dict[(i,j)] = list()
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
    for seed_val in all_nodes:
        max_val,max_id = 0,"hi"
        for sent_val in all_sents:
            if((sent_val,seed_val) in seed_dict):
                if len(seed_dict[(sent_val,seed_val)]) > max_val:
                    max_val = len(seed_dict[(sent_val,seed_val)])
                    max_id = sent_val
        id_vals = []
        for sent_val in all_sents:
            if len(seed_dict[(sent_val,seed_val)]) ==  max_val:
                id_vals.append(sent_val)
        for i in id_vals:
            if i not in best_sent:
                best_sent[i] = set()
            best_sent[i].add(seed_val)
    for val in all_nodes:
        if val not in best_sent:
            best_sent[val] = []
    return best_sent

def find_F(curr_set,label_dict):

    full_size = 0 
    best_id = 0
    det_labs = set()
    for c in curr_set:
        if c in label_dict:
            l = set(label_dict[c])
            det_labs = det_labs.union(l)

    unq_F = 0 
    unq_id = 0
    unq_add = {}
    for node in label_dict:
        node_lab = set(label_dict[node])
        unq_nodes = node_lab.difference(det_labs)
        unq_add[node] = unq_nodes

    return unq_add

def find_I(curr_set,seed_dict):
    # start with largest F value
    full_size = 0 
    best_id = 0
    det_labs = set()
    for c in curr_set:
        if c in seed_dict:
            l = set(seed_dict[c])
            det_labs = det_labs.union(l)
    unq_id = 0
    unq_add = {}
    for node in seed_dict:
        node_lab = set(seed_dict[node])
        unq_nodes = node_lab.difference(det_labs)
        unq_add[node] = unq_nodes
    return unq_add

def find_U(num_add,node_ids,alpha,F_dict,I_dict):

    curr_set = set()
    node_ids = set([n for n in node_ids])
    counter = 0
    f_sav,i_sav,u_sav = [],[],[]
    max_u,max_id = 0,""
    temp_f,temp_i = 0,0
    f_set,i_set = set(),set()
    f_lab,i_lab = set(),set()
    temp_i,temp_f = 0,0
    for node_id in node_ids:
        F_val,I_val = 0,0
        if(node_id in unq_F):
            F_val = len(F_dict[node_id])
            f_set = F_dict[node_id]
            f_lab =  F_dict[node_id]
        if(node_id in unq_I):
            I_val = len(unq_I[node_id])
            i_set = I_dict[node_id]
            i_lab = I_dict[node_id]
        u_val = alpha*(F_val) + (1.0-alpha)*(I_val)
        if u_val > max_u and (node_id not in curr_set):
            max_u = u_val
            max_id = node_id
            if node_id in unq_F:
                temp_f = len(F_dict[node_id])
            if node_id in unq_I:
                temp_i = len(I_dict[node_id])
    curr_set.add(max_id)
    if max_id in node_ids:
        node_ids.remove(max_id)
    f_sav.append(temp_f)
    i_sav.append(temp_i)
    u_sav.append(max_u)
    counter +=1 

    while counter < num_add:
        max_u,max_id = 0,""
        temp_i,temp_f = 0,0
        for node_id in node_ids:
            if node_id not in curr_set:
                F_diff,I_diff = 0,0
                F_val,I_val = 0,0
                if(node_id in F_dict):
                    F_diff = F_dict[node_id].difference(f_lab)
                    F_val = len(F_diff)
                if(node_id in I_dict):
                    I_diff = I_dict[node_id].difference(i_lab)
                    I_val = len(I_diff)
                u_val = alpha*(F_val) + (1.0-alpha)*(I_val)
                if u_val > max_u:
                    max_u = u_val
                    max_id = node_id
                    temp_f = len(F_diff)
                    temp_i = len(I_diff)
        if max_id != "":
            f_lab = f_lab.union(F_dict[max_id])
            i_lab = i_lab.union(I_dict[max_id])
            curr_set.add(max_id)
            if max_id in node_ids:
                node_ids.remove(max_id)
            print(temp_f)
            print(temp_i)
            f_sav.append(temp_f)
            i_sav.append(temp_i)
            u_sav.append(max_u)
        else:
            break
        counter +=1 


    save_dict = {"u_set":list(curr_set),"F":f_sav,"I":i_sav,"U":u_sav}
    return save_dict



if __name__ == "__main__":
    year_fn = "data_y_real.csv"
    lab_folder= "data/y_lab/"
    node_ids = pd.read_csv(year_fn)
    node_ids = set(node_ids["sent"])
    num_add,alpha = 20,0
    alphas = [1]
    F_dict = create_F_matrix(year_fn)
    I_dict = create_I_matrix(lab_folder)
    for a in alphas:
        save_dict = find_U(num_add,node_ids,a,F_dict,I_dict)
        dict_title = "best_U_"+str(a)+".csv"
        # now, lets just blind add best degree
        all_df = pd.DataFrame(save_dict)
        all_df.to_csv(dict_title)







