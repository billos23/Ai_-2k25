"""
Abstract base class for heuristic functions.
"""

from abc import ABC, abstractmethod
from a_star_solver.puzzles.base_puzzle import PuzzleState


class HeuristicFunction(ABC):
    """
    Abstract base class for heuristic functions used in A* search.
    
    Heuristic functions estimate the cost from a given state to the goal state.
    For A* to guarantee optimal solutions, heuristics must be admissible
    (never overestimate the actual cost).
    """
    
    @abstractmethod
    def calculate(self, state: PuzzleState) -> int:
        """
        Calculate the heuristic value for a given state.
        
        Args:
            state: The puzzle state to evaluate
            
        Returns:
            Estimated cost from this state to the goal state
        """
        pass
    
    @abstractmethod
    def is_admissible(self) -> bool:
        """
        Check if this heuristic is admissible.
        
        An admissible heuristic never overestimates the actual cost
        to reach the goal state.
        
        Returns:
            True if the heuristic is admissible, False otherwise
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this heuristic function.
        
        Returns:
            Human-readable name of the heuristic
        """
        pass
