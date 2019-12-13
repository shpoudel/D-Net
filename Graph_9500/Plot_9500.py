import numpy as numpy
import json
import networkx as nx

with open('LineData.json', 'r') as f:
    LineData = json.load(f)

# Introduce new key
for l in LineData:
    l['feeder'] = 0

# Add X and Y coordinate for each node of a line
f = open("coordinates.txt","r")
for l in LineData:
    f = open("coordinates.txt","r")
    for line in f:
        if line.strip(): 
            row = line.split()
            coor = row[0].split(',')
            # print(coor)
            node = coor[0]
            X = float(coor[1])
            Y = float(coor[2])
            if node.lower() == l['from_br'].lower():
                l['f_X'] = X 
                l['f_Y'] = Y 
            if node.lower() == l['to_br'].lower():
                l['t_X'] = X 
                l['t_Y'] = Y

# Find the lines belong to S1, S2 or S3
G = nx.Graph()
for l in LineData:
    G.add_edge(l['from_br'], l['to_br'])
T = list(nx.bfs_tree(G, source = 'SOURCEBUS').edges())
Nodes = list(nx.bfs_tree(G, source = 'SOURCEBUS').nodes())

G3 = nx.Graph()
nor_open1 = ['hvmv69s2b2_sw','hvmv69s1b1_sw']  
for l in LineData:
    if l['line'] not in nor_open1:
        G3.add_edge(l['from_br'], l['to_br'])
T3 = list(nx.bfs_tree(G3, source = 'SOURCEBUS').edges())
for l in LineData:
    edge = set([l['from_br'], l['to_br']])
    for t in T3:
        if set(t) == edge:
            l['feeder'] = 3

G2 = nx.Graph()
nor_open1 = ['hvmv69s2b3_sw','hvmv69s1b1_sw']  
for l in LineData:
    if l['line'] not in nor_open1:
        G2.add_edge(l['from_br'], l['to_br'])
T2 = list(nx.bfs_tree(G2, source = 'SOURCEBUS').edges())
for l in LineData:
    edge = set([l['from_br'], l['to_br']])
    for t in T2:
        if set(t) == edge:
            l['feeder'] = 2

G1 = nx.Graph()
nor_open1 = ['hvmv69s2b3_sw','hvmv69s2b1_sw']  
for l in LineData:
    if l['line'] not in nor_open1:
        G1.add_edge(l['from_br'], l['to_br'])
T1 = list(nx.bfs_tree(G1, source = 'SOURCEBUS').edges())
for l in LineData:
    edge = set([l['from_br'], l['to_br']])
    for t in T1:
        if set(t) == edge:
            l['feeder'] = 1

G0 = nx.Graph()
nor_open1 = ['hvmv69s3b1_sw','hvmv69s2b1_sw','hvmv69s1b1_sw']  
for l in LineData:
    if l['line'] not in nor_open1:
        G0.add_edge(l['from_br'], l['to_br'])
T0 = list(nx.bfs_tree(G0, source = 'SOURCEBUS').edges())
for l in LineData:
    edge = set([l['from_br'], l['to_br']])
    for t in T0:
        if set(t) == edge:
            l['feeder'] = 0

with open('LineDataXY.json', 'w') as fp:
    json.dump(LineData, fp)