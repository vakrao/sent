from tkinter import N
import networkx as nx
from shapely import node
from shapely import Point
from sent_si import *
import random
import geopandas 
import pandas as pd
import matplotlib.pyplot as plt
from find_seeds import *
from cent_funcs import *
from spatial import *





fig_x,fig_y = 18,10
fig,axs = plt.subplots(2,3,figsize=(fig_x,fig_y))
comm_data = pd.read_csv("results/all_stats.csv")
ranks = ["dF_sum","dI_mean","dT_mean"]
label_ranks = [r"$F$",r"$I$",r"$T$"]
colors = ["blue","red","green"]
fs = 20

for i,r in enumerate(ranks):
    print(i,r)
    axs[0][i].scatter(comm_data["FIRST_IN_MOMENT"],comm_data[r],color=colors[i])
    axs[0][i].set_xlabel("In-Moment")
    axs[0][i].set_yscale("log")
    axs[0][i].set_ylabel(label_ranks,size=fs)
   # axs[0][i].yaxis.set_inverted(True)
    axs[1][i].scatter(comm_data["FIRST_OUT_MOMENT"],comm_data[r],color=colors[i])
    axs[1][i].set_xlabel("Out-Moment")
    axs[1][i].set_ylabel(label_ranks,size=fs)
    axs[1][i].set_yscale("log")
   # axs[1][i].yaxis.set_inverted(True)

fig.savefig("results/all_moments.png")

deg_fig,deg_axs = plt.subplots(2,3,figsize=(fig_x,fig_y))
comm_data = pd.read_csv("results/all_stats.csv")

colors = ["blue","red","green"]
map_choice = "viridis_r"
for i,r in enumerate(ranks):
    a = deg_axs[0][i].scatter(comm_data["FIRST_IN_MOMENT"],comm_data[r],c=comm_data["i_d"],cmap=map_choice,label="In-Degree")
    deg_axs[0][i].yaxis.set_inverted(True)
    deg_axs[0][i].set_xlabel("In-Moment",size=fs)
    deg_axs[0][i].set_yscale("log")
    deg_axs[0][i].set_xscale("log")
    deg_axs[1][i].set_xscale("log")
    deg_axs[0][i].tick_params(labelsize="large")
    deg_axs[0][i].set_ylabel(label_ranks[i],size=fs)
#    deg_axs[0][i].yaxis.set_inverted(True)
    b = deg_axs[1][i].scatter(comm_data["FIRST_IN_MOMENT"],comm_data[r],c=comm_data["i_w"],cmap=map_choice,label="In-Weight")
    deg_axs[1][i].yaxis.set_inverted(True)
    deg_axs[1][i].set_xlabel("In-Moment")
    deg_axs[1][i].set_ylabel(label_ranks[i],size=fs)
    deg_axs[1][i].set_yscale("log")
    deg_axs[1][i].tick_params(labelsize="large")
    deg_axs[1][i].set_xscale("log")
#    deg_axs[1][i].yaxis.set_inverted(True)
    deg_axs[0][i].legend()
    deg_axs[1][i].legend()
    deg_fig.colorbar(a,ax=deg_axs[0][i])
    deg_fig.colorbar(b,ax=deg_axs[1][i])
deg_fig.savefig("results/all_degree.png")

dist_fig,dist_axs= plt.subplots(2,3,figsize=(fig_x,fig_y))
colors = ["blue","red","green"]
for i,r in enumerate(ranks):
    dist_axs[0][i].scatter(comm_data["MAX_DIST_IN"],comm_data[r],c=colors[i],label=r)
    dist_axs[0][i].set_xlabel("Max In-Distance")
    dist_axs[0][i].set_xscale("log")
#    dist_axs[0][i].set_yscale("log")
    dist_axs[0][i].set_ylabel(label_ranks[i],fontsize=fs)
    dist_axs[0][i].tick_params(labelsize="large")
    dist_axs[1][i].scatter(comm_data["MAX_DIST_OUT"],comm_data[r],c=colors[i],label=r)
    dist_axs[1][i].set_xlabel("Max Out-Distance")
    dist_axs[1][i].set_ylabel(label_ranks[i],fontsize=fs)
    dist_axs[1][i].tick_params(labelsize="large")
    dist_axs[1][i].set_xscale("log")
#    dist_axs[1][i].set_yscale("log")
    dist_axs[0][i].legend()
    dist_axs[1][i].legend()


dist_fig.savefig("results/max_distance.png")

avg_dist_fig,avg_dist_axs= plt.subplots(2,3,figsize=(fig_x,fig_y))
colors = ["blue","red","green"]
for i,r in enumerate(ranks):
    avg_dist_axs[0][i].scatter(comm_data["AVG_DIST_IN"],comm_data[r],c=colors[i],label=r)
    avg_dist_axs[0][i].set_xlabel("Average In-Distance")
    avg_dist_axs[0][i].set_xscale("log")
#    avg_dist_axs[0][i].set_yscale("log")
    avg_dist_axs[0][i].set_ylabel(label_ranks[i],fontsize=fs)
    avg_dist_axs[0][i].tick_params(labelsize="large")
    avg_dist_axs[1][i].scatter(comm_data["AVG_DIST_OUT"],comm_data[r],c=colors[i],label=r)
    avg_dist_axs[1][i].set_xlabel("Average Out-Distance")
    avg_dist_axs[1][i].set_ylabel(label_ranks[i],fontsize=fs)
    avg_dist_axs[1][i].set_xscale("log")
#    avg_dist_axs[1][i].set_yscale("log")
    avg_dist_axs[1][i].tick_params(labelsize="large")
    avg_dist_axs[0][i].legend()
    avg_dist_axs[1][i].legend()


avg_dist_fig.savefig("results/avg_distance.png")


deg_fig,deg_axs = plt.subplots(2,3,figsize=(fig_x,fig_y))
#comm_data = pd.read_csv("results/all_stats.csv")
colors = ["blue","red","green"]
map_choice = "viridis_r"
for i,r in enumerate(ranks):
    a = deg_axs[0][i].scatter(comm_data["AVG_DIST_IN"],comm_data[r],c=comm_data["i_d"],cmap=map_choice,label="In-Degree")
#    deg_axs[0][i].yaxis.set_inverted(True)
    deg_axs[0][i].set_xlabel("Average In-Distance",fontsize=fs)
    deg_axs[0][i].tick_params(labelsize="large")
#    deg_axs[0][i].set_yscale("log")
    deg_axs[0][i].set_xscale("log")
    deg_axs[1][i].set_xscale("log")
    deg_axs[0][i].set_ylabel(label_ranks[i],fontsize=fs)
#    deg_axs[0][i].yaxis.set_inverted(True)
    b = deg_axs[1][i].scatter(comm_data["AVG_DIST_IN"],comm_data[r],c=comm_data["i_w"],cmap=map_choice,label="In-Weight")
#    deg_axs[1][i].yaxis.set_inverted(True)
    deg_axs[1][i].set_xlabel("Average In-Distance",fontsize=fs)
    deg_axs[1][i].set_ylabel(label_ranks[i],fontsize=fs)
    deg_axs[1][i].tick_params(labelsize="large")
#    deg_axs[1][i].set_yscale("log")
    deg_axs[1][i].set_xscale("log")
#    deg_axs[1][i].yaxis.set_inverted(True)
    deg_axs[0][i].legend()
    deg_axs[1][i].legend()
    deg_fig.colorbar(a,ax=deg_axs[0][i])
    deg_fig.colorbar(b,ax=deg_axs[1][i])
deg_fig.savefig("results/dist_cent.png")
