import copy
import random
import pygame
import sys


class Piece:
    def __init__(self, game, p_type="z"):
        self.game = game
        x = random.randint(1, self.game.game_area[0] - 4)
        self.origin = [x, 0]
        self.image = self.game.images[p_type.upper()]
        self.type = p_type
        self.swapped = False

        # Each list of offsets should have the same amount of tuples
        self.offsets = []
        self.offset_num = 0
        if self.type.upper() == "I":
            self.offsets = [
                [(0, 1), (1, 1), (2, 1), (3, 1)],
                [(2, 0), (2, 1), (2, 2), (2, 3)],
                [(0, 2), (1, 2), (2, 2), (3, 2)],
                [(1, 0), (1, 1), (1, 2), (1, 3)]
            ]
        elif self.type.upper() == "O":
            self.offsets = [
                [(1, 1), (1, 2), (2, 1), (2, 2)],
            ]
        elif self.type.upper() == "T":
            self.offsets = [
                [(1, 0), (0, 1), (1, 1), (2, 1)],
                [(1, 0), (1, 1), (2, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (1, 2)],
                [(1, 0), (0, 1), (1, 1), (1, 2)]
            ]
        elif self.type.upper() == "J":
            self.offsets = [
                [(1, 0), (1, 1), (1, 2), (0, 2)],
                [(0, 1), (1, 1), (2, 1), (2, 0)],
                [(1, 0), (1, 1), (1, 2), (2, 2)],
                [(0, 1), (1, 1), (2, 1), (0, 2)]
            ]
        elif self.type.upper() == "L":
            self.offsets = [
                [(1, 0), (1, 1), (1, 2), (2, 2)],
                [(0, 1), (1, 1), (2, 1), (0, 0)],
                [(0, 0), (1, 0), (1, 1), (1, 2)],
                [(0, 1), (1, 1), (2, 1), (2, 2)]
            ]
        elif self.type.upper() == "S":
            self.offsets = [
                [(1, 0), (2, 0), (0, 1), (1, 1)],  # Original position
                [(0, 0), (0, 1), (1, 1), (1, 2)],  # Rotated 90 degrees clockwise
                [(1, 1), (2, 1), (0, 0), (1, 0)],  # Rotated 180 degrees clockwise
                [(1, 0), (1, 1), (2, 1), (2, 2)]  # Rotated 270 degrees clockwise
            ]
        elif self.type.upper() == "Z":
            self.offsets = [
                [(0, 0), (1, 0), (1, 1), (2, 1)],  # Original position
                [(1, 0), (1, 1), (0, 1), (0, 2)],  # Rotated 90 degrees clockwise
                [(2, 1), (1, 1), (1, 0), (0, 0)],  # Rotated 180 degrees clockwise
                [(0, 2), (0, 1), (1, 1), (1, 0)]  # Rotated 270 degrees clockwise
            ]

    def render(self, origin_overwrite=None):
        if origin_overwrite:
            origin = origin_overwrite
        else:
            origin = (self.origin[0] + self.game.game_location[0], self.origin[1] + self.game.game_location[1])
        for offset in self.offsets[self.offset_num]:
            image = self.game.images[self.type.upper()]
            image = pygame.transform.scale(image, (self.game.grid_size, self.game.grid_size))
            location = (origin[0] * self.game.grid_size + offset[0] * self.game.grid_size,
                        origin[1] * self.game.grid_size + offset[1] * self.game.grid_size)
            self.game.screen.blit(image, tuple(location))

    def update_board(self):
        blocks = []
        for offset in self.offsets[self.offset_num]:
            block = {
                "location": (offset[0] + self.origin[0], offset[1] + self.origin[1]),
                "image": self.image
            }
            blocks.append(block)
            if block["location"][1] <= 0:
                self.game.app_state = "game_over"
                self.game.update_menu()

        self.game.board.extend(blocks)

    def update_blocks(self, direction=None):
        # returns True if a collision is made

        block_locations = []
        for offset in self.offsets[self.offset_num]:
            block_locations.append((offset[0] + self.origin[0], offset[1] + self.origin[1]))

        board_locations = []
        for block in self.game.board:
            board_locations.append(block["location"])

        for block_location in block_locations:
            if block_location[1] >= self.game.game_area[1]:
                return True
            if block_location[0] >= self.game.game_area[0] or block_location[0] < 0:
                return True
            if block_location in board_locations:
                return True

    def move(self, direction):
        origin = self.origin.copy()
        if direction == "down":
            self.origin[1] += 1
        elif direction == "left":
            self.origin[0] -= 1
        elif direction == "right":
            self.origin[0] += 1
        # if collision is made, rollback changes and update the rects back to rollback state
        if self.update_blocks(direction):
            self.origin = origin
            self.update_blocks()
            if direction == "down":
                self.update_board()
                self.new_piece()
                # return True for collision
                return True

    def new_piece(self):
        self.game.pieces.remove(self.game.pieces[0])
        b_type = random.choice(self.game.types).upper()
        self.game.pieces.append(Piece(self.game, b_type))


class Game:
    def __init__(self):
        pygame.init()
        default_grid_size = 30
        self.screen_grid = (22, 22)
        self.screen = pygame.display.set_mode((self.screen_grid[0] * default_grid_size, self.screen_grid[1] * default_grid_size), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        self.app_state = "menu"
        self.menu_buttons = []
        self.update_menu()

        self.fps = 60
        self.types = ["I", "o", "t", "j", "l", "s", "z"]
        self.images = {
            'I': pygame.image.load("data/images/blocks/cyan.png"),
            'O': pygame.image.load("data/images/blocks/yellow.png"),
            'T': pygame.image.load("data/images/blocks/purple.png"),
            'J': pygame.image.load("data/images/blocks/blue.png"),
            'L': pygame.image.load("data/images/blocks/orange.png"),
            'S': pygame.image.load("data/images/blocks/green.png"),
            'Z': pygame.image.load("data/images/blocks/red.png")
        }

        self.grid_size = self.screen.get_size()[0] / self.screen_grid[0]
        self.game_location = (6, 1)
        self.game_area = (10, 20)

        self.pieces = [
            Piece(self, "l"),
            Piece(self, "s"),
            Piece(self, "j"),
            Piece(self, "z"),
        ]
        self.stored_pieces = []

        # Reset variables
        self.board = []
        self.score = 0
        self.move_down_delay = 30

        self.USEREVENT = 1
        pygame.time.set_timer(self.USEREVENT, 250)

    def update_menu(self):
        if self.app_state == "menu":
            self.menu_buttons = [
                {"image": pygame.image.load("data/images/buttons/play.png"), "location": (200, 200), "size": (100, 50), "action": "game"},
                {"image": pygame.image.load("data/images/buttons/quit.png"), "location": (300, 200), "size": (100, 50), "action": "quit"}
            ]
        elif self.app_state == "game_over":
            self.menu_buttons = [
                {"image": pygame.image.load("data/images/buttons/play_again.png"), "location": (200, 200), "size": (100, 50), "action": "game"},
                {"image": pygame.image.load("data/images/buttons/quit.png"), "location": (300, 200), "size": (100, 50), "action": "quit"}
            ]
        elif self.app_state == "paused":
            self.menu_buttons = [
                {"image": pygame.image.load("data/images/buttons/play.png"), "location": (200, 200), "size": (100, 50), "action": "game"},
                {"image": pygame.image.load("data/images/buttons/quit.png"), "location": (300, 200), "size": (100, 50), "action": "quit"},
                {"image": pygame.image.load("data/images/buttons/menu.png"), "location": (300, 250), "size": (100, 50), "action": "menu"}
            ]
        for button in self.menu_buttons:
            if button["size"]:
                button["image"] = pygame.transform.scale(button["image"], (button["size"][0], button["size"][1]))
            button["rect"] = button["image"].get_rect(topleft=button["location"])

    def handle_game_input_frame(self, keys_pressed=None):
        if keys_pressed:
            if keys_pressed[pygame.K_s]:
                if self.move_down_delay > 0:
                    self.move_down_delay -= 1
                else:
                    self.move_down_delay = 5
                    self.pieces[0].move("down")
            else:
                self.move_down_delay = 0

    def handle_game_input_event(self, event=None, keys_pressed=None):
        direction = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                while not self.pieces[0].move("down"):
                    pass
            if event.key == pygame.K_ESCAPE:
                self.app_state = "paused"
                self.update_menu()
            if event.key == pygame.K_c:
                if len(self.stored_pieces) < 1:
                    self.stored_pieces.append(self.pieces[0])
                    self.pieces[0].new_piece()
            if event.key == pygame.K_f:
                if not self.pieces[0].swapped:
                    self.stored_pieces.append(self.pieces[0])
                    self.pieces.remove(self.pieces[0])
                    self.pieces.insert(0, self.stored_pieces[0])
                    self.stored_pieces.remove(self.stored_pieces[0])
                    self.pieces[0].origin[1] = 0
                    self.pieces[0].swapped = True
            if event.key == pygame.K_d:
                self.pieces[0].move("right")
            if event.key == pygame.K_a:
                self.pieces[0].move("left")
            if event.key == pygame.K_w:
                self.pieces[0].offset_num = (self.pieces[0].offset_num + 1) % len(self.pieces[0].offsets)
        if keys_pressed:
            if event.type == self.USEREVENT and not keys_pressed[pygame.K_s]:
                self.pieces[0].move("down")

        # Check for full row
        rows = []
        for i in range(self.game_area[1]):
            rows.append(0)

        for block in self.board:
            for i in range(len(rows)):
                if block["location"][1] == i:
                    rows[i] += 1
                    if rows[i] >= self.game_area[0]:
                        self.board = [block for block in self.board if block["location"][1] != i]
                        for block in self.board:
                            if block["location"][1] < i:
                                block["location"] = (block["location"][0], block["location"][1] + 1)

    def render_game(self):
        # draw game area in game location
        pygame.draw.rect(self.screen, "black", (
            self.game_location[0] * self.grid_size,
            self.game_location[1] * self.grid_size,
            self.game_area[0] * self.grid_size,
            self.game_area[1] * self.grid_size
        ))
        for i, piece in enumerate(self.pieces):
            if i == 0:
                piece.render()
            if i >= 1:
                piece.render((2, (i-1)*5 + 2))

        for i, piece in enumerate(self.stored_pieces):
            piece.render((17, i*5 + 2))

        for block in self.board:
            image = block["image"]
            image = pygame.transform.scale(image, (self.grid_size, self.grid_size))
            location = (block["location"][0] * self.grid_size + self.game_location[0] * self.grid_size, block["location"][1] * self.grid_size + self.game_location[1] * self.grid_size)
            self.screen.blit(image, tuple(location))

    def handle_general_input_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode((event.w, event.w), pygame.RESIZABLE)
            self.grid_size = round(self.screen.get_size()[0] / self.screen_grid[0])

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.app_state == "paused":
                if event.key == pygame.K_ESCAPE:
                    self.app_state = "game"
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.menu_buttons:
                if button["rect"].collidepoint(event.pos):
                    if button["action"] == "quit":
                        pygame.quit()
                        sys.exit()
                    if button["action"] == "game":
                        self.board = []
                        self.pieces = [
                            Piece(self, "l"),
                            Piece(self, "s"),
                            Piece(self, "j"),
                            Piece(self, "z"),
                        ]
                        self.score = 0
                    self.app_state = button["action"]
                    self.update_menu()

    def render_menu(self):
        for button in self.menu_buttons:
            image = pygame.transform.scale(button["image"], (button["rect"].width, button["rect"].height))
            self.screen.blit(image, button["rect"].topleft)

    def start(self):
        while True:
            if self.app_state == "menu":
                for event in pygame.event.get():
                    self.handle_general_input_event(event=event)
                    self.handle_menu_input(event=event)
                # Render
                self.render_menu()

            elif self.app_state == "game_over" or self.app_state == "paused":
                for event in pygame.event.get():
                    self.handle_general_input_event(event=event)
                    self.handle_menu_input(event=event)
                # Render
                self.render_game()
                self.render_menu()

            elif self.app_state == "game":
                for event in pygame.event.get():
                    self.handle_general_input_event(event=event)
                    self.handle_game_input_event(event=event, keys_pressed=pygame.key.get_pressed())
                self.handle_game_input_frame(keys_pressed=pygame.key.get_pressed())
                # Render
                self.render_game()

            pygame.display.update()
            self.screen.fill("white")
            self.clock.tick(self.fps)


Game().start()
