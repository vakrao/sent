import pandas as pd
import numpy as np

def classify_comms():

    A = {}
    # (row is sentinel)
    # (col is seed)
    for i in seed:
        for j in seed:
            f_val = F[i][j]
            i_val = I[i][j]
            t_val = T[i][j]
            tensor = [f_val,i_val,t_val]
            A[(i,j)] = tensor
    return A


"""
Return the id-values of all seeds associated with a sentinel
"""
def choose_freq(fn):
    sent_data = pd.read_csv(fn)
    sent_vals = list(sent_data["sent"])
    seed_vals = list(sent_data["seed"])
    df_vals = list(sent_data["d_f"])
    all_ids = {}
    for i in range(0,len(sent_vals)):
        sentinel = sent_vals[i]
        all_ids[sentinel] = []
    for i in range(0,len(sent_vals)):
        sentinel = sent_vals[i]
        seed = seed_vals[i]
        d_f = df_vals[i]
        if d_f == 1:
            all_ids[sentinel].append(seed)

    return all_ids


"""
For every sentinel, find the nodes that work best 
that generate the largest increase in node coverage
per node
"""
def greedy_freq(fn,num_add):

    
    best_add = {}
    label_dict = choose_freq(fn)
    # start with largest F value
    full_size = 0 
    best_id = 0
    all_labels = set()
    for i in label_dict:
        if len(label_dict[i]) > full_size:
            full_size = len(label_dict[i])
            all_labels = set(label_dict[i])
            best_id = i

    greedy_set = set()
    greedy_set.add(best_id)
    full_size = len(all_labels)
    k = full_size
    best_add[1] = (best_id,k)
    for i in range(2,num_add):
        best_id = 0
        k = 0
        for j in label_dict:
            if j not in greedy_set:
                j_df = set(label_dict[j])
                unique_add = all_labels.union(j_df)
                num_unique = len(unique_add) - len(all_labels)
                if num_unique > k:
                    k = num_unique
                    temp_labels = unique_add
                    best_id = j
        all_labels = temp_labels
        greedy_set.add(best_id)
        best_add[i] = (best_id,k)
    return best_add
            
if __name__ == "__main__":
    year_fn = "data/data_y_real.csv"
    all_sents = choose_freq(year_fn)
    num_add = 100
    add_dict = greedy_freq(year_fn,num_add)
    sent_id,b_id,add_amount,total = [],[],[],[]
    add_total = 0
    for num in add_dict:
        add_id = add_dict[num][0]
        add_val = add_dict[num][1]
        sent_id.append(add_id)
        add_amount.append(add_val)
        add_total += add_val
        total.append(add_total)
    ## create dictionary
    all_dict = {"sent_id":sent_id,"add_amount":add_amount,"old_T":total}
    dict_title = "best_y_greedy.csv"
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(dict_title)







