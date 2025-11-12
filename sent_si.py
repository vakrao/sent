import csv
from tqdm import tqdm
import random
import copy
import numpy as np
from decimal import Decimal
from find_seeds import *
import math



def read_network_data (filename):
    in_bond = {}
    out_bond = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        for row in rows:
            if first_row > 0:
                s = (row[1])
                d = (row[2])
                w = row[3]
                if s == '0':
                    print("zero source value")
                if d == "0":
                    print("zero dest value")
                ##
                if d not in in_bond:
                    in_bond[d] = {}
                if s not in in_bond[d]:
                    in_bond[d][s] = float(0)
                in_bond[d][s] += float(w)
                ##
                if s not in out_bond:
                    out_bond[s] = {}
                if d not in out_bond[s]:
                    out_bond[s][d] = float(0)
                out_bond[s][d] += float(w)
                ##
            first_row = 1
    # now, let's pass in in_bond
    # and out_bond to prune G
    _,real_in_bond,real_out_bond = create_network(in_bond,out_bond)


    return real_in_bond,real_out_bond

#####
def read_property_data (filename):

    prop_size = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        for row in rows:
            if first_row > 0:
                i = (row[0])
                s = (1.0)
                if len(row[3])>0:
                    s = float(row[3])
                prop_size[i] = float(s)
            first_row = 1

    return prop_size



########

### tau = 365 
### (each week to give some number of infections) 
### 


"""
   Find time increment dt for each node n
    PARAMTERS
    min_value: float of minimum time increment
    state: dictionary of level of infections of nodes N
    in_bond: dictionary of dictionaries
"""
def determine_time_increment (min_value,state, in_bond, beta_bet, beta_wit,tau=365):

    min_inc = min_value
    for n in state:
        if state[n] < 1.0 and n in in_bond:
            tmp = (0)
            for m in in_bond[n]:
                init_mult =(in_bond[n][m]/tau) * state[m] 
                tmp += init_mult
            sus = (1.0-state[n]) 
            tmp = tmp * beta_bet * sus
            tmp = tmp + (beta_wit * state[n]*sus)
            if tmp > 0:
                frac = sus / tmp
                if min_inc > frac:
                    min_inc = frac
    return min_inc


#####


"""
   Find new level of infection I_n for each node n 
   PARAMTERS
    old_state: dictionary of level of infections of nodes N
    in_bond: dictionary of dictionaries
        key: String node id n
        values: dictionary of incoming nodes K to node n, with weights of movements m for each node k 
    prop_size: dictionary of property sizes
    F: number of plants per hectare
    beta_bet: float of b_b param
    beta_wit: float of b_w param
    dt: float of time increment
"""
def compute_variation (old_state, in_bond,prop_size, beta_bet, beta_wit, dt,F,tau):
    new_state = {}
    
    for n in old_state:
        if old_state[n] < 1.0:
            bet_pct = (0)
            all_cont = (0)
            if n in in_bond:
                for m in in_bond[n]:
                    if m != n and old_state[m] > 0.0:
                        a_ij = (in_bond[n][m])
                        cont_val = (a_ij * (old_state[m]))/(tau*1.0)
                        all_cont += cont_val
            sus = (1.0 - old_state[n])
            bet_pct = all_cont*(beta_bet)*sus
            min_infec = (1/(F*prop_size[n]))
            # minimum amount to infect one plant
            if bet_pct < min_infec:
                bet_pct = 0
            wit_pct = (beta_wit) * (old_state[n])*sus
            total = float(wit_pct + bet_pct)
            new_val = float((old_state[n]) + (total * dt))
            # check if infection exceeds minimum infection
            # threshold for individaul farm
            new_state[n] = min(1.0,max(0,new_val))
        else:
            new_state[n] = float(1.0)

    return new_state



def update_sent_stats(state, time, D, T, d_t,d_i):

    infected_farms = 0
    new_infec = set()
    new_t,new_i = copy.deepcopy(d_t),copy.deepcopy(d_i)
    for n in state:
        if state[n]  > D:
            infected_farms += 1.0
            if n not in d_i:
                continue
            if d_t[n] == 0 :
                new_t[n] = time
                new_infec.add(n)
    # go through all newly-infected farms, and update d_i
    for n in new_infec:
        if n in d_i:
            new_i[n] = infected_farms

    return new_t,new_i,infected_farms



