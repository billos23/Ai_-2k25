"""
Sokoban puzzle state representation and operations.
"""

from typing import List, Tuple, Set, FrozenSet
from a_star_solver.puzzles.base_puzzle import PuzzleState


class SokobanState(PuzzleState):
    """
    Represents a state in a Sokoban puzzle.
    
    Sokoban is a puzzle where the player pushes boxes to goal locations.
    The player can only push boxes (not pull), and only one box at a time.
    """
    
    def __init__(self, walls: Set[Tuple[int, int]], 
                 boxes: Set[Tuple[int, int]], 
                 goals: Set[Tuple[int, int]], 
                 player: Tuple[int, int],
                 width: int, height: int):
        """
        Initialize a Sokoban puzzle state.
        
        Args:
            walls: Set of (row, col) positions that are walls
            boxes: Set of (row, col) positions that have boxes
            goals: Set of (row, col) positions that are goal locations
            player: (row, col) position of the player
            width: Width of the puzzle
            height: Height of the puzzle
        """
        self.walls = frozenset(walls)
        self.boxes = frozenset(boxes)
        self.goals = frozenset(goals)
        self.player = player
        self.width = width
        self.height = height
        
        # Cache for state hash
        self._hash = None
    
    @classmethod
    def from_string(cls, level_string: str) -> 'SokobanState':
        """
        Create a Sokoban state from a string representation.
        
        Args:
            level_string: Multi-line string representing the level
            
        Returns:
            SokobanState instance
        """
        lines = level_string.strip().split('\n')
        
        walls = set()
        boxes = set()
        goals = set()
        player = None
        
        height = len(lines)
        width = max(len(line) for line in lines) if lines else 0
        
        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                pos = (row, col)
                
                if char == '#':
                    walls.add(pos)
                elif char == '@':
                    player = pos
                elif char == '+':  # Player on goal
                    player = pos
                    goals.add(pos)
                elif char == '$':
                    boxes.add(pos)
                elif char == '*':  # Box on goal
                    boxes.add(pos)
                    goals.add(pos)
                elif char == '.':
                    goals.add(pos)
        
        if player is None:
            raise ValueError("No player position found in level")
        
        if not goals:
            raise ValueError("No goal positions found in level")
        
        if len(boxes) != len(goals):
            raise ValueError(f"Number of boxes ({len(boxes)}) must equal number of goals ({len(goals)})")
        
        return cls(walls, boxes, goals, player, width, height)
    
    def is_goal_state(self) -> bool:
        """
        Check if this is a goal state (all boxes on goals).
        
        Returns:
            True if all boxes are on goal positions
        """
        return self.boxes == self.goals
    
    def get_state_hash(self) -> str:
        """
        Get a unique hash for this state.
        
        Returns:
            String hash representing this state
        """
        if self._hash is None:
            # Sort boxes for consistent hashing
            boxes_tuple = tuple(sorted(self.boxes))
            self._hash = f"{self.player}|{boxes_tuple}"
        return self._hash
    
    def get_possible_moves(self) -> List[str]:
        """
        Get all possible moves from this state.
        
        Returns:
            List of move directions: 'U', 'D', 'L', 'R'
        """
        moves = []
        directions = [
            ('U', (-1, 0)),  # Up
            ('D', (1, 0)),   # Down
            ('L', (0, -1)),  # Left
            ('R', (0, 1))    # Right
        ]
        
        player_row, player_col = self.player
        
        for move_name, (dr, dc) in directions:
            new_player_pos = (player_row + dr, player_col + dc)
            
            # Check if new position is a wall
            if new_player_pos in self.walls:
                continue
            
            # Check if new position has a box
            if new_player_pos in self.boxes:
                # Check if we can push the box
                box_new_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
                
                # Can't push if there's a wall or another box
                if box_new_pos in self.walls or box_new_pos in self.boxes:
                    continue
                
                # Check for deadlock: box pushed into corner
                if self._is_deadlock_position(box_new_pos):
                    continue
            
            moves.append(move_name)
        
        return moves
    
    def _is_deadlock_position(self, pos: Tuple[int, int]) -> bool:
        """
        Check if a box position would create a deadlock.
        
        A simple deadlock check: box in corner not on goal.
        This is a conservative check - it may miss some deadlocks but won't
        incorrectly mark valid positions as deadlocks.
        
        Args:
            pos: Position to check
            
        Returns:
            True if position creates a deadlock
        """
        # If position is a goal, it's NEVER a deadlock
        if pos in self.goals:
            return False
        
        row, col = pos
        
        # Check if box is in a corner (two adjacent walls)
        up_wall = (row - 1, col) in self.walls
        down_wall = (row + 1, col) in self.walls
        left_wall = (row, col - 1) in self.walls
        right_wall = (row, col + 1) in self.walls
        
        # Corner deadlocks (only if NOT on a goal)
        if (up_wall and left_wall) or (up_wall and right_wall) or \
           (down_wall and left_wall) or (down_wall and right_wall):
            return True
        
        if self._is_wall_deadlock(pos, up_wall, down_wall, left_wall, right_wall):
            return True
        
        return False
    
    def _is_wall_deadlock(self, pos: Tuple[int, int], up_wall: bool, down_wall: bool, 
                          left_wall: bool, right_wall: bool) -> bool:
        row, col = pos
        
        if up_wall or down_wall:
            has_goal_on_row = any(g[0] == row and g not in self.boxes for g in self.goals)
            if not has_goal_on_row:
                return True
        
        if left_wall or right_wall:
            has_goal_on_col = any(g[1] == col and g not in self.boxes for g in self.goals)
            if not has_goal_on_col:
                return True
        
        return False
    
    def _is_freeze_deadlock(self, new_boxes: Set[Tuple[int, int]]) -> bool:
        for box in new_boxes:
            if box in self.goals:
                continue
            
            row, col = box
            
            vertical_blocked = (
                ((row - 1, col) in self.walls or (row - 1, col) in new_boxes) and
                ((row + 1, col) in self.walls or (row + 1, col) in new_boxes)
            )
            
            horizontal_blocked = (
                ((row, col - 1) in self.walls or (row, col - 1) in new_boxes) and
                ((row, col + 1) in self.walls or (row, col + 1) in new_boxes)
            )
            
            if vertical_blocked and horizontal_blocked:
                return True
        
        return False
    
    def apply_move(self, move: str) -> 'SokobanState':
        """
        Apply a move and return the new state.
        
        Args:
            move: Move direction ('U', 'D', 'L', 'R')
            
        Returns:
            New SokobanState after applying the move
        """
        direction_map = {
            'U': (-1, 0),
            'D': (1, 0),
            'L': (0, -1),
            'R': (0, 1)
        }
        
        if move not in direction_map:
            raise ValueError(f"Invalid move: {move}")
        
        dr, dc = direction_map[move]
        player_row, player_col = self.player
        new_player_pos = (player_row + dr, player_col + dc)
        
        # Check if move is valid
        if new_player_pos in self.walls:
            raise ValueError(f"Cannot move into wall")
        
        new_boxes = set(self.boxes)
        
        # Check if pushing a box
        if new_player_pos in self.boxes:
            box_new_pos = (new_player_pos[0] + dr, new_player_pos[1] + dc)
            
            if box_new_pos in self.walls or box_new_pos in self.boxes:
                raise ValueError(f"Cannot push box")
            
            # Move the box
            new_boxes.remove(new_player_pos)
            new_boxes.add(box_new_pos)
            
            if self._is_freeze_deadlock(new_boxes):
                raise ValueError(f"Freeze deadlock detected")
        
        return SokobanState(
            self.walls,
            new_boxes,
            self.goals,
            new_player_pos,
            self.width,
            self.height
        )
    
    def display(self) -> str:
        """
        Get a string representation of the puzzle state.
        
        Returns:
            Multi-line string showing the current state
        """
        lines = []
        
        for row in range(self.height):
            line = []
            for col in range(self.width):
                pos = (row, col)
                
                if pos in self.walls:
                    line.append('#')
                elif pos == self.player:
                    if pos in self.goals:
                        line.append('+')  # Player on goal
                    else:
                        line.append('@')
                elif pos in self.boxes:
                    if pos in self.goals:
                        line.append('*')  # Box on goal
                    else:
                        line.append('$')
                elif pos in self.goals:
                    line.append('.')
                else:
                    line.append(' ')
            
            lines.append(''.join(line))
        
        return '\n'.join(lines)
    
    
    
  


