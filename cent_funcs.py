import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np


def ret_in_deg(node_id,in_bond,out_bond):
    in_deg = len(in_bond[node_id])
    return in_deg
def ret_out_deg(node_id,in_bond,out_bond):
    out_deg = len(out_bond[node_id])
    return out_deg
def ret_in_w(node_id,in_bond,out_bond):
    total_w = 0
    for i in in_bond[node_id]:
        total_w += (in_bond[node_id][i])
    return total_w
def ret_out_w(node_id,in_bond,out_bond):
    total_w = 0
    for i in out_bond[node_id]:
        total_w += (out_bond[node_id][i])
    return total_w
def ret_total_w(node_id,in_bond,out_bond):
    in_w,out_w = 0,0
    if node_id in in_bond:
        in_w = ret_in_w(node_id,in_bond,out_bond)
    if node_id in out_bond:
        out_w = ret_out_w(node_id,in_bond,out_bond)
    total_w = in_w + out_w
    return total_w

"""
Functions for networkx centrality functions
-one liners mostly written for organization purposes
"""

def ret_closeness(G):
    return nx.closeness_centrality(G)

def ret_bc(G):
    return nx.betweenness_centrality(G)

def ret_subgraph(G):
    return nx.subgraph_centrality(G)

def ret_ev(G,iter):
    return nx.eigenvector_centrality(G,max_iter=iter)

def ret_harmonic(G):
    return nx.harmonic_centrality(G)

def ret_katz(G):
    return nx.katz_centrality(G,max_iter=10000)



