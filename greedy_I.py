import pandas as pd
import numpy as np
import glob as glob
import os

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
def avg_infec(fn):
    sent_data = pd.read_csv(fn)
    sent_vals = list(sent_data["sent"])
    seed_vals = list(sent_data["seed"])
    di_vals = list(sent_data["d_i"])
    dc_vals = list(sent_data["d_c"])
    os_vals = [di_vals[i] + dc_vals[i] for i in range(0,len(di_vals))]

    
    all_avg = {}
    for i in range(0,len(sent_vals)):
        sentinel = sent_vals[i]
        all_avg[sentinel] = []
    for i in range(0,len(sent_vals)):
        sentinel = sent_vals[i]
        seed = seed_vals[i]
        d_i = di_vals[i]
        o_s = os_vals[i]
        if o_s > 0:
            all_avg[sentinel].append(d_i/o_s)
        else:
            all_avg[sentinel].append(0)

    for s in all_avg:
        all_avg[s] = np.mean(all_avg[s])


    return all_avg



"""
For every sentinel, find the nodes that work best 
that generate the largest increase in node coverage
per node
"""
def greedy_avg_infec(fn,num_add):
    
    best_add = {}
    avg_I = avg_infec(fn)
    # start with largest I value
    best_I = 0 
    all_labels = set()
    for i in avg_I:
        if avg_I[i] > best_I:
            full_size = avg_I[i]
            best_I = i
            best_id = i

    greedy_set = set()
    greedy_set.add(best_id)
    k = full_size
    best_add[1] = (best_id,k)
    avg_amount = 0
    for i in range(2,num_add+1):
        k = 0
        for j in avg_I:
            if j not in greedy_set:
                j_df = avg_I[j]
                best_increase = j_df - avg_amount
                if best_increase> k:
                    k = best_increase
                    best_id = j
        #all_labels = temp_labels
        greedy_set.add(best_id)
        best_add[i] = (best_id,k)
    return best_add
            
def best_deg(fn,cent_type,num_add):

    year_cent = "data/y_cent.csv"
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
    for t in top_ids:
        if counter < num_add:
            avg_I = I_dict[t]
            add_amount = 0
            if avg_I > old_avg:
                add_amount = avg_I - old_avg
                old_avg = avg_I
            all_total.append(old_avg)
            all_unique.append(add_amount)
            all_ids.append(t)
            counter += 1
        else:
            break
    print(len(all_ids))
    print(len(all_ids))
    print(len(all_total))
    all_dict = {"sent_id":all_ids,"add_amount":all_unique,"old_T":all_total}
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(cent_title)
    return all_df

def find_label_dict(lab_folder):
    files = glob.glob(lab_folder+"/*.csv")
    for file in os.listdir(lab_folder):
        fp = lab_folder + file
        lab_df = pd.read_csv(fp)
        indv_sent = list(lab_df["sent"])[0]
        all_labs = list(lab_df["lab"])
if __name__ == "__main__":
    year_fn = "data/data_y_real.csv"
    lab_folder= "data/y_lab/"
    num_add = 10
    #lab_dict = find_label_dict(lab_folder)
    add_dict = greedy_avg_infec(year_fn,num_add)
    print("first infection")
    sent_id,b_id,add_amount,total = [],[],[],[]
    add_total = 0
    cent_type = "w"
    add_deg_df = best_deg(year_fn,cent_type,num_add)
    for num in add_dict:
        add_id = add_dict[num][0]
        add_val = add_dict[num][1]
        sent_id.append(add_id)
        add_amount.append(add_val)
        add_total += add_val
        print(num)
        total.append(add_total)
    ## create dictionary
    all_dict = {"sent_id":sent_id,"add_amount":add_amount,"old_T":total}
    dict_title = "best_I_greedy.csv"
    # now, lets just blind add best degree
    all_df = pd.DataFrame(all_dict)
    all_df.to_csv(dict_title)







