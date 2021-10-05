import pygame
import math
from queue import PriorityQueue

from pygame.constants import CONTROLLER_BUTTON_DPAD_LEFT

#Set up the GUI as a square
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

#Here we determine how the algorithm will indentify each node
    #Return coordinates of the node
    def get_pos(self):
        return self.row, self.col
    #Nodes already visited and considered
    def is_closed(self):
        return self.color == RED
    #If the node is in the open set
    def is_open(self):
        return self.color == GREEN
    def is_barrier(self):
        return self.color == BLACK
    def is_start(self):
        return self.color == ORANGE
    def is_end(self):
        return self.color == TURQUOISE    
    def reset(self):
        self.color = WHITE
    
    #Will make the node the selected color
    def make_closed(self):
        self.color = RED
    def make_open(self):
        self.color = GREEN
    def make_barrier(self):
        self.color = BLACK
    def make_start(self):
        self.color = ORANGE
    def make_end(self):
        self.color = TURQUOISE
    def make_path(self):
        self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    #checks the adjacent nodes and makes sure they are not barriers
    #if not, adds them in the neighbor list
    def update_neighbors(self, grid):
        self.neighbors = []
        #down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        #up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        #right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        #left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

        

    #"less than", compare the actual node with another node,
    #and will always confirm that 'other' spot is greater than the actual spot
    def __lt__(self, other):
        return False

#The heuristic, that gets us the distance between start(p1) and end node(p2)
#using Manhattan distance   
def heuristic(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

#goes from the end node to the start node and display the path
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

#The actual algorithm to find the path
def algorithm(draw, grid, start, end):
    #in case there is a tie on the weight of 2 nodes, checks who came first
    count = 0 
    #keep tracks of the smaller item
    open_set = PriorityQueue()
    #adds start to the open set with priority queue
    open_set.put((0, count, start)) 
    #dictionary to see from where the node came from
    came_from = {} 

    #with this method we make sure that even if we reach the end node
    #we do not assume that is the shortest path but we still check
    #for better options
    #g_score tracks the current shortest distance from start to finish
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    #f_score estimates how far is the end node from the beginning
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    #keeps track of item in the priority queue and item that are not
    open_set_hash = {start}

    #if we have checked all nodes might mean that there is no path
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        #we get the node associated with the smallest value
        current = open_set.get()[2]
        #removes the set from the priority queue and 
        #insert it in the hash, to make sure we do not have duplicates
        open_set_hash.remove(current)

        #means we found the shortest path, and now we backtrack to the start
        #thus creating the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        #considers all of the neighbors of the current node
        #and we go to the next one
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            #in case this neighbor is better that the last one
            #we update the path and update the hash (if not already there)
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + heuristic(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current != start:
            current.make_closed()

    return None

#Iterates by creating lists inside a list, in order to create a grid with nodes inside it
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid

#Draw the grid lines (for visual)
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        #draws horizontal lines
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            #draws vertical lines
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

#Colors the map
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)
    
    draw_grid(win, rows, width)
    pygame.display.update()

#Gets where the mouse is and where is clicking
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y,x = pos
    #Tells in which node (cube) we are
    row = y // gap
    col = x //gap

    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    #Checks for every event occurring
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            #[0] = left mouse button
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                #which node we clicked on
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                #if not already setted, creates start and end node
                #and also make sure that they cannot be the same node
                if not start and node != end:
                    start = node
                    start.make_start()
                
                elif not end and node != start:
                    end = node
                    end.make_end()
                #Only if we're not clicking on start or end
                #then every click will create a barrier
                elif node != end and node != start:
                    node.make_barrier()


            #[2] = right mouse button, for 'resetting' elements
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None
            #if spacebar is pressed the algorithm will start
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    #calls the algorithm (through a Lambda function)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                
                #resets the grid when 'C' is pressed
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()

main(WIN, WIDTH)

