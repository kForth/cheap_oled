#!/usr/bin/env python
#
# Maze generator example for RPi-SSD1306
#
# Adapted from:
#    https://github.com/rm-hull/maze/blob/master/src/maze/generator.clj

import time
from random import randrange

from PIL import Image
from cheap_oled import OLED_SSD1306, OLED_SH1106, OLED_Canvas

NORTH = 1
WEST = 2

class Maze(object):

    def __init__(self, size):
        self.width = size[0]
        self.height = size[1]
        self.size = int(self.width * self.height)
        self.generate()

    def offset(self, coords):
        """ Converts [x,y] co-ords into an offset in the maze data """
        return ((coords[1] % self.height) * self.width) + (coords[0] % self.width)

    def coords(self, offset):
        """ Converts offset to [x,y] co-ords """
        return (offset % self.width, offset / self.width)

    def neighbours(self, pos):
        neighbours = []

        if pos > self.width:
            neighbours.append(pos - self.width)

        if pos % self.width > 0:
            neighbours.append(pos - 1)

        if pos % self.width < self.width - 1:
            neighbours.append(pos + 1)

        if pos + self.width < self.size:
            neighbours.append(pos + self.width)

        return neighbours

    def is_wall_between(self, p1, p2):
        """ Checks to see if there is a wall between two (adjacent) points
            in the maze. The return value will indicate true if there is a
            wall else false. If the points aren't adjacent, false is
            returned. """
        if p1 > p2:
            return self.is_wall_between(p2, p1)

        if p2 - p1 == self.width:
            return self.data[p2] & NORTH != 0

        if p2 - p1 == 1:
            return self.data[p2] & WEST != 0

        return False

    def knockdown_wall(self, p1, p2):
        """ Knocks down the wall between the two given points in the maze.
            Assumes that they are adjacent, otherwise it doesn't make any
            sense (and wont actually make any difference anyway) """
        if p1 > p2:
            return self.knockdown_wall(p2, p1)
        if p2 - p1 == self.width:
            self.data[p2] &= WEST

        if p2 - p1 == 1:
            self.data[p2] &= NORTH

    def generate(self):
        self.data = [ NORTH | WEST ] * self.size
        visited = { 0: True }
        stack = [0]
        not_visited = lambda x: not visited.get(x, False)

        while len(stack) > 0:
            curr = stack[-1]
            n = list(filter(not_visited, self.neighbours(curr)))
            sz = len(n)
            if sz == 0:
                stack.pop()
            else:
                np = n[randrange(sz)]
                self.knockdown_wall(curr, np)
                visited[np] = True
                if sz == 1:
                    stack.pop()
                stack.append(np)

    def render(self, draw, scale=lambda a: a):

        for i in range(self.size):
            line = []
            p1 = self.coords(i)

            if self.data[i] & NORTH > 0:
                p2 = (p1[0]+1, p1[1])
                line += p2 + p1

            if self.data[i] & WEST > 0:
                p3 = (p1[0], p1[1]+1)
                line += p1 + p3

            draw.line(list(map(scale, line)), fill=1)

        draw.rectangle(list(map(scale, [0, 0, self.width, self.height])), outline=1)

    def to_string(self):
        s = ""
        for y in range(self.height):
            for x in range(self.width):
                s += "+"
                if self.data[self.offset(x, y)] & NORTH != 0:
                    s += "---"
                else:
                    s += "   "
            s += "+\n"
            for x in range(self.width):
                if self.data[self.offset(x, y)] & WEST != 0:
                    s += "|"
                else:
                    s += " "
                s += "   "
            s += "|\n"
        s += "+---" * self.width
        s += "+\n"

        return s

def demo(pi, iterations):
    device = OLED_SSD1306(pi, port=1, address=0x3C)
    for loop in range(iterations):
        for scale in [2,3,4,3]:
            sz = [e // scale - 1 for e in (device.width, device.height)]
            with OLED_Canvas(device) as draw:
                Maze(sz).render(draw, lambda x: int(x * scale))
                time.sleep(1)
    device.close()

if __name__ == "__main__":
    import pigpio

    pi = pigpio.pi()

    if not pi.connected:
        exit()

    demo(pi, 20)
    
    pi.stop()
