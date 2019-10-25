import json
import networkx as nx 
import numpy as np
from pulp import *
import math
from Isolation import OpenSw

class Restoration:
    """
    This code is for solving the restoration problem for IEEE test cases. The planning model is used as
    input and real time load data is required.

    """
    def __init__(self):
        """
        Inputs:
           LinePar
           LoadData
           Graph =  G (V,E)
        """
        pass        
   
    def res9500 (self, Linepar, LoadData, fault):    
        
        # Find Tree and Planning model using Linepar
        G = nx.Graph()
        
        # Note: If required, this nor_open list can be obtained from Platform
        nor_open = ['ln0653457_sw','v7173_48332_sw', 'tsw803273_sw', 'a333_48332_sw','tsw320328_sw',\
                   'a8645_48332_sw','tsw568613_sw', 'wf856_48332_sw', 'wg127_48332_sw']  
        for l in Linepar:
            if l['line'] not in nor_open:
                G.add_edge(l['from_br'], l['to_br'])
        T = list(nx.bfs_tree(G, source = 'SOURCEBUS').edges())
        Nodes = list(nx.bfs_tree(G, source = 'SOURCEBUS').nodes())
        
        for l in Linepar:
            if l['line'] in nor_open:
                SW = (l['from_br'], l['to_br'])
                T.append(SW)
                G.add_edge(l['from_br'], l['to_br'])             

        # parameters
        nNodes = G.number_of_nodes()
        nEdges = G.number_of_edges() 
        fr, to = zip(*T)
        fr = list(fr)
        to = list(to) 
        bigM = 15000        
        
        # Different variables for optimization function
        si = LpVariable.dicts("s_i", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        vi = LpVariable.dicts("v_i", ((i) for i in range(nNodes) ), lowBound=0, upBound=1, cat='Binary')
        xij = LpVariable.dicts("x_ij", ((i) for i in range(nEdges) ), lowBound=0, upBound=1, cat='Binary')
        Pija = LpVariable.dicts("xPa", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Pijb = LpVariable.dicts("xPb", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Pijc = LpVariable.dicts("xPc", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qija = LpVariable.dicts("xQa", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qijb = LpVariable.dicts("xQb", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Qijc = LpVariable.dicts("xQc", ((i) for i in range(nEdges) ), lowBound=-bigM, upBound=bigM, cat='Continous')
        Via = LpVariable.dicts("xVa", ((i) for i in range(nNodes) ), lowBound=0.6, upBound=1.1025, cat='Continous')
        Vib = LpVariable.dicts("xVb", ((i) for i in range(nNodes) ), lowBound=0.6, upBound=1.1025, cat='Continous')
        Vic = LpVariable.dicts("xVc", ((i) for i in range(nNodes) ), lowBound=0.6, upBound=1.1025, cat='Continous')

        # Optimization problem objective definitions
        # Maximize the power flow from feeder 
        prob = LpProblem("Resilient Restoration",LpMinimize)
        No = [2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753]
        prob += -(Pija[0] + Pijb[0] + Pijc[0]) - lpSum(xij[i] for i in range(nEdges-9)) + 5 * lpSum(xij[No[k]] for k in range(9))

        # Constraints (v_i<=1)
        for k in range(nNodes):
            prob += vi[k] <= 1
        
        # Constraints (s_i<=1)
        for k in range(nNodes):
            prob += si[k] <= 1
        
        # Constraints (x_ij<=v_i*v_j)
        for k in range(nEdges):
            n1 = fr[k] 
            n2 = to[k]     
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)
            prob += xij[k] <= vi[ind1]
            prob += xij[k] <= vi[ind2]

        # Real power flow equation for Phase A, B, and C
        #Phase A   
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'A':
                    demandP += d['kW']
                    demandQ += d['kVaR']
            prob += lpSum(Pija[pa[j]] for j in N) - demandP * si[indb] == \
                    lpSum(Pija[ch[j]] for j in M)
            prob += lpSum(Qija[pa[j]] for j in N) - demandQ * si[indb] == \
                    lpSum(Qija[ch[j]] for j in M)

        # Phase B
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'B':
                    demandP += d['kW']
                    demandQ += d['kVaR']
            prob += lpSum(Pijb[pa[j]] for j in N) - demandP * si[indb] == \
                    lpSum(Pijb[ch[j]] for j in M)
            prob += lpSum(Qijb[pa[j]] for j in N) - demandQ * si[indb] == \
                    lpSum(Qijb[ch[j]] for j in M)

        # Phase C
        for i in range(nEdges):    
            node = to[i]     
            indb = Nodes.index(node)
            ch = [n for n, e in enumerate(fr) if e == node]
            pa = [n for n, e in enumerate(to) if e == node]
            M = range(len(ch))
            N = range(len(pa))
            demandP = 0.
            demandQ = 0.
            for d in LoadData:
                if node == d['bus'] and d['Phase'] == 'C':
                    demandP += d['kW']
                    demandQ += d['kVaR']
            prob += lpSum(Pijc[pa[j]] for j in N) - demandP * si[indb] == \
                    lpSum(Pijc[ch[j]] for j in M)
            prob += lpSum(Qijc[pa[j]] for j in N) - demandQ * si[indb] == \
                    lpSum(Qijc[ch[j]] for j in M)

        # Big-M method for real power flow and switch variable
        for k in range(nEdges):    
            prob += Pija[k] <= bigM * xij[k]
            prob += Pijb[k] <= bigM * xij[k]
            prob += Pijc[k] <= bigM * xij[k] 
            prob += Qija[k] <= bigM * xij[k]
            prob += Qijb[k] <= bigM * xij[k]
            prob += Qijc[k] <= bigM * xij[k] 
            # For reverse flow
            prob += Pija[k] >= -bigM * xij[k]
            prob += Pijb[k] >= -bigM * xij[k] 
            prob += Pijc[k] >= -bigM * xij[k] 
            prob += Qija[k] >= -bigM * xij[k]
            prob += Qijb[k] >= -bigM * xij[k] 
            prob += Qijc[k] >= -bigM * xij[k] 

        # Voltage constraints by coupling with switch variable
        base_Z = 7.2**2
        M = 4
        unit = 1.
        # Phase A
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_aa,x_aa,r_ab,x_ab,r_ac,x_ac = Rmatrix[0], Xmatrix[0], Rmatrix[1], Xmatrix[1], Rmatrix[2], Xmatrix[2]
            # Write voltage constraints
            if l['is_Switch'] == 1:
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1000)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1000)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1000)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1000)*Qijc[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1000)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1000)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1000)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1000)*Qijc[k] + M*(1-xij[k]) >= 0
            else: 
                prob += Via[ind1]-Via[ind2] - \
                2*r_aa*length/(unit*base_Z*1000)*Pija[k]- \
                2*x_aa*length/(unit*base_Z*1000)*Qija[k]+ \
                (r_ab+np.sqrt(3)*x_ab)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_ab-np.sqrt(3)*r_ab)*length/(unit*base_Z*1000)*Qijb[k] +\
                (r_ac-np.sqrt(3)*x_ac)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_ac+np.sqrt(3)*r_ac)*length/(unit*base_Z*1000)*Qijc[k] == 0

        # Phase B
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_bb,x_bb,r_ba,x_ba,r_bc,x_bc = Rmatrix[4], Xmatrix[4], Rmatrix[3], Xmatrix[3], Rmatrix[5], Xmatrix[5]
            # Write voltage constraints
            if l['is_Switch'] == 1:
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1000)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1000)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1000)*Qijc[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1000)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1000)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1000)*Qijc[k] + M*(1-xij[k]) >= 0
            else: 
                prob += Vib[ind1]-Vib[ind2] - \
                2*r_bb*length/(unit*base_Z*1000)*Pijb[k]- \
                2*x_bb*length/(unit*base_Z*1000)*Qijb[k]+ \
                (r_ba+np.sqrt(3)*x_ba)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ba-np.sqrt(3)*r_ba)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_bc-np.sqrt(3)*x_bc)*length/(unit*base_Z*1000)*Pijc[k] +\
                (x_bc+np.sqrt(3)*r_bc)*length/(unit*base_Z*1000)*Qijc[k] == 0

        # Phase C
        for m, l in enumerate(Linepar):
            k = l['index']
            n1 = l['from_br'] 
            n2 = l['to_br']    
            ind1 = Nodes.index(n1)
            ind2 = Nodes.index(n2)   
            length = l['length']
            Rmatrix =  l['r']
            Xmatrix =  l['x']
            r_cc,x_cc,r_ca,x_ca,r_cb,x_cb = Rmatrix[8], Xmatrix[8], Rmatrix[6], Xmatrix[6], Rmatrix[7], Xmatrix[7]
            # Write voltage constraints
            if l['is_Switch'] == 1:
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1000)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1000)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1000)*Qijb[k] - M*(1-xij[k]) <= 0
                # Another inequality        
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1000)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1000)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1000)*Qijb[k] + M*(1-xij[k]) >= 0
            else: 
                prob += Vic[ind1]-Vic[ind2] - \
                2*r_cc*length/(unit*base_Z*1000)*Pijc[k]- \
                2*x_cc*length/(unit*base_Z*1000)*Qijc[k]+ \
                (r_ca+np.sqrt(3)*x_ca)*length/(unit*base_Z*1000)*Pija[k] +\
                (x_ca-np.sqrt(3)*r_ca)*length/(unit*base_Z*1000)*Qija[k] +\
                (r_cb-np.sqrt(3)*x_cb)*length/(unit*base_Z*1000)*Pijb[k] +\
                (x_cb+np.sqrt(3)*r_cb)*length/(unit*base_Z*1000)*Qijb[k] == 0
        
        # Initialize source bus at 1.05 p.u. V^2 = 1.1025
        prob += Via[0] == 1.1025
        prob += Vib[0] == 1.1025
        prob += Vic[0] == 1.1025

        # Insert Fault        
        pr = OpenSw(fault, Linepar)
        op = pr.fault_isolation()
        for k in range(len(op)):
            prob += xij[op[k]] == 0
        
        # Cyclic constraints
        fault = []
        f1 = OpenSw(fault, Linepar)
        loop = f1.find_all_cycles()
        for k in range(len(loop)):
            sw = loop[k]
            nSw_C =  len(sw) 
            prob += lpSum(xij[sw[j]] for j in range(nSw_C)) <= nSw_C - 1

        # No reverse real power flow in substation
        sub = [4, 27, 34]
        for s in sub:
            prob += Pija[s] >= 0
            prob += Pijb[s] >= 0
            prob += Pijc[s] >= 0

        # Transformers KVA ratings. Three main transformers for three substation are at:
        # The transformers are located at index 6, 30, and 37 and their rating is: 
        Xfm = [6, 30, 37]
        print ('..........')
        # Call solver 
        # prob.solve()
        prob.solve(CPLEX(msg=0))
        prob.writeLP("Check.lp")
        print ("Status:", LpStatus[prob.status])
        print(Pija[0].varValue, Pijb[0].varValue, Pijc[0].varValue )
        print(Pija[0].varValue + Pijb[0].varValue + Pijc[0].varValue)
        print ('..........')
        print(Qija[0].varValue, Qijb[0].varValue, Qijc[0].varValue )
        print(Qija[0].varValue + Qijb[0].varValue + Qijc[0].varValue)
        print ('..........')

        # Each substation power flow
        print(' Substation #1:', Pija[4].varValue, Pijb[4].varValue, Pijc[4].varValue )
        print(' Substation #2:', Pija[27].varValue, Pijb[27].varValue, Pijc[27].varValue )
        print(' Substation #3:', Pija[34].varValue, Pijb[34].varValue, Pijc[34].varValue )
        print ('..........')
        print(' Tie Switch Status:')        
        for k in range(len(No)):
            print(xij[No[k]].varValue)