'''
Models for the cAndCwithStickyE paper, in the form of extensions to AgentType
subclasses from the ../ConsumptionSaving folder.  This module defines four new
AgentType subclasses for use in this project:
    
1) StickyEconsumerType: An extention of AggShockConsumerType that can be used in
    the Cobb-Douglas or small open economy specifications.
2) StickyEmarkovConsumerType: An extention of AggShockMarkovConsumerType that can
    be used in the Cobb-Douglas Markov or small open Markov economy specifications.
3) StickyErepAgent: An extention of RepAgentConsumerType that can be used in the
    representative agent specifications.
4) StickyEmarkovRepAgent: An extension of RepAgentMarkovConsumerType that can be
    used in the Markov representative agent specifications.
    
The Markov-based AgentTypes are imported by StickyE_MAIN, the main file for this
project.  Non-Markov AgentTypes are imported by StickyE_NO_MARKOV.
Calibrated parameters for each type are found in StickyEparams.
'''

#import sys 
#import os
#sys.path.insert(0, os.path.abspath('../'))
#sys.path.insert(0, os.path.abspath('../ConsumptionSaving'))

import numpy as np
from sympy import *
from ConsAggShockModel import AggShockConsumerType, AggShockMarkovConsumerType, CobbDouglasEconomy, CobbDouglasMarkovEconomy
from RepAgentModel import RepAgentConsumerType, RepAgentMarkovConsumerType

