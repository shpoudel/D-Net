import win32com.client
import matplotlib.pyplot as plt
import json
import networkx as nx 
import numpy as np

class Power_Flow:
    """
    This code is for extracting the data from OpenDSS (Line parameters, Load, Graph, Xfrms). 
    Also, the load in secondary is transferred into primary side if service transformer is not modeled
 
    """
    def __init__(self, f2, f3, filename = ""):
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

        # use the Text interface to OpenDSS
        self.text = self.engine.Text
        self.circuit = self.engine.ActiveCircuit
        self.DSSLines = self.circuit.Lines
        self.DSSXfrm = self.circuit.Transformers
        self.DSSLoad = self.circuit.Loads        
        if filename != "":
            self.text.Command = "compile " + filename        
        self.G = nx.Graph()
        
    # Checking the interface
    def Solve(self, f2, f3):    
        
        line_ind = 0
        Linepar = []   
        Xfmr = []  
        nor_open = ['ln0653457_sw','v7173_48332_sw', 'tsw803273_sw', 'a333_48332_sw','tsw320328_sw',\
                   'a8645_48332_sw','tsw568613_sw', 'wf856_48332_sw', 'wg127_48332_sw']    
        for i in range(7):
            next (f2)  
        for k in range(7):
            next(f3)

        for line in f2:
            if line.strip():                               
                row = line.split()
                element = row[0].strip('"')
                attr = element.split('.') 
                # Store lines from the network              
                if attr[0] == 'Line': 
                    el_name = attr[1]  
                    self.DSSLines.Name = el_name
                    if self.DSSLines.Name not in nor_open:
                        is_sw = 0
                        if self.DSSLines.R1 == 0.001:
                            is_sw = 1
                        bus1 = self.DSSLines.Bus1.split('.')
                        Phase ='ABC'
                        if len(bus1) >= 2:
                            ph = bus1[1:]                          
                            if ph == ['1']:
                                Phase = 'A'
                            if ph == ['2']:
                                Phase = 'B'
                            if ph == ['3']:
                                Phase = 'C'
                            if ph == ['1','3']:
                                Phase = 'AC'
                        message = dict(line = self.DSSLines.Name,
                                    index = line_ind,
                                    from_br = row[1],
                                    to_br = row[2],
                                    is_Switch = is_sw,
                                    nPhase = self.DSSLines.Phases,
                                    Phase = Phase,
                                    length = self.DSSLines.Length,
                                    r = self.DSSLines.Rmatrix,
                                    x = self.DSSLines.Xmatrix)
                        Linepar.append(message)
                        line_ind += 1   
                        self.G.add_edge(row[1], row[2])

                # Store transformers from the network
                if attr[0] == 'Transformer': 
                    el_name = attr[1]               
                    self.DSSXfrm.Name = el_name
                    # Treat them as switch where no loss occurs and length is small
                    message = dict(line = self.DSSXfrm.Name,
                                   index = line_ind,
                                   from_br = row[1],
                                   to_br = row[2],
                                   is_Switch = 0,
                                   nPhase = 3,
                                   Phase = 'ABC',
                                   length = 0.001,
                                   r = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001],
                                   x = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001])
                    Xfmr.append(message)
                    line_ind += 1 
                    Linepar.append(message)
                    self.G.add_edge(row[1], row[2])
                
                if attr[0] == 'Reactor':
                    # Treat them as switch where no loss occurs and length is small
                    message = dict(line = 'HVMV_SUB_HSB',
                                   index = line_ind,
                                   from_br = row[1],
                                   to_br = row[2],
                                   is_Switch = 0,
                                   length = 0.001,
                                   nPhase = 3,
                                   Phase = 'ABC',
                                   r = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001],
                                   x = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001])
                    line_ind += 1 
                    self.G.add_edge(row[1], row[2])
                    Linepar.append(message)

        # BFS search for forming a radial tree from the network
        Tree = list(nx.bfs_tree(self.G, source = 'SOURCEBUS').edges())
        Nodes = list(nx.bfs_tree(self.G, source = 'SOURCEBUS').nodes())
        for line in Linepar:
            fr_to = set([line['from_br'], line['to_br']])
            for k in range(self.G.number_of_edges()):
                edge = set(list(Tree[k]))
                if fr_to == edge:
                    line['index'] = k                    

        # Nodes = list(nx.bfs_tree(self.G, source = 'SOURCEBUS').nodes())
        print("\n Number of Nodes:", self.G.number_of_nodes(), "\n", "Number of Edges:", self.G.number_of_edges())

        # Adding normally open switches in the Graph and updating tree with those switches
        for line in f3:
            if line.strip():                              
                row = line.split()
                element = row[0].strip('"')
                attr = element.split('.') 
                # Store lines from the network              
                if attr[0] == 'Line': 
                    el_name = attr[1]  
                    self.DSSLines.Name = el_name
                    if self.DSSLines.Name in nor_open:                    
                        message = dict(line = self.DSSLines.Name,
                                        index = line_ind,
                                        from_br = row[1],
                                        to_br = row[2],
                                        is_Switch = 1,
                                        length = 0.001,
                                        nPhase = self.DSSLines.Phases,
                                        Phase = 'ABC',
                                        r = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001],
                                        x = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001])
                        line_ind += 1 
                        Linepar.append(message)
                        self.G.add_edge(row[1], row[2])
                        SW = (row[1], row[2])
                        Tree.append(SW)

        with open('LineData.json', 'w') as fp:
            json.dump(Linepar, fp)
        print("\n", "Number of Edges with switches:", self.G.number_of_edges())
        # print(list(nx.find_cycle(self.G, source = 'SOURCEBUS', orientation=None)))
        Num_Cycles = len(nx.cycle_basis(self.G, root = 'SOURCEBUS'))
        loops = (nx.cycle_basis(self.G.to_undirected()))
        # Check if the edges in cycle has switches. If yes, then number of closed switches has to be limited for 
        # ensuring the radial operation
        fr, to = zip(*Tree)
        fr = list(fr)
        to = list(to) 

        # Checking Linepar and forming R and X matrix to be 9 by 9 always. Especially the capacitor control element
        # and two phase line. Other will be always 9*9
        for line in Linepar:
            if line['nPhase'] == 2:
                line['r'] = [1.13148, 0.0, 0.142066, 0.0, 0.001, 0.0, 0.142066, 0.0, 1.13362]
                line['x'] = [0.884886, 0.0, 0.366115, 0.0, 0.001, 0.0, 0.366115, 0.0, 0.882239]

        for line in Linepar:
            if line['nPhase'] == 1 and line['Phase'] == 'A':
                r = line['r']
                x = line['x']
                line['r'] = [r[0], 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001]
                line['x'] = [x[0], 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001]

        for line in Linepar:
            if line['nPhase'] == 1 and line['Phase'] == 'B':
                r = line['r']
                x = line['x']
                line['r'] = [0.001, 0.0, 0.0, 0.0, r[0], 0.0, 0.0, 0.0, 0.001]
                line['x'] = [0.001, 0.0, 0.0, 0.0, x[0], 0.0, 0.0, 0.0, 0.001]

        for line in Linepar:
            if line['nPhase'] == 1 and line['Phase'] == 'C':
                r = line['r']
                x = line['x']
                line['r'] = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, r[0]]
                line['x'] = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, x[0]]

        cap = [32, 605, 482, 1811]
        for line in Linepar:
            if line['index'] in cap:
                line['r'] = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001]
                line['x'] = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001]

        # Add few more lines for DG virtual switch
        message = dict(line = 'dgv1',
                            index = 2754,
                            from_br = 'SOURCEBUS',
                            to_br = 'M1209DER480-1',
                            is_Switch = 1,
                            length = 0.001,
                            nPhase = 3,
                            Phase = 'ABC',
                            r = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001],
                            x = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001])
        Linepar.append(message)
        message = dict(line = 'dgv2',
                            index = 2755,
                            from_br = 'SOURCEBUS',
                            to_br = 'M1142DER480-1',
                            is_Switch = 1,
                            length = 0.001,
                            nPhase = 3,
                            Phase = 'ABC',
                            r = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001],
                            x = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001])
        Linepar.append(message)
        return  Linepar, Tree, self.G, Nodes    
     
   


