# import networkx as nx
# import numpy as np
# import matplotlib.pyplot as plt

# file = open("/Users/aarongao/Desktop/Master Project/decomp/chlamydomonas_lna_cycles_fluxes.txt", 'r')
# lines = file.readlines()
# path = []
# for inx in range(1,11):
#     fig = plt.figure()

#     line = lines[-inx]
#     value = line.split('/')[-1]
#     elements = line.split('/')[0].split(' ')
#     nodes = []
#     for i in range(0, len(elements)):
#         if i == (len(elements)-1):
#             node = (elements[i], elements[0])
#             nodes.append(node)
#             break
#         nodes.append((elements[i], elements[i+1]))
        
#     G = nx.DiGraph()
#     G.add_edges_from(nodes, length=1)

#     # Specify the edges you want here

#     edges = [edge for edge in G.edges()]

#     # Need to create a layout when doing
#     # separate calls to draw nodes and edges
#     labels = {}
#     # for idx, node in enumerate(G.nodes()):
#     #     labels[node] = node


#     pos = nx.circular_layout(G,scale=100)
#     # nx.draw(G, pos, with_labels=True, node_size=30, arrows=True, edge_color='black', alpha=0)
#     nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size=1200, node_color='white', alpha=0)
#     nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='black', arrows=True, alpha=0.3)
#     nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='red')
#     plt.axis('off')
#     plt.text(0, 0, str(value), horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='red', alpha=0.5), size=12)
#     # plt.show()
#     # nx.draw(G, pos=nx.circular_layout(G), node_size=1200, node_color='lightblue',
#     #     linewidths=0.25, font_size=10, font_weight='bold', with_labels=True)
#     save_path = './' + str(inx) + '.png'
#     fig.savefig(save_path, dpi=200)
#     # plt.close()˜
# file.close()

import networkx as nx
import pandas as pd
from tarjan import *
from collections import defaultdict
import re, mmap

with open("/Users/aarongao/Desktop/Decomposition_scripts/compartments/u/lna/chlamydomonas_lna.csv_cycles_fluxes.txt", 'rb') as file, mmap.mmap(file.fileno(),0,access=mmap.ACCESS_READ) as m:
    pattern = rb'^(\w+(\s||/)){1,}(\+){0,1}\d+(.){0,1}\d$'
    lines = file.readlines()
    pat = re.compile(pattern)
    for line in lines:
        line = line.strip(b'\n')
        a = pat.search(line)
        print(a)
# cycles = list(nx.simple_cycles(G))