# Make an extension of the base type for the heterogeneous agents versions
class StickyEconsumerType(AggShockConsumerType):
    '''
    A class for representing consumers who have sticky expectations about the
    macroeconomy because they do not observe aggregate variables every period.
    ''' 
    def simBirth(self,which_agents):
        '''
        Makes new consumers for the given indices.  Slightly extends base method by also setting
        pLvlErrNow = 1.0 for new agents, indicating that they correctly perceive their productivity.
        
        Parameters
        ----------
        which_agents : np.array(Bool)
            Boolean array of size self.AgentCount indicating which agents should be "born".
        
        Returns
        -------
        None
        '''
        AggShockConsumerType.simBirth(self,which_agents)
        if hasattr(self,'pLvlErrNow'):
            self.pLvlErrNow[which_agents] = 1.0
            #self.pSocial[which_agents] = (self.pSocial[which_agents]*float(2*self.NetSiz+1)-self.Pcvd[which_agents]+self.PlvlAggNow)/(2*self.NetSiz+1)
            self.PSocial[which_agents] = self.PlvlAggNow          
            self.Pcvd[which_agents] = self.PlvlAggNow
            self.Pcvd_pre[which_agents] = self.PlvlAggNow
            self.pInd[which_agents] = 1.0
            self.pLvlNow[which_agents] = self.PlvlAggNow
        else:
            self.pLvlErrNow = np.ones(self.AgentCount)
            self.PSocial = np.ones(self.AgentCount)
            self.Pcvd = np.ones(self.AgentCount)
            self.Pcvd_pre = np.ones(self.AgentCount)
            self.pInd = np.ones(self.AgentCount)
            #self.pLvlNow = np.ones(self.AgentCount)

            
    def getUpdaters(self):
        '''
        Determine which agents update this period vs which don't.  Fills in the
        attributes update and dont as boolean arrays of size AgentCount.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        how_many_update = int(round(self.UpdatePrb*self.AgentCount))
        base_bool = np.zeros(self.AgentCount,dtype=bool)
        base_bool[0:how_many_update] = True
        self.update = self.RNG.permutation(base_bool)
        self.dont = np.logical_not(self.update)
        
        
        #Determine which agents update his belief through his social network
        how_many_social = int(round(self.SocialPrb*self.AgentCount))
        social_bool = np.zeros(self.AgentCount,dtype=bool)
        social_bool[0:how_many_social] = True     
        social = self.RNG.permutation(social_bool)
        
        nsocial=np.logical_not(social)
        
        self.social_act=social&self.dont
        self.neither=nsocial&self.dont
        self.social_index=np.where(self.social_act==True)[0]
        self.how_many_act_social=len(self.social_index)
        
    def getpLvlError(self):
        '''
        Calculates and returns the misperception of this period's shocks.  Updaters
        have no misperception this period, while those who don't update don't see
        the value of the aggregate permanent shock and assume aggregate growth
        equals its expectation.
        
        
        Parameters
        ----------
        None
        
        Returns
        -------
        pLvlErr : np.array
            Array of size AgentCount with this period's (new) misperception.
        '''
        pLvlErr = np.ones(self.AgentCount)
        #pLvlErr[self.neither] = self.PermShkAggNow/self.PermGroFacAgg
        #pLvlErr[self.social_act] = (self.pLvlNow[self.social_act]*self.PermShkAggNow)/(self.PermGroFacAgg*self.pSocial[self.social_act]*self.pInd[self.social_act])
        return pLvlErr
        
            
    def getShocks(self):
        '''
        Gets permanent and transitory shocks (combining idiosyncratic and aggregate shocks), but
        only consumers who update their macroeconomic beliefs this period incorporate all pre-
        viously unnoticed aggregate permanent shocks.  Agents correctly observe the level of all
        real variables (market resources, consumption, assets, etc), but misperceive the aggregate
        productivity level.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        # The strange syntax here is so that both StickyEconsumerType and StickyEmarkovConsumerType
        # run the getShocks method of their first superclass: AggShockConsumerType and
        # AggShockMarkovConsumerType respectively.  This will be simplified in Python 3.
        super(self.__class__,self).getShocks() # Get permanent and transitory combined shocks
        newborns = self.t_age == 0
        self.TranShkNow[newborns] = self.TranShkAggNow*self.wRteNow # Turn off idiosyncratic shocks for newborns       
        self.PermShkNow[newborns] = self.PermShkAggNow
        self.getUpdaters() # Randomly draw which agents will update their beliefs 
        ##############Debug###################
        #self.NewBorn=np.where((self.t_age == 0)&(self.social_act))[0]
        #self.SimSocial=np.where((self.pSocial == 2.5)&(self.social_act))[0]
        ##############Debug###################        
        
        self.IdioPermShk=self.PermShkNow/float(self.PermShkAggNow)
        
        ##########################Debug#############
        self.TrueShock=self.PermShkNow
        #self.Pcvd1=self.Pcvd
        #self.Pcvd2=self.pLvlNow/self.pInd
        #self.Difference=self.Pcvd1-self.Pcvd2
        #########################Debug##############
        #self.Pcvd=self.PlvlAggNow/self.pLvlErrNow
        # Calculate innovation to the productivity level perception error
        pLvlErrNew = self.getpLvlError()
        
        self.pLvlErrNow *= pLvlErrNew # Perception error accumulation
        ######################################################
        #Assign agents with overlap neighborhood into one group based on their distance between each other
        
