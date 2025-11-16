"""
Board module for the board game simulator.
Represents the game board and handles spatial logic.
"""
from typing import List, Tuple, Optional, Dict
from enum import Enum
import random


class TileType(Enum):
    """Enumeration of tile types."""
    EMPTY = "empty"
    WALL = "wall"
    START = "start"
    EXIT = "exit"
    TREASURE = "treasure"
    TRAP = "trap"
    MONSTER = "monster"
    REST = "rest"
    MERCHANT = "merchant"
    BOSS = "boss"


class Tile:
    """
    Represents a single tile on the board.
    
    Attributes:
        position (tuple): (x, y) coordinates
        tile_type (TileType): Type of tile
        occupant: Entity occupying the tile (player, monster, etc.)
        event: Event associated with the tile
        visited (bool): Whether the tile has been visited
        passable (bool): Whether entities can move through this tile
    """
    
    def __init__(self, position: Tuple[int, int], tile_type: TileType = TileType.EMPTY):
        """
        Initialize a Tile.
        
        Args:
            position (tuple): (x, y) coordinates
            tile_type (TileType): Type of tile
        """
        self.position = position
        self.tile_type = tile_type
        self.occupant = None
        self.event = None
        self.visited = False
        self.passable = tile_type != TileType.WALL
    
    def set_occupant(self, occupant):
        """
        Place an entity on this tile.
        
        Args:
            occupant: Entity to place on the tile
        """
        self.occupant = occupant
    
    def remove_occupant(self):
        """Remove the entity from this tile."""
        self.occupant = None
    
    def set_event(self, event):
        """
        Associate an event with this tile.
        
        Args:
            event: Event to associate
        """
        self.event = event
    
    def __str__(self) -> str:
        """String representation of the tile."""
        if self.occupant:
            return "P" if hasattr(self.occupant, 'player_type') else "M"
        
        tile_chars = {
            TileType.EMPTY: ".",
            TileType.WALL: "#",
            TileType.START: "S",
            TileType.EXIT: "E",
            TileType.TREASURE: "T",
            TileType.TRAP: "X",
            TileType.MONSTER: "M",
            TileType.REST: "R",
            TileType.MERCHANT: "$",
            TileType.BOSS: "B"
        }
        return tile_chars.get(self.tile_type, "?")


