clear all
clc

fname = 'LineDataXY.json';
val = jsondecode(fileread(fname));

for k = 1:2745
    X = [];
    Y = [];
    X = [X val{k}.f_X val{k}.t_X];
    Y = [Y val{k}.f_Y val{k}.t_Y];
    
    if val{k}.feeder == 3
        plot(Y,X,'r','LineWidth',1)
    end
    if val{k}.feeder == 1
        plot(Y,X,'k','LineWidth',1)
    end
    if val{k}.feeder == 2
        plot(Y,X,'b','LineWidth',1)
    end
    if val{k}.feeder == 0
        plot(Y,X,'g','LineWidth',2)
    end
    hold on
end

DER1 = [46.71874612 -119.1699247];
plot(DER1(2),DER1(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER2 = [46.69740198 -119.1626142];
plot(DER2(2),DER2(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER3 = [46.72702242 -119.2273648];
plot(DER3(2),DER3(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER4 = [46.71025202 -119.1944673];
plot(DER4(2),DER4(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER5 = [46.66124764 -119.1730578];
plot(DER5(2),DER5(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER6 = [46.60462034,-119.1976004];
plot(DER6(2),DER6(1), 'v', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER7 = [46.60450,-119.1955];
plot(DER7(2),DER7(1), 'v', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER8 = [46.6081051 -119.1939451];
plot(DER8(2),DER8(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER9 = [46.60636272, -119.1939451];
plot(DER9(2),DER9(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER10 = [46.60462034 -119.1939451];
plot(DER10(2),DER10(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER11 = [46.67387988 -119.1177065]; 
plot(DER11(2),DER11(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
DER12 = [46.6777131,-119.0761929];
plot(DER12(2),DER12(1), 'o', 'MarkerEdgeColor','k','MarkerFaceColor','y', 'MarkerSize',3)
hold on
% Regultor and Capacitors
cap1 = [46.63797664,-119.1884169];
plot(cap1(2),cap1(1), 'v', 'MarkerEdgeColor','k','MarkerFaceColor','c', 'MarkerSize',5)
hold on
cap2 = [46.68625238,-119.0790649];
plot(cap2(2),cap2(1), 'v', 'MarkerEdgeColor','k','MarkerFaceColor','c', 'MarkerSize',5)
hold on
cap3 = [46.6822144,-119.1122683];
plot(cap3(2),cap3(1), 'v', 'MarkerEdgeColor','k','MarkerFaceColor','c', 'MarkerSize',5)
hold on
cap4 = [46.7210112,-119.1846503];
plot(cap4(2),cap4(1), 'v', 'MarkerEdgeColor','k','MarkerFaceColor','c', 'MarkerSize',5)
hold on

reg1 = [46.65406032,-119.1645463];
plot(reg1(2),reg1(1), 's', 'MarkerEdgeColor','k','MarkerFaceColor','m', 'MarkerSize',5)
hold on
reg2 = [46.71630678,-119.1902789];
plot(reg2(2),reg2(1), 's', 'MarkerEdgeColor','k','MarkerFaceColor','m', 'MarkerSize',5)
hold on
reg3 = [46.71529276,-119.1460857];
plot(reg3(2),reg3(1), 's', 'MarkerEdgeColor','k','MarkerFaceColor','m', 'MarkerSize',5)
hold on
regs = [46.69304604,-119.0738431];
plot(regs(2),regs(1), 's', 'MarkerEdgeColor','k','MarkerFaceColor','m', 'MarkerSize',5)
set(gca,'xtick',[])
set(gca,'ytick',[])






