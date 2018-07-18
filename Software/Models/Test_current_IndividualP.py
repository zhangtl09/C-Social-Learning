# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 07:58:40 2018

@author: Tongli
"""
import numpy as np
import time
from sympy import *

t0 = time.clock()
SocialPrb=0.20
UpdatePrb=0.25
AgentCount=2000
NetSiz=2
N=1
Pcvd=np.array(range(AgentCount))
pInd=np.array(range(AgentCount))*0.01
pLvlNow=Pcvd*pInd
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
social = np.random.RandomState(seed=46).permutation(social_bool)
#############################################################
social_act=social&dont
social_index=np.where(social_act==True)[0]
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
for i in range(1):
    i=0
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
        Variable_dummy=list(Pcvd)
        Equations=[]
        Solution=[]
        for index_of_index in range(Num_agent_in_group):
            Variable_dummy[Group[i][index_of_index]]=Social_sym[index_of_index]
        Variable_dummy=Variable_dummy*pInd
        for index_of_index in range(Num_agent_in_group):
            Social_pos=Group[i][index_of_index]
            Left_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos-NetSiz):(Social_pos)]])
            if ((Social_pos-NetSiz)<0):
                Left_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+AgentCount-NetSiz):]])+sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:Social_pos]])
            if (Social_pos+NetSiz<=(AgentCount-1)):
                Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+1):(Social_pos+1+NetSiz)]])
            if (Social_pos+NetSiz>(AgentCount-1)):
                if ((Social_pos+1)>(AgentCount-1)):
                    Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:NetSiz]])
                else:
                    Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+1):]])+sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:(Social_pos+NetSiz+1-AgentCount)]])
            s=(Left_sum+Right_sum+Pcvd_pre[Social_pos])/float(2*NetSiz+1)-Social_sym[index_of_index]
            Equations.append(s)
        Solution=np.array(next(iter(linsolve(Equations,Social_sym))))
        for index_of_index in range(Num_agent_in_group):
            Social_pos=Group[i][index_of_index]
            PSocial[Social_pos]=Solution[index_of_index]
pLvlNow=pInd*PSocial
t1=time.clock()
print('Total time to run is '+str(t1-t0)+'s.')




















#SocialSolve=np.zeros(how_many_act_social, dtype=bool)
#
##End_dis=social_index[-1]-social_index[-2]
##End_overlap=(End_dis<=N)
#End_group=[social_index[-1]]
#
###################################################
##Solve for all equations code        
#
#Social_sym=symbols('a0:%d'%how_many_act_social)
#Vdummy=[]
#social_index_list=list(social_index)
#for i in range(AgentCount):
#    Vdummy.append(shock[i])
#    if(i in social_index):
#        j=social_index_list.index(i)
#        Vdummy[-1]=Social_sym[j]
##################################################    
#
#for i in range((how_many_act_social-1)):
#    OverlapGroup=[]
#    Equation=[]
#    Group_symbol=[]
#    Overlap_bool=False
#    if (~SocialSolve[i]):
#        Search=True
#        j=1
#        while (Search&(i+j<how_many_act_social)):
#            Forward=social_index[i+j]-social_index[i+j-1]
#            if (Forward<=N):
#                OverlapGroup.append(social_index[i+j-1])
#                if (i+j==how_many_act_social-1):
#                   End_group = OverlapGroup
#                j=j+1
#            else:
#                Search=False
#        
#        if (len(OverlapGroup)>0):
#           OverlapGroup.append(social_index[i+j-1])
#           Overlap_bool=True
#           IsEnd=(social_index[0] in OverlapGroup) & (social_index[-1] in OverlapGroup)
#           #print(OverlapGroup)
#           if(~IsEnd):
#               Group=OverlapGroup
#               Group_size=len(Group)
#               for k in range(Group_size):
#                   SocialPosition=Group[k]
#                   left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:SocialPosition]])
#                   right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:SocialPosition+N+1]])
#                   s=(left_sum+right_sum+shock[SocialPosition])/(2*N+1)-Vdummy[SocialPosition] 
#                   Equation.append(s)
#                   Index_of_index=social_index_list.index(Group[k])
#                   Symbol_k=Social_sym[Index_of_index]
#                   Group_symbol.append(Symbol_k)
#                   SocialSolve[Index_of_index]=True               
#               solution[Group]=np.array(next(iter(linsolve(Equation,Group_symbol))))
#               #print(Equation)
#        if (i==0):
#            if (Overlap_bool):
#                Front_group=OverlapGroup
#            else:
#                Front_group=[social_index[0]]
#            
#        
#    
#Equation=[]
#Group=[]
#Group_symbol=[]
####################################################
#Dis_back=social_index[0]+AgentCount-social_index[-1]
#Combine_bool=(Dis_back<=N)
#if (Combine_bool):
#    Equation=[]
#    Group=[]
#    Group_symbol=[]
#    Group=Front_group+End_group
#    Group_size=len(Group)
#    for k in range(Group_size):
#        SocialPosition=Group[k]
#        left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:SocialPosition]])
#        right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:SocialPosition+N+1]])
#        if (SocialPosition-N<0):
#            left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition]])
#        if (SocialPosition+N>(AgentCount-1)):
#            right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition+N-(AgentCount-1)]])
#        s=(left_sum+right_sum+shock[SocialPosition])/(2*N+1)-Vdummy[SocialPosition] 
#        Equation.append(s)
#        Index_of_index=social_index_list.index(Group[k])
#        Symbol_k=Social_sym[Index_of_index]
#        Group_symbol.append(Symbol_k)
#        SocialSolve[Index_of_index]=True               
#    solution[Group]=np.array(next(iter(linsolve(Equation,Group_symbol))))
#else:
#    if(len(Front_group)>1):
#        Equation=[]
#        Group=[]
#        Group_symbol=[]
#        Group=Front_group
#        Group_size=len(Group)
#        for k in range(Group_size):
#            SocialPosition=Group[k]
#            left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:SocialPosition]])
#            right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:SocialPosition+N+1]])
#            if (SocialPosition-N<0):
#                left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition]])
#            if (SocialPosition+N>(AgentCount-1)):
#                right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition+N-(AgentCount-1)]])
#            s=(left_sum+right_sum+shock[SocialPosition])/(2*N+1)-Vdummy[SocialPosition] 
#            Equation.append(s)
#            Index_of_index=social_index_list.index(Group[k])
#            Symbol_k=Social_sym[Index_of_index]
#            Group_symbol.append(Symbol_k)
#            SocialSolve[Index_of_index]=True               
#        solution[Group]=np.array(next(iter(linsolve(Equation,Group_symbol))))
#    if(len(End_group)>1):
#        Equation=[]
#        Group=[]
#        Group_symbol=[]
#        Group=End_group
#        Group_size=len(Group)
#        for k in range(Group_size):
#            SocialPosition=Group[k]
#            left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:SocialPosition]])
#            right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:SocialPosition+N+1]])
#            if (SocialPosition-N<0):
#                left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition]])
#            if (SocialPosition+N>(AgentCount-1)):
#                right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition+N-(AgentCount-1)]])
#            s=(left_sum+right_sum+shock[SocialPosition])/(2*N+1)-Vdummy[SocialPosition] 
#            Equation.append(s)
#            Index_of_index=social_index_list.index(Group[k])
#            Symbol_k=Social_sym[Index_of_index]
#            Group_symbol.append(Symbol_k)
#            SocialSolve[Index_of_index]=True               
#        solution[Group]=np.array(next(iter(linsolve(Equation,Group_symbol))))
#
#Index_unsolve_2=np.where(SocialSolve==True)[0]
#Index_unsolve=social_act[Index_unsolve_2]
#print(Combine_bool)
#t1 = time.clock()
#total=t1-t0
#print(total)
#        if ((i+j==(how_many_act_social-1))&End_overlap&(i<(how_many_act_social-1))):
#            End_group=OverlapGroup
#########################################
#Solve for all equations code        
#shock=list(shock)
#Social_sym=symbols('a0:%d'%how_many_act_social)
#Equation=[]
#Vdummy=[]
#social_index_list=list(social_index)
#for i in range(AgentCount):
#    Vdummy.append(shock[i])
#    if(i in social_index):
#        j=social_index_list.index(i)
#        Vdummy[-1]=Social_sym[j]
#    

############################################
#gross overlap
#Distance=social_index[1:]-social_index[0:(how_many_act_social-1)]
#Overlap_bool=list((Distance<=N))
#Overlap_bool.append(False)
#if(social_index[0]+AgentCount-social_index[-1]<=N):
#    Overlap_bool[-1]=True
#
#Overlap_bool=np.array(Overlap_bool)
#Overlap_indexofindex=np.where(Overlap_bool==True)[0]
############################################

##########################################################
#solve all socail updaters' equations
#for i in range(how_many_act_social):
#    SocialPosition=social_index[i]
#    left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:SocialPosition]])
#    right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:SocialPosition+N+1]])
#    if (SocialPosition-N<0):
#        left_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition-N:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition]])
#    if (SocialPosition+N>(AgentCount-1)):
#        right_sum=sum([Vdummyi for Vdummyi in Vdummy[SocialPosition+1:]])+sum([Vdummyi for Vdummyi in Vdummy[0:SocialPosition+N-(AgentCount-1)]])
#    s=(left_sum+right_sum+shock[SocialPosition])/(2*N+1)-Vdummy[SocialPosition]
#    Equation.append(s)
#
#t0 = time.time()
#linsolve(Equation,Social_sym)
#t1 = time.time()
#
#total=t1-t0
#print(total)
################################################


###############################################
#Test code

#Rest=symbols('a0:2')
#b1=2
#b2=8
#C=[b1,b2,Rest[0],Rest[1]]
#Equation=[]
#s=sum([Ci for Ci in C[2:4]])-C[0]
#Equation.append(s)
#ss=C[2]-C[3]-C[1]
#Equation.append(ss)
#linsolve(Equation,(C[2],C[3]))