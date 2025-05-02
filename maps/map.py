import pygame
from pytmx import TiledTileLayer
from pytmx.util_pygame import load_pygame

TILE_SIZE = 32


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)


class Map:
    def __init__(self, tmx_file):
        self.display_surface = pygame.display.get_surface()
        self.tmx_data = load_pygame(tmx_file)

        self.tile_layers = {
            "grass": pygame.sprite.Group(),
            "road": pygame.sprite.Group(),
            "shop": pygame.sprite.Group(),
            "houses": pygame.sprite.Group(),
            "library": pygame.sprite.Group(),
            "fastfood": pygame.sprite.Group(),
            "hospital": pygame.sprite.Group(),
        }

        self.load_layers()

    def load_layers(self):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                for x, y, image in layer.tiles():
                    tile = Tile(x, y, image)
                    if layer.name in self.tile_layers:
                        self.tile_layers[layer.name].add(tile)

    def draw_map(self):
        for group in self.tile_layers.values():
            for tile in group:
                self.display_surface.blit(tile.image, tile.rect.topleft)

    def is_allowed(self, pos):
        x, y = pos
        walkable_layers = ["road", "fastfood", "shop", "library", "hospital", "houses"]
        px, py = x * TILE_SIZE, y * TILE_SIZE

        for layer_name in walkable_layers:
            for tile in self.tile_layers[layer_name]:
                if tile.rect.collidepoint(px, py):
                    return True
        return False

    def get_current_layers(self, x, y):
        current_layers = []
        px, py = x * TILE_SIZE, y * TILE_SIZE

        for layer_name, group in self.tile_layers.items():
            for tile in group:
                if tile.rect.collidepoint(px, py):
                    current_layers.append(layer_name)

        return current_layers

    def get_layer_positions_normalized(self, layer_name):
        positions = []
        for tile in self.tile_layers[layer_name]:
            positions.append((tile.rect.x // TILE_SIZE, tile.rect.y // TILE_SIZE))
        return positions
