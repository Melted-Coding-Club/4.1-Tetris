import pygame
import sys

fps = 60


class Piece:
    def __init__(self, game, p_type="z", colour="red"):
        self.game = game
        self.origin = [0, 0]
        self.colour = colour
        self.type = p_type

        # Each list of offsets should have the same amount of tuples
        self.offsets = []
        self.offset_num = 0
        if self.type == "z":
            self.offsets = [
                [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)],
                [(1, 0), (1, 1), (0, 1), (0, 2), (7, 1)],
            ]

    def render(self):
        for offset in self.offsets[self.offset_num]:
            pygame.draw.rect(self.game.screen, self.colour, pygame.Rect(
                self.origin[0] * self.game.grid_size + offset[0] * self.game.grid_size + self.game.game_location[0],
                self.origin[1] * self.game.grid_size + offset[1] * self.game.grid_size + self.game.game_location[1],
                self.game.grid_size,
                self.game.grid_size
            ))

    def update_rects(self):
        blocks = []
        # returns True if a collision is made
        for offset in self.offsets[self.offset_num]:
            blocks.append({
                "location": (offset[0] + self.origin[0], offset[1] + self.origin[1]),
                "colour": self.colour
            })

        board_locations = []
        for block in self.game.board:
            board_locations.append(block["location"])

        for block in blocks:
            if block["location"][1] >= self.game.game_area[1]:
                self.game.board.extend(blocks)
                return True

            if block["location"] in board_locations:
                self.game.board.extend(blocks)
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
        if self.update_rects():
            self.origin = origin
            self.update_rects()
            # return true for collision
            return True


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        self.grid_size = 20
        self.game_location = (220, 40)
        self.game_area = (10, 20)

        self.pieces = [
            Piece(self),
        ]

        self.board = []

        self.USEREVENT = 1
        pygame.time.set_timer(self.USEREVENT, 250)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        direction = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                direction = "right"
            if event.key == pygame.K_a:
                direction = "left"
            if event.key == pygame.K_w:
                self.pieces[0].offset_num = (self.pieces[0].offset_num + 1) % len(self.pieces[0].offsets)
        if event.type == self.USEREVENT:
            direction = "down"
        # if a collision is made while moving piece
        if self.pieces[0].move(direction):
            # spawn a new piece
            self.pieces.insert(0, Piece(self))

    def render(self):
        self.screen.fill("white")

        # draw game area in game location
        pygame.draw.rect(self.screen, "black", (
            self.game_location[0],
            self.game_location[1],
            self.game_area[0] * self.grid_size,
            self.game_area[1] * self.grid_size
        ))
        for piece in self.pieces:
            piece.render()

        pygame.display.update()

    def start(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.render()

            self.clock.tick(fps)


Game().start()
