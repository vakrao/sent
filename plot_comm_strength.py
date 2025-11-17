import networkx as nx
from shapely import node
from shapely import Point
from sent_si import *
import random
import geopandas 
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from find_seeds import *
from cent_funcs import *
from spatial import *






all_data= pd.read_csv("results/all_stats.csv")
community_meta = pd.read_csv("results/louvain_data.csv", usecols=["PROPERTY_ID","COMM_ID"])
all_data = all_data.merge(
    community_meta,
    left_on="NODE_ID",
    right_on="PROPERTY_ID",
    how="left"
)
all_data = all_data.rename(columns={"COMM_ID": "COMMUNITY_ID"})
all_data = all_data.drop(columns=["PROPERTY_ID"])

net_fn = "params/hort365_NZ.csv"
in_bond, out_bond = read_network_data(net_fn)
all_data["s_within_in"] = (all_data["i_w"] - all_data["FIRST_IN_MOMENT"])/(all_data["i_w"])
all_data["s_within_out"] = (all_data["o_w"] - all_data["FIRST_OUT_MOMENT"])/(all_data["o_w"])
all_data["s_between_in"] = (all_data["FIRST_IN_MOMENT"])/(all_data["i_w"])
all_data["s_between_out"] = (all_data["FIRST_OUT_MOMENT"])/(all_data["o_w"])
all_data["s_between"] = all_data["s_between_in"] + all_data["s_between_out"]
all_data["s_within"] = all_data["s_within_in"] + all_data["s_within_out"]
all_data["d_within_in"] = (all_data["i_d"] - all_data["FIRST_IN_DEG_MOMENT"])/(all_data["d"])
all_data["d_within_out"] = (all_data["o_d"] - all_data["FIRST_OUT_DEG_MOMENT"])/(all_data["d"])
all_data["d_between_in"] = (all_data["FIRST_IN_DEG_MOMENT"])/(all_data["d"])
all_data["d_between_out"] = (all_data["FIRST_OUT_DEG_MOMENT"])/(all_data["d"])
all_data["d_between"] = all_data["d_between_in"] + all_data["d_between_out"]
all_data["d_within"] = all_data["d_within_in"] + all_data["d_within_out"]
all_data["d_between_abs"] = all_data["FIRST_IN_DEG_MOMENT"] + all_data["FIRST_OUT_DEG_MOMENT"]
all_data["d_within_abs"] = (all_data["i_d"] - all_data["FIRST_IN_DEG_MOMENT"]) + (all_data["o_d"] - all_data["FIRST_OUT_DEG_MOMENT"])



# s moment save
fig_x,fig_y = 15,5
fs = 18
fig,axs = plt.subplots(1,3,figsize=(fig_x,fig_y))
axs[0].scatter(all_data["s_within_in"],all_data["s_between_in"],color="blue",alpha=0.2,label="In")
axs[0].set_xlabel(r"$S^{within}$",fontsize=fs)
axs[0].set_ylabel(r"$S^{between}$",fontsize=fs)
axs[0].tick_params(labelsize="large")
axs[0].legend()
axs[1].scatter(all_data["s_within_out"],all_data["s_between_out"],color="orange",alpha=0.2,label="Out")
axs[1].set_xlabel(r"$S^{within}$",fontsize=fs)
axs[1].set_ylabel(r"$S^{between}$",fontsize=fs)
axs[1].tick_params(labelsize="large")
axs[1].legend()
axs[2].scatter(all_data["s_within"],all_data["s_between"],color="black",alpha=0.2,label="Out")
axs[2].tick_params(labelsize="large")
axs[2].set_xlabel(r"$S^{within}$",fontsize=fs)
axs[2].set_ylabel(r"$S^{between}$",fontsize=fs)
axs[2].legend()
fig.savefig("results/s_between.png")
# degree moment save
d_fig,d_axs = plt.subplots(1,3,figsize=(fig_x,fig_y))
d_axs[0].scatter(all_data["d_within_in"],all_data["d_between_in"],color="blue",alpha=0.2,label="In")
d_axs[0].set_xlabel(r"$D^{within}$",fontsize=fs)
d_axs[0].set_ylabel(r"$D^{between}$",fontsize=fs)
d_axs[0].tick_params(labelsize="large")
d_axs[0].legend()
d_axs[1].scatter(all_data["d_within_out"],all_data["d_between_out"],color="orange",alpha=0.2,label="Out")
d_axs[1].set_xlabel(r"$D^{within}$",fontsize=fs)
d_axs[1].set_ylabel(r"$D^{between}$",fontsize=fs)
d_axs[1].tick_params(labelsize="large")
d_axs[1].legend()
d_axs[2].scatter(all_data["d_within"],all_data["d_between"],color="black",alpha=0.2,label="Out")
d_axs[2].set_xlabel(r"$D^{within}$",fontsize=fs)
d_axs[2].set_ylabel(r"$D^{between}$",fontsize=fs)
d_axs[2].tick_params(labelsize="large")
d_axs[2].legend()
d_fig.savefig("results/d_between.png")



