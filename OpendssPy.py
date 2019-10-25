import win32com.client
import matplotlib.pyplot as plt
import json
import math
import numpy as np
import networkx as nx 
from Radial9500 import Power_Flow
from Optimization import Restoration


class Data:
    """
    This code is for extracting the data from OpenDSS (Line parameters, Load, Graph, Xfrms). 
    Also, the load in secondary is transferred into primary side if service transformer is not modeled
    shiva.poudel@wsu.edu 2019-10-25

    """
    def __init__(self, f, filename = ""):
        """
        Inputs:
            filename - string - DSS input file
        Side effects:
            start DSS via COM
        Contains the following DSS COM objects:
            engine
            text
            circuit
        """
        self.engine = win32com.client.Dispatch("OpenDSSEngine.DSS")
        self.engine.Start("0")

        self.text = self.engine.Text
        self.text.Command = "clear"
        self.circuit = self.engine.ActiveCircuit
        self.DSSLines = self.circuit.Lines
        self.DSSXfrm = self.circuit.Transformers
        self.DSSLoad = self.circuit.Loads        
        if filename != "":
            self.text.Command = "compile " + filename 
        self.G = nx.Graph()
        
    # Checking the interface
    def Extract_Data(self, f):        
        for i in range(7):
            next (f)  
        load_ind = 0  
        LoadData = []  
        Xfmr = []  
        xf_ind = 0
        for line in f:
            if line.strip():                               
                row = line.split()
                element = row[0].strip('"')
                attr = element.split('.') 

                # Store transformers from the network such that load behind the transformers are later on pulled back to primary
                if attr[0] == 'Transformer': 
                    el_name = attr[1]               
                    self.DSSXfrm.Name = el_name
                    message = dict(Xfmr = self.DSSXfrm.Name,
                                   index = xf_ind,
                                   from_br = row[1],
                                   to_br = row[2])
                    Xfmr.append(message)
                    xf_ind += 1 

                # Store loads from the network
                if attr[0] == 'Load': 
                    el_name = attr[1]               
                    self.DSSLoad.Name = el_name
                    load_ph = row[1]
                    message = dict(load = self.DSSLoad.Name,
                                   bus = row[1],
                                   index = load_ind,
                                   kW = self.DSSLoad.kW,
                                   Phase = load_ph[-1],
                                   pf = self.DSSLoad.pf,
                                   kVaR = self.DSSLoad.kW* np.tan(math.acos(self.DSSLoad.pf)))
                    LoadData.append(message)
                    load_ind += 1
        with open('XmfrData.json', 'w') as fp:
            json.dump(Xfmr, fp)
        return  Xfmr, LoadData
    
def TransferLoad(Xfmr, LoadData):       
    # Secondary load data transferred to Primary side via triplex line
    sumP = 0.
    sumQ = 0.
    for ld in LoadData:
        node = ld['bus'].strip('S')
        sumP += ld['kW']
        sumQ += ld['kVaR']
        # Find this node in Xfrm to_br
        for tr in Xfmr:
            sec = tr['to_br']
            if sec == node:
                # Transfer this load to primary and change the node name
                ld['bus'] = tr['from_br']
    print(sumP, sumQ)
    # Store Load data into json file
    with open('LoadData.json', 'w') as fp:
        json.dump(LoadData, fp)

if __name__ == '__main__':
    f1 = open("Test9500new_Elementsbal.txt","r")
    f2 = open("Test9500new_Elements_Radial.txt","r")
    f3 = open("Test9500new_Elements_Radial.txt","r")
    d1 = Data(f1,r"C:\Users\Auser\Desktop\Shiva\PyParse\IEEE9500\Master-bal-new.dss")

    # Extract Load and Xfmr data. The secondary loads are transferred into primary side
    Xfmr, LoadData  = d1.Extract_Data(f1)
    TransferLoad(Xfmr, LoadData)
    
    # Radial Class 
    # This class forms a graph and collects lineparameters for the edges within the Graph only.    
    d2 = Power_Flow(f2,f3, r"C:\Users\Auser\Desktop\Shiva\PyParse\IEEE9500\Master-bal-new.dss")
    Linepar, T, G, Nodes = d2.Solve(f2, f3)
    fault = ['M1125902']
    # fault = []
    opt = Restoration()    
    opt.res9500(Linepar, LoadData, fault)
    


