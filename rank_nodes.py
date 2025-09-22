import igraph as ig
import networkx as nx
import matplotlib.pyplot as plt
import random


def static_graph_report(in_bond,out_bond,save_name):
    in_deg,out_deg = {},{}
    in_w,out_w = {},{}
        
    # in-bond static
    for i in in_bond:
        deg_amount = len(list(in_bond[i].keys()))
        for k in in_bond[i]:
            if i not in in_bond:
                in_deg[i] = 1
                in_w[i] = in_bond[i][k]
            else:
                in_deg[i] += 1
                in_w[i] += in_bond[i][k]
    # out-bond static
    for i in out_bond:
        for k in out_bond[i]:
            if i not in out_bond:
                out_deg[i] = 1
                out_w[i] = out_bond[i][k]
            else:
                out_deg[i] += 1
                out_w[i] += out_bond[i][k]
   return in_deg,in_w,out_deg,out_w






