from gym.envs.registration import register

register(
    id='puissance4-v0',
    entry_point='gym_puissance4.envs:Puissance4Env',
    reward_threshold=50.0
)