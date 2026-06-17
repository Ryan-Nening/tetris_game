from settings import *
import math
from tetromino import Tetromino
import pygame.freetype as ft

class ScoreboardInterface:
    # Abstraction: UI drawing logic is separated from the main game engine
    def __init__(self, app):
        self.app = app
        self._font_engine = ft.Font(FONT_PATH)

    # Encapsulation: Internal method for calculating dynamic colors
    def _calculate_rainbow_color(self):
        time = pg.time.get_ticks() * 0.001
        n_sin = lambda t: (math.sin(t) * 0.5 + 0.5) * 255
        return n_sin(time * 0.5), n_sin(time * 0.2), n_sin(time * 0.9)

    def draw_hud(self):
        self._font_engine.render_to(self.app.screen, (WIN_W * 0.595, WIN_H * 0.02), text='TETRIS', fgcolor=self._calculate_rainbow_color(), size=TILE_SIZE * 1.65, bgcolor='black')
        self._font_engine.render_to(self.app.screen, (WIN_W * 0.65, WIN_H * 0.22), text='next', fgcolor='orange', size=TILE_SIZE * 1.4, bgcolor='black')
        self._font_engine.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.67), text='score', fgcolor='orange', size=TILE_SIZE * 1.4, bgcolor='black')
        
        # Encapsulation: Safely accessing the private score via a getter
        current_score = self.app.tetris_engine.current_score
        self._font_engine.render_to(self.app.screen, (WIN_W * 0.64, WIN_H * 0.8), text=f'{current_score}', fgcolor='white', size=TILE_SIZE * 1.8)


class TetrisEngine:
    # Encapsulation: Game state and matrix variables are protected
    def __init__(self, app):
        self.app = app
        self.sprite_group = pg.sprite.Group()
        self._field_array = self._initialize_empty_matrix()
        self.active_tetromino = Tetromino(self)
        self.next_tetromino = Tetromino(self, current=False)
        self._is_fast_dropping = False
        self._total_score = 0
        self._lines_cleared_this_frame = 0
        self._score_multiplier = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    # Abstraction: Generating the initial 2D array matrix
    def _initialize_empty_matrix(self):
        return [[0 for x in range(FIELD_W)] for y in range(FIELD_H)]

    # Abstraction: Converting a landed shape into grid matrix zeroes and ones
    def _lock_tetromino_to_matrix(self):
        for block in self.active_tetromino.blocks:
            x, y = int(block.grid_position.x), int(block.grid_position.y)
            self._field_array[y][x] = block

    # Abstraction: Core matrix shift and line clearing logic
    def _process_line_clears(self):
        row_target = FIELD_H - 1
        for y in range(FIELD_H - 1, -1, -1):
            for x in range(FIELD_W):
                self._field_array[row_target][x] = self._field_array[y][x]
                if self._field_array[y][x]:
                    self._field_array[row_target][x].grid_position = vec(x, y)

            if sum(map(bool, self._field_array[y])) < FIELD_W:
                row_target -= 1
            else:
                for x in range(FIELD_W):
                    self._field_array[row_target][x].deactivate()
                    self._field_array[row_target][x] = 0
                self._lines_cleared_this_frame += 1

    def _calculate_score(self):
        self._total_score += self._score_multiplier[self._lines_cleared_this_frame]
        self._lines_cleared_this_frame = 0

    def _check_game_over_state(self):
        if self.active_tetromino.blocks[0].grid_position.y == INIT_POS_OFFSET[1]:
            pg.time.wait(300)
            return True
        return False

    def _evaluate_landing(self):
        if self.active_tetromino.landing:
            if self._check_game_over_state():
                self.__init__(self.app)
            else:
                self._is_fast_dropping = False
                self._lock_tetromino_to_matrix()
                self.next_tetromino.is_current = True
                self.active_tetromino = self.next_tetromino
                self.next_tetromino = Tetromino(self, current=False)

    # Encapsulation: Getters for external read-only access
    @property
    def field_array(self):
        return self._field_array
        
    @property
    def current_score(self):
        return self._total_score

    # Abstraction: Handling different input commands cleanly
    def handle_input(self, pressed_key):
        if pressed_key == pg.K_LEFT:
            self.active_tetromino.move(direction='left')
        elif pressed_key == pg.K_RIGHT:
            self.active_tetromino.move(direction='right')
        elif pressed_key == pg.K_UP:
            self.active_tetromino.rotate()
        elif pressed_key == pg.K_DOWN:
            self._is_fast_dropping = True

    def draw_grid_lines(self):
        for x in range(FIELD_W):
            for y in range(FIELD_H):
                pg.draw.rect(self.app.screen, 'black', (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

    def update_engine(self):
        trigger = [self.app.anim_trigger, self.app.fast_anim_trigger][self._is_fast_dropping]
        if trigger:
            self._process_line_clears()
            self.active_tetromino.update()
            self._evaluate_landing()
            self._calculate_score()
        self.sprite_group.update()

    def draw_elements(self):
        self.draw_grid_lines()
        self.sprite_group.draw(self.app.screen)