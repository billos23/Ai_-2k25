"""
Abstract base classes for puzzle state representation.
"""

from abc import ABC, abstractmethod
from typing import List, Any


class PuzzleState(ABC):
    """
    Abstract base class for representing puzzle states.
    
    This class defines the interface that all puzzle state implementations
    must follow to work with the A* solver.
    """
    
    @abstractmethod
    def get_possible_moves(self) -> List[Any]:
        """
        Get all possible moves from the current state.
        
        Returns:
            List of possible moves that can be applied to this state
        """
        pass
    
    @abstractmethod
    def apply_move(self, move: Any) -> 'PuzzleState':
        """
        Apply a move to create a new state.
        
        Args:
            move: The move to apply
            
        Returns:
            New PuzzleState after applying the move
        """
        pass
    
    @abstractmethod
    def is_goal_state(self) -> bool:
        """
        Check if this state is the goal state.
        
        Returns:
            True if this is the goal state, False otherwise
        """
        pass
    
    @abstractmethod
    def get_state_hash(self) -> str:
        """
        Get a unique hash string for this state.
        
        Returns:
            String hash that uniquely identifies this state
        """
        pass
    
    @abstractmethod
    def display(self) -> str:
        """
        Get a string representation of the state for display.
        
        Returns:
            Human-readable string representation of the state
        """
        pass
    
    @abstractmethod
    def equals(self, other: 'PuzzleState') -> bool:
        """
        Check if this state equals another state.
        
        Args:
            other: Another PuzzleState to compare with
            
        Returns:
            True if states are equal, False otherwise
        """
        pass
    
    def __eq__(self, other) -> bool:
        """Override equality operator to use the equals method."""
        if not isinstance(other, PuzzleState):
            return False
        return self.equals(other)
    
    def __hash__(self) -> int:
        """Override hash to use state hash."""
        return hash(self.get_state_hash())