# now, let us plot the distributions for the SBM plot
fs = 18
fig,axs = plt.subplots(1,2,figsize=(fig_x,fig_y))
axs[0].hist(all_data["d_within"])
axs[0].set_xlabel(r"$D^{within}$",fontsize=fs)
axs[0].set_ylabel(r"Node Number",fontsize=fs)
axs[0].tick_params(labelsize="large")
axs[1].hist(all_data["d_between"])
axs[1].set_xlabel(r"$D^{between}$",fontsize=fs)
axs[1].set_ylabel(r"Node Number",fontsize=fs)
axs[1].tick_params(labelsize="large")
fig.savefig("results/d_hist.png")
"""
# degree moment save
d_fig,d_axs = plt.subplots(1,3,figsize=(fig_x,fig_y))
d_axs[0].scatter(all_data["d_within_in"],all_data["d_between_in"],color="blue",alpha=0.2,label="In")
d_axs[0].set_xlabel(r"$D^{within}$")
d_axs[0].set_ylabel(r"$D^{between}$")
d_axs[0].legend()
d_axs[1].scatter(all_data["d_within_out"],all_data["d_between_out"],color="orange",alpha=0.2,label="Out")
d_axs[1].set_xlabel(r"$D^{within}$")
d_axs[1].set_ylabel(r"$D^{between}$")
d_axs[1].legend()
d_axs[2].scatter(all_data["d_within"],all_data["d_between"],color="black",alpha=0.2,label="Out")
d_axs[2].set_xlabel(r"$D^{within}$")
d_axs[2].set_ylabel(r"$D^{between}$")
d_axs[2].legend()
d_fig.savefig("results/d_compare.png")
"""


d_fig,d_axs = plt.subplots(1,3,figsize=(fig_x,fig_y))
d_axs[0].scatter(all_data["d_within"],all_data["d"],color="blue",alpha=0.2)
d_axs[0].set_xlabel(r"$D^{within}$")
d_axs[0].set_ylabel(r"$D^{total}$")
d_axs[0].set_yscale("log")
d_axs[1].scatter(all_data["d_between"],all_data["d"],color="orange",alpha=0.2)
d_axs[1].set_xlabel(r"$D^{between}$")
d_axs[1].set_ylabel(r"$D^{total}$")
d_axs[1].set_yscale("log")
d_axs[2].scatter(all_data["d_within_abs"],all_data["d_between_abs"],color="black",alpha=0.2)
d_axs[2].set_xlabel(r"$D^{within}$")
d_axs[2].set_xscale("log")
d_axs[2].set_yscale("log")
d_axs[2].set_ylabel(r"$D^{between}$")
d_axs[2].legend()
d_fig.savefig("results/d_compare.png")

