'''
This module runs the exercises and regressions for the cAndCwithStickyE paper.
User can choose which among the three models are actually run.  Descriptive
statistics and regression results are both output to screen and saved in a log
file in the results directory.  TeX code for tables in the paper are saved in
the tables directory.  See StickyEparams for calibrated model parameters.
'''

import sys 
import os
#sys.path.insert(0, os.path.abspath('../'))
#sys.path.insert(0, os.path.abspath('../ConsumptionSaving'))

import numpy as np
import csv
from time import clock
from copy import deepcopy
import subprocess
from SocialEmodel_current_IndividualP_no_pre_growth import StickyEmarkovConsumerType, StickyEmarkovRepAgent, StickyCobbDouglasMarkovEconomy
from ConsAggShockModel import SmallOpenMarkovEconomy
from HARKutilities import plotFuncs
import matplotlib.pyplot as plt
import scipy as sp
import SocialEparams as Params
from StickyEtools import makeStickyEdataFile, runStickyEregressions, makeResultsTable,\
                  runStickyEregressionsInStata, makeParameterTable, makeEquilibriumTable,\
                  makeMicroRegressionTable, extractSampleMicroData, makeuCostVsPiFig, \
                  makeValueVsAggShkVarFig, makeValueVsPiFig

# Choose which models to do work for
do_SOE  = True
do_DSGE = False
do_RA   = False

# Choose what kind of work to do for each model
run_models = True       # Whether to solve models and generate new simulated data
calc_micro_stats = True # Whether to calculate microeconomic statistics (only matters when run_models is True)
make_tables = False      # Whether to make LaTeX tables in the /Tables folder
make_emp_table = False   # Whether to run regressions for the U.S. empirical table (automatically done in Stata)
make_histogram = False   # Whether to construct the histogram of "habit" parameter estimates (automatically done in Stata)
use_stata = False        # Whether to use Stata to run the simulated time series regressions
save_data = True        # Whether to save data for use in Stata (as a tab-delimited text file)
run_ucost_vs_pi = False  # Whether to run an exercise that finds the cost of stickiness as it varies with update probability
run_value_vs_aggvar = False # Whether to run an exercise to find value at birth vs variance of aggregate permanent shocks

ignore_periods = Params.ignore_periods # Number of simulated periods to ignore as a "burn-in" phase
interval_size = Params.interval_size   # Number of periods in each non-overlapping subsample
total_periods = Params.periods_to_sim  # Total number of periods in simulation
interval_count = (total_periods-ignore_periods)/interval_size # Number of intervals in the macro regressions
periods_to_sim_micro = Params.periods_to_sim_micro # To save memory, micro regressions are run on a smaller sample
AgentCount_micro = Params.AgentCount_micro # To save memory, micro regressions are run on a smaller sample
my_counts = [interval_size,interval_count]
alt_counts = [interval_size*interval_count,1]
mystr = lambda number : "{:.3f}".format(number)
results_dir = Params.results_dir
empirical_dir = Params.empirical_dir

# Define the function to run macroeconomic regressions, depending on whether Stata is used
if use_stata:
    runRegressions = lambda a,b,c,d,e : runStickyEregressionsInStata(a,b,c,d,e,Params.stata_exe)
else:
    runRegressions = lambda a,b,c,d,e : runStickyEregressions(a,b,c,d,e)

#Chosse the folder to save the output graphs
Folder_path='..\Result'

Min_siz=1
Max_siz=2
# Run models and save output if this module is called from main
if __name__ == '__main__':
    
    ###############################################################################
    ########## SMALL OPEN ECONOMY WITH MACROECONOMIC MARKOV STATE##################
    ###############################################################################
    c_std=[]
    C_std=[]
    #print('Size of the social network is:',NetSiz)
    Params.init_SOE_mrkv_consumer['NetSiz']=1
    StickySOEmarkovBaseType = StickyEmarkovConsumerType(**Params.init_SOE_mrkv_consumer)
    StickySOEmarkovBaseType.IncomeDstn[0] = Params.StateCount*[StickySOEmarkovBaseType.IncomeDstn[0]]
    StickySOEmarkovBaseType.track_vars = ['aLvlNow','cLvlNow','yLvlNow','pLvlTrue','t_age','TranShkNow']
    StickySOEmarkovConsumers = []
    for n in range(Params.TypeCount):
        StickySOEmarkovConsumers.append(deepcopy(StickySOEmarkovBaseType))
        StickySOEmarkovConsumers[-1].seed = n
        StickySOEmarkovConsumers[-1].DiscFac = Params.DiscFacSetSOE[n]
            
    # Make a small open economy for the agents
    StickySOmarkovEconomy = SmallOpenMarkovEconomy(agents=StickySOEmarkovConsumers, **Params.init_SOE_mrkv_market)
    StickySOmarkovEconomy.track_vars += ['TranShkAggNow','wRteNow']
    StickySOmarkovEconomy.makeAggShkHist() # Simulate a history of aggregate shocks
    for n in range(Params.TypeCount):
        StickySOEmarkovConsumers[n].getEconomyData(StickySOmarkovEconomy) # Have the consumers inherit relevant objects from the economy
            
    # Solve the small open Markov model
    t_start = clock()
    StickySOmarkovEconomy.solveAgents()
    t_end = clock()
    print('Solving the small open Markov economy took ' + mystr(t_end-t_start) + ' seconds.')
    for NetSiz in range(Min_siz,Max_siz):
        print('Size of the social network is:',NetSiz)
