from gym.envs.registration import register

register(
    id='puissance4-v0',
    entry_point='gym-puissance4.envs:Puissance4Env',
)