#        if (self.how_many_act_social>=1):
#            Agent_dis=self.social_index[1:]-self.social_index[0:self.how_many_act_social-1]
#            Group=[]
#            #First_group is the group that includes the first socially update agent in the row
#            First_group=[self.social_index[0]]
#            #Start_from is the index of first socially update agent after all agents in First_group
#            Start_from=1
#            #Find the overlap group that contains the first socially update agent
#            for i in range(self.how_many_act_social-1):
#                if (Agent_dis[i]<=self.NetSiz):
#                    First_group.append(self.social_index[i+1])
#                    Start_from=i+2
#                else:
#                    break
#            #End_group is the group that includes the last socially update agent in the row
#            GroupSiz=0 #measures the total number of agents in the first group and the end group
#            if (Start_from<=(self.how_many_act_social-1)):
#                #Combine=False
#                Combine_group=[]
#                End_group=[self.social_index[self.how_many_act_social-1]]
#                End_at=self.how_many_act_social-1-1
#                for i in range(self.how_many_act_social-2,Start_from-1,-1):
#                    if (Agent_dis[i]<=self.NetSiz):
#                        End_group.insert(0, self.social_index[i])
#                        End_at=i-1
#                    else:
#                        break
#                if((self.social_index[0]+self.AgentCount-self.social_index[self.how_many_act_social-1])<=self.NetSiz):
#                    #Combine=True
#                    Combine_group=np.array(End_group+First_group)
#                    Group.append(Combine_group)
#                    GroupSiz=len(Combine_group)
#                else:
#                    Group.append(np.array(First_group))
#                    Group.append(np.array(End_group))
#                    GroupSiz=len(First_group)+len(End_group)
#
#            else:   
#                Group.append(np.array(First_group))
#                GroupSiz=len(First_group)
#            #Assign all other socially update agents into group
#            Start=Start_from
#            End=End_at
#            Insert_at=1
#            if(GroupSiz<=self.how_many_act_social):
#                while(Start<=End):
#                    MovGroup=[self.social_index[Start]]
#                    i=Start
#                    while (i<=End):
#                        if (Agent_dis[i]<=self.NetSiz):
#                            MovGroup.append(self.social_index[i+1])
#                            i=i+1
#                        else:
#                            Start=i+1
#                            Group.insert(Insert_at,np.array(MovGroup))
#                            Insert_at=Insert_at+1
#                            MovGroup=[]
#                            break
#            self.group=Group
        ###############################################################
        
        # Calculate (mis)perceptions of the permanent shock
        PermShkPcvd = self.PermShkNow/pLvlErrNew
        PermShkPcvd[self.update] *= self.pLvlErrNow[self.update] # Updaters see the true permanent shock and all missed news        
        self.pLvlErrNow[self.update] = 1.0
        #self.PermShkNow = PermShkPcvd
        ##################################
        #Calculate perceived productivity for agents that update to the news and agents that don't update at all.        
        pLvlPrev = self.pLvlNow
        self.prev=pLvlPrev
        self.pLvlNow = pLvlPrev*self.PermShkNow
        self.PlvlAggNow *= self.PermShkAggNow
        #self.pLvlTrue = self.pLvlNow*self.pLvlErrNow
        self.pInd *= self.IdioPermShk
        self.pLvlTrue=self.PlvlAggNow*self.pInd
        self.Pcvd_pre=self.Pcvd
        self.Pcvd=self.pLvlNow/self.pInd
        
        self.PSocial=self.Pcvd
        self.pLvlErrNow[self.social_act] = 1.0
        ################Need to change it to Pcvd in actural program
