# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 12:31:52 2018

@author: Tongli
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DeltaLogC_stdev_frictionless=0.010551994946000001
#DeltaLogc_stdev_frictionless=0.060693527772294961
DeltaLogc_stdev_frictionless=0.0977443702736
DeltaLogC_stdev_sticky=0.00681149331603
#Deltalogc_stdev_sticky=0.061464262113268463
Deltalogc_stdev_sticky=0.0976642990455
Var_C_frictionless=DeltaLogC_stdev_frictionless**2
Var_c_frictionless=DeltaLogc_stdev_frictionless**2
Var_C_Sticky=DeltaLogC_stdev_sticky**2
Var_c_Sticky=Deltalogc_stdev_sticky**2
Var_C_equiv=0.0000499465803926267
Var_c_equiv=0.0976269153799**2
#Var_c_equiv=0.0975644**2
plot_pcvd=False
#plot the variance of aggregate consumption for pcvd case
if plot_pcvd:
    Result_data_path='Pcvd_Agg.png'
    plt.ylabel('Variance of Aggregate Consumption')
    plt.xlabel('Size of Social Network') 
    Max_siz=10
    plt.xlim(0.0,Max_siz+4)
    plt.ylim(plt.ylim(0.0,0.0002))
    C_std=np.array(pd.read_csv('Pcvd_Agg.csv',header=None)[0])
    Social_siz=np.array(list(range(1,Max_siz+1)))
    plt.scatter(Social_siz,C_std)
    plt.gcf().subplots_adjust(left=0.15)
    # Draw the line for StickyE solution
    Sticky_C=np.ones(Max_siz+5)*Var_C_Sticky
    Frictionless_C=np.ones(Max_siz+5)*Var_C_frictionless
    Sticky_x=np.arange(Max_siz+5)
    StickyLine, =plt.plot(Sticky_x,Sticky_C, '-',color='red')
    FrictionlessLine, =plt.plot(Sticky_x,Frictionless_C, '-',color='blue')
    Equiv_C=np.ones(Max_siz+5)*Var_C_equiv
    EquivLine, =plt.plot(Sticky_x,Equiv_C, '-',color='green')
    #plt.legend(handles=[StickyLine, FrictionlessLine])
    plt.legend([StickyLine, FrictionlessLine, EquivLine], ['StickyE', 'Frictionless','Equiv-StickyE'],loc='upper right')
    plt.savefig(Result_data_path,dpi=600)
    plt.clf()
    #plot the variance of aggregate consumption for pcvd case
    Result_data_path='Pcvd_Ind.png'
    plt.ylabel('Variance of Individual Consumption')
    plt.xlabel('Size of Social Network') 
    Max_siz=10
    plt.xlim(0.0,Max_siz+4)
    #plt.ylim(plt.ylim(0.0,0.0002))
    c_std=np.array(pd.read_csv('Pcvd_Ind.csv',header=None)[0])
    Social_siz=np.array(list(range(1,Max_siz+1)))
    plt.scatter(Social_siz,c_std)
    plt.gcf().subplots_adjust(left=0.15)
    # Draw the line for StickyE solution
    Sticky_c=np.ones(Max_siz+5)*Var_c_Sticky
    Frictionless_c=np.ones(Max_siz+5)*Var_c_frictionless
    Sticky_x=np.arange(Max_siz+5)
    StickyLine, =plt.plot(Sticky_x,Sticky_c, '-',color='red')
    FrictionlessLine, =plt.plot(Sticky_x,Frictionless_c, '-',color='blue')
    Equiv_c=np.ones(Max_siz+5)*Var_c_equiv
    EquivLine, =plt.plot(Sticky_x,Equiv_c, '-',color='green')
    #plt.legend(handles=[StickyLine, FrictionlessLine])
    plt.legend([StickyLine, FrictionlessLine, EquivLine], ['StickyE', 'Frictionless','Equiv-StickyE'],loc='upper right')
    plt.savefig(Result_data_path,dpi=600)
'''
The follwoing code plot the variance of aggregate consumption 
and individual consumption for model simulation
'''
####Plot for simulation result of p with Individual factor
#plot the variance of aggregate consumption for pInd case
Result_data_path='p_agg.png'
plt.ylabel('Variance of Aggregate Consumption')
plt.xlabel('Size of Social Network')
C_std=np.array(pd.read_csv('p_agg.csv',header=None)[0]) 
Max_siz=len(C_std)
plt.xlim(0.0,Max_siz+4)
plt.ylim(plt.ylim(0.0,0.0003))
Social_siz=np.array(list(range(1,Max_siz+1)))
Social_siz[-1]=10
plt.scatter(Social_siz,C_std)
plt.plot(Social_siz,C_std)
plt.gcf().subplots_adjust(left=0.15)
# Draw the line for StickyE solution
Sticky_C=np.ones(Max_siz+5)*Var_C_Sticky
Frictionless_C=np.ones(Max_siz+5)*Var_C_frictionless
Sticky_x=np.arange(Max_siz+5)
StickyLine, =plt.plot(Sticky_x,Sticky_C, '-',color='red')
FrictionlessLine, =plt.plot(Sticky_x,Frictionless_C, '-',color='blue')
Equiv_C=np.ones(Max_siz+5)*Var_C_equiv
EquivLine, =plt.plot(Sticky_x,Equiv_C, '-',color='green')
#plt.legend(handles=[StickyLine, FrictionlessLine])
plt.legend([StickyLine, FrictionlessLine, EquivLine], ['StickyE', 'Frictionless','Equiv-StickyE'],loc='upper right')
plt.savefig(Result_data_path,dpi=600)
plt.clf()

#plot the variance of individual consumption for pInd case
Result_data_path='p_ind.png'
plt.ylabel('Variance of Individual Consumption')
plt.xlabel('Size of Social Network') 
c_std=np.array(pd.read_csv('p_ind.csv',header=None)[0])
Max_siz=len(c_std)
plt.xlim(0.0,Max_siz+4)
#plt.ylim(plt.ylim(0.0,0.0002))
Social_siz=np.array(list(range(1,Max_siz+1)))
Social_siz[-1]=10
plt.scatter(Social_siz,c_std)
plt.plot(Social_siz,c_std)
plt.gcf().subplots_adjust(left=0.15)
# Draw the line for StickyE solution
Sticky_c=np.ones(Max_siz+5)*Var_c_Sticky
Frictionless_c=np.ones(Max_siz+5)*Var_c_frictionless
Sticky_x=np.arange(Max_siz+5)
StickyLine, =plt.plot(Sticky_x,Sticky_c, '-',color='red')
FrictionlessLine, =plt.plot(Sticky_x,Frictionless_c, '-',color='blue')
Equiv_c=np.ones(Max_siz+5)*Var_c_equiv
EquivLine, =plt.plot(Sticky_x,Equiv_c, '-',color='green')
#plt.legend(handles=[StickyLine, FrictionlessLine])
plt.legend([StickyLine, FrictionlessLine, EquivLine], ['StickyE', 'Frictionless','Equiv-StickyE'],loc='upper right')
plt.savefig(Result_data_path,dpi=600)
plt.clf()