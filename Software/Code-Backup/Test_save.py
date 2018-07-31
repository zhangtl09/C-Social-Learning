# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 05:57:38 2018

@author: Tongli
"""

import numpy as np
#Folder_path='..\..\..\Result'
C_std=np.array([0.1,0.2,0.3,0.4])
c_std=np.array([1,2,3,4,5])
Min_siz=12
Max_siz=13

#Name_Agg='\Test_C_agg'+'_Min_'+str(Min_siz)+'_Max_'+str(Max_siz)+'.txt'
#Name_Ind='\Test_c_ind'+'_Min_'+str(Min_siz)+'_Max_'+str(Max_siz)+'.txt'
Agg_path='Test_C_agg'+'_Min_'+str(Min_siz)+'_Max_'+str(Max_siz)+'.txt'
Ind_path='Test_c_ind'+'_Min_'+str(Min_siz)+'_Max_'+str(Max_siz)+'.txt'
np.savetxt(Agg_path, C_std, delimiter="\n")
np.savetxt(Ind_path, c_std, delimiter="\n")