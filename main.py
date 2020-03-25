#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 22:06:15 2020

@author: thomasmonks
"""

import concurrent.futures
import simpy
import random
import numpy as np
import itertools
from dataclasses import dataclass, field
       
            
class Entity(object):
    def __init__(self, env, servers, mean_delay):
        self.env = env
        self.servers = servers
        self.mean_delay = mean_delay
        self.wait = 0.0
        
    def enter_queue(self):
        self.arrive = self.env.now
        with self.servers.request() as server:
            yield server
            self.wait = self.env.now - self.arrive
            
            delay = random.expovariate(1 / self.mean_delay) 
            yield self.env.timeout(delay)
            
            
def observe_queue(env, res, interval, results):
   """
   Observe a queue length for a resource at a specified interval and store 
   results
   
   Parameters:
   -------
   env - Simpy environment
   res - resource to monitor
   interval - observation interval
   results - results list.  stores Q lengths
   """
   for i in itertools.count():
       yield env.timeout(interval)
       queue_l = len(res.queue)
       results.append(queue_l)
       
       
class MMSQueueModel(object):
    '''
    MMS Queue Model
    
    Very simple queuing simulation model.
    '''
    def __init__(self, args):
        self.env = simpy.Environment()
        self.mean_arrivals = args.mean_arrivals
        self.mean_delay = args.mean_delay
        self.servers = simpy.Resource(self.env, capacity=args.n_servers)
        
        self.entities = []
        
    def source(self, warm_up):
        """Create new entities until the sim time reaches end"""
        while True:
            iat = random.expovariate(self.mean_arrivals)
            yield self.env.timeout(iat) 
            
            arrival = Entity(self.env, self.servers, self.mean_delay)
            if self.env.now >= warm_up:
                self.entities.append(arrival)
            self.env.process(arrival.enter_queue())
            
    def run(self, run_length=1440, warm_up=0):
        """Start model run"""
        self.q_lengths = []

        self.env.process(self.source(warm_up))
        self.env.process(observe_queue(self.env, self.servers,
                                            120, self.q_lengths))
        self.env.run(until=run_length+warm_up)
        


@dataclass(frozen=True)
class Scenario:
    mean_arrivals: float = 300 / 24 / 60
    mean_delay: float = 150
    n_servers: float = 28
    
    

def multiple_replications(scenario, run_length, warm_up=0, n_reps=5):
    '''
    Runs multiple indepdent replications of the simulation model
    '''
    rep_results = []
    for rep in range(n_reps):
        model = MMSQueueModel(scenario)
        model.run(run_length, warm_up)
        mean_q = np.array(model.q_lengths).mean()
        rep_results.append(mean_q)
        
    return rep_results
        


if __name__ == '__main__':
    #NOTE TIME UNITS IN MINS
    #average 300 arrivals per day.
    #average service time = 150 mins
    #28 servers
    RUN_LENGTH = 1440
    
    base_scenario = Scenario()
    results = multiple_replications(base_scenario, RUN_LENGTH, n_reps=100)
    print(np.array(results).mean())

        
    
    