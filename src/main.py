from tkinter import *
from tkinter import font
from tkinter import messagebox
from functools import partial
from operator import attrgetter
import numpy
import random
import math
import os

class MainMaze:

    class CreateToolTip(object):
        def __init__(self, widget, text='widget info'):
            self.waittime = 500 
            self.wraplength = 180 
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)
            self._id = None
            self.tw = None

        def enter(self, event=None):
            self.schedule()

        def leave(self, event=None):
            self.unschedule()
            self.hidetip()

        def schedule(self):
            self.unschedule()
            self._id = self.widget.after(self.waittime, self.showtip)

        def unschedule(self):
            _id = self._id
            self._id = None
            if _id:
                self.widget.after_cancel(_id)

        def showtip(self, event=None):
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            self.tw = Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = Label(self.tw, text=self.text, justify='left', background="#ffffff",
                          relief='solid', borderwidth=1, wraplength=self.wraplength)
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tw
            self.tw = None
            if tw:
                tw.destroy()

    class MyMaze(object):

        def __init__(self, x_dimension, y_dimension):
            self.dimensionX = x_dimension         
            self.dimensionY = y_dimension
            self.gridDimensionX = x_dimension * 2 + 1 
            self.gridDimensionY = y_dimension * 2 + 1
            self.mazeGrid = [[' ' for y in range(self.gridDimensionY)] for x in range(self.gridDimensionX)]
            self.cells = [[self.Cell(x, y, False) for y in range(self.dimensionY)] for x in range(self.dimensionX)]
            self.generate_maze()
            self.update_grid()

        class Cell(object):
            def __init__(self, x, y, is_wall=True):
                self.neighbors = []  
                self.open = True   
                self.x = x          
                self.y = y
                self.wall = is_wall 

            def add_neighbor(self, other):
                if other not in self.neighbors: 
                    self.neighbors.append(other)
                if self not in other.neighbors: 
                    other.neighbors.append(self)

            def is_cell_below_neighbor(self):
                return self.__class__(self.x, self.y + 1) in self.neighbors

            def is_cell_right_neighbor(self):
                return self.__class__(self.x + 1, self.y) in self.neighbors

            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    return self.x == other.x and self.y == other.y
                else:
                    return False

        def generate_maze(self):
            start_at = self.get_cell(0, 0)
            start_at.open = False 
            cells = [start_at]
            while cells:
                if random.randint(0, 9) == 0:
                    cell = cells.pop(random.randint(0, cells.__len__()) - 1)
                else:
                    cell = cells.pop(cells.__len__() - 1)
                neighbors = []
                potential_neighbors = [self.get_cell(cell.x + 1, cell.y), self.get_cell(cell.x, cell.y + 1),
                                       self.get_cell(cell.x - 1, cell.y), self.get_cell(cell.x, cell.y - 1)]
                for other in potential_neighbors:
                    if other is None or other.wall or not other.open:
                        continue
                    neighbors.append(other)
                if not neighbors:
                    continue
                selected = neighbors[random.randint(0, neighbors.__len__()) - 1]
                selected.open = False
                cell.add_neighbor(selected)
                cells.append(cell)
                cells.append(selected)

        def get_cell(self, x, y):
            if x < 0 or y < 0:
                return None
            try:
                return self.cells[x][y]
            except IndexError:
                return None

        def update_grid(self):
            back_char = ' '
            wall_char = 'X'
            cell_char = ' '
            for x in range(self.gridDimensionX):
                for y in range(self.gridDimensionY):
                    self.mazeGrid[x][y] = back_char
            for x in range(self.gridDimensionX):
                for y in range(self.gridDimensionY):
                    if x % 2 == 0 or y % 2 == 0:
                        self.mazeGrid[x][y] = wall_char
            for x in range(self.dimensionX):
                for y in range(self.dimensionY):
                    current = self.get_cell(x, y)
                    grid_x = x * 2 + 1
                    grid_y = y * 2 + 1
                    self.mazeGrid[grid_x][grid_y] = cell_char
                    if current.is_cell_below_neighbor():
                        self.mazeGrid[grid_x][grid_y + 1] = cell_char
                    if current.is_cell_right_neighbor():
                        self.mazeGrid[grid_x + 1][grid_y] = cell_char

    class Cell(object):

        def __init__(self, row, col):
            self.row = row  
            self.col = col
            self.dist = 0
            self.prev = self.__class__

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.row == other.row and self.col == other.col
            else:
                return False

    INFINITY = sys.maxsize 
    EMPTY = 0    
    OBST = 1        
    ROBOT = 2      
    TARGET = 3     
    FRONTIER = 4    
    CLOSED = 5      
    ROUTE = 6 

    def __init__(self, maze):
        self.center(maze)

        self.rows = 41                            
        self.columns = 41                          
        self.square_size = int(500/self.rows)    

        self.openSet = []    
        self.closedSet = []  
        self.graph = []      

        self.robotStart = self.Cell(self.rows - 2, 1)    
        self.targetPos = self.Cell(1, self.columns - 2)  

        self.grid = [[]]
        self.found = False       
        self.searching = False   
        self.endOfSearch = False 
        self.animation = False   
        self.delay = 1           
        self.expanded = 0         

        self.array = numpy.array([0] * (83 * 83))
        self.cur_row = self.cur_col = self.cur_val = 0
        app_highlight_font = font.Font(app, family='Helvetica', size=10, weight='bold')


        self.buttons = list()
        for i, action in enumerate(("Clear", "Maze", "Go")):
            btn = Button(app, text=action,  width=20, font=app_highlight_font,  bg="light grey",
                         command=partial(self.select_action, action))
            btn.place(x=8+164*i, y=505)
            self.buttons.append(btn)

        self.canvas = Canvas(app, bd=0, highlightthickness=0)
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.drag)

        self.initialize_grid(False)

    def select_action(self, action):
        if action == "Clear":
            self.reset_click()
        elif action == "Maze":
            self.maze_click()
        elif action == "Go":
            self.animation_click()


    def left_click(self, event):
        row = int(event.y/self.square_size)
        col = int(event.x/self.square_size)
        if row in range(self.rows) and col in range(self.columns):
            if True if False else (not self.found and not self.searching):
                self.cur_row = row
                self.cur_col = col
                self.cur_val = self.grid[row][col]
                if self.cur_val == self.EMPTY:
                    self.grid[row][col] = self.OBST
                    self.paint_cell(row, col, "BLACK")
                if self.cur_val == self.OBST:
                    self.grid[row][col] = self.EMPTY
                    self.paint_cell(row, col, "WHITE")

    def drag(self, event):
        row = int(event.y/self.square_size)
        col = int(event.x/self.square_size)
        if row in range(self.rows) and col in range(self.columns):
            if True if False else (not self.found and not self.searching):
                if self.Cell(row, col) != self.Cell(self.cur_row, self.cur_col) and\
                        self.cur_val in [self.ROBOT, self.TARGET]:
                    new_val = self.grid[row][col]
                    if new_val == self.EMPTY:
                        self.grid[row][col] = self.cur_val
                        if self.cur_val == self.ROBOT:
                            self.grid[self.robotStart.row][self.robotStart.col] = self.EMPTY
                            self.paint_cell(self.robotStart.row, self.robotStart.col, "WHITE")
                            self.robotStart.row = row
                            self.robotStart.col = col
                            self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
                            self.paint_cell(self.robotStart.row, self.robotStart.col, "RED")
                        else:
                            self.grid[self.targetPos.row][self.targetPos.col] = self.EMPTY
                            self.paint_cell(self.targetPos.row, self.targetPos.col, "WHITE")
                            self.targetPos.row = row
                            self.targetPos.col = col
                            self.grid[self.targetPos.row][self.targetPos.col] = self.TARGET
                            self.paint_cell(self.targetPos.row, self.targetPos.col, "GREEN")
                        self.cur_row = row
                        self.cur_col = col
                        self.cur_val = self.grid[row][col]
                elif self.grid[row][col] != self.ROBOT and self.grid[row][col] != self.TARGET:
                    self.grid[row][col] = self.OBST
                    self.paint_cell(row, col, "BLACK")

    def initialize_grid(self, make_maze):
        if make_maze and self.rows % 2 == 0:
            self.rows -= 1
        if make_maze and self.columns % 2 == 0:
            self.columns -= 1
        self.square_size = int(500/(self.rows if self.rows > self.columns else self.columns))
        self.grid = self.array[:self.rows*self.columns]
        self.grid = self.grid.reshape(self.rows, self.columns)
        self.canvas.configure(width=self.columns*self.square_size+1, height=self.rows*self.square_size+1)
        self.canvas.place(x=10, y=10)
        self.canvas.create_rectangle(0, 0, self.columns*self.square_size+1,
                                     self.rows*self.square_size+1, width=0, fill="DARK GREY")
        for r in list(range(self.rows)):
            for c in list(range(self.columns)):
                self.grid[r][c] = self.EMPTY
        self.robotStart = self.Cell(self.rows-2, 1)
        self.targetPos = self.Cell(1, self.columns-2)
        self.fill_grid()
        if make_maze:
            maze = self.MyMaze(int(self.rows/2), int(self.columns/2))
            for x in range(maze.gridDimensionX):
                for y in range(maze.gridDimensionY):
                    if maze.mazeGrid[x][y] == 'X':  # maze.wall_char:
                        self.grid[x][y] = self.OBST
        self.repaint()

    def fill_grid(self):
        if self.searching or self.endOfSearch:
            for r in list(range(self.rows)):
                for c in list(range(self.columns)):
                    if self.grid[r][c] in [self.FRONTIER, self.CLOSED, self.ROUTE]:
                        self.grid[r][c] = self.EMPTY
                    if self.grid[r][c] == self.ROBOT:
                        self.robotStart = self.Cell(r, c)
            self.searching = False
        else:
            for r in list(range(self.rows)):
                for c in list(range(self.columns)):
                    self.grid[r][c] = self.EMPTY
            self.robotStart = self.Cell(self.rows-2, 1)
            self.targetPos = self.Cell(1, self.columns-2)
        self.expanded = 0
        self.found = False
        self.searching = False
        self.endOfSearch = False

        self.openSet.clear()
        self.closedSet.clear()
        self.openSet = [self.robotStart]
        self.closedSet = []

        self.grid[self.targetPos.row][self.targetPos.col] = self.TARGET
        self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT

        self.repaint()

    def repaint(self):
        color = ""
        for r in list(range(self.rows)):
            for c in list(range(self.columns)):
                if self.grid[r][c] == self.EMPTY:
                    color = "WHITE"
                elif self.grid[r][c] == self.ROBOT:
                    color = "RED"
                elif self.grid[r][c] == self.TARGET:
                    color = "GREEN"
                elif self.grid[r][c] == self.OBST:
                    color = "BLACK"
                elif self.grid[r][c] == self.FRONTIER:
                    color = "BLUE"
                elif self.grid[r][c] == self.CLOSED:
                    color = "CYAN"
                elif self.grid[r][c] == self.ROUTE:
                    color = "YELLOW"
                self.paint_cell(r, c, color)

    def paint_cell(self, row, col, color):
        self.canvas.create_rectangle(1 + col * self.square_size, 1 + row * self.square_size,
                                     1 + (col + 1) * self.square_size - 1, 1 + (row + 1) * self.square_size - 1,
                                     width=0, fill=color)

    def reset_click(self):
        self.animation = False
        for but in self.buttons:
            but.configure(state="normal")
        self.initialize_grid(False)

    def maze_click(self):
        self.animation = False
        for but in self.buttons:
            but.configure(state="normal")
        self.initialize_grid(True)


    def animation_click(self):
        self.animation = True
        if not self.searching:
            self.initialize_dijkstra()
        self.searching = True
        self.animation_action()

    def animation_action(self):
        if self.animation:
            self.check_termination()
            if self.endOfSearch:
                return
            self.canvas.after(self.delay, self.animation_action)


    def check_termination(self):
        if (not self.graph):
            self.endOfSearch = True
            self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
            self.buttons[2].configure(state="disabled")
            self.repaint()
        else:
            self.expand_node()
            if self.found:
                self.endOfSearch = True
                self.plot_route()
                self.buttons[2].configure(state="disabled")

    def expand_node(self):
        if not self.graph:
            return
        u = self.graph.pop(0)
        self.closedSet.append(u)
        if u == self.targetPos:
            self.found = True
            return
        self.expanded += 1
        self.grid[u.row][u.col] = self.CLOSED
        self.paint_cell(u.row, u.col, "CYAN")
        if u.dist == self.INFINITY:
            return
        neighbors = self.create_successors(u, False)
        for v in neighbors:
            alt = u.dist + self.dist_between(u, v)
            if alt < v.dist:
                v.dist = alt
                v.prev = u
                self.grid[v.row][v.col] = self.FRONTIER
                self.paint_cell(v.row, v.col, "BLUE")
                self.graph.sort(key=attrgetter("dist"))

    def create_successors(self, current, make_connected):
        r = current.row
        c = current.col
        temp = []

        if r > 0 and self.grid[r-1][c] != self.OBST:
            cell = self.Cell(r-1, c)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if r > 0 and c < self.columns-1 and self.grid[r-1][c+1] != self.OBST and \
                (self.grid[r-1][c] != self.OBST or self.grid[r][c+1] != self.OBST):
            cell = self.Cell(r-1, c+1)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if c < self.columns-1 and self.grid[r][c+1] != self.OBST:
            cell = self.Cell(r, c+1)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if r < self.rows-1 and c < self.columns-1 and self.grid[r+1][c+1] != self.OBST and \
                (self.grid[r+1][c] != self.OBST or self.grid[r][c+1] != self.OBST):
            cell = self.Cell(r+1, c+1)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if r < self.rows-1 and self.grid[r+1][c] != self.OBST:
            cell = self.Cell(r+1, c)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if r < self.rows-1 and c > 0 and self.grid[r+1][c-1] != self.OBST and \
                (self.grid[r+1][c] != self.OBST or self.grid[r][c-1] != self.OBST):
            cell = self.Cell(r+1, c-1)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if c > 0 and self.grid[r][c-1] != self.OBST:
            cell = self.Cell(r, c-1)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        if r > 0 and c > 0 and self.grid[r-1][c-1] != self.OBST:
            cell = self.Cell(r-1, c-1)
            if make_connected:
                temp.append(cell)
            elif cell in self.graph:
                graph_index = self.graph.index(cell)
                temp.append(self.graph[graph_index])

        return temp

    def dist_between(self, u, v):
        dx = u.col - v.col
        dy = u.row - v.row
        return math.sqrt(dx*dx + dy*dy)

    def plot_route(self):
        self.repaint()
        self.searching = False
        steps = 0
        distance = 0.0
        index = self.closedSet.index(self.targetPos)
        cur = self.closedSet[index]
        self.grid[cur.row][cur.col] = self.TARGET
        self.paint_cell(cur.row, cur.col, "GREEN")
        while cur != self.robotStart:
            steps += 1
            dx = cur.col - cur.prev.col
            dy = cur.row - cur.prev.row
            distance += math.sqrt(dx*dx + dy*dy)
            cur = cur.prev
            self.grid[cur.row][cur.col] = self.ROUTE
            self.paint_cell(cur.row, cur.col, "YELLOW")

        self.grid[self.robotStart.row][self.robotStart.col] = self.ROBOT
        self.paint_cell(self.robotStart.row, self.robotStart.col, "RED")

    def find_connected_component(self, v):
        stack = [v]
        self.graph.append(v)
        while stack:
            v = stack.pop()
            successors = self.create_successors(v, True)
            for c in successors:
                if c not in self.graph:
                    stack.append(c)
                    self.graph.append(c)

    def initialize_dijkstra(self):
        self.graph.clear()
        self.find_connected_component(self.robotStart)
        for v in self.graph:
            v.dist = self.INFINITY
            v.prev = None
        self.graph[self.graph.index(self.robotStart)].dist = 0
        self.graph.sort(key=attrgetter("dist"))
        self.closedSet.clear()
   

    @staticmethod
    def center(window):
        window.update_idletasks()
        w = window.winfo_screenwidth()
        h = window.winfo_screenheight()
        size = tuple(int(_) for _ in window.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        window.geometry("%dx%d+%d+%d" % (size + (x, y)))


def on_closing():
    if messagebox.askokcancel("Sair", "Você deseja sair?"):
        os._exit(0)


if __name__ == '__main__':
    app = Tk()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.title("Dijkstra")
    app.geometry("513x548")
    app.resizable(False, False)
    MainMaze(app)
    app.mainloop()
