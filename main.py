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

        self.rects = []
        for i in range(len(self.offsets[self.offset_num])):
            x = self.game.grid_size * self.offsets[self.offset_num][i][0] + self.origin[0] + game.game_location[0]
            y = self.game.grid_size * self.offsets[self.offset_num][i][1] + self.origin[1] + game.game_location[1]
            rect = pygame.Rect(x, y, self.game.grid_size, self.game.grid_size)
            self.rects.append(rect)

    def render(self):
        for rect in self.rects:
            pygame.draw.rect(self.game.screen, self.colour, rect)

    def update_rects(self):
        # returns True if a collision is made
        for i, rect in enumerate(self.rects):
            rect.x = self.game.grid_size * self.offsets[self.offset_num][i][0] + self.origin[0] + self.game.game_location[0]
            rect.y = self.game.grid_size * self.offsets[self.offset_num][i][1] + self.origin[1] + self.game.game_location[1]

            if rect.bottom > self.game.game_location[1] + self.game.game_area[1]:
                return True

            for other_piece in self.game.pieces:
                if other_piece == self:
                    continue
                for other_rect in other_piece.rects:
                    if rect.colliderect(other_rect):
                        return True

    def move(self, direction):
        origin = self.origin.copy()
        if direction == "down":
            self.origin[1] += self.game.grid_size
        elif direction == "left":
            self.origin[0] -= self.game.grid_size
        elif direction == "right":
            self.origin[0] += self.game.grid_size
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
        self.game_area = (10 * self.grid_size, 20 * self.grid_size)

        self.pieces = [
            Piece(self),
        ]

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
        pygame.draw.rect(self.screen, "black", (self.game_location[0], self.game_location[1], self.game_area[0], self.game_area[1]))
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
