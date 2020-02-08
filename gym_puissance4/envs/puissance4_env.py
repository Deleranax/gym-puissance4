from threading import \
    Thread

import gym
from gym import error, utils, spaces

try:
    import tkinter as tk
except ImportError as ie:
    error.DependencyNotInstalled(ie)


class Puissance4Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # Variables
        self.grid = []
        self.has_won = False
        self.turn = 0
        self.turn_logical = False
        self.pawn = 0
        self.reward = 0
        self.last_turn_reward = [0, 0]
        self.thread = None
        self.done = False

        # Créer la grille
        for y in range(6):
            self.grid.append([0] * 7)

        # Env
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Tuple((
            spaces.Discrete(2),
            spaces.Tuple(tuple(
                spaces.Tuple(tuple(
                    spaces.Discrete(3) for i in range(7)
                )) for i in range(6)
            ))
        ))

    def step(self, action):
        if not self.turn_logical:
            self.pawn = 1
        else:
            self.pawn = 2

        if not action >= 0 or action <= 6:
            error.InvalidAction("Action must be a number between 0 and 6 inclued.")

        play_valid = self.add_pawn(action)
        self.reward = -1

        if play_valid:
            self.reward = self.get_reward()

        if not self.turn_logical:
            self.turn_logical = True
        else:
            self.turn_logical = False
            self.turn += 1

        self.done = self.has_won or self.is_grid_full()

        return (self.pawn-1, tuple(tuple(i) for i in self.grid)), self.reward, self.done, {}

    def reset(self):
        if self.thread is not None:
            self.thread.stop()
        self.__init__()

    def render(self, mode='human', close=False):
        if close:
            self.thread.done = False
        if self.thread is None:
            self.thread = WindowThread()
        else:
            self.thread.update(self.grid, self.pawn, self.reward, self.done)

    def is_column_full(self, colonne):
        for i in self.grid:
            if i[colonne] == 0:
                return False
        return True

    def is_grid_full(self):
        for i in range(len(self.grid[0])):
            if not self.is_column_full(i):
                return False
        return True

    def add_pawn(self, colonne):
        if self.is_column_full(colonne):
            return False
        else:
            for i in range(len(self.grid)):
                if self.grid[i][colonne] != 0:
                    self.grid[i - 1][colonne] = self.pawn
                    return True
                elif i == len(self.grid) - 1:
                    self.grid[i][colonne] = self.pawn
                    return True

    def count_lines(self, length):
        count = 0

        # Colonnes
        for x in range(len(self.grid[0])):
            for y in range(len(self.grid) - length + 1):
                condition = True
                for i in range(length):
                    condition = condition and self.grid[y + i][x] == self.pawn
                if condition:
                    count += 1

        # Lignes
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0]) - length + 1):
                condition = True
                for i in range(length):
                    condition = condition and self.grid[y][x + i] == self.pawn
                if condition:
                    count += 1

        # Digonales 1
        for y in range(len(self.grid) - length + 1):
            for x in range(len(self.grid[0]) - length + 1):
                condition = True
                for i in range(length):
                    condition = condition and self.grid[y + i][x + i] == self.pawn
                if condition:
                    count += 1

        # Digonales 2
        for y in range(len(self.grid) - length + 1):
            for x in range(length-1, len(self.grid[0])):
                condition = True
                for i in range(length):
                    condition = condition and self.grid[y + i][x - i] == self.pawn
                if condition:
                    count += 1
        if length == 4 and count > 0:
            self.has_won = True
        return count

    def get_reward(self):
        if self.count_lines(4) >= 1:
            reward = 50.0
        elif self.turn_logical:
            reward = (self.count_lines(3) * 6) + self.count_lines(2) - (0.1*self.turn)
            self.last_turn_reward[1] = reward
            reward = reward - (0.1*self.last_turn_reward[0])
        else:
            reward = (self.count_lines(3) * 6) + self.count_lines(2) - (0.1*self.turn)
            self.last_turn_reward[0] = reward
            reward = reward - (0.1*self.last_turn_reward[1])
        return reward


class WindowThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.loop = True
        self.update_needed = False
        self.grid = None
        self.pawn = None
        self.done = False
        self.reward = None
        self.canvas = None
        self.window = None
        self.start()

    def update(self, grid, pawn, reward, done):
        self.grid = grid
        self.pawn = pawn
        self.reward = reward
        self.update_needed = True
        self.done = done

    def destroyed(self):
        if self.done:
            self.window.destroy()
            self.window = None
            self.loop = False

    def stop(self):
        self.loop = False
        if self.window is not None:
            self.window.destroy()
            self.window = None
            self.loop = False

    def run(self):
        while self.loop:
            if self.window is None and not self.done:
                self.window = tk.Tk()
                self.window.protocol("WM_DELETE_WINDOW", self.destroyed)
                self.window.geometry('700x650')
                self.window.resizable(0, 0)
                self.window.title = "Puissance4"

                self.canvas = tk.Canvas(self.window, height=600, width=700)
                self.canvas.pack()
                tk.Label(self.window, text="Yellow: Player 0 | Red: Player 1").pack()
                self.label = tk.Label(self.window, text="Player 1 Score: 0.0")
                self.label.pack()

            if self.update_needed:
                self.update_needed = False
                self.canvas.create_rectangle(0, 0, 700, 600)
                for y in range(len(self.grid)):
                    for x in range(len(self.grid[y])):
                        if self.grid[y][x] == 0:
                            self.canvas.create_rectangle(x*100, y*100, (x+1)*100, (y+1)*100, fill="white")
                        elif self.grid[y][x] == 1:
                            self.canvas.create_rectangle(x*100, y*100, (x+1)*100, (y+1)*100, fill="yellow")
                        else:
                            self.canvas.create_rectangle(x*100, y*100, (x+1)*100, (y+1)*100, fill="red")
                self.label.configure(text="Player {} ".format(self.pawn-1) + "Score: {}".format(self.reward))

            if self.loop and self.window is not None:
                self.window.update()

            if self.done:
                self.stop()
