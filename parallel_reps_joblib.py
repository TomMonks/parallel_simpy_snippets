#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 22:06:15 2020

@author: thomasmonks

Example uses joblib Parallel with 'loky' backend for 
parallel execution of simulation replications.

"""
import numpy as np
from joblib import Parallel, delayed
from mms import MMSQueueModel, Scenario
            
def multiple_replications(scenario, run_length, warm_up=0, n_reps=5, n_jobs=1):
    '''
    Runs multiple indepdent replications of the simulation model    
    '''
    #res = [single_run(scenario, run_length, warm_up) for _ in range(n_reps)]
    res = Parallel(n_jobs=n_jobs)(delayed(single_run)(scenario, run_length, 
                   warm_up) for _ in range(n_reps))
    return res
        
def single_run(scenario, run_length, warm_up=0):
    model = MMSQueueModel(scenario)
    model.run(run_length, warm_up)
    return np.array(model.q_lengths).mean()


if __name__ == '__main__':
    #NOTE TIME UNITS IN MINS
    #average 300 arrivals per day.
    #average service time = 150 mins
    #28 servers
    RUN_LENGTH = 1440
    
    base_scenario = Scenario()
    results = multiple_replications(base_scenario, RUN_LENGTH, n_reps=1000, 
                                    n_jobs=-1)
    print(np.array(results).mean())
    print(np.array(results).std())
   

        
    
    