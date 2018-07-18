# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 07:58:40 2018

@author: Tongli
"""
import numpy as np
import time
from sympy import *
import random
from natsort import natsorted

t0 = time.clock()
SocialPrb=0.2
UpdatePrb=0.25
AgentCount=2000
NetSiz=10
N=1
Pcvd=np.array(range(AgentCount))
pInd=np.array(range(AgentCount))*0.01
pLvlNow=Pcvd*pInd
Growth_markov=np.array(range(AgentCount))*0.1+11
#shock=np.array(range(AgentCount))
#shock=list(shock) #********************
#solution=0.01*np.array(range(AgentCount))#********************
##################################################
how_many_update = int(round(UpdatePrb*AgentCount))
base_bool = np.zeros(AgentCount,dtype=bool)
base_bool[0:how_many_update] = True
####################Permutation with Seed####################
#update = np.random.permutation(base_bool)
update = np.random.RandomState(seed=42).permutation(base_bool)
#############################################################
dont = np.logical_not(update)

how_many_social = int(round(SocialPrb*AgentCount))
social_bool = np.zeros(AgentCount,dtype=bool)
social_bool[0:how_many_social] = True 
##################Permutation with Seed######################
#social = np.random.permutation(social_bool)    
social = np.random.RandomState(seed=45).permutation(social_bool)
#############################################################
social_act=social&dont
social_index=np.where(social_act==True)[0]
how_many_act_social=len(social_index)

how_many_act_social=len(social_index)
###################################
social_index=np.array([   5,   19,   33,   44,   49,   52,   54,   60,   63,   69,   77,
         89,   96,   97,   99,  135,  139,  143,  152,  177,  193,  195,
        208,  210,  211,  212,  220,  222,  230,  233,  235,  237,  239,
        240,  242,  259,  272,  277,  287,  290,  291,  303,  309,  312,
        314,  327,  330,  344,  345,  350,  362,  368,  374,  397,  408,
        427,  428,  436,  440,  444,  445,  446,  455,  470,  475,  477,
        480,  494,  518,  519,  525,  537,  539,  550,  556,  560,  569,
        571,  577,  584,  585,  586,  590,  594,  595,  600,  602,  631,
        633,  635,  638,  645,  656,  663,  665,  668,  679,  687,  688,
        706,  707,  717,  730,  732,  738,  742,  744,  756,  761,  770,
        784,  813,  817,  824,  832,  841,  845,  848,  851,  855,  857,
        861,  866,  869,  870,  872,  878,  886,  890,  892,  900,  905,
        907,  909,  920,  923,  928,  942,  945,  954,  957,  971,  972,
        983,  985, 1000, 1001, 1010, 1016, 1018, 1043, 1046, 1055, 1058,
       1060, 1063, 1064, 1074, 1084, 1095, 1098, 1099, 1103, 1104, 1110,
       1111, 1114, 1115, 1118, 1128, 1138, 1149, 1163, 1173, 1208, 1209,
       1223, 1228, 1234, 1237, 1239, 1243, 1255, 1258, 1266, 1273, 1274,
       1287, 1295, 1296, 1300, 1302, 1310, 1311, 1319, 1321, 1322, 1327,
       1345, 1361, 1364, 1367, 1373, 1374, 1399, 1405, 1406, 1408, 1409,
       1416, 1423, 1424, 1426, 1427, 1437, 1446, 1448, 1451, 1459, 1462,
       1476, 1478, 1501, 1508, 1510, 1511, 1521, 1525, 1536, 1538, 1542,
       1543, 1544, 1547, 1555, 1582, 1592, 1593, 1596, 1598, 1599, 1624,
       1625, 1633, 1639, 1641, 1647, 1658, 1662, 1666, 1672, 1673, 1692,
       1699, 1706, 1728, 1730, 1732, 1733, 1740, 1748, 1749, 1754, 1759,
       1760, 1775, 1780, 1783, 1789, 1793, 1803, 1804, 1825, 1828, 1836,
       1838, 1841, 1852, 1871, 1872, 1894, 1896, 1898, 1913, 1918, 1923,
       1926, 1930, 1948, 1960, 1964, 1969, 1985, 1996, 1997])
how_many_act_social=len(social_index)
#Assign agents with overlap neighborhood into one group based on their distance between each other
Agent_dis=social_index[1:]-social_index[0:how_many_act_social-1]
Group=[]
#First_group is the group that includes the first socially update agent in the row
First_group=[social_index[0]]
#Start_from is the index of first socially update agent after all agents in First_group
Start_from=1
#Find the overlap group that contains the first socially update agent
for i in range(how_many_act_social-1):
    if (Agent_dis[i]<=NetSiz):
        First_group.append(social_index[i+1])
        Start_from=i+2
    else:
        break
#End_group is the group that includes the last socially update agent in the row
GroupSiz=0 #measures the total number of agents in the first group and the end group
if (Start_from<=(how_many_act_social-1)):
    Combine=False
    Combine_group=[]
    End_group=[social_index[how_many_act_social-1]]
    End_at=how_many_act_social-1-1
    for i in range(how_many_act_social-2,Start_from-1,-1):
        if (Agent_dis[i]<=NetSiz):
            End_group.insert(0, social_index[i])
            End_at=i-1
        else:
            break
    if((social_index[0]+AgentCount-social_index[how_many_act_social-1])<=NetSiz):
        Combine=True
        Combine_group=np.array(End_group+First_group)
        Group.append(Combine_group)
        GroupSiz=len(Combine_group)
    else:
        Group.append(np.array(First_group))
        Group.append(np.array(End_group))
        GroupSiz=len(First_group)+len(End_group)

else:   
    Group.append(np.array(First_group))
    GroupSiz=len(First_group)
#Assign all other socially update agents into group
Start=Start_from
End=End_at
Insert_at=1
if(GroupSiz<=how_many_act_social):
    while(Start<=End):
        MovGroup=[social_index[Start]]
        i=Start
        while (i<=End):
            if (Agent_dis[i]<=NetSiz):
               MovGroup.append(social_index[i+1])
               i=i+1
            else:
                Start=i+1
                Group.insert(Insert_at,np.array(MovGroup))
                Insert_at=Insert_at+1
                MovGroup=[]
                break

########################
#solve linear equation system for simultaneously socially updating agents
Pcvd_pre=Pcvd
Num_groups=len(Group)
################Need to change it to PSocial in actural program
PSocial=np.array(range(AgentCount))*0.0001
Growth_social=Growth_markov
for i in range(Num_groups):
    #print(i)
    Num_agent_in_group=len(Group[i])
    if (Num_agent_in_group<=1):
        Social_pos=Group[i][0]
        Left_sum_char=sum(pLvlNow[(Social_pos-NetSiz):(Social_pos)])
        #########################growth1
        Left_growth=list(Growth_markov[(Social_pos-NetSiz):(Social_pos)])
        #########################growth1
        if ((Social_pos-NetSiz)<0):
            Left_sum_char=sum(pLvlNow[(Social_pos+AgentCount-NetSiz):])+sum(pLvlNow[0:(Social_pos)])
            ########################growth2
            Left_growth=list(Growth_markov[(Social_pos+AgentCount-NetSiz):])+list(Growth_markov[0:(Social_pos)])
            #######################growth2
        if (Social_pos+NetSiz<=(AgentCount-1)):
            Right_sum_char=sum(pLvlNow[(Social_pos+1):(Social_pos+NetSiz+1)])
            #########################growth3
            Right_growth=list(Growth_markov[(Social_pos+1):(Social_pos+NetSiz+1)])
            #########################growth3
        if (Social_pos+NetSiz>(AgentCount-1)):
            if ((Social_pos+1)>(AgentCount-1)):
                Right_sum_char=sum(pLvlNow[0:NetSiz])
                #########################growth4
                Right_growth=list(Growth_markov[0:NetSiz])
                #########################growth4
            else:
                Right_sum_char=sum(pLvlNow[(Social_pos+1):])+sum(pLvlNow[0:(Social_pos+NetSiz+1-AgentCount)])
                #########################growth5
                Right_growth=list(Growth_markov[(Social_pos+1):])+list(Growth_markov[0:(Social_pos+NetSiz+1-AgentCount)])
                #########################growth5
        PSocial[Social_pos]=(Left_sum_char+Right_sum_char+Pcvd_pre[Social_pos])/float(2*NetSiz+1)
        ########################growth6
        Growth_set=Left_growth+Right_growth
        Growth_social[Social_pos]=random.choice(Growth_set)
        ########################growth6
        
    else:
        Social_sym=symbols('a0:%d'%Num_agent_in_group)
        #######################growth7
        Population_sym=symbols('M0:%d'%AgentCount)
        #######################growth7
        
        #######################Change8
        Variable_dummy=list(Population_sym)
        #######################Change8
        Equations=[]
        Solution=[]
        ######################change for individual p
        Social_sym_p=symbols('p0:%d'%Num_agent_in_group)
        Variable_dummy_p=list(Pcvd)
        Equations_p=[]
        Solution_p=[]
        ######################change for individual p
        for index_of_index in range(Num_agent_in_group):
            Variable_dummy[Group[i][index_of_index]]=Social_sym[index_of_index]
            Variable_dummy_p[Group[i][index_of_index]]=Social_sym_p[index_of_index]
        Variable_dummy_p=Variable_dummy_p*pInd
        for index_of_index in range(Num_agent_in_group):
            Social_pos=Group[i][index_of_index]
            Left_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos-NetSiz):(Social_pos)]])
            Left_sum_p=sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[(Social_pos-NetSiz):(Social_pos)]])
            if ((Social_pos-NetSiz)<0):
                Left_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+AgentCount-NetSiz):]])+sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:Social_pos]])
                Left_sum_p=sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[(Social_pos+AgentCount-NetSiz):]])+sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[0:Social_pos]])
            if (Social_pos+NetSiz<=(AgentCount-1)):
                Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+1):(Social_pos+1+NetSiz)]])
                Right_sum_p=sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[(Social_pos+1):(Social_pos+1+NetSiz)]])
            if (Social_pos+NetSiz>(AgentCount-1)):
                if ((Social_pos+1)>(AgentCount-1)):
                    Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:NetSiz]])
                    Right_sum_p=sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[0:NetSiz]])
                else:
                    Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+1):]])+sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:(Social_pos+NetSiz+1-AgentCount)]])
                    Right_sum_p=sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[(Social_pos+1):]])+sum([Variable_dummy_pi for Variable_dummy_pi in Variable_dummy_p[0:(Social_pos+NetSiz+1-AgentCount)]])
            s=((Left_sum+Right_sum)/(2*NetSiz)-Variable_dummy[Social_pos])
            s_p=(Left_sum_p+Right_sum_p)/float(2*NetSiz)-Social_sym_p[index_of_index]
            Equations.append(s)
            Equations_p.append(s_p)
        
        #####################change9
        Solution=solve(Equations,Social_sym,simplify=False,rational=False)
        Solution_p=solve(Equations_p,Social_sym_p,simplify=False,rational=False)
        #####################change9
        for index_of_index in range(Num_agent_in_group):
            Social_pos=Group[i][index_of_index]
            #######################growth10
            Name_set=natsorted([str(Name) for Name in list(Solution[Social_sym[index_of_index]].free_symbols)])
            Gro_Value_set=[Growth_social[int(Name[1:])] for Name in Name_set]
            Prob_set=Poly(Solution[Social_sym[index_of_index]]).coeffs()
            Growth_social[Social_pos]=np.random.choice(Gro_Value_set,1,p=Prob_set)
            PSocial[Social_pos]=Solution_p[Social_sym_p[index_of_index]]
t1=time.clock()
print('Total time to run is '+str(t1-t0)+'s.')
