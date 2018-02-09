import gym
import gym_gomoku
import numpy as np

env = gym.make('Gomoku19x19-v0') # default 'beginner' level opponent policy

env.reset()
s, r, d, _ = env.step(360)
env.render()
s1, r1, d1, _ = env.step(24)
env.render()

print(str(s))
flat_s = np.reshape(s, [-1])
for idx in range(len(flat_s)):
    if flat_s[idx] >= 2:
        flat_s[idx] = -1

print(flat_s)


'''
# play a game
env.reset()
for _ in range(20):
    action = env.action_space.sample() # sample without replacement
    observation, reward, done, info = env.step(action)
    env.render()
    if done:
        print ("Game is Over")
        break
'''
