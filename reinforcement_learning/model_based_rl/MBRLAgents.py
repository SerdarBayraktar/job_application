#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model-based Reinforcement Learning policies
Practical for course 'Reinforcement Learning',
Bachelor AI, Leiden University, The Netherlands
By Thomas Moerland
"""
import numpy as np
from queue import PriorityQueue
from MBRLEnvironment import WindyGridworld

class DynaAgent:

    def __init__(self, n_states, n_actions, learning_rate, gamma):
        self.n_states = n_states
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.Q_sa = np.zeros((n_states,n_actions))
        # TO DO: Initialize count tables, and reward sum tables.
        self.n = np.zeros((n_states, n_actions, n_states))
        self.Rsum = np.zeros((n_states, n_actions, n_states))
        
    def select_action(self, s, epsilon):
        # TO DO: Change this to e-greedy action selection
        a = np.random.randint(0, self.n_actions)  # Replace this with correct action selection
        if np.random.random() < epsilon:
            return a
        else:
            return np.argmax(self.Q_sa[s])

    def update(self, s, a, r, done,s_next,n_planning_updates):
        #add latest values, they will be used in model
        self.n[s, a, s_next] += 1
        self.Rsum[s, a, s_next] += r
        #update q value
        self.Q_sa[s, a] += self.learning_rate * (r + self.gamma * np.max(self.Q_sa[s_next]) - self.Q_sa[s, a])
        for _ in range(n_planning_updates):
            # checks if they are bigger than 0 so they are previouslt observed
            # from book
            s = np.random.choice(np.where(self.n.sum(axis=(1, 2)) > 0)[0])
            a = np.random.choice(np.where(self.n[s].sum(axis=1) > 0)[0])
            # use model to make a chocice
            s_next = np.random.choice(self.n_states, p=self.n[s, a] / np.sum(self.n[s, a]))
            r = self.Rsum[s, a, s_next] / self.n[s, a, s_next]

            # update q value again
            self.Q_sa[s, a] += self.learning_rate * (r + self.gamma * np.max(self.Q_sa[s_next]) - self.Q_sa[s, a])

    def evaluate(self,eval_env,n_eval_episodes=30, max_episode_length=100):
        returns = []  # list to store the reward per episode
        for i in range(n_eval_episodes):
            s = eval_env.reset()
            R_ep = 0
            for t in range(max_episode_length):
                a = np.argmax(self.Q_sa[s]) # greedy action selection
                s_prime, r, done = eval_env.step(a)
                R_ep += r
                if done:
                    break
                else:
                    s = s_prime
            returns.append(R_ep)
        mean_return = np.mean(returns)
        return mean_return

class PrioritizedSweepingAgent:

    def __init__(self, n_states, n_actions, learning_rate, gamma, max_queue_size=200, priority_cutoff=0.01):
        self.n_states = n_states
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.priority_cutoff = priority_cutoff
        
        self.Q_sa = np.zeros((n_states,n_actions))
        # TO DO: Initialize count tables, reward sum tables, priority queue
        self.n = np.zeros((n_states, n_actions, n_states))
        self.Rsum = np.zeros((n_states, n_actions, n_states))
        self.queue = PriorityQueue()

    def select_action(self, s, epsilon):
        # TO DO: Change this to e-greedy action selection
        a = np.random.randint(0, self.n_actions)  # Replace this with correct action selection
        if np.random.random() < epsilon:
            return a
        else:
            return np.argmax(self.Q_sa[s])


    def update(self,s,a,r,done,s_next,n_planning_updates):
        # TO DO: Add Prioritized Sweeping code

        # Helper code to work with the queue
        # Put (s,a) on the queue with priority p (needs a minus since the queue pops the smallest priority first)
        # self.queue.put((-p,(s,a)))
        # Retrieve the top (s,a) from the queue
        # _,(s,a) = self.queue.get() # get the top (s,a) for the queue
        self.Q_sa[s, a] += self.learning_rate * (r + self.gamma * np.max(self.Q_sa[s_next]) - self.Q_sa[s, a])
        #update model
        self.n[s, a, s_next] += 1
        self.Rsum[s, a, s_next] += r
        #p calculation
        p = abs(r + self.gamma * np.max(self.Q_sa[s_next]) - self.Q_sa[s, a])
        if p > self.priority_cutoff:
            self.queue.put((-p, (s, a)))  #because of explanation above

        for _ in range(n_planning_updates):
            if self.queue.empty():  # this is in the book
                break
            _, (s, a) = self.queue.get()  # from descp above
            s_next = np.argmax(self.n[s, a])
            r = self.Rsum[s, a, s_next] / self.n[s, a, s_next]

            self.Q_sa[s, a] += self.learning_rate * (r + self.gamma * np.max(self.Q_sa[s_next]) - self.Q_sa[s, a])

            for s_sim in range(self.n_states):
                for a_sim in range(self.n_actions):
                    if self.n[s_sim, a_sim, s] > 0:
                        # use model to simulate
                        r_sim = self.Rsum[s_sim, a_sim, s] / self.n[s_sim, a_sim, s]
                        p = abs(r_sim + self.gamma * np.max(self.Q_sa[s]) - self.Q_sa[s_sim, a_sim])
                        if p > self.priority_cutoff:
                            self.queue.put((-p, (s_sim, a_sim)))

    def evaluate(self,eval_env,n_eval_episodes=30, max_episode_length=100):
        returns = []  # list to store the reward per episode
        for i in range(n_eval_episodes):
            s = eval_env.reset()
            R_ep = 0
            for t in range(max_episode_length):
                a = np.argmax(self.Q_sa[s]) # greedy action selection
                s_prime, r, done = eval_env.step(a)
                R_ep += r
                if done:
                    break
                else:
                    s = s_prime
            returns.append(R_ep)
        mean_return = np.mean(returns)
        return mean_return        

def test():

    n_timesteps = 1001
    gamma = 1.0

    # Algorithm parameters
    policy = 'dyna' # or 'ps' 
    epsilon = 0.1
    learning_rate = 0.2
    n_planning_updates = 3

    # Plotting parameters
    plot = True
    plot_optimal_policy = True
    step_pause = 0.0001
    
    # Initialize environment and policy
    env = WindyGridworld()
    if policy == 'dyna':
        pi = DynaAgent(env.n_states,env.n_actions,learning_rate,gamma) # Initialize Dyna policy
    elif policy == 'ps':    
        pi = PrioritizedSweepingAgent(env.n_states,env.n_actions,learning_rate,gamma) # Initialize PS policy
    else:
        raise KeyError('Policy {} not implemented'.format(policy))
    
    # Prepare for running
    s = env.reset()  
    continuous_mode = True
    
    for t in range(n_timesteps):            
        # Select action, transition, update policy
        a = pi.select_action(s,epsilon)
        s_next,r,done = env.step(a)
        pi.update(s=s,a=a,r=r,done=done,s_next=s_next,n_planning_updates=n_planning_updates)

        if(t % 100 ==  0 ):
            print('asd')
        # Render environment
        if plot:
            env.render(Q_sa=pi.Q_sa,plot_optimal_policy=plot_optimal_policy,
                       step_pause=step_pause)
            
        # Ask user for manual or continuous execution
        if not continuous_mode:
            key_input = input("Press 'Enter' to execute next step, press 'c' to run full algorithm")
            continuous_mode = True if key_input == 'c' else False

        # Reset environment when terminated
        if done:
            s = env.reset()
        else:
            s = s_next
            
    
if __name__ == '__main__':
    test()
