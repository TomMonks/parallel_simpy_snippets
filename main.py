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


class Entity(object):
    def enter_queue(self, env, servers, mean_delay):
        self.arrive = env.now
        with servers.request():
            self.wait = env.now - self.arrive
            delay = random.expovariate(1 / mean_delay) 
            yield env.timeout(delay)
            
            
class MMSQueueModel(object):
    def __init__(self, mean_iat, mean_delay, n_servers):
        self.env = simpy.Environment()
        self.mean_iat = mean_iat
        self.mean_delay = mean_delay
        self.servers = simpy.Resource(self.env, capacity=n_servers)
        self.entities = []
        
    def source(self):
        """Create new entities until the sim time reaches Sim end"""
        while True:
            iat = random.expovariate(self.mean_iat)   
            yield self.env.timeout(iat) 
            arrival = Entity()
            self.entities.append(arrival)
            self.env.process(arrival.enter_queue(self.env, 
                                                 self.servers,
                                                 self.mean_delay))
   
    def run(self, run_length=1440):
        """Start model run"""
        self.env.process(self.source())
        self.env.run(until=run_length)
        
        
        
        
if __name__ == '__main__':
    #TIME UNITS IN MINS
    MEAN_IAT = 0.8
    MEAN_DELAY = 150
    N_SERVERS = 3
    RUN_LENGTH = 1440
    model = MMSQueueModel(MEAN_IAT, MEAN_DELAY, N_SERVERS)
    model.run(RUN_LENGTH)
    
    wait_times = []
    for entity in model.entities:
        wait_times.append(entity.wait)
        
    mean_wait = np.array(wait_times).mean()
    print(mean_wait)
        
    
    