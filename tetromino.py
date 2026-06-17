from settings import *
import random
import pygame as pg

class GridBlock(pg.sprite.Sprite):
    def __init__(self, parent_tetromino, start_position):
        self._parent_tetromino = parent_tetromino
        
        # Encapsulation: Ginawa ko pong private ang variables para iwas accidental edit sa labas ng class, at may safe access lang sa pamamagitan ng methods
        self._grid_position = vec(start_position) + INIT_POS_OFFSET
        self._next_grid_position = vec(start_position) + NEXT_POS_OFFSET
        self._is_active = True

        super().__init__(parent_tetromino.tetris_engine.sprite_group)
        self.image = parent_tetromino.block_image
        self.rect = self.image.get_rect()

        self._sfx_image = self.image.copy()
        self._sfx_image.set_alpha(110)
        self._sfx_speed = random.uniform(0.2, 0.6)
        self._sfx_cycles = random.randrange(6, 8)
        self._cycle_counter = 0

    # Abstraction: Tinago ko po yung logic sa class na ito.
    def _check_sfx_completion(self):
        if self._parent_tetromino.tetris_engine.app.anim_trigger:
            self._cycle_counter += 1
            if self._cycle_counter > self._sfx_cycles:
                self._cycle_counter = 0
                return True
        return False

    def _execute_death_animation(self):
        self.image = self._sfx_image
        self._grid_position.y -= self._sfx_speed
        self.image = pg.transform.rotate(self.image, pg.time.get_ticks() * self._sfx_speed)

    def process_lifecycle(self):
        if not self._is_active:
            if not self._check_sfx_completion():
                self._execute_death_animation()
            else:
                self.kill()

    def calculate_rotation(self, pivot_position):
        translated_vector = self._grid_position - pivot_position
        rotated_vector = translated_vector.rotate(90)
        return rotated_vector + pivot_position

    def update_rectangle_position(self):
        is_current = self._parent_tetromino.is_current
        current_pos = [self._next_grid_position, self._grid_position][is_current]
        self.rect.topleft = current_pos * TILE_SIZE

    def update(self):
        self.process_lifecycle()
        self.update_rectangle_position()

    def check_boundary_collision(self, target_position):
        x, y = int(target_position.x), int(target_position.y)
        engine = self._parent_tetromino.tetris_engine
        if 0 <= x < FIELD_W and y < FIELD_H and (y < 0 or not engine.field_array[y][x]):
            return False
        return True
    
    # Encapsulation: Safe way para ma-access at ma-set yung position
    @property
    def grid_position(self):
        return self._grid_position
        
    @grid_position.setter
    def grid_position(self, new_pos):
        self._grid_position = new_pos
        
    def deactivate(self):
        self._is_active = False


# Inheritance: Ito po yung parent class na may hawak ng basic gravity at collision rules
class BaseTetromino:
    def __init__(self, tetris_engine, shape_key, is_current=True):
        self.tetris_engine = tetris_engine
        self.shape_id = shape_key
        self.block_image = random.choice(tetris_engine.app.images)
        self._blocks = [GridBlock(self, pos) for pos in TETROMINOES[shape_key]]
        self._is_landing = False
        self.is_current = is_current

    def rotate(self):
        pivot_position = self._blocks[0].grid_position
        new_positions = [block.calculate_rotation(pivot_position) for block in self._blocks]

        if not self._detect_collision(new_positions):
            for i, block in enumerate(self._blocks):
                block.grid_position = new_positions[i]

    def _detect_collision(self, block_positions):
        return any(map(GridBlock.check_boundary_collision, self._blocks, block_positions))

    def move(self, direction):
        movement_vector = MOVE_DIRECTIONS[direction]
        new_positions = [block.grid_position + movement_vector for block in self._blocks]
        
        if not self._detect_collision(new_positions):
            for block in self._blocks:
                block.grid_position += movement_vector
        elif direction == 'down':
            self._is_landing = True

    def update(self):
        self.move(direction='down')
        
    @property
    def blocks(self):
        return self._blocks
        
    @property
    def landing(self):
        return self._is_landing
    
    @landing.setter
    def landing(self, state):
        self._is_landing = state


# Polymorphism: Mga specific na shapes na magmamana po ng rules from BaseTetromino
class OShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'O', current)

    # Polymorphism: Parehas lang po itsura ng square kahit i-rotate, so 'pass' na lang para tipid sa CPU haha
    def rotate(self):
        pass

class IShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'I', current)

class TShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'T', current)

class LShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'L', current)

class JShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'J', current)

class SShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'S', current)

class ZShape(BaseTetromino):
    def __init__(self, engine, current=True):
        super().__init__(engine, 'Z', current)


def Tetromino(tetris_engine, current=True):
    available_shapes = [OShape, IShape, TShape, LShape, JShape, SShape, ZShape]
    selected_shape_class = random.choice(available_shapes)
    return selected_shape_class(tetris_engine, current)