class Board:
    """
    Represents the game board.
    
    Attributes:
        width (int): Width of the board
        height (int): Height of the board
        tiles (list): 2D array of Tile objects
        start_position (tuple): Starting position coordinates
        exit_position (tuple): Exit position coordinates
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize a Board.
        
        Args:
            width (int): Width of the board
            height (int): Height of the board
        """
        self.width = width
        self.height = height
        self.tiles = [[Tile((x, y)) for x in range(width)] for y in range(height)]
        self.start_position = (0, 0)
        self.exit_position = (width - 1, height - 1)
        
        # Set start and exit tiles
        self.get_tile(self.start_position).tile_type = TileType.START
        self.get_tile(self.exit_position).tile_type = TileType.EXIT
    
    def get_tile(self, position: Tuple[int, int]) -> Optional[Tile]:
        """
        Get the tile at a specific position.
        
        Args:
            position (tuple): (x, y) coordinates
            
        Returns:
            Tile: Tile at the position, or None if invalid
        """
        x, y = position
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def set_tile_type(self, position: Tuple[int, int], tile_type: TileType):
        """
        Set the type of a tile at a position.
        
        Args:
            position (tuple): (x, y) coordinates
            tile_type (TileType): New tile type
        """
        tile = self.get_tile(position)
        if tile:
            tile.tile_type = tile_type
            tile.passable = tile_type != TileType.WALL
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position is valid on the board.
        
        Args:
            position (tuple): (x, y) coordinates
            
        Returns:
            bool: True if position is within board bounds
        """
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_passable(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position is passable.
        
        Args:
            position (tuple): (x, y) coordinates
            
        Returns:
            bool: True if position is passable
        """
        tile = self.get_tile(position)
        return tile is not None and tile.passable
    
    def move_entity(self, entity, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        Move an entity from one position to another.
        
        Args:
            entity: Entity to move
            from_pos (tuple): Starting position
            to_pos (tuple): Target position
            
        Returns:
            bool: True if move was successful
        """
        if not self.is_valid_position(to_pos) or not self.is_passable(to_pos):
            return False
        
        # Remove from old position
        from_tile = self.get_tile(from_pos)
        if from_tile and from_tile.occupant == entity:
            from_tile.remove_occupant()
        
        # Place at new position
        to_tile = self.get_tile(to_pos)
        if to_tile and to_tile.occupant is None:
            to_tile.set_occupant(entity)
            entity.move(to_pos)
            to_tile.visited = True
            return True
        
        return False
    
    def place_entity(self, entity, position: Tuple[int, int]) -> bool:
        """
        Place an entity at a position.
        
        Args:
            entity: Entity to place
            position (tuple): Target position
            
        Returns:
            bool: True if placement was successful
        """
        tile = self.get_tile(position)
        if tile and tile.passable and tile.occupant is None:
            tile.set_occupant(entity)
            entity.move(position)
            return True
        return False
    
    def remove_entity(self, entity, position: Tuple[int, int]):
        """
        Remove an entity from a position.
        
        Args:
            entity: Entity to remove
            position (tuple): Position to remove from
        """
        tile = self.get_tile(position)
        if tile and tile.occupant == entity:
            tile.remove_occupant()
    
    def get_adjacent_positions(self, position: Tuple[int, int], include_diagonal: bool = False) -> List[Tuple[int, int]]:
        """
        Get all adjacent positions to a given position.
        
        Args:
            position (tuple): Center position
            include_diagonal (bool): Whether to include diagonal positions
            
        Returns:
            List[tuple]: List of adjacent positions
        """
        x, y = position
        adjacent = []
        
        # Cardinal directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        # Add diagonal directions if requested
        if include_diagonal:
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
        
        for dx, dy in directions:
            new_pos = (x + dx, y + dy)
            if self.is_valid_position(new_pos):
                adjacent.append(new_pos)
        
        return adjacent
    
    def get_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int], manhattan: bool = True) -> float:
        """
        Calculate distance between two positions.
        
        Args:
            pos1 (tuple): First position
            pos2 (tuple): Second position
            manhattan (bool): Use Manhattan distance (True) or Euclidean (False)
            
        Returns:
            float: Distance between positions
        """
        x1, y1 = pos1
        x2, y2 = pos2
        
        if manhattan:
            return abs(x2 - x1) + abs(y2 - y1)
        else:
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path between two positions using A* algorithm.
        
        Args:
            start (tuple): Starting position
            end (tuple): End position
            
        Returns:
            List[tuple]: Path as list of positions, or None if no path exists
        """
        if not self.is_passable(start) or not self.is_passable(end):
            return None
        
        # Simple breadth-first search for now
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            if current == end:
                return path
            
            for neighbor in self.get_adjacent_positions(current):
                if neighbor not in visited and self.is_passable(neighbor):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def generate_random_layout(self, wall_probability: float = 0.2):
        """
        Generate a random board layout.
        
        Args:
            wall_probability (float): Probability of a tile being a wall
        """
        for y in range(self.height):
            for x in range(self.width):
                pos = (x, y)
                
                # Skip start and exit
                if pos == self.start_position or pos == self.exit_position:
                    continue
                
                # Randomly place walls
                if random.random() < wall_probability:
                    self.set_tile_type(pos, TileType.WALL)
        
        # Ensure there's a path from start to exit
        if not self.find_path(self.start_position, self.exit_position):
            # Clear a simple path
            x1, y1 = self.start_position
            x2, y2 = self.exit_position
            
            # Horizontal path
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.set_tile_type((x, y1), TileType.EMPTY)
            
            # Vertical path
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.set_tile_type((x2, y), TileType.EMPTY)
    
    def display(self) -> str:
        """
        Create a text representation of the board.
        
        Returns:
            str: String representation of the board
        """
        lines = []
        for row in self.tiles:
            lines.append(" ".join(str(tile) for tile in row))
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """String representation of the board."""
        return self.display()
    
    def __repr__(self) -> str:
        """Detailed representation of the board."""
        return f"Board(width={self.width}, height={self.height})"