"""
reference for months associated with seasons
    # for seasonal variation
    sum_monts = ["12","01","02"]
    aut_months = ["03","04","05"]
    wint_months = ["06","07","08"]
    spring_months = ["09","10","11"]
"""
"""
    deltaT = 1 or 3 or 12
    init_seed = amount to initialize seed at start
"""
def sent_si_model (in_bond, out_bond,net_file, prop_size, b_b, b_w, D, seeds, T, max_infected,deltaT,min_inc,alpha,F,init_month):

    s_name = ["SM","AT","WT","SP"]
    days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    #season = {1:"SM",2:"SM",3:"AT",4:"AT",5:"AT",6:"SP",7:"SP",8:"SP",9:"WT",10:"WT",11:"WT",12:"SM"}
    season = {12:"SM",1:"SM",2:"SM",
              3:"AT",4:"AT",5:"AT",
              6:"WT",7:"WT",8:"WT",
              9:"SP",10:"SP",11:"SP"}
    ##initialize state based on all properties 
    state = {}
    x, y, z = [], [], []
    d_c, d_i,d_t,d_f = {},{},{},{}
    i_inf = 0
    month_counter = 0 
    day_counter = 1
    curr_month = init_month
    curr_month_amount = days[init_month]
    file_ending = "_2022.csv"
    tau = deltaT*30

    # choose network based on tau setting
    if deltaT == 1:
        if net_file == "horticulture365.csv":
            folder = "params/month_tau/"
        else:
            folder = "params/new_month_tau/"
        if curr_month < 10:
            tau_string = "0"+str(curr_month)
        else: 
            tau_string = str(curr_month)
    if deltaT == 3:
        if net_file == "horticulture365.csv":
            folder = "params/season_tau/"
        else:
            folder = "params/new_season_tau/"

        tau_string = season[curr_month]
    if deltaT == 12:
        folder = ""
        tau_string = net_file
        file_ending = ""
        tau = 365

    if isinstance(seeds,list) == False:
        seeds = [seeds]
    start_infec = 0
    ##state must be initialized from full network
    for n in in_bond:
        state[n] = float(0.0)
        if n not in seeds:  
            d_t[n] = 0
            d_c[n] = 0
            d_i[n] = start_infec
            d_f[n] = 0
    for n in out_bond:
        state[n]  = float(0.0)
        if n not in seeds:
            d_t[n] = 0
            d_c[n] = 0
            d_i[n] = start_infec
            d_f[n] = 0
    ##initial conditions
    for n in seeds:
        state[n] = float(alpha)
    tau_init_file = f"{folder}{tau_string}{file_ending}"
    #initial network based on first tau month
    in_bond, out_bond = read_network_data(tau_init_file)
    t = 0.0


    d_t,d_i,infected_farms = update_sent_stats(state, t, D,T, d_t,d_i)
    b_b = float(b_b)
    b_w = float(b_w)
    tau = float(tau)
    # minimum time increment for the model
    min_value = 1
    day_counter = 0
    if deltaT < 12:
        assert(curr_month == init_month)
        if deltaT == 3:
            if curr_month == 12 or curr_month == 1 or curr_month == 2:
                assert(tau_string == "SM")
            if curr_month == 3 or curr_month == 4 or curr_month == 5:
                assert(tau_string == "AT")
            if curr_month == 6 or curr_month == 7 or curr_month == 8:
                assert(tau_string == "WT")
            if curr_month == 9 or curr_month == 10 or curr_month == 11:
                assert(tau_string == "SP")
        if deltaT == 1:
            test_month = str(init_month)
            if curr_month < 10:
                test_month = "0"+str(init_month)
            assert(tau_string == str(test_month))
            
    while t < T and infected_farms < max_infected:
        old_state = copy.deepcopy(state)
        dt = determine_time_increment (min_value,old_state, in_bond, b_b, b_w,tau)
        t += dt
        day_counter += dt
        new_state= compute_variation (old_state, in_bond,prop_size, b_b, b_w, dt,F,tau)

        new_dt,new_di,infected_farms = update_sent_stats(new_state, t, D,T, d_t,d_i)
        d_t = new_dt
        d_i = new_di
        state = copy.deepcopy(new_state)
        new_state = {}
        if day_counter == curr_month_amount and deltaT < 12:
            assert(day_counter == days[curr_month])
            month_counter += 1
            day_counter = 0
            # updating network 
            update_file = f"{tau_string}{file_ending}"
            update_file = folder+update_file
            # potential for network to change every month
            # depending on deltaT
            if month_counter == 1 and deltaT != 12:
                next_month = curr_month + 1
                update_file = ""
                # delta == 1 is monthly aggregation
                if deltaT == 1:
                    # check if we exceed 12 months
                    if next_month == 13:
                        next_month = 1
                    tau_string = str(next_month)
                    if next_month < 10:
                        tau_string = "0"+tau_string
                    update_file = f"{tau_string}{file_ending}"
                    update_file = folder+update_file
                    # change how many days in month
                    curr_month_amount = days[next_month]
                    curr_month = next_month
                    # updating in,out bound dicts
                    in_bond,out_bond = {},{}
                    new_in,new_out = read_network_data(update_file)
                    in_bond = new_in
                    out_bond = new_out
                # deltaT == 3 is seasonal
                if deltaT == 3:
                    if next_month  == 13:
                        next_season = season[1]
                        curr_season = season[12]
                        next_month = 1
                    else:
                        curr_season = season[curr_month]
                        next_season = season[next_month]
                    if curr_season != next_season:
                        tau_string = next_season
                        update_file = f"{tau_string}{file_ending}"
                        update_file = folder+update_file
                        # updating in,out bound dicts
                        new_in,new_out = read_network_data(update_file)
                        in_bond = new_in
                        out_bond = new_out
                    curr_month_amount = days[next_month]
                    curr_month = next_month
                month_counter =0 
    i_inf = infected_farms
    for c in d_i:
        if d_i[c] != start_infec:   
            d_c[c] = i_inf - d_i[c]
            d_f[c] = 1
        else:
            d_i[c] = 0
            d_c[c] = 0
            d_f[c] = 0
            d_t[c] = 0

        #if d_i[c] != start_infec:
        #    d_c[c] = i_inf - d_i[c]
        #else:
        #    d_c[c] = i_inf 

    return d_i,d_t,d_c,d_f
