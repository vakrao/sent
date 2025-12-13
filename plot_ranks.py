import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 14})
import numpy as np
import pandas as pd
import math
from sklearn.metrics import jaccard_score
from sklearn.metrics import normalized_mutual_info_score
from scipy.stats import spearmanr
import seaborn as sns
import sys



seas = sys.argv[1]
compare = False
if seas == "both":
    compare = True
    seas = "y"
    fig_x,fig_y = 3,3
rank_path = "data/"+seas+"_rank.csv"
rank_df = pd.read_csv(rank_path)
cent_path = "data/"+seas+"_cent.csv"
cent_df = pd.read_csv(cent_path)
cent_df = cent_df.rename(columns={'node_id':'sent'})
agg = rank_df.merge(cent_df,on="sent")


if seas == "m":
    marker = "x"
if seas == "s":
    marker = "v"
if seas == "y":
    marker = "o"
# Run for R_F vs R_T
f_y = np.asarray(agg["dF_sum"], dtype=float)
i_y = np.asarray(agg["dI_mean"], dtype=float)
t_y = np.asarray(agg["dT_mean"], dtype=float)

pairs = [
        (f_y, i_y, r"$F_Y$", r"$I_Y$"),
        (f_y,t_y, r"$F_Y$", r"$T_Y$"),
        (i_y,t_y,  r"$I_Y$", r"$T_Y$")
        ]


fig, axes = plt.subplots(1, 3, figsize=(18, 5))

if compare == True:
    fig, axs = plt.subplots(fig_x,fig_y, figsize=(15,10))
    m_fp = "data/m_rank.csv"
    s_fp = "data/s_rank.csv"
    m_dat =pd.read_csv(m_fp)
    s_dat =pd.read_csv(s_fp)
    f_s = np.asarray(s_dat["dF_sum"], dtype=float)
    i_s = np.asarray(s_dat["dI_mean"], dtype=float)
    t_s = np.asarray(s_dat["dT_mean"], dtype=float)
    f_m = np.asarray(m_dat["dF_sum"], dtype=float)
    i_m = np.asarray(m_dat["dI_mean"], dtype=float)
    t_m = np.asarray(m_dat["dT_mean"], dtype=float)
    pairs = [
        (f_y, f_s, r"$F_Y$", r"$F_S$"),
        (i_y,i_s, r"$I_Y$", r"$I_S$"),
        (t_y,t_s,  r"$T_Y$", r"$T_S$"),
        (f_y, f_m, r"$F_Y$", r"$F_M$"),
        (i_y,i_m , r"$I_Y$", r"$I_M$"),
        (t_y,t_m,  r"$T_S$", r"$T_M$"),
        (f_s, f_m, r"$F_S$", r"$F_M$"),
        (i_s,i_m , r"$I_S$", r"$I_M$"),
        (t_s,t_m,  r"$T_S$", r"$T_M$")
    ]

if compare == True:
    counter = 0
    for i in range(0,fig_x):
        for j in range(0,fig_y):
            x,y = pairs[counter][0],pairs[counter][1] 
            xlab,ylab = pairs[counter][2],pairs[counter][3]
            axs[i,j].scatter(x, y, s=20, alpha=0.55,marker=marker)
            
            # consistent limits and inverted orientation
            r_min, r_max = 0, 1
       
#            axs.plot([r_min, r_max], [r_min, r_max], "--", color="k", lw=1)
            
       
            # axis labels and title
            axs[i,j].set_xlabel(f"{xlab}",size=24)
            axs[i,j].set_ylabel(f"{ylab}",size=24)
            axs[i,j].tick_params(axis="both",labelsize=18)
            axs[i,j].set_title(f"{xlab} vs {ylab}",size=32)
            axs[i,j].grid(True, linestyle="--", alpha=0.3)
            counter += 1
else:


    for ax, (x, y, xlab, ylab) in zip(axes, pairs):
        mask = np.isfinite(x) & np.isfinite(y)
        x, y = x[mask], y[mask]
       
        ax.scatter(x, y, s=20, alpha=0.55,marker=marker)
        
        # consistent limits and inverted orientation
        r_min, r_max = 0, 1
       
        ax.plot([r_min, r_max], [r_min, r_max], "--", color="k", lw=1)
        
        ax.set_xscale("log")
        ax.set_yscale("log")
       # ax.set_xlim(r_max, r_min)
       # ax.set_ylim(r_max, r_min)
       
        # axis labels and title
        ax.set_xlabel(f"{xlab}",size=22)
        ax.set_ylabel(f"{ylab}",size=22)
        ax.tick_params(axis="both",labelsize=18)
        ax.set_title(f"{xlab} vs {ylab}")
        ax.grid(True, linestyle="--", alpha=0.3)


compare_fig = "results/"+seas+"/"+seas+"_rank_compare.png"
if compare == True:
    compare_fig = "results/all_temp_rank_compare.png"
plt.tight_layout()
plt.savefig(compare_fig, dpi=300, bbox_inches="tight")
plt.show()




# Load the datase
# Define metric columns and readable labels
metric_map = {
    "i_d": "In-degree",
    "w": "Total weight",
    "close": "Closeness centrality",
    "harm": "Harmonic centrality",
    "ev": "Eigenvector centrality",
    'bc': "Betweeness centrality",
    'clust':'Clustering coeffiecent',
    'h': 'Hectares'
}

# Ensure R_F is numeric
metrics = ["dF_sum","dI_mean","dT_mean"]
for m in metrics:
#    agg["R_F"] = pd.to_numeric(agg["dF_sum"], errors="coerce")
    
    # Set up plotting grid
    cols = 2
    rows = (len(metric_map) + cols - 1) // cols
    plt.figure(figsize=(6 * cols, 4 * rows))
    
    # Generate scatter plots
    for i, (col, label) in enumerate(metric_map.items(), 1):
        ax = plt.subplot(rows, cols, i)
        
        # Drop NA and filter positive values for log scaling
        subdf = agg[[col, m]].dropna()
        subdf = subdf[(subdf[col] > 0) & (subdf[m] > 0)]
        
        # Compute correlations
        #pearson_corr, _ = pearsonr(subdf[col], subdf["dF_sum"])
        #spearman_corr, _ = spearmanr(subdf[col], subdf["dF_sum"])
        
        # Plot
        sns.scatterplot(x=subdf[col], y=subdf[m],marker=marker, s=25, alpha=0.7)
       # ax.set_ylim(.05,.15)
        ax.set_xscale("log")
        ax.set_yscale("log")
  #      ax.invert_yaxis()
        ax.set_xlabel(label)
        y_lab = m[1]
        ax.set_ylabel(f"${y_lab}$")
        ax.set_title(f"{label}")
        ax.grid(True, linestyle="--", alpha=0.3)
    
    save_name = "results/"+seas+"/"+seas+y_lab+"_cent_loglog.png"
    plt.tight_layout()
    plt.savefig(save_name, dpi=300, bbox_inches="tight")
