import gym
from gym import error, utils, spaces

try:
    import tkinter
except ImportError as ie:
    error.DependencyNotInstalled(ie)


class Puissance4Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # Variables
        self.grille = []
        self.has_won = False

        # Créer la grille
        for y in range(6):
            self.grille.append([" "] * 7)

        # Env
        self.action_space = spaces.Tuple((spaces.Discrete(7),spaces.Discrete(2)))
        self.observation_space = spaces.Tuple((spaces.Tuple()))

    def step(self, action):
        pawn = action[0]
        action = action[1]
        play_valid = self.add_pawn(action, pawn)
        reward = -1
        if play_valid:
            reward = self.get_reward(pawn)
        return tuple(tuple(i) for i in self.grille), reward, self.has_won, {}

    def reset(self):
        self.__init__()

    def render(self, mode='human', close=False):
        print("\n* " + "− " * len(self.grille[0]) + "*", end="\n")
        for y in self.grille:
            print("|", end=" ")
            for x in y:
                print(x, end=" ")
            print("|")
        print("* " + "- " * len(self.grille[0]) + "*\n")

    def is_column_full(self, colonne):
        for i in self.grille:
            if i[colonne] == " ":
                return False
        return True

    def is_grid_full(self):
        for i in range(len(self.grille[0])):
            if not self.is_column_full(i):
                return False
        return True

    def add_pawn(self, colonne, pawn):
        if self.is_column_full(colonne):
            return False
        else:
            for i in range(len(self.grille)):
                if self.grille[i][colonne] != " ":
                    self.grille[i - 1][colonne] = pawn
                    return True
                elif i == len(self.grille) - 1:
                    self.grille[i][colonne] = pawn
                    return True

    def count_lines(self, length, pawn):
        count = 0

        # Colonnes
        for x in range(len(self.grille[0])):
            for y in range(len(self.grille) - 3):
                condition = True
                for i in range(length):
                    condition = condition and self.grille[y + i][x] == pawn
                if condition:
                    count += 1
        # Lignes
        for y in range(len(self.grille)):
            for x in range(len(self.grille[0]) - 3):
                condition = True
                for i in range(length):
                    condition = condition and self.grille[y][x + i] == pawn
                if condition:
                    count += 1

        # Digonales 1
        for y in range(len(self.grille) - 3):
            for x in range(len(self.grille[0]) - 3):
                condition = True
                for i in range(length):
                    condition = condition and self.grille[y + i][x + i] == pawn
                if condition:
                    count += 1

        # Digonales 2
        for y in range(len(self.grille) - 3):
            for x in range(3, len(self.grille[0])):
                condition = True
                for i in range(length):
                    condition = condition and self.grille[y + i][x - i] == pawn
                if condition:
                    count += 1
        if length == 4 and count > 0:
            self.has_won = True
        return count

    def get_reward(self, pawn):
        return self.count_lines(3, pawn) * 3 + self.count_lines(2, pawn)