#        if (self.how_many_act_social>=1):
#            #solve linear equation system for simultaneously socially updating agents
#            Num_groups=len(Group)
#            #Pcvd_solution=np.array(range(AgentCount))*0.0001
#            for i in range(Num_groups):
#                Num_agent_in_group=len(Group[i])
#                if (Num_agent_in_group<=1):
#                    Social_pos=Group[i][0]
#                    Left_sum_char=sum(self.Pcvd[(Social_pos-self.NetSiz):(Social_pos)])
#                    if ((Social_pos-self.NetSiz)<0):
#                        Left_sum_char=sum(self.Pcvd[(Social_pos+self.AgentCount-self.NetSiz):])+sum(self.Pcvd[0:(Social_pos)])
#                    if (Social_pos+self.NetSiz<=(self.AgentCount-1)):
#                        Right_sum_char=sum(self.Pcvd[(Social_pos+1):(Social_pos+self.NetSiz+1)])
#                    if (Social_pos+self.NetSiz>(self.AgentCount-1)):
#                        if ((Social_pos+1)>(self.AgentCount-1)):
#                            Right_sum_char=sum(self.Pcvd[0:self.NetSiz])
#                        else:
#                            Right_sum_char=sum(self.Pcvd[(Social_pos+1):])+sum(self.Pcvd[0:(Social_pos+self.NetSiz+1-self.AgentCount)])
#                    self.PSocial[Social_pos]=(Left_sum_char+Right_sum_char)/float(2*self.NetSiz)
#            
#                else:
#                    Social_sym=symbols('a0:%d'%Num_agent_in_group)
#                    Variable_dummy=list(self.Pcvd)
#                    Equations=[]
#                    Solution=[]
#                    for index_of_index in range(Num_agent_in_group):
#                        Variable_dummy[Group[i][index_of_index]]=Social_sym[index_of_index]
#                    for index_of_index in range(Num_agent_in_group):
#                        Social_pos=Group[i][index_of_index]
#                        Left_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos-self.NetSiz):(Social_pos)]])
#                        if ((Social_pos-self.NetSiz)<0):
#                            Left_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+self.AgentCount-self.NetSiz):]])+sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:Social_pos]])
#                        if (Social_pos+self.NetSiz<=(self.AgentCount-1)):
#                            Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+1):(Social_pos+1+self.NetSiz)]])
#                        if (Social_pos+self.NetSiz>(self.AgentCount-1)):
#                            if ((Social_pos+1)>(self.AgentCount-1)):
#                                Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:self.NetSiz]])
#                            else:
#                                Right_sum=sum([Variable_dummyi for Variable_dummyi in Variable_dummy[(Social_pos+1):]])+sum([Variable_dummyi for Variable_dummyi in Variable_dummy[0:(Social_pos+self.NetSiz+1-self.AgentCount)]])
#                        s=(Left_sum+Right_sum)/float(2*self.NetSiz)-Variable_dummy[Social_pos]
#                        Equations.append(s)
#                    Solution=np.array(next(iter(linsolve(Equations,Social_sym))))
#                    for index_of_index in range(Num_agent_in_group):
#                        Social_pos=Group[i][index_of_index]
#                        self.PSocial[Social_pos]=Solution[index_of_index]
        
    def getStates(self):
        '''
        Gets simulated consumers pLvl and mNrm for this period, but with the alteration that these
        represent perceived rather than actual values.  Also calculates mLvlTrue, the true level of
        market resources that the individual has on hand.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
#        Not_social_act=np.logical_not(self.social_act)
#        self.Pcvd[self.social_act]=np.average(self.Pcvd[self.update])
#        self.pLvlNow[self.social_act]=self.Pcvd[self.social_act]*self.pInd[self.social_act]
#        self.pLvlErrNow[self.social_act]=self.pLvlTrue[self.social_act]/self.pLvlNow[self.social_act]
        # Update consumers' perception of their permanent income level
        #pLvlPrev = self.pLvlNow
        #self.prev=pLvlPrev 
        #self.pLvlNow = pLvlPrev*self.PermShkNow # Perceived permanent income level (only correct if macro state is observed this period)
        #self.PlvlAggNow *= self.PermShkAggNow # Updated aggregate permanent productivity level
        #self.pLvlTrue = self.pLvlNow*self.pLvlErrNow
        #self.pInd *= self.IdioPermShk
        #plvlNow=self.pLvlNow
        #self.Pcvd=self.pLvlNow/self.pInd
        #self.Pcvd=self.PlvlAggNow/self.pLvlErrNow
#        ###############################################
#        pAve=np.ones(self.AgentCount)
#        #Test=np.ones(self.AgentCount)
#        #PG=np.ones(self.AgentCount)
#        for SocialCounter in range(self.AgentCount):
#            #GrowthRate=self.PermGroFacAgg[self.MrkvNowPcvd[SocialCounter]]
#            #SocialPos=SocialCounter
#            self.correction=self.Pcvd[SocialCounter]-self.Pcvd[SocialCounter]
#            #self.correction=-self.Pcvd[SocialCounter]
#            ##################            
#            #Test[SocialCounter]=self.Pcvd[SocialCounter]-self.Pcvd[SocialCounter]
#            ############3
#            Left_sum=sum(self.Pcvd[(SocialCounter-self.NetSiz):(SocialCounter)])
#            Right_sum=sum(self.Pcvd[(SocialCounter):(SocialCounter+self.NetSiz+1)])
#            if ((SocialCounter-self.NetSiz)<0):
#                Left_sum=sum(self.Pcvd[0:(SocialCounter)])+sum(self.Pcvd[(self.AgentCount+SocialCounter-self.NetSiz):])
#            if ((SocialCounter+self.NetSiz+1)>self.AgentCount):
#                Right_sum=sum(self.Pcvd[SocialCounter:])+sum(self.Pcvd[0:(SocialCounter+self.NetSiz+1-self.AgentCount)])
#      #      Left_sum=Left_sum+correction            
##            pAve[SocialCounter]=(Left_sum+Right_sum+self.correction)/(2*self.NetSiz+1)
#            pAve[SocialCounter]=(Left_sum+Right_sum+self.correction)/float(2*self.NetSiz+1)
#            #pAve[SocialCounter]=self.PermGroFacAgg[SocialCounter]*(Left_sum+Right_sum)/(2*self.NetSiz+1)        
#        self.pSocial=pAve
#        #self.test=Test
#        ##################################################        
        # Calculate what the consumers perceive their normalized market resources to be
        RfreeNow = self.getRfree()
        bLvlNow = RfreeNow*self.aLvlNow # This is the true level
        
        yLvlNow = self.pLvlTrue*self.TranShkNow # This is true income level
        mLvlTrueNow = bLvlNow + yLvlNow # This is true market resource level
        mNrmPcvdNow = mLvlTrueNow/self.pLvlNow # This is perceived normalized resources
        self.mNrmNow = mNrmPcvdNow
        self.mLvlTrueNow = mLvlTrueNow
        self.yLvlNow = yLvlNow # Only labor income

        
    def getMaggNow(self):
        '''
        Gets each consumer's perception of normalized aggregate market resources.
        Very simple overwrite of method from superclass.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        MaggPcvdNow : np.array
            1D array of perceived normalized aggregate market resources.
        '''
        MaggPcvdNow = self.MaggNow*self.pLvlErrNow  # Agents know the true level of aggregate market resources,
        return MaggPcvdNow # but have erroneous perception of pLvlAgg.

        
    def getPostStates(self):
        '''
        Slightly extends the base version of this method by recalculating aLvlNow to account for the
        consumer's (potential) misperception about their productivity level.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        AggShockConsumerType.getPostStates(self)
        self.cLvlNow = self.cNrmNow*self.pLvlNow # True consumption level
        self.aLvlNow = self.mLvlTrueNow - self.cLvlNow # True asset level
        self.aNrmNow = self.aLvlNow/self.pLvlNow # Perceived normalized assets
        

        
