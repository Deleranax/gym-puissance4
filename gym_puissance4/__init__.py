from gym.envs.registration import register
import gym_puissance4.envs

register(
    id='puissance4-v0',
    entry_point='gym_puissance4.envs:Puissance4Env',
)