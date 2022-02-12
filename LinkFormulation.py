#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIE335 - Project

Link formulation for the static RWA problem, given the example of
the Checkpoint 2 of the project description

"""

from gurobipy import Model, GRB, quicksum

#Input Data

node_num = 6
link_num = 16
#V
node_list = set([0,1,2,3,4,5])
#L
link_list = [[0,1],[1,2],[2,5],[5,4],[4,3],[3,0],[3,2],[2,5],[1,0],[2,1],[5,2],[4,5],[3,4],[0,3],[2,3],[5,2]]
#T
request_list = [[0,2,1,2,3,0],
                [2,0,3,0,1,0],
                [2,0,0,3,3,0],
                [0,2,3,0,0,3],
                [1,2,3,1,0,2],
                [2,1,0,1,3,0]]
#W
wavelength_num = 5

# --------------------------------------

#Process request data

#SD
request_pair = []
request_dict = {}
for source in node_list:
    for destination in node_list:
        if request_list[source][destination] > 0:
            request_dict[(source,destination)] = request_list[source][destination]
            request_pair.append((source,destination))

request_num=len(request_dict)


#Generate delta vals

deltaplus = {}
deltaminus = {}
for link_id,link in enumerate(link_list):
    if link[0] in deltaplus:
        deltaplus[link[0]].add(link_id)
    else:
        deltaplus[link[0]]=set([link_id])
    if link[1] in deltaminus:
        deltaminus[link[1]].add(link_id)
    else:
        deltaminus[link[1]]=set([link_id])
        

# --------------------------------------

#Build Model & variables

model = Model("RWA")
x = model.addVars(request_num, link_num, wavelength_num, vtype=GRB.BINARY, name = "x")

#Objective function (1.a): Maximize the number of granted requests

model.setObjective((quicksum(x[i,j,k] for i in range(request_num) for j in deltaplus[request_pair[i][0]] for k in range(wavelength_num))) , GRB.MAXIMIZE)

#Constraints

#Constraint (1.b): Avoid wavelength conflict
model.addConstrs((quicksum(x[i,j,k] for i in range(request_num))<=1 for j in range(link_num) for k in range(wavelength_num)) , name = "Wavelength conflict")

#Constraint (1.c): Wavelength continuity
model.addConstrs(((quicksum(x[i,j,k] for j in deltaplus[v])-quicksum(x[i,j,k] for j in deltaminus[v]))==0 for k in range(wavelength_num) for i in range(request_num) for v in (node_list-set([request_pair[i][0],request_pair[i][1]]))) , name = "wavelength_continuity")

#Constraint (1.d): No loop
model.addConstrs((quicksum(x[i,j,k] for j in deltaminus[request_pair[i][0]] for k in range(wavelength_num))==0 for i in range(request_num)) , name = "No_loop1")
model.addConstrs((quicksum(x[i,j,k] for j in deltaplus[request_pair[i][1]] for k in range(wavelength_num))==0 for i in range(request_num)) , name = "No_loop2")

#Constraint (1.e): Demand
model.addConstrs((quicksum(x[i,j,k] for j in deltaplus[request_pair[i][0]] for k in range(wavelength_num))<=request_dict[request_pair[i]] for i in range(request_num)) , name = "Demand")

#Solve the model
model.optimize()






