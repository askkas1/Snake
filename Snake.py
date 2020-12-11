from random import randint, randrange
import pygame
import threading
from time import sleep


class Field():
    fps = 60
    food_list = []
    snakes_list = []
    margin = 1
    frame_color = (0, 200, 200)
    white = (255, 255, 255)
    blue = (204, 255, 255)
    test_color = (100, 100, 100)
    food_color = (255, 69, 0)
    get_color = lambda self, x, y: self.white if (x + y) % 2 == 0 else self.blue

    def __init__(self, count_blocks_x=10, count_blocks_y=10, size_block=25, snake_length=5):
        self.count_blocks_x = count_blocks_x
        self.count_blocks_y = count_blocks_y
        self.size_block = size_block
        self.snake_length = snake_length
        self.init_game()

    def add_snake(self, snake):
        self.snakes_list.append(snake)

    def field_map(self):
        for snake in self.snakes_list:
            pass

    def generate_food(self, cnt=5):
        for i in range(cnt):
            x, y = self.get_empty_field()
            if x + y:
                self.food_list.append((x, y))

    def check_xy_in_snake(self, x, y):
        for snakes in self.snakes_list:
            if (x, y) in snakes.snake_xy:
                return True
        return False

    def cell_fill_color(self, x, y, color=False):
        pygame.draw.rect(self.screen, self.get_color(x, y) if not color else color,
                         [10 + x * self.size_block + self.margin * (x + 1),
                          70 + y * self.size_block + self.margin * (y + 1),
                          self.size_block,
                          self.size_block])

    def get_empty_field(self):
        counter = 100
        while counter != 0:
            counter -= 1
            x     = randrange(0, self.count_blocks_x)
            y     = randrange(0, self.count_blocks_y)
            if not (x, y) in self.food_list:
                if not self.check_xy_in_snake(x, y):
                    return x, y
        return False

    def init_game(self):
        pygame.init()
        pygame.display.set_caption('Змейка')
        size = (self.count_blocks_x * (self.size_block + self.margin) + 700,
                self.count_blocks_y * (self.size_block + self.margin) + 100)
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(self.frame_color)
        self.draw_field()

    def game(self):
        clock = pygame.time.Clock()
        while True:
            pygame.event.get()
            # pygame.event.pump()
            # pygame.event.wait()
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         pygame.quit()

            self.render()
            pygame.display.update()
            clock.tick(self.fps)

    def draw_food(self):
        for food in self.food_list:
            self.cell_fill_color(food[0], food[1], self.food_color)

    def eat_food(self, x, y):
        self.food_list.remove((x, y))
        self.cell_fill_color(x, y, self.get_color(x, y))

    def draw_field(self):
        self.food_list.clear()
        for row in range(self.count_blocks_y):
            for column in range(self.count_blocks_x):
                if (column + row) % 2 == 0:
                    pygame.draw.rect(self.screen, self.white,
                                     [10 + column * self.size_block + self.margin * (column + 1),
                                      70 + row * self.size_block + self.margin * (row + 1), self.size_block,
                                      self.size_block])
                else:
                    pygame.draw.rect(self.screen, self.blue,
                                     [10 + column * self.size_block + self.margin * (column + 1),
                                      70 + row * self.size_block + self.margin * (row + 1), self.size_block,
                                      self.size_block])

    def render(self):
        self.draw_food()
        pass