class StickyEmarkovConsumerType(AggShockMarkovConsumerType,StickyEconsumerType):
    '''
    A class for representing consumers who have sticky expectations about the macroeconomy
    because they do not observe aggregate variables every period.  This version lives
    in an economy subject to Markov shocks to the aggregate income process.  Agents don't
    necessarily update their perception of the aggregate productivity level or the discrete
    Markov state (governing aggregate growth) in every period.  Most of its methods are
    directly inherited from one of its parent classes.
    '''
    def simBirth(self,which_agents): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.simBirth(self,which_agents)
        
    def getShocks(self): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.getShocks(self)
        
    def getStates(self): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.getStates(self)
        
    def getPostStates(self): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.getPostStates(self)
        
    def getMaggNow(self): # Inherit from StickyE rather than AggShock
        return StickyEconsumerType.getMaggNow(self)
        
    def getMrkvNow(self): # Agents choose control based on *perceived* Markov state
        return self.MrkvNowPcvd

    
    def getUpdaters(self):
        '''
        Determine which agents update this period vs which don't.  Fills in the
        attributes update and dont as boolean arrays of size AgentCount.  This
        version also updates perceptions of the Markov state.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        StickyEconsumerType.getUpdaters(self)
        # Only updaters change their perception of the Markov state
        if hasattr(self,'MrkvNowPcvd'):
            #self.MrkvNowPcvd[self.update] = self.MrkvNow
            self.MrkvNowPcvd = np.ones(self.AgentCount,dtype=int)*self.MrkvNow
        else: # This only triggers in the first simulated period
            self.MrkvNowPcvd = np.ones(self.AgentCount,dtype=int)*self.MrkvNow

       
    def getpLvlError(self):
        '''
        Calculates and returns the misperception of this period's shocks.  Updaters
        have no misperception this period, while those who don't update don't see
        the value of the aggregate permanent shock and thus base their belief about
        aggregate growth on the last Markov state that they actually observed,
        which is stored in MrkvNowPcvd.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        pLvlErr : np.array
            Array of size AgentCount with this period's (new) misperception.
        '''
        pLvlErr = np.ones(self.AgentCount)
        #pLvlErr[self.dont] = self.PermShkAggNow/self.PermGroFacAgg[self.MrkvNowPcvd[self.dont]]
        pLvlErr[self.neither] = self.PermShkAggNow/self.PermGroFacAgg[self.MrkvNowPcvd[self.neither]]
        #pLvlErr[self.social_act] = (self.pLvlNow[self.social_act]*self.PermShkAggNow)/(self.PermGroFacAgg[self.MrkvNowPcvd[self.social_act]]*self.pSocial[[self.social_act]]*self.pInd[[self.social_act]])        
        #pLvlErr[self.social_act] = (self.Pcvd[self.social_act]*self.PermShkAggNow)/(self.PermGroFacAgg[self.MrkvNowPcvd[self.social_act]]*self.pSocial[[self.social_act]])        
        return pLvlErr
    


class StickyErepAgent(RepAgentConsumerType):
    '''
    A representative consumer who has sticky expectations about the macroeconomy because
    he does not observe aggregate variables every period.  Agent lives in a Cobb-Douglas economy.
    '''
    def simBirth(self,which_agents):
        '''
        Makes new consumers for the given indices.  Slightly extends base method by also setting
        pLvlTrue = 1.0 in the very first simulated period.
        
        Parameters
        ----------
        which_agents : np.array(Bool)
            Boolean array of size self.AgentCount indicating which agents should be "born".
        
        Returns
        -------
        None
        '''
        super(self.__class__,self).simBirth(which_agents)
        if self.t_sim == 0: # Make sure that pLvlTrue and aLvlNow exist
            self.pLvlTrue = np.ones(self.AgentCount)
            self.aLvlNow = self.aNrmNow*self.pLvlTrue

            
    def getShocks(self):
        super(self.__class__,self).getShocks() # Get actual permanent and transitory shocks
        
         
    def getStates(self):
        '''
        Calculates updated values of normalized market resources and permanent income level.
        Makes both perceived and true values.  The representative consumer will act on the
        basis of his *perceived* normalized market resources.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        # Calculate perceived and true productivity level
        aLvlPrev = self.aLvlNow
        self.pLvlTrue = self.pLvlTrue*self.PermShkNow
        self.pLvlNow = self.getpLvlPcvd()
        
        # Calculate true values of variables
        self.kNrmTrue = aLvlPrev/self.pLvlTrue
        self.yNrmTrue = self.kNrmTrue**self.CapShare*self.TranShkNow**(1.-self.CapShare) - self.kNrmTrue*self.DeprFac
        self.Rfree = 1. + self.CapShare*self.kNrmTrue**(self.CapShare-1.)*self.TranShkNow**(1.-self.CapShare) - self.DeprFac
        self.wRte  = (1.-self.CapShare)*self.kNrmTrue**self.CapShare*self.TranShkNow**(-self.CapShare)
        self.mNrmTrue = self.Rfree*self.kNrmTrue + self.wRte*self.TranShkNow
        self.mLvlTrue = self.mNrmTrue*self.pLvlTrue
        
        # Calculate perception of normalized market resources
        self.mNrmNow = self.mLvlTrue/self.pLvlNow

        
    def getControls(self):
        super(self.__class__,self).getControls()
        self.cLvlNow = self.cNrmNow*self.pLvlNow # This is true

        
    def getPostStates(self):
        '''
        Slightly extends the base version of this method by recalculating aLvlNow to account for the
        consumer's (potential) misperception about their productivity level.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        RepAgentConsumerType.getPostStates(self)
        self.aLvlNow = self.mLvlTrue - self.cLvlNow # This is true
        self.aNrmNow = self.aLvlNow/self.pLvlTrue # This is true
        
    def getpLvlPcvd(self):
        '''
        Finds the representative agent's (average) perceived productivity level.
        Average perception of productivity gets UpdatePrb weight on the true level,
        for those that update, and (1-UpdatePrb) weight on the previous average
        perception times expected aggregate growth, for those that don't update.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        pLvlPcvd : np.array
            Size 1 array with average perception of productivity level.
        '''
        pLvlPcvd = self.UpdatePrb*self.pLvlTrue + (1.0-self.UpdatePrb)*(self.pLvlNow*self.PermGroFac[self.t_cycle[0]-1])
        return pLvlPcvd
    

    
class StickyEmarkovRepAgent(RepAgentMarkovConsumerType,StickyErepAgent):
    '''
    A representative consumer who has sticky expectations about the macroeconomy because
    he does not observe aggregate variables every period.  Agent lives in a Cobb-Douglas
    economy that has a discrete Markov state.  If UpdatePrb < 1, the representative agent's
    perception of the Markov state is distributed across the previous states visited.
    '''
    def simBirth(self,which_agents):
        '''
        Makes new consumers for the given indices.  Slightly extends base method by also setting
        pLvlTrue = 1.0 in the very first simulated period, as well as initializing the perception
        of aggregate productivity for each Markov state.  The representative agent begins with
        the correct perception of the Markov state.
        
        Parameters
        ----------
        which_agents : np.array(Bool)
            Boolean array of size self.AgentCount indicating which agents should be "born".
        
        Returns
        -------
        None
        '''
        if which_agents==np.array([True]):
            RepAgentMarkovConsumerType.simBirth(self,which_agents)
            if self.t_sim == 0: # Initialize perception distribution for Markov state
                self.pLvlTrue = np.ones(self.AgentCount)
                self.aLvlNow = self.aNrmNow*self.pLvlTrue
                StateCount = self.MrkvArray.shape[0]
                self.pLvlNow = np.ones(StateCount) # Perceived productivity level by Markov state
                self.MrkvPcvd = np.zeros(StateCount) # Distribution of perceived Markov state
                self.MrkvPcvd[self.MrkvNow[0]] = 1.0 # Correct perception of state initially

        
    def getShocks(self): # Inherit from StickyE rather than RepresentativeAgent
        StickyErepAgent.getShocks(self)
        
    def getStates(self): # Inherit from StickyE rather than RepresentativeAgent
        StickyErepAgent.getStates(self)
        
    def getPostStates(self): # Inherit from StickyE rather than RepresentativeAgent
        StickyErepAgent.getPostStates(self)

        
    def getpLvlPcvd(self):
        '''
        Finds the representative agent's (average) perceived productivity level
        for each Markov state, as well as the distribution of the representative
        agent's perception of the Markov state.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        pLvlPcvd : np.array
            Array with average perception of productivity level by Markov state.
        '''
        StateCount = self.MrkvArray.shape[0]
        t = self.t_cycle[0]
        i = self.MrkvNow[0]
        
        dont_mass = self.MrkvPcvd*(1.-self.UpdatePrb) # pmf of non-updaters
        update_mass = np.zeros(StateCount)
        update_mass[i] = self.UpdatePrb # pmf of updaters
        
        dont_pLvlPcvd = self.pLvlNow*self.PermGroFac[t-1] # those that don't update think pLvl grows at PermGroFac for last observed state
        update_pLvlPcvd = np.zeros(StateCount)
        update_pLvlPcvd[i] = self.pLvlTrue # those that update see the true pLvl
        
        # Combine updaters and non-updaters to get average pLvl perception by Markov state
        self.MrkvPcvd = dont_mass + update_mass # Total mass of agent in each state
        pLvlPcvd = (dont_mass*dont_pLvlPcvd + update_mass*update_pLvlPcvd)/self.MrkvPcvd
        pLvlPcvd[self.MrkvPcvd==0.] = 1.0 # Fix division by zero problem when MrkvPcvd[i]=0
        return pLvlPcvd

        
    def getControls(self):
        '''
        Calculates consumption for the representative agent using the consumption functions.
        Takes the weighted average of cLvl across perceived Markov states.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        StateCount = self.MrkvArray.shape[0]
        t = self.t_cycle[0]
        
        cNrmNow = np.zeros(StateCount) # Array of chosen cNrm by Markov state
        for i in range(StateCount):
            cNrmNow[i] = self.solution[t].cFunc[i](self.mNrmNow[i])
        self.cNrmNow = cNrmNow
        self.cLvlNow = np.dot(cNrmNow*self.pLvlNow,self.MrkvPcvd) # Take average of cLvl across states
        

        
