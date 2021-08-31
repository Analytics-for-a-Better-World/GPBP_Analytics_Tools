#!/usr/bin/env python
# coding: utf-8

def getvariables(n, m, X, Y):
    
    import numpy as np
    
    Xvalues = np.zeros(m)
    Yvalues = np.zeros(n+m)
    for i in range(m):
        Xvalues[i]=X[i].x
    for i in range(n):
        Yvalues[i]=Y[i].x
    
    return(Xvalues, Yvalues)
    

def OptimizationModel(array_household, current_hospitals_ID, new_hospitals_ID, distance_matrix, S, hosp_count, maxTimeInSeconds=100, mipGap=.01, trace=False):
    
    import time
    import gurobipy as gb
    from gurobipy import GRB
    import numpy as np
    import pandas as pd
    
    #Data preprocessing
    tstart = time.time()
    obj_val_array = []
    existinghosp = len(current_hospitals_ID)
    m = len(current_hospitals_ID) + len(new_hospitals_ID)
    n = len(array_household)
    p = existinghosp + 0       #total number of hospitals to be optimized
    
    # Only keep the combinations of houses/hospitals which are less or equal to the maximum distance
    dist = distance_matrix[distance_matrix.distance<=S]
    
    # collect the indices of the distances below the threshold 
    II = dist['Pop_ID']
    JJ = dist['Hosp/Cluster']
    
    IJ = { i : [] for i in range(n) }
    for i,j in zip(II,JJ):
        IJ[i].append(j) 
    
    # Create the model
    M = gb.Model("Facility location problem")
    
    M.Params.OutputFlag = trace 
    M.Params.mipgap     = mipGap
    M.Params.timelimit  = maxTimeInSeconds
    
    # Decision variables
    X = M.addVars(m, vtype=GRB.BINARY)
    Y = M.addVars(n, vtype=GRB.BINARY)
    
    # Objective
    obj = gb.LinExpr( array_household, Y.select('*') )
    M.setObjective(obj, gb.GRB.MAXIMIZE)
    
    # Constraints
    # Set existing hospitals to one
    M.addConstrs(X[j] == 1 for j in current_hospitals_ID)

    # Limit number of hospitals a household is connected to, let a household only connect to an opened facility
    M.addConstrs((Y[i] <= (gb.quicksum(X[j] for j in IJ[i]))) for i in range(n))
#     M.addConstrs(Y[i] <= (gb.quicksum(X[j] for j in dist['Hosp/Cluster'].loc[dist['Pop_ID']==i])) for i in range(n))

    
    # Limit number of facilities located 
    s = M.addLConstr(gb.quicksum(X[j] for j in range(m))<= p)
    
    tModelling = time.time()-tstart
    tstart = time.time()
    
    # Optimize the model and extract solution
    M.optimize() 
    obj_val = M.objVal
    Xvalues, Yvalues = getvariables(n, m, X, Y)

    obj_val_array.append([S,0,obj_val,list(Xvalues),list(Yvalues)])
    
    
    
    # Iterate for multiple additional hospital facilities
    for each_hosp_count in hosp_count:
        M.remove(s)
        p = existinghosp + each_hosp_count
        s = M.addConstr(gb.quicksum(X[j] for j in range(m))<= p, name = "Budget")
        
        M.optimize()
        obj_val = M.objVal
        Xvalues, Yvalues = getvariables(n, m, X, Y)

        obj_val_array.append([S,each_hosp_count,obj_val,list(Xvalues),list(Yvalues)])
    
    tSolving = time.time() - tstart 
    
    df_opt_array = pd.DataFrame(obj_val_array)
    df_opt_array.columns = ['km','number_of_new_hospitals','count','array_hosp','array_hh']
    df_opt_array['number_of_hospitals'] = df_opt_array['number_of_new_hospitals']+existinghosp
    df_opt_array['%'] = df_opt_array['count']*100/sum(array_household)
    df_opt_array['%'] = df_opt_array['%'].round(1)
    
    return df_opt_array, tModelling, tSolving
        
    

