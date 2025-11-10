"""
Loader for Sokoban level files.
"""

from typing import List, Dict
from a_star_solver.puzzles.sokoban_puzzle import SokobanState


class SokobanLevel:
    """Represents a Sokoban level with metadata."""
    
    def __init__(self, number: int, level_string: str, title: str = "", 
                 author: str = "", moves: int = 0):
        """
        Initialize a Sokoban level.
        
        Args:
            number: Level number
            level_string: String representation of the level
            title: Level title
            author: Level author
            moves: Optimal number of moves
        """
        self.number = number
        self.level_string = level_string
        self.title = title
        self.author = author
        self.moves = moves
        self.state = SokobanState.from_string(level_string)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Level {self.number}: {self.title} by {self.author} ({self.moves} moves)"


class SokobanLevelLoader:
    """Loads Sokoban levels from .sok files."""
    
    @staticmethod
    def load_from_file(filename: str) -> List[SokobanLevel]:
        """
        Load Sokoban levels from a .sok file.
        
        Args:
            filename: Path to the .sok file
            
        Returns:
            List of SokobanLevel objects
        """
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return SokobanLevelLoader.parse_sok_content(content)
    
    @staticmethod
    def parse_sok_content(content: str) -> List[SokobanLevel]:
        """
        Parse Sokoban levels from .sok file content.
        
        Args:
            content: Content of the .sok file
            
        Returns:
            List of SokobanLevel objects
        """
        levels = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith(';') or line.startswith('::') or \
               line.startswith('Copyright') or line.startswith('Email') or \
               line.startswith('Homepage') or line.startswith('This is'):
                i += 1
                continue
            
            # Check if this is a level number
            if line.isdigit():
                level_number = int(line)
                i += 1
                
                # Read the level grid
                level_lines = []
                while i < len(lines):
                    level_line = lines[i]
                    
                    # Stop if we hit metadata or next level
                    if level_line.strip().startswith('Title:') or \
                       level_line.strip().startswith('Author:') or \
                       level_line.strip().startswith('Moves:') or \
                       (level_line.strip().isdigit() and level_line.strip() != ''):
                        break
                    
                    # Check if line contains level characters
                    if any(c in level_line for c in '#@$.*+ '):
                        level_lines.append(level_line.rstrip())
                    
                    i += 1
                
                # Read metadata
                title = ""
                author = ""
                moves = 0
                
                while i < len(lines):
                    meta_line = lines[i].strip()
                    
                    if meta_line.startswith('Title:'):
                        title = meta_line.replace('Title:', '').strip()
                    elif meta_line.startswith('Author:'):
                        author = meta_line.replace('Author:', '').strip()
                    elif meta_line.startswith('Moves:'):
                        try:
                            moves = int(meta_line.replace('Moves:', '').strip())
                        except ValueError:
                            moves = 0
                    elif meta_line.isdigit() or not meta_line:
                        # Next level or empty line
                        break
                    
                    i += 1
                
                # Create level if we have valid grid
                if level_lines:
                    level_string = '\n'.join(level_lines)
                    try:
                        level = SokobanLevel(
                            level_number,
                            level_string,
                            title,
                            author,
                            moves
                        )
                        levels.append(level)
                    except Exception as e:
                        print(f"Warning: Could not parse level {level_number}: {e}")
            else:
                i += 1
        
        return levels
    
    @staticmethod
    def get_level_by_number(levels: List[SokobanLevel], number: int) -> SokobanLevel:
        """
        Get a specific level by number.
        
        Args:
            levels: List of levels
            number: Level number to find
            
        Returns:
            SokobanLevel object
            
        Raises:
            ValueError: If level not found
        """
        for level in levels:
            if level.number == number:
                return level
        
        raise ValueError(f"Level {number} not found")