import pygame
import numpy as np
from pygame.constants import MOUSEMOTION

x_res = 1400
y_res = 900

block_size = 20
grid = []

base_color_updating_mask = [[(1,3, 1), (1, 1, 1), (1, 1, 2)],
                            [(1, 1, 1), (-10, -33, 14), (1, 1, 1)],
                            [(7, 1, 1), (1, 1, 1), (1, 5, 1)]]


class Block:
    def __init__(self, position, colour):
        self.position = position
        self.colour = colour
        self.visible = False

    def add_colour(self, colour_addition):
        colour_1 = Block.normalize_colour_element(self.colour[0] + colour_addition[0])
        colour_2 = Block.normalize_colour_element(self.colour[1] + colour_addition[1])
        colour_3 = Block.normalize_colour_element(self.colour[2] + colour_addition[2])

        self.colour = (colour_1, colour_2, colour_3)

    @staticmethod
    def normalize_colour_element(colour_element):
        if colour_element > 255:
            return colour_element - 255
        if colour_element < 0:
            return 0 - colour_element
        return colour_element

    def get_block_center(self):
        return self.position[0] + self.position[2] / 2, self.position[1] + self.position[3] / 2

    def set_visible(self, visible):
        self.visible = visible

    def get_brightness(self):
        return self.colour[0] + self.colour[1] + self.colour[2]


class BlockDrawer:
    def __init__(self, sc, draw):
        self.sc = sc
        self.draw = draw

    def draw_blocks(self, block_grid):
        for block_row in block_grid:
            for block in block_row:
                if block.visible:
                    self.draw.rect(self.sc, block.colour, block.position)


def is_exist(grid_size, x, y):
    return 0 <= x < grid_size[0] and 0 <= y < grid_size[1]


def is_first_is_brigther(first_cell, second_cell):
    return first_cell.get_brightness() > second_cell.get_brightness()


class ColorUpdatingMask:
    def __init__(self, mask):
        self.mask = mask
        self.width = len(mask[0])
        self.height = len(mask)

    def get_updating_grid(self, grid_size):
        updating_grid = []
        for i in range(grid_size[0]):
            updating_grid_row = []
            for j in range(grid_size[1]):
                updating_grid_row.append((0, 0, 0))
            updating_grid.append(updating_grid_row)

        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                for k in range(self.height):
                    for l in range(self.width):
                        update_row = i + self.height // 2 - k
                        update_column = j + self.width // 2 - l
                        if is_exist(grid_size, update_row, update_column):
                            r, g, b = updating_grid[update_row][update_column]
                            a_r, a_g, a_b = self.mask[k][l]
                            new_r = ColorUpdatingMask.normalize_colour_element(r + a_r)
                            new_g = ColorUpdatingMask.normalize_colour_element(g + a_g)
                            new_b = ColorUpdatingMask.normalize_colour_element(b + a_b)
                            updating_grid[update_row][update_column] = (new_r, new_g, new_b)

        return updating_grid

    @staticmethod
    def normalize_colour_element(colour_element):
        if colour_element > 255:
            return colour_element - 255
        if colour_element < 0:
            return 0 - colour_element
        return colour_element


def update_colors(grid, color_updating_mask):
    grid_row_size = len(grid)
    grid_columns_size = len(grid[0])
    mask = color_updating_mask.mask
    for i in range(grid_row_size):
        for j in range(grid_columns_size):
            for k in range(color_updating_mask.height):
                for l in range(color_updating_mask.width):
                    update_row = i + color_updating_mask.height // 2 - k
                    update_column = j + color_updating_mask.width // 2 - l
                    if is_exist((grid_row_size, grid_columns_size), update_row, update_column) and is_first_is_brigther(grid[i][j], grid[update_row][update_column]):
                        grid[update_row][update_column].add_colour(mask[k][l])


def update_sector(block_sector, mask_sector):
    for i in range(len(block_sector)):
        for j in range(len(block_sector[0])):
            block_sector[i][j].add_colour(mask_sector[i][j])


def get_block(x, y):
    x_i = x // block_size
    y_i = y // block_size
    return grid[x_i][y_i]


pygame.init()

sc = pygame.display.set_mode((x_res, y_res))
clock = pygame.time.Clock()


def get_func(block):
    x, y = block.get_block_center()
    x = (700 - x) / 350
    y = (450 - y) / 350
    return (x * x + y * y - 1) ** 3 - x * x * y * y * y < 0.00001


def get_swastic_function(block):
    x = block.position[0]
    y = block.position[1]
    if (650 < x < 750 and 50 < y < 850) or (
            300 < x < 1100 and 400 < y < 500):
        return True
    if (450 < x < 750 and 775 < y < 850) or (
            650 < x < 950 and 50 < y < 125):
        return True
    if (300 < x < 375 and 200 < y < 500) or (
            1025 < x < 1100 and 400 < y < 700):
        return True
    return False


def get_dist(m_x, m_y, block):
    x, y = block.get_block_center()

    return ((m_x - x) ** 2 + (m_y - y) ** 2) ** 0.5


for i in range((x_res // block_size)):
    row = []
    for j in range((y_res // block_size)):
        if i == 0 or j == 0:
            row.append(Block((i * block_size + 1, j * block_size + 1, block_size - 2, block_size - 2), (-999999, -999999, -999999)))
        else:
            row.append(Block((i * block_size + 1, j * block_size + 1, block_size - 2, block_size - 2), (100, 100, 100)))

    grid.append(row)

t = 0
m_x, m_y = 730, 450
block_drawer = BlockDrawer(sc, pygame.draw)

colour_updating_mask = ColorUpdatingMask(base_color_updating_mask)
color_updating_grid = colour_updating_mask.get_updating_grid((len(grid), len(grid[0])))

cursor_block = Block((0, 0, 0, 0), (0, 0, 0))

for row in grid:
    for cell in row:
        color = (0, 0, 0)
        dist_k = get_dist(m_x, m_y, cell) / 300
        if get_func(cell):
            cell.set_visible(True)

while True:
    sc.fill((0, 0, 0))
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            m_x, m_y = pygame.mouse.get_pos()
            if 0 < m_x < x_res - block_size and 0 < m_y < y_res - block_size:
                cursor_block = get_block(m_x, m_y)
                if event.button == 1:
                    cursor_block.add_colour((100, 20, 10))
                if event.button == 3:
                    cursor_block.set_visible(not cursor_block.visible)

    update_colors(grid, colour_updating_mask)

    block_drawer.draw_blocks(grid)

    pygame.display.update()