# now, let us plot the distributions for the SBM plot
"""
deg_fig,deg_axs = plt.subplots(2,3,figsize=(fig_x,fig_y))
#comm_data = pd.read_csv("results/all_stats.csv")
ranks = ["R_F","R_I","R_T"]
colors = ["blue","red","green"]
map_choice = "viridis_r"
for i,r in enumerate(ranks):
    a = deg_axs[0][i].scatter(comm_data["d_between_in"],comm_data[r],c=comm_data["d_within_in"],cmap=map_choice,label="Between Community Degree")
    deg_axs[0][i].yaxis.set_inverted(True)
    deg_axs[0][i].set_xlabel("In-Moment")
    deg_axs[0][i].set_yscale("log")
    deg_axs[0][i].set_xscale("log")
    deg_axs[1][i].set_xscale("log")
    deg_axs[0][i].set_ylabel(r)
#    deg_axs[0][i].yaxis.set_inverted(True)
    b = deg_axs[1][i].scatter(comm_data["s_between_in"],comm_data[r],c=comm_data["s_within_in"],cmap=map_choice,label="In-Weight")
    deg_axs[1][i].yaxis.set_inverted(True)
    deg_axs[1][i].set_xlabel("In-Moment")
    deg_axs[1][i].set_ylabel(r)
    deg_axs[1][i].set_yscale("log")
    deg_axs[1][i].set_xscale("log")
#    deg_axs[1][i].yaxis.set_inverted(True)
    deg_axs[0][i].legend()
    deg_axs[1][i].legend()
    deg_fig.colorbar(a,ax=deg_axs[0][i])
    deg_fig.colorbar(b,ax=deg_axs[1][i])
"""

community_data = all_data.dropna(subset=["COMMUNITY_ID"]).copy()
if not community_data.empty:
    community_data["COMMUNITY_ID"] = (
        community_data["COMMUNITY_ID"]
        .astype("Int64")
        .astype(str)
    )
    grouped = community_data.groupby("COMMUNITY_ID")
    cmap = plt.get_cmap("tab20", grouped.ngroups if grouped.ngroups else 1)
    presentation_fonts = {
        "axes.titlesize": 18,
        "axes.labelsize": 16,
        "xtick.labelsize": 14,
        "ytick.labelsize": 14,
        "legend.fontsize": 14,
    }
    panel_specs = [
        ("d_within", (0, 0), r"$D^{within}$"),
        ("d_between", (0, 1), r"$D^{between}$"),
        ("s_within", (1, 0), r"$S^{within}$"),
        ("s_between", (1, 1), r"$S^{between}$"),
    ]
    legend_handles = []
    with plt.rc_context(presentation_fonts):
        fig, axes = plt.subplots(2, 2, figsize=(15, 12), sharey=False)
        axes = axes.reshape(2, 2)
        for idx, (community_id, group) in enumerate(grouped):
            color = cmap(idx)
            legend_handles.append(
                Patch(facecolor=color, alpha=0.5, label=f"Community {community_id}")
            )
            for feature, (row_idx, col_idx), _ in panel_specs:
                ax = axes[row_idx][col_idx]
                values = group[feature].dropna()
                if values.empty:
                    continue
                ax.hist(
                    values,
                    bins=30,
                    density=True,
                    histtype="stepfilled",
                    alpha=0.35,
                    color=color,
                    edgecolor=color,
                    linewidth=1.4,
                )
        for feature, (row_idx, col_idx), label in panel_specs:
            ax = axes[row_idx][col_idx]
            ax.set_title(f"{label} Distribution")
            ax.set_xlabel(label)
            if col_idx == 0:
                ax.set_ylabel("Density")
            ax.grid(alpha=0.2)
        fig.suptitle("Community-level Within/Between Distributions", y=0.96)
        fig.legend(
            handles=legend_handles,
            loc="upper center",
            ncol=3,
            frameon=False,
            bbox_to_anchor=(0.5, 0.995),
        )
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig("results/community_distribution_panels.png", dpi=300)