class Snake():
    direction_dict = {0: "left", 1: "right", 2: "up", 3: "down"}
    directions_for_move = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
    snake_xy = []
    reward = 0
    scores = 0
    steps = 0
    dqn_vision_cnt = 2

    def __init__(self, field):
        r = randrange(150, 200)
        g = randrange(20, 100)
        b = randrange(100, 200)
        self.snake_color = (r, g, b)
        self.snake_head_color = (r - 20, g - 20, b - 20)
        self.generate_snake(field)
        field.add_snake(self)
        self.draw_snake(field)

    def generate_snake(self, field):
        reward = 0
        scores = 0
        steps = 0
        while True:
            self.snake_xy = []
            temp_xy = []
            x, y = (randrange(1, field.count_blocks_x - 1), randrange(2, field.count_blocks_y - 1))
            for l in range(field.snake_length):
                cell=self.check_cell_in_field(field, x, y)
                if cell !=0:
                    temp_xy = []
                    break
                temp_xy.append((x, y))
                y += 1
            if len(temp_xy)==field.snake_length:
                self.snake_xy = temp_xy.copy()
                break

    def check_cell_in_field(self, field, x, y):
        if (x, y) in field.food_list:
            return 1  # GET_FOOD
        for other_snakes in field.snakes_list:
            if (x, y) in other_snakes.snake_xy:
                # and id(self) != id(other_snakes):
                return 2  # Snake in  Snake
        if x < 0 or y < 0 or x >= field.count_blocks_x - 1 or y >= field.count_blocks_y - 1:
            return 3  # Snake out of border
        return 0  # all is ok

    def reset_snake(self, field):

        for x, y in self.snake_xy:
            field.cell_fill_color(x, y, field.get_color(x, y))
        self.generate_snake(field)
        self.draw_snake(field)

    def check_move(self, field, direction):
        dx, dy = self.directions_for_move.get(self.direction_dict.get(direction))
        return self.check_cell_in_field(field, self.snake_xy[0][0] + dx, self.snake_xy[0][1] + dy)

    def move(self, field, direction):
        dx, dy = self.directions_for_move.get(self.direction_dict.get(direction))
        move_result = self.check_move(field, direction)
        self.reward = self.get_reward(move_result)

        if move_result == 1:
            f.eat_food(self.snake_xy[0][0] + dx, self.snake_xy[0][1] + dy)
            self.snake_xy.append((self.snake_xy[-1][0] + dx, self.snake_xy[-1][1] + dy))
        if move_result in [0, 1]:
            field.cell_fill_color(self.snake_xy[-1][0], self.snake_xy[-1][1],
                                  field.get_color(self.snake_xy[-1][0], self.snake_xy[-1][1], ))
            self.snake_xy = [(l[0] + dx, l[1] + dy) if index == 0 else self.snake_xy[index - 1] for index, l in
                             enumerate(self.snake_xy)]
        if move_result == 2:
            self.reset_snake(field)
        if move_result == 3:
            self.reset_snake(field)
        self.draw_snake(field)
        sleep(1/field.fps)

    def draw_snake(self, field):
        for index, xy in enumerate(self.snake_xy):
            x = xy[0]
            y = xy[1]
            pygame.draw.rect(field.screen, self.snake_head_color if index == 0 else self.snake_color,
                             [10 + x * f.size_block + f.margin * (x + 1),
                              70 + y * f.size_block + f.margin * (y + 1), f.size_block,
                              f.size_block])

    def render(self, field):
        self.draw_snake(field)

    @staticmethod
    def get_reward(move_result):
        if move_result == 3:  # Out of border
            return -1
        elif move_result == 2:  # Snake in other snake
            return -1
        elif move_result == 1:
            return 1
        # elif:
        #     pass
        ##### CALCULATE FIELDFOOD DISTANCE
        else:
            return 0

    def dqn_get_field(self, field):
        x, y = self.snake_xy[0]
        return [[self.get_reward(self.check_cell_in_field(field, xx, yy)) for xx in
                 range(x - self.dqn_vision_cnt, x + self.dqn_vision_cnt + 1)] for yy in
                range(y - self.dqn_vision_cnt, y + self.dqn_vision_cnt + 1)]


def make_snake_thread(field):
    s = Snake(field)
    while True:
        pygame.event.get()
        s.move(f, randrange(0, 4))




if __name__ == '__main__':
    f = Field(count_blocks_x=150, count_blocks_y=100, size_block=10, snake_length=5)
    main_threat = threading.Thread(target=f.game)
    f.generate_food(1000)
    main_threat.start()
    i=1
    for i in range(100):
        s=threading.Thread(name=f"Thread_{i}",target=make_snake_thread,args=(f,))
        s.start()




