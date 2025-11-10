"""
Data class for representing A* solver results.
"""

from dataclasses import dataclass
from typing import List, Optional
from a_star_solver.puzzles.base_puzzle import PuzzleState


@dataclass
class SolutionResult:
    """
    Data class containing the results of an A* search.
    
    This class encapsulates all information about the search process,
    including the solution path (if found) and performance metrics.
    """
    
    solution_found: bool
    """True if a solution was found, False otherwise"""
    
    solution_path: Optional[List[PuzzleState]]
    """List of states from initial to goal state, None if no solution"""
    
    states_explored: int
    """Number of states that were expanded during the search"""
    
    states_generated: int
    """Total number of states generated during the search"""
    
    execution_time: float
    """Time taken to complete the search in seconds"""
    
    solution_length: int
    """Number of moves in the solution (0 if no solution found)"""
    
    def __post_init__(self):
        """Validate the solution result after initialization."""
        if self.solution_found:
            if self.solution_path is None:
                raise ValueError("solution_path cannot be None when solution_found is True")
            if len(self.solution_path) == 0:
                raise ValueError("solution_path cannot be empty when solution_found is True")
            if self.solution_length != len(self.solution_path) - 1:
                raise ValueError("solution_length must equal len(solution_path) - 1")
        else:
            if self.solution_length != 0:
                raise ValueError("solution_length must be 0 when no solution is found")
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of the search results.
        
        Returns:
            Formatted string summarizing the search results
        """
        if self.solution_found:
            return (f"Solution found in {self.solution_length} moves\n"
                   f"States explored: {self.states_explored}\n"
                   f"States generated: {self.states_generated}\n"
                   f"Execution time: {self.execution_time:.3f} seconds")
        else:
            return (f"No solution found\n"
                   f"States explored: {self.states_explored}\n"
                   f"States generated: {self.states_generated}\n"
                   f"Execution time: {self.execution_time:.3f} seconds")