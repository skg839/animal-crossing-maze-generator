import random

class Cell:
    wall_pairs = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'N': True, 'S': True, 'E': True, 'W': True}

    def has_all_walls(self):
        return all(self.walls.values())

    def knock_down_wall(self, other, wall):
        self.walls[wall] = False
        other.walls[Cell.wall_pairs[wall]] = False

class Maze:
    def __init__(self, nx, ny, ix=0, iy=0):
        self.nx, self.ny = nx, ny
        self.ix, self.iy = ix, iy
        self.maze_map = [[Cell(x, y) for y in range(ny)] for x in range(nx)]

    def cell_at(self, x, y):
        return self.maze_map[x][y]

    def __str__(self):
        maze_rows = ['-' * self.nx * 2]
        for y in range(self.ny):
            maze_row = ['|']
            for x in range(self.nx):
                if self.maze_map[x][y].walls['E']:
                    maze_row.append(' |')
                else:
                    maze_row.append('  ')
            maze_rows.append(''.join(maze_row))
            maze_row = ['|']
            for x in range(self.nx):
                if self.maze_map[x][y].walls['S']:
                    maze_row.append('-+')
                else:
                    maze_row.append(' +')
            maze_rows.append(''.join(maze_row))
        return '\n'.join(maze_rows)

    def write_svg(self, filename):
        aspect_ratio = self.nx / self.ny
        padding = 0
        height = 480
        width = int(height * aspect_ratio)
        scy, scx = height / self.ny, width / self.nx

        def write_wall(f, x1, y1, x2, y2):
            print('<line x1="{}" y1="{}" x2="{}" y2="{}"/>'
                  .format(x1, y1, x2, y2), file=f)

        with open(filename, 'w') as f:
            print('<?xml version="1.0" encoding="utf-8"?>', file=f)
            print('<svg xmlns="http://www.w3.org/2000/svg"', file=f)
            print('    xmlns:xlink="http://www.w3.org/1999/xlink"', file=f)
            print('    width="{:d}" height="{:d}" viewBox="{} {} {} {}">'
                  .format(width+2*padding, height+2*padding,
                          -padding, -padding, width+2*padding, height+2*padding),
                  file=f)
            print('<defs>\n<style type="text/css"><![CDATA[', file=f)
            print('line {', file=f)
            print('    stroke: #000000;\n    stroke-linecap: square;', file=f)
            print('    stroke-width: 5;\n}', file=f)
            print(']]></style>\n</defs>', file=f)

            for x in range(self.nx):
                for y in range(self.ny):
                    if self.cell_at(x, y).walls['S']:
                        x1, y1_, x2, y2_ = x*scx, (y+1)*scy, (x+1)*scx, (y+1)*scy
                        write_wall(f, x1, y1_, x2, y2_)
                    if self.cell_at(x, y).walls['E']:
                        x1, y1_, x2, y2_ = (x+1)*scx, y*scy, (x+1)*scx, (y+1)*scy
                        write_wall(f, x1, y1_, x2, y2_)
            print('<line x1="0" y1="0" x2="{}" y2="0"/>'.format(width), file=f)
            print('<line x1="0" y1="0" x2="0" y2="{}"/>'.format(height), file=f)
            print('</svg>', file=f)

    def find_valid_neighbours(self, cell):
        delta = [('W', (-1, 0)),
                 ('E', (1, 0)),
                 ('S', (0, 1)),
                 ('N', (0, -1))]
        neighbours = []
        for direction, (dx, dy) in delta:
            x2, y2 = cell.x + dx, cell.y + dy
            if (0 <= x2 < self.nx) and (0 <= y2 < self.ny):
                neighbour = self.cell_at(x2, y2)
                if neighbour.has_all_walls():
                    neighbours.append((direction, neighbour))
        return neighbours

    def make_maze(self):
        n = self.nx * self.ny
        cell_stack = []
        current_cell = self.cell_at(self.ix, self.iy)
        nv = 1

        while nv < n:
            neighbours = self.find_valid_neighbours(current_cell)

            if not neighbours:
                current_cell = cell_stack.pop()
                continue
            direction, next_cell = random.choice(neighbours)
            current_cell.knock_down_wall(next_cell, direction)
            cell_stack.append(current_cell)
            current_cell = next_cell
            nv += 1