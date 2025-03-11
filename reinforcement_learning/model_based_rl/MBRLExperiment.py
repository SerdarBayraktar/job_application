#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model-based Reinforcement Learning experiments
Practical for course 'Reinforcement Learning',
Bachelor AI, Leiden University, The Netherlands
By Thomas Moerland
"""
import numpy as np
from MBRLEnvironment import WindyGridworld
from MBRLAgents import DynaAgent, PrioritizedSweepingAgent
from Helper import LearningCurvePlot, smooth
import matplotlib.pyplot as plt

def run_repetitions_dyna(n_rep, n_timesteps, eval_interval, epsilon, learning_rate, n_planning_updates, wind_proportion):
    learning_curves = []
    max_episode_length = 100
    for rep in range(n_rep):
        env = WindyGridworld(wind_proportion=wind_proportion)
        agent = DynaAgent(n_states=env.n_states,
                          n_actions=env.n_actions,
                          learning_rate=learning_rate,
                          gamma=1.0)

        evaluations = []
        s = env.reset()
        for timestep in range(n_timesteps):
            print(timestep)
            a = agent.select_action(s, epsilon)
            s_next, r, done = env.step(a)
            agent.update(s=s, a=a, r=r, done=done, s_next=s_next, n_planning_updates=n_planning_updates)
            #if timestep == 10000:
                #env.render(Q_sa=agent.Q_sa, plot_optimal_policy=True,)
            # set environment state again.
            if done:
                s = env.reset()
            else:
                s = s_next
            if timestep % eval_interval == 0:
                eval_return = agent.evaluate(env, n_eval_episodes=30, max_episode_length=max_episode_length)
                evaluations.append(eval_return)
        learning_curves.append(evaluations)

    avg_learning_curve = np.mean(learning_curves, axis=0)
    return avg_learning_curve

def run_repetitions_prioritized(n_rep, n_timesteps, eval_interval, epsilon, learning_rate, n_planning_updates, wind_proportion):
    learning_curves = []
    max_episode_length = 100

    for rep in range(n_rep):
        env = WindyGridworld(wind_proportion=wind_proportion)
        agent = PrioritizedSweepingAgent(n_states=env.n_states,
                          n_actions=env.n_actions,
                          learning_rate=learning_rate,
                          gamma=1.0)

        evaluations = []
        s = env.reset()
        for timestep in range(n_timesteps):
            #if(timestep == n_timesteps-1):
            #    print(timestep)
            a = agent.select_action(s, epsilon)
            s_next, r, done = env.step(a)
            agent.update(s=s, a=a, r=r, done=done, s_next=s_next, n_planning_updates=n_planning_updates)
            # set environment state again.
            if done:
                s = env.reset()
            else:
                s = s_next

            if timestep % eval_interval == 0:
                eval_return = agent.evaluate(env, n_eval_episodes=30, max_episode_length=max_episode_length)
                evaluations.append(eval_return)

        learning_curves.append(evaluations)

    avg_learning_curve = np.mean(learning_curves, axis=0)


    return avg_learning_curve

def experiment_dyna():
    n_planning_updates = [1, 3, 5]

    for i in n_planning_updates:
        avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                         epsilon=0.1, learning_rate=0.2,
                                         n_planning_updates=i, wind_proportion=0.9)

        avg_curve = smooth(avg_curve, window=20, )

        plt.plot(avg_curve, label=f'n_planning_updates={i}')
    avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=0, wind_proportion=0.9)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label=f'model-free q-learning baseline')
    plt.xlabel('Evaluations')
    plt.ylabel('Episode Return')
    plt.legend()
    plt.title('Performance of DynaAgent with 0.9 wind')
    plt.savefig('dyna_09_wind.png', dpi=300, )
    plt.show()


    for i in n_planning_updates:
        avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                         epsilon=0.1, learning_rate=0.2,
                                         n_planning_updates=i, wind_proportion=1.0)

        avg_curve = smooth(avg_curve, window=20, )

        plt.plot(avg_curve, label=f'n_planning_updates={i}')

    avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=0, wind_proportion=1.0)
    avg_curve = smooth(avg_curve, window=20,)
    plt.plot(avg_curve, label=f'model-free q-learning baseline')

    plt.xlabel('Evaluations')
    plt.ylabel('Episode Return')
    plt.legend()
    plt.title('Performance of DynaAgent with 1.0 wind')

    plt.savefig('dyna_1_wind.png')
    plt.show()

def experiment_prioritized():
    n_planning_updatess = [1,3,5]
    for i in n_planning_updatess:
        avg_curve = run_repetitions_prioritized(n_rep=10, n_timesteps=10001, eval_interval=250,
                                         epsilon=0.1, learning_rate=0.2,
                                         n_planning_updates=i, wind_proportion=0.9)
        avg_curve = smooth(avg_curve, window=20,)

        plt.plot(avg_curve, label=f'n_planning_updates={i}')
        print(i)
    avg_curve = run_repetitions_prioritized(n_rep=10, n_timesteps=10001, eval_interval=250,
                                            epsilon=0.1, learning_rate=0.2,
                                            n_planning_updates=0, wind_proportion=0.9)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label=f'model-free q-learning baseline')

    plt.xlabel('Evaluations')
    plt.ylabel('Average Return')
    plt.legend()
    plt.title('Performance of Prioritized sweeping with 0.9 wind')
    plt.savefig('ps_09_wind.png')
    plt.show()

    for i in n_planning_updatess:
        avg_curve = run_repetitions_prioritized(n_rep=10, n_timesteps=10001, eval_interval=250,
                                         epsilon=0.1, learning_rate=0.2,
                                         n_planning_updates=i, wind_proportion=1.0)
        avg_curve = smooth(avg_curve, window=20,)

        plt.plot(avg_curve, label=f'n_planning_updates={i}')
        print(i)
    avg_curve = run_repetitions_prioritized(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=0, wind_proportion=1.0)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label=f'model-free q-learning baseline')
    plt.xlabel('Evaluations')
    plt.ylabel('Average Return')
    plt.legend()
    plt.title('Performance of Prioritized sweeping  with 1.0 wind')
    plt.savefig('ps_1_wind.png')
    plt.show()

def comparison_experiment_stochastic():
    avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=3, wind_proportion=0.9)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label='Dyna with 3 planing updates')

    avg_curve = run_repetitions_prioritized(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=3, wind_proportion=0.9)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label='Prioritized sweeping with 3 planning updates')
    avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=0, wind_proportion=0.9)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label=f'q-learning baseline')
    plt.xlabel('Evaluations')
    plt.ylabel('Average Return')
    plt.legend()
    plt.title('Comparison of best performing models with 0.9 wind')
    plt.savefig('comparison_09_wind.png')
    plt.show()


def comparison_experiment_deterministic():
    # deterministic
    avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=5, wind_proportion=1.0)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label='Dyna with 5 planing updates')

    avg_curve = run_repetitions_prioritized(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=5, wind_proportion=1.0)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label='Prioritized sweeping with 5 planing updates')
    avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=10001, eval_interval=250,
                                     epsilon=0.1, learning_rate=0.2,
                                     n_planning_updates=0, wind_proportion=1.0)
    avg_curve = smooth(avg_curve, window=20, )
    plt.plot(avg_curve, label=f'q-learning baseline')

    plt.xlabel('Evaluations')
    plt.ylabel('Average Return')
    plt.legend()
    plt.title('Comparison of best performing models with 1.0 wind')
    plt.savefig('comparison_1_wind.png')
    plt.show()

def experiment_dyna_further():
        for i in [3, 5]:
            avg_curve = run_repetitions_dyna(n_rep=10, n_timesteps=30001, eval_interval=250,
                                             epsilon=0.1, learning_rate=0.2,
                                             n_planning_updates=i, wind_proportion=0.9)

            avg_curve = smooth(avg_curve, window=20, )

            plt.plot(avg_curve, label=f'n_planning_updates={i}')
        plt.xlabel('Evaluations')
        plt.ylabel('Average Return')
        plt.legend()
        plt.title('Performance of Dyna sweeping  with 0.9 wind')
        plt.savefig('dyna_further_search.png')
        plt.show()

def experiment():
    n_timesteps = 10001
    eval_interval = 250
    n_repetitions = 10
    gamma = 1.0
    learning_rate = 0.2
    epsilon=0.1
    wind_proportions=[0.9,1.0]
    # I used them in experiment functions.
    experiment_dyna()
    experiment_dyna_further()
    experiment_prioritized()
    comparison_experiment_stochastic()
    comparison_experiment_deterministic()
    
if __name__ == '__main__':
    experiment()
