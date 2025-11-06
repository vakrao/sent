from tkinter import N
import networkx as nx
from shapely import node
from shapely import Point
from sent_si import *
import random
import geopandas 
import pandas as pd
from find_seeds import *
from cent_funcs import *
from spatial import *






all_data= pd.read_csv("results/all_stats.csv")

net_fn = "params/hort365_NZ.csv"
in_bond, out_bond = read_network_data(net_fn)
all_data["s_inter_in"] = (all_data["i_w"] - all_data["FIRST_IN_MOMENT"])/(all_data["w"])
all_data["s_inter_out"] = (all_data["o_w"] - all_data["FIRST_OUT_MOMENT"])/(all_data["w"])
all_data["s_intra_in"] = (all_data["FIRST_IN_MOMENT"])/(all_data["w"])
all_data["s_intra_out"] = (all_data["FIRST_OUT_MOMENT"])/(all_data["w"])

print(all_data.loc[all_data["s_inter_in"] < 0])
print(all_data.loc[all_data["s_inter_in"] < 0]["FIRST_IN_MOMENT"])
print(all_data.loc[all_data["s_inter_in"] < 0]["i_w"])
print(all_data.loc[all_data["s_inter_in"] < 0]["o_w"])
print(all_data.loc[all_data["s_inter_in"] < 0]["w"])


plt.scatter(all_data["s_inter_in"],all_data["s_inter_out"])
plt.xlabel(r"$S^{inter}_{in}$")
plt.ylabel(r"$S^{inter}_{out}$")
plt.savefig("inter_comp.png")
plt.scatter(all_data["s_inter_in"],all_data["i_w"])
plt.xlabel(r"$S^{inter}_{in}$")
plt.ylabel(r"$S^{inter}_{out}$")
plt.savefig("inter_comp.png")
