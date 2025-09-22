import numpy as np
import copy
import pandas as pd
from gen_heatmap import *

# days in each month 
days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}



def prune_i(full_i,all_t,T):
    clean_i = {}
    finished_i = []
    last_val = full_i[-1]
    if last_val > T:
        for i in range(0,len(full_i)):
            rounded_t = round(all_t[i])
            if rounded_t not in clean_i:
                clean_i[rounded_t] = [full_i[i]]  
            else:
                clean_i[rounded_t].append(full_i[i])
        for c in clean_i:
            clean_i[c] = np.max(clean_i[c])
        finished_i = list(clean_i.values())
        return finished_i
    else:
        finished_i = copy.deepcopy(full_i)
        for i in range(len(full_i),T):
            finished_i.append(full_i[-1])
    return finished_i



"""
clean_temp_shift 
Description: shortens daily infection list to create
monthly infection list. We strictly filter the daily infection based on the number of days in a month
Parameters: 
    i(list) - daily list of infections
    t_m(int) - lenght of list of real infections
    cal_month(int) - starting calendar month ID
    shifts(int) - determines how many months left shift occurs
Returns:
    shift_i (list) - aggregated monthly infections
    clean_t (list) - month associated with each shift
"""
def clean_temp_shift(i,t_m,cal_month,shifts):
    month_counter = 0
    shift_i = []
    curr_days = 0
    ord_count = cal_month
    assert(len(i) > 0 ),"Error: i is too small"
    while(month_counter < t_m):
        days_amount = days[ord_count]
        curr_days += days_amount
        assert(curr_days <= len(i)), f"Error: curr_days:{curr_days} is greater than length of i: {len(i)}"
        # this samples the cumulative value for the month
        month_value = i[curr_days-1]
        shift_i.append(month_value) 
        ord_count += 1
        if ord_count > 12:
            ord_count = 1
        month_counter += 1
    # pop out the shifts
    shift_i = shift_i[shifts:]
    clean_t = [i for i in range(0,len(shift_i))]
    return shift_i,clean_t