class StickyCobbDouglasEconomy(CobbDouglasEconomy):            
    '''
    This is almost identical to CobbDouglasEconomy, except it overrides the mill
    rule to use pLvlTrue instead of pLvlNow
    '''
    def __init__(self,agents=[],tolerance=0.0001,act_T=1000,**kwds):
        '''
        Make a new instance of StickyCobbDouglasEconomy by filling in attributes
        specific to this kind of market.
        
        Parameters
        ----------
        agents : [ConsumerType]
            List of types of consumers that live in this economy.
        tolerance: float
            Minimum acceptable distance between "dynamic rules" to consider the
            solution process converged.  Distance depends on intercept and slope
            of the log-linear "next capital ratio" function.
        act_T : int
            Number of periods to simulate when making a history of of the market.
            
        Returns
        -------
        None
        '''
        CobbDouglasEconomy.__init__(self,agents=agents,tolerance=tolerance,act_T=act_T,**kwds)
        self.reap_vars = ['aLvlNow','pLvlTrue']
    
    def millRule(self,aLvlNow,pLvlTrue):
        '''
        Function to calculate the capital to labor ratio, interest factor, and
        wage rate based on each agent's current state.  Just calls calcRandW().
        
        See documentation for calcRandW for more information.
        '''
        return self.calcRandW(aLvlNow,pLvlTrue)


   
