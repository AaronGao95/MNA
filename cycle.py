import pandas as pd
import networkx as nx

file = pd.read_csv("/Users/aarongao/Desktop/Master Project/Mass calculation/decomposition_example.csv")
f = []
s = []
for row in file.itertuples(index=False):
    first = row[0].split('->')[0].split()
    second = row[0].split('->')[1].split(';')[0].split()
    value = row[0].split('->')[1].split(';')[1]
    value = float(value)
    if len(first) >1:
        first = first[1]
    else:
        first = first[0]
    if len(second)>1:
        second = second[1]
    else:
        second = second[0]
    if value < 0:
        t = first
        first = second
        second = t
    f.append(first)
    s.append(second)
g = nx.DiGraph()
g.add_edges_from(list(zip(f,s)))

# cycles = list(nx.simple_cycles(g))
