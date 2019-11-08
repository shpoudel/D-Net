# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 22:50:45 2018
@author: Shiva
"""

# Python program to print all paths from a source to destination. 
import numpy as np
import networkx as nx
import json

class OpenSw(object):
    """
    Isolate the fault
    """
    def __init__(self, fault, LineSW):
        """
        Fault Isolation class.
        Parameters
        ----------
        fault : Fault Location in the feeder
        """
        self.fault = fault
        self.LineSW = LineSW

    def fault_isolation(self):   
        """
        Finds the set of switches to open for isolating the fault 
        """    
        nor_open = ['ln0653457_sw','v7173_48332_sw', 'tsw803273_sw', 'a333_48332_sw','tsw320328_sw',\
                   'a8645_48332_sw','tsw568613_sw', 'wf856_48332_sw', 'wg127_48332_sw']

        G = nx.Graph()        
        # For isolation take a meshed network
        for l in self.LineSW:
            G.add_edge(l['from_br'], l['to_br'])

        Source = 'SOURCEBUS'
        Fault = self.fault 
        print(" \n Now isolating the fault.... \n ")

        # ways stores all possible paths from source to fault location
        ways = list(nx.all_simple_paths(G, source = Source, target = Fault))
        s = []
        ind = []
        vector = []
        # Find all possible paths     
        for i in range(len(ways)):  
            flag = 0          
            ls = ways[i].__len__()   
            a = ways[i]
            isolate=[] 
            # print (ls, a)
            for m in range(ls-1):                
                store = set ([a[ls-m-1], a[ls-m-2]])
                for l in self.LineSW:
                    if l['is_Switch']:
                        check = set([l['from_br'], l['to_br']])
                        if check == store:
                            vector.append(check)
                            flag = 1
                            break
                if flag == 1:
                    break
        for v in vector:
            if v not in s:
                s.append(v)
        print ('The Switches to open for Fault Isolation are: \n ', s)
        

        # Find indices to include in optimization problem for x_ij variable
        for sw in s:
            for l in self.LineSW:
                if l['is_Switch']:
                    check = set([l['from_br'], l['to_br']])
                    if check == sw:
                        ind.append(l['index'])
        print('\n')
        print ('The indices to open for Fault Isolation are: \n ', ind) 
        return ind
    

    def find_all_cycles(self, source=None, cycle_length_limit=None):
        G = nx.Graph()
        G = nx.Graph()
        nor_open = ['wg127_48332_sw']
        for l in self.LineSW:
        # if l['line'] not in nor_open:
            G.add_edge(l['from_br'], l['to_br'])
        if source is None:
            # produce edges for all components
            nodes=[list(i)[0] for i in nx.connected_components(G)]            
        else:
            # produce edges for components with source
            nodes=[source]
        # extra variables for cycle detection:
        cycle_stack = []
        output_cycles = set()
    
        def get_hashable_cycle(cycle):
            m = min(cycle)
            mi = cycle.index(m)
            mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
            if cycle[mi-1] > cycle[mi_plus_1]:
                result = cycle[mi:] + cycle[:mi]
            else:
                result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
            return tuple(result)
        
        for start in nodes:
            if start in cycle_stack:
                continue
            cycle_stack.append(start)
            
            stack = [(start,iter(G[start]))]
            while stack:
                parent,children = stack[-1]
                try:
                    child = next(children)
                    
                    if child not in cycle_stack:
                        cycle_stack.append(child)
                        stack.append((child,iter(G[child])))
                    else:
                        i = cycle_stack.index(child)
                        if i < len(cycle_stack) - 2: 
                            output_cycles.add(get_hashable_cycle(cycle_stack[i:]))
                    
                except StopIteration:
                    stack.pop()
                    cycle_stack.pop()

        output_cycles = list(output_cycles)
        open_for_radial = []
        open_radial = []
        radial = []
        for k in range(len(output_cycles)):
            loop = output_cycles[k]
            res = []
            sw_cycle = []
            for i in range(len(loop)):                
                j = (i + 1) % len(loop)
                edge = {loop[i], loop[j]}
                for l in self.LineSW:
                    if l['is_Switch']:
                        check = set([l['from_br'], l['to_br']])
                        if check == edge:
                            res.append(check)
                            sw_cycle.append(l['index'])
            open_for_radial.append(res)
            radial.append(sw_cycle)
        return radial

    
