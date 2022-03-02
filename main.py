
from os import system, name as OSname
import keyboard
import cursor
import random
import copy
import time

# i refers to the row
# j refers to the column
# x refers to the position from the left (=j)
# y refers to the position from the top (=i)

class Tetris:

    def __init__(self, rows=20, columns=10):
        # Shapes and orientations
        S = [['.....',
            '......',
            '..00..',
            '.00...',
            '.....'],
            ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]
        
        Z = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
            ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]
        
        I = [['..0..',
            '..0..',
            '..0..',
            '..0..',
            '.....'],
            ['.....',
            '0000.',
            '.....',
            '.....',
            '.....']]
        
        O = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]
        
        J = [['.....',
            '.0...',
            '.000.',
            '.....',
            '.....'],
            ['.....',
            '..00.',
            '..0..',
            '..0..',
            '.....'],
            ['.....',
            '.....',
            '.000.',
            '...0.',
            '.....'],
            ['.....',
            '..0..',
            '..0..',
            '.00..',
            '.....']]
        
        L = [['.....',
            '...0.',
            '.000.',
            '.....',
            '.....'],
            ['.....',
            '..0..',
            '..0..',
            '..00.',
            '.....'],
            ['.....',
            '.....',
            '.000.',
            '.0...',
            '.....'],
            ['.....',
            '.00..',
            '..0..',
            '..0..',
            '.....']]
        
        T = [['.....',
            '..0..',
            '.000.',
            '.....',
            '.....'],
            ['.....',
            '..0..',
            '..00.',
            '..0..',
            '.....'],
            ['.....',
            '.....',
            '.000.',
            '..0..',
            '.....'],
            ['.....',
            '..0..',
            '.00..',
            '..0..',
            '.....']]
        
        BLACK_SQUARE = '\U00002B1B'
        BLUE_SQUARE = '\U0001F7E6'
        BROWN_SQUARE = '\U0001F7EB'
        ORANGE_SQUARE = '\U0001F7E7'
        YELLOW_SQUARE = '\U0001F7E8'
        RED_SQUARE = '\U0001F7E5'
        GREEN_SQUARE = '\U0001F7E9'
        PURPLE_SQUARE = '\U0001F7EA'
        STAR = '\U0001F929'

        self.height = rows
        self.width = columns
        self.shapes = [S, Z, I, O, J, L, T]
        self.shape_emojis = [GREEN_SQUARE, RED_SQUARE, BROWN_SQUARE, YELLOW_SQUARE, BLUE_SQUARE, ORANGE_SQUARE, PURPLE_SQUARE] # need 7 block emojis that aren't black/white
        self.empty_space = BLACK_SQUARE
        self.star = STAR
        self.score = 0
        self.grid = None
        # Dictionary for all the pieces' positions that have landed
        self.taken_cells = {}
        self.current_piece = self.get_piece()
        self.next_piece = self.get_piece()
        self.next_piece_image = self.create_next_piece_image()
        self.lost = False


    class Piece:
        def __init__(self, x, y, shape, emoji):
            self.x = x
            self.y = y
            self.shape = shape
            self.block = emoji
            self.rotation = 0

        def format(self):
            positions = [] # list of coordinates in tuples

            # format in a way that translates x to j and y to i
            orientation = self.shape[self.rotation % len(self.shape)]

            for i, line in enumerate(orientation):
                row = list(line)
                for j, column in enumerate(row):
                    if column == '0':
                        # formatted as row then column
                        positions.append((self.y + i, self.x + j))

            for i, point in enumerate(positions):
                # off sets shape strings to the top left
                positions[i] = (point[0] - 3, point[1] - 2)

            return positions

    # Retruns a piece object
    def get_piece(self):
        i = random.randrange(len(self.shapes))
        # Makes every piece immediately visible once in play
        if i > 3:
            return self.Piece(5, 1, self.shapes[i], self.shape_emojis[i])
        return self.Piece(5, 0, self.shapes[i], self.shape_emojis[i])

    # Gets a new piece after the last one has entirely fallen
    def change_piece(self):
        # add most recently fallen piece to 'taken_cells'
        piece_positions = self.current_piece.format()
        for position in piece_positions:
            self.taken_cells[position] = self.current_piece.block

        # if the next piece would spawn inside of the last, the game has been lost
        new_piece_positions = self.next_piece.format()
        for new_piece_position in new_piece_positions:
            for position in piece_positions:
                if new_piece_position == position:
                    self.lost = True

        self.current_piece = self.next_piece
        self.next_piece = self.get_piece()
        self.next_piece_image = self.create_next_piece_image()

        self.create_grid()
        self.clear_rows()

    # updates self.grid which holds the positions of available spaces
    def create_grid(self):
        self.grid = [[self.empty_space for _ in range(self.width)] for _ in range(self.height)]

        # adds fallen pieces to the grid
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in self.taken_cells:
                    colour = self.taken_cells[(i, j)]
                    self.grid[i][j] = colour

    # returns if space is available for the current piece
    def valid_space(self):
        valid_spaces = [[(i, j) for j in range(self.width) if self.grid[i][j] == self.empty_space] for i in range(self.height)]
        valid_spaces = [x for sub in valid_spaces for x in sub] # makes list 1 dimensional

        # format the piece here
        piece_positions = self.current_piece.format()

        for position in piece_positions:
            if position not in valid_spaces:
                # if the piece is above the game panel, it won't be counted
                if position[0] > -1:
                    return False
                # if piece is partly above screen, it can't go too far to the side or it can get caught on the edge
                else:
                    if position[1] not in list(range(self.width)):
                        return False
        return True

    # displays current game state in the terminal
    def draw_game_panel(self):
        # The original grid is used for valid_space() so we need a copy to allow the game to work and have the current piece drawn
        text_grid = copy.deepcopy(self.grid)

        piece_positions = self.current_piece.format()

        for k in range(len(piece_positions)):
            i, j = piece_positions[k]
            if i > -1:
                text_grid[i][j] = self.current_piece.block

        game_string = ''
        for row in text_grid:
            game_string += ''.join(row) + '\n'

        game_string += self.next_piece_image

        return game_string

    # Displays which piece will appear in the game next
    def create_next_piece_image(self):
        string = '\nNext piece: \n'

        positions = self.next_piece.format()

        i_positions = [x[0] for x in positions]
        j_positions = [x[1] for x in positions]

        min_i = min(i_positions)
        min_j = min(j_positions)

        # this code creates a canvas which scales to the piece, however isn't printed over correctly
        # max_i = max(i_positions)
        # max_j = max(j_positions)
        # canvas = [[self.empty_space for _ in range((max_j-min_j) + 1)] for _ in range((max_i-min_i) + 1)]

        # uses a canvas big enough for all pieces since the spaces needs to be written over in the current system
        canvas = [[self.empty_space for _ in range(3)] for _ in range(4)]

        for k, position in enumerate(positions):
            positions[k] = (position[0] -
             min_i, position[1] - min_j)

        for position in positions:
            # since the piece starts above the panel +min_i and -min_j sets the smallest value to 0 for each
            canvas[position[0]][position[1]] = self.next_piece.block

        for row in canvas:
            string += ''.join(row) + '\n'

        return string

    # Converts completed rows into 'STAR' emojis
    def flourish(self):
        # Makes rows to be cleared 'STAR's
        text_grid = copy.deepcopy(self.grid)

        for i, row in enumerate(text_grid):
            if self.empty_space not in row:
                for j in range(len(row)):
                    text_grid[i][j] = self.star

        game_string = ''
        for row in text_grid:
            game_string += ''.join(row) + '\n'

        print(game_string)
        time.sleep(0.5)
        self.clear_terminal()

    # Removes completed rows
    def clear_rows(self):
        cleared_row = None
        full_rows = 0

        for row in self.grid:
            if self.empty_space not in row:
                full_rows += 1

        if full_rows > 0:
            print("\033[H",end="")
            self.flourish()

        for _ in range(full_rows):
            for i in range(self.height-1, -1, -1):
                #iterates from bottom of the grid, upwards
                row = self.grid[i]
                if self.empty_space not in row:
                    cleared_row = i
                    for j in range(len(row)):
                        del self.taken_cells[(i, j)]
                    break

            # sorts taken_cells by the key, by the row
            for key in sorted(list(self.taken_cells))[::-1]:
                i, j = key
                if i < cleared_row:
                    new_key = (i+1, j)
                    self.taken_cells[new_key] = self.taken_cells.pop(key)

            self.create_grid()
    
            # increase score
            self.score += 10

    # Moves current piece to the left
    def move_left(self):
        self.current_piece.x -= 1
        if not self.valid_space():
            self.current_piece.x += 1

    # Moves current piece down
    def move_down(self):
        self.current_piece.y += 1
        if not self.valid_space():
            self.current_piece.y -= 1

    # Moves current piece to the right
    def move_right(self):
        self.current_piece.x += 1
        if not self.valid_space():
            self.current_piece.x -= 1

    # Moves current piece rotate
    def rotate(self):
        self.current_piece.rotation += 1
        if not self.valid_space():
            self.current_piece.rotation -= 1

    def clear_terminal(self):
        system('cls' if OSname == 'nt' else 'clear')

    def play(self):
        cursor.hide()
        self.clear_terminal()
        self.create_grid()
        print("""
Welcome to Textris!\n
Controls:
w or up - to rotate the piece,
a or left - to move the piece left,
s or down - to move the piece down,
d or right - to move the piece right,
and escape to exit\n
Enjoy! \n\n\n
        """)
        print("Press Enter to start.")
        keyboard.wait('enter')
        self.clear_terminal()
        print(self.draw_game_panel())
        run = True
        start_time = time.time()
        current_time = time.time()
        input_timer = time.time()
        level_time = time.time()
        input_gap = 0.09
        fall_time = 0.3

        while run:

            if self.lost:
                print("Game Over")
                print(f"Score: {self.score}")
                time.sleep(5)
                run = False
            else:
                print("\033[H",end="")
                print(self.draw_game_panel())

                current_time = time.time()

                # Staggers registered inputs so holding down a key doesn't trigger too many inputs
                if current_time - input_timer > input_gap:
                    input_timer = current_time
                    if keyboard.is_pressed("w") or keyboard.is_pressed("up"):
                        self.rotate()
                        # staggers rotation more than other inputs to keep other inputs smoother
                        input_timer += 0.07
                    if keyboard.is_pressed("a") or keyboard.is_pressed("left"):
                        self.move_left()
                    if keyboard.is_pressed("s") or keyboard.is_pressed("down"):
                        self.move_down()
                    if keyboard.is_pressed("d") or keyboard.is_pressed("right"):
                        self.move_right()
                    if keyboard.is_pressed("esc"):
                        self.clear_terminal()
                        exit()
               
                passed_time = current_time - start_time
                
                if passed_time > fall_time:
                    start_time = current_time

                    self.current_piece.y += 1
                    if not self.valid_space():
                        self.current_piece.y -= 1
                        self.change_piece()    

                if current_time - level_time > 10:
                    level_time = current_time
                    if fall_time > 0.14:
                        fall_time -= 0.005

        self.clear_terminal()         



if __name__ == '__main__':
    tetris = Tetris()
    tetris.play()