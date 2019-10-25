# D-Net

Network data structure of distribution feeders from OpenDSS. 

## Requirements

This repository requires OpenDSS to be installed and python packages like networkx, numpy, math. Run the optimization after extracting the data and forming the problem. Use PuLP or CPLEX if available.

## Execution

After cloning, run OpendssPy.py. It will invoke all the required class and run the optimization problem. The .txt files are obtained from OpenDSS using show->Elements and show->Buses. It might require slight manual modification in those txt files depending on regulator control and capacitor control element.