class StickyCobbDouglasMarkovEconomy(CobbDouglasMarkovEconomy):            
    '''
    This is almost identical to CobbDouglasmarkovEconomy, except it overrides the
    mill rule to use pLvlTrue instead of pLvlNow.
    '''
    def __init__(self,agents=[],tolerance=0.0001,act_T=1000,**kwds):
        '''
        Make a new instance of StickyCobbDouglasMarkovEconomy by filling in attributes
        specific to this kind of market.
        
        Parameters
        ----------
        agents : [ConsumerType]
            List of types of consumers that live in this economy.
        tolerance: float
            Minimum acceptable distance between "dynamic rules" to consider the
            solution process converged.  Distance depends on intercept and slope
            of the log-linear "next capital ratio" function.
        act_T : int
            Number of periods to simulate when making a history of of the market.
            
        Returns
        -------
        None
        '''
        CobbDouglasMarkovEconomy.__init__(self,agents=agents,tolerance=tolerance,act_T=act_T,**kwds)
        self.reap_vars = ['aLvlNow','pLvlTrue']
        
    def millRule(self,aLvlNow,pLvlTrue):
        '''
        Function to calculate the capital to labor ratio, interest factor, and
        wage rate based on each agent's current state.  Just calls calcRandW()
        and adds the Markov state index.
        
        See documentation for calcRandW for more information.
        '''
        MrkvNow = self.MrkvNow_hist[self.Shk_idx]
        temp =  self.calcRandW(aLvlNow,pLvlTrue)
        temp(MrkvNow = MrkvNow)
        
        # Overwrite MaggNow, wRteNow, and RfreeNow if requested
        if self.overwrite_hist:
            t = self.Shk_idx-1
            temp(MaggNow = self.MaggNow_overwrite[t])
            temp(wRteNow = self.wRteNow_overwrite[t])
            temp(RfreeNow = self.RfreeNow_overwrite[t])
        
        return temp