#        Params.init_SOE_mrkv_consumer['NetSiz']=NetSiz
#        StickySOEmarkovBaseType = StickyEmarkovConsumerType(**Params.init_SOE_mrkv_consumer)
#        StickySOEmarkovBaseType.IncomeDstn[0] = Params.StateCount*[StickySOEmarkovBaseType.IncomeDstn[0]]
#        StickySOEmarkovBaseType.track_vars = ['aLvlNow','cLvlNow','yLvlNow','pLvlTrue','t_age','TranShkNow']
#        StickySOEmarkovConsumers = []
#        for n in range(Params.TypeCount):
#            StickySOEmarkovConsumers.append(deepcopy(StickySOEmarkovBaseType))
#            StickySOEmarkovConsumers[-1].seed = n
#            StickySOEmarkovConsumers[-1].DiscFac = Params.DiscFacSetSOE[n]
#            
#        # Make a small open economy for the agents
#        StickySOmarkovEconomy = SmallOpenMarkovEconomy(agents=StickySOEmarkovConsumers, **Params.init_SOE_mrkv_market)
#        StickySOmarkovEconomy.track_vars += ['TranShkAggNow','wRteNow']
#        StickySOmarkovEconomy.makeAggShkHist() # Simulate a history of aggregate shocks
#        for n in range(Params.TypeCount):
#                StickySOEmarkovConsumers[n].getEconomyData(StickySOmarkovEconomy) # Have the consumers inherit relevant objects from the economy
#            
#        # Solve the small open Markov model
#        t_start = clock()
#        StickySOmarkovEconomy.solveAgents()
#        t_end = clock()
#        print('Solving the small open Markov economy took ' + mystr(t_end-t_start) + ' seconds.')
        
        # Plot the consumption function in each Markov state
        print('Consumption function for one type in the small open Markov economy:')
        m = np.linspace(0,20,500)
        M = np.ones_like(m)
        c = np.zeros((Params.StateCount,m.size))
        for i in range(Params.StateCount):
            c[i,:] = StickySOEmarkovConsumers[0].solution[0].cFunc[i](m,M)
            plt.plot(m,c[i,:])
        plt.show()
            
        # Simulate the sticky small open Markov economy
        t_start = clock()
        for agent in StickySOmarkovEconomy.agents:
            agent(UpdatePrb = 1.0)
            agent(SocialPrb = 0.0)
            agent(NetSiz = NetSiz)
        StickySOmarkovEconomy.makeHistory()
        t_end = clock()
        print('Simulating the sticky small open Markov economy took ' + mystr(t_end-t_start) + ' seconds.')
        # Make results for the sticky small open Markov economy
        desc = 'Results for the sticky small open Markov economy with update probability ' + mystr(Params.UpdatePrb)
        name = 'SocialEFrictionP'+str(Min_siz)+'_'+str(Max_siz)
        makeStickyEdataFile(StickySOmarkovEconomy,ignore_periods,description=desc,filename=name,save_data=save_data,calc_micro_stats=calc_micro_stats)
        if calc_micro_stats:
            micro_stat_periods = int((StickySOmarkovEconomy.agents[0].T_sim-ignore_periods)*0.1)
            sticky_SOEmarkov_micro_data = extractSampleMicroData(StickySOmarkovEconomy, np.minimum(StickySOmarkovEconomy.act_T-ignore_periods-1,periods_to_sim_micro), np.minimum(StickySOmarkovEconomy.agents[0].AgentCount,AgentCount_micro), ignore_periods)
            not_newborns = (np.concatenate([this_type.t_age_hist[(ignore_periods+1):(ignore_periods+micro_stat_periods),:] for this_type in StickySOmarkovEconomy.agents],axis=1) > 1).flatten()
        DeltaLogC_stdev = np.genfromtxt(results_dir + name+'Results.csv', delimiter=',')[3]    
        Deltalogc_stdev=np.nanstd(sticky_SOEmarkov_micro_data[not_newborns,0])
        C_std.append(DeltaLogC_stdev)
        c_std.append(Deltalogc_stdev)

#############################################################
    DeltaLogC_stdev_frictionless=0.010551994946000001
    DeltaLogc_stdev_frictionless=0.060693527772294961
    DeltaLogC_stdev_sticky=0.00681149331603
    Deltalogc_stdev_sticky=0.061464262113268463
    Var_C_frictionless=DeltaLogC_stdev_frictionless**2
    Var_c_frictionless=DeltaLogc_stdev_frictionless**2
    Var_C_Sticky=DeltaLogC_stdev_sticky**2
    Var_c_Sticky=Deltalogc_stdev_sticky**2
    
    Social_siz=np.array(list(range(Min_siz,Max_siz)))
    c_std=np.array(c_std)**2
    C_std=np.array(C_std)**2
    Name_Agg='\Standard_Aggregate_Variance_Growth'+'_Min_'+str(Min_siz)+'_Max_'+str(Max_siz)+'.csv'
    Name_Ind='\Standard_Individual_Variance_Growth'+'_Min_'+str(Min_siz)+'_Max_'+str(Max_siz)+'.csv'
    Agg_path=Folder_path+Name_Agg
    Ind_path=Folder_path+Name_Ind
    np.savetxt(Agg_path, C_std, delimiter=",")
    np.savetxt(Ind_path, c_std, delimiter=",")
    
    #plt.title('Change in Std of Aggregate Consumption Following Increase in the size of Social Network')
    #plt.figure(figsize=(20,20))
    #plt.rcParams.update({'axes.labelsize': 'medium'})
    Result_data_path = Folder_path+'\AggCVar_Growth_NetSize_'+str(Min_siz)+'_'+str(Max_siz)+'.png'
    plt.ylabel('Variance of Aggregate Consumption')
    plt.xlabel('Size of Social Network')    
    plt.ylim(0.0,0.0004)
    plt.xlim(0.0,Max_siz+4)
    plt.scatter(Social_siz,C_std)
    plt.gcf().subplots_adjust(left=0.15)
    # Draw the line for StickyE solution
    Sticky_C=np.ones(Max_siz+5)*Var_C_Sticky
    Frictionless_C=np.ones(Max_siz+5)*Var_C_frictionless
    Sticky_x=np.arange(Max_siz+5)
    StickyLine, =plt.plot(Sticky_x,Sticky_C, '-',color='red')
    FrictionlessLine, =plt.plot(Sticky_x,Frictionless_C, '-',color='blue')
    #plt.legend(handles=[StickyLine, FrictionlessLine])
    plt.legend([StickyLine, FrictionlessLine], ['StickyE', 'Frictionless'],loc='upper right')
    #plt.plot(Social_siz, m*Social_siz + b, '-')
    plt.savefig(Result_data_path,dpi=600)
    slope, intercept, r_value, p_value, std_err = sp.stats.linregress(Social_siz,C_std)
    print('Slope=' + str(slope) + ', intercept=' + str(intercept) + ', r_square=' + str(r_value**2) + ', p_value=' + str(p_value)+', std=' + str(std_err))

    #plt.title('Change in Std of individual Consumption Following Increase in the size of Social Network')
    plt.clf()    
    Result_data_path = Folder_path+'\IndcVar_Growth_NetSize_'+str(Min_siz)+'_'+str(Max_siz)+'.png'
    plt.ylabel('Variance of Individual Consumption')
    plt.xlabel('Size of Social Network')    
    #plt.ylim(0.0,0.006)
    plt.xlim(0.0,Max_siz+4)
    plt.scatter(Social_siz,c_std)
    # Draw the linear fitted line
    #m, b = np.polyfit(Social_siz,c_std, 1)
    Frictionless_c=np.ones(Max_siz+5)*Var_c_frictionless
    Sticky_c=np.ones(Max_siz+5)*Var_c_Sticky
    Sticky_x=np.arange(Max_siz+5)
    StickyLine, = plt.plot(Sticky_x,Sticky_c, '-',color='red')
    FrictionlessLine, = plt.plot(Sticky_x,Frictionless_c, '-',color='blue')
    plt.legend([StickyLine, FrictionlessLine], ['StickyE', 'Frictionless'],loc='upper right')
    plt.savefig(Result_data_path,dpi=600)
    slope, intercept, r_value, p_value, std_err = sp.stats.linregress(Social_siz,c_std)
    print('Slope=' + str(slope) + ', intercept=' + str(intercept) + ', r_square=' + str(r_value**2) + ', p_value=' + str(p_value)+', std=' + str(std_err))
#####################################################################

#9.98577527e-06 growth=1, lagged
#