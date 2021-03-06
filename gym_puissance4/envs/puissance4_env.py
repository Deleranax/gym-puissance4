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
        self.thread = None
        self.done = False
        self.columns = [0, 0, 0, 0, 0, 0, 0]
        self.last_three_lines = [0, 0]
        self.last_two_lines = [0, 0]

        # Créer la grille
        for y in range(6):
            self.grid.append([0] * 7)

        # Env
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Tuple((
            spaces.Discrete(2),
            spaces.Tuple(tuple(
                spaces.Tuple(tuple(
                    spaces.Discrete(3) for e in range(7)
                )) for i in range(6)
            ))
        ))

    def step(self, action):
        if not self.turn_logical:
            self.pawn = 1
        else:
            self.pawn = 2

        play_valid = self.add_pawn(action)

        if not self.turn_logical:
            self.turn_logical = True
        else:
            self.turn_logical = False
            self.turn += 1

        self.get_reward(play_valid)

        self.done = self.has_won or self.is_grid_full()

        return tuple(tuple(i) for i in self.grid), self.reward, self.done, {}

    def reset(self):
        # Variables
        self.grid = []
        self.has_won = False
        self.turn = 0
        self.turn_logical = False
        self.pawn = 0
        self.reward = 0
        self.done = False
        self.columns = [0, 0, 0, 0, 0, 0, 0]
        self.last_three_lines = [0, 0]
        self.last_two_lines = [0, 0]

        # Créer la grille
        for y in range(6):
            self.grid.append([0] * 7)

        return tuple(tuple(i) for i in self.grid)

    def render(self, mode='human', close=False):
        if close:
            if self.thread is not None:
                self.thread.close()
            return
        if self.thread is None:
            self.thread = WindowThread()
        else:
            self.thread.update(self.grid, self.pawn, self.reward, self.done)

    def is_column_full(self, colonne):
        if self.columns[colonne] < 6:
            return False
        return True

    def is_grid_full(self):
        if self.columns[0] + self.columns[1] + self.columns[2] + self.columns[3] + self.columns[4] + self.columns[5] + self.columns[6] < 42:
            return False
        return True

    def add_pawn(self, colonne):
        if self.is_column_full(colonne):
            return False
        else:
            self.grid[5 - self.columns[colonne]][colonne] = self.pawn
            self.columns[colonne] += 1
            return True

    def count_lines(self):
        lines = [0, 0, 0]

        # Colonnes
        for x in range(len(self.grid[0])):
            for y in range(len(self.grid) - 3):
                condition = True
                for i in range(0, 4):
                    condition = condition and self.grid[y + i][x] == self.pawn
                    if condition and i > 0:
                        lines[i - 1] += 1

        # Lignes
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0]) - 3):
                condition = True
                for i in range(0, 4):
                    condition = condition and self.grid[y][x + i] == self.pawn
                    if condition and i > 0:
                        lines[i - 1] += 1

        # Digonales 1
        for y in range(len(self.grid) - 3):
            for x in range(len(self.grid[0]) - 3):
                condition = True
                for i in range(0, 4):
                    condition = condition and self.grid[y + i][x + i] == self.pawn
                    if condition and i > 0:
                        lines[i - 1] += 1

        # Digonales 2
        for y in range(len(self.grid) - 3):
            for x in range(3, len(self.grid[0])):
                condition = True
                for i in range(0, 4):
                    condition = condition and self.grid[y + i][x - i] == self.pawn
                    if condition and i > 0:
                        lines[i - 1] += 1

        if lines[2] > 0:
            self.has_won = True
        return lines[2], lines[1], lines[0]

    def get_reward(self, valid):
        four_lines, three_lines, two_lines = self.count_lines()
        if not valid:
            self.reward = -0.1
        elif self.is_grid_full():
            self.reward = 0.5
        elif four_lines > 0:
            self.reward = 1
        elif three_lines > self.last_three_lines[self.pawn-1]:
            self.reward = 0.5
        elif two_lines > self.last_two_lines[self.pawn-1]:
            self.reward = 0.1
        else:
            self.reward = 0
        self.last_three_lines[self.pawn-1], self.last_two_lines[self.pawn-1] = three_lines, two_lines


class WindowThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.has_to_close = False
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

    def stop(self):
        self.loop = False
        if self.window is not None:
            self.window.destroy()
            self.window = None
            self.loop = False

    def close(self):
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

            if not self.loop:
                self.stop()
