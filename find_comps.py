import igraph as ig
import networkx as nx
import matplotlib.pyplot as plt
import random
from mod_si import *

hort_data= "../params/horticulture365_check_NZ.csv"
in_data,out_data = read_network_data(hort_data)
vert_amount = max(len(in_data.keys()),len(out_data.keys()))


id_to_index = {}
index_to_id = {}
counter = 0

for n in in_data:
    id_to_index[n] = counter
    index_to_id[counter] = n
    counter += 1

for n in out_data:
    if n not in id_to_index:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1


# convet id values to 0-vertex_amount
mod_in_data = {}
for d in in_data:
    x = in_data[d]
    new_d = id_to_index[d]
    mod_in_data[new_d] = {}
    for s in x:
        new_s = id_to_index[s]
        mod_in_data[new_d][new_s] = x[s]

mod_out_data = {}
for s in out_data:
    x = out_data[s]
    new_s = id_to_index[s]
    mod_out_data[new_s] = {}
    for d in x:
        new_d = id_to_index[d]
        mod_out_data[new_s][new_d] = x[d]
all_edges = []
weights = []
# now, create graph
for d in mod_in_data:
    x = mod_in_data[d]
    for s in x:
        #all_edges.append((d,s))
        weight_val = mod_in_data[d][s]
        #weights.append(weight_val)
        all_edges.append((d,s,weight_val))
G = nx.DiGraph()
# now, create graph
for s in mod_out_data:
    x = mod_out_data[s]
    for d in x:
        #all_edges.append((d,s))
        weight_val = mod_out_data[s][d]
        #weights.append(weight_val)
#        all_edges.append((s,d,weight_val))
        G.add_edge(s,d,weight=weight_val)


#G.add_nodes_from(counter)
#G.add_edges_from(all_edges)
comp_amount = 0
max_nodes = 0
for component in nx.strongly_connected_components(G):
    comp_amount += 1
largest = (max(nx.strongly_connected_components(G), key=len))


#nx.draw(largest)
#plt.show()
#plt.savefig("net_plot.png")
g = ig.Graph()
g.add_vertices(counter)
g.add_edges(all_edges)
g.es["w"] = weights

# get connected components
components = g.connected_components(mode='weak')
fig, ax = plt.subplots()
ig.plot(
    components,
    target=ax,
    palette=ig.RainbowPalette(),
    vertex_size=10,
    vertex_color=list(map(int, ig.rescale(components.membership, (0, 200), clamp=True))),
    edge_width=0.2
)
#plt.show()
plt.savefig("net_plot.png")
