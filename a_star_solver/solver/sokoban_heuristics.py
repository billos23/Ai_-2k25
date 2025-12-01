"""
Heuristic functions specific to Sokoban puzzles.
"""

from typing import Dict, Tuple
from a_star_solver.solver.heuristic_base import HeuristicFunction
from a_star_solver.puzzles.base_puzzle import PuzzleState
from a_star_solver.puzzles.sokoban_puzzle import SokobanState


class SokobanManhattanHeuristic(HeuristicFunction):
    """
    Manhattan distance heuristic for Sokoban.
    
    Calculates the sum of Manhattan distances from each box to its nearest goal.
    This is admissible because each box must move at least its Manhattan distance
    to reach a goal.
    """
    
    def __init__(self):
        """Initialize the Sokoban Manhattan heuristic."""
        self._cache = {}
      
    
    def calculate(self, state: PuzzleState) -> int:
        """
        Calculate the Manhattan distance heuristic for a Sokoban state.
        
        Args:
            state: The Sokoban state to evaluate
            
        Returns:
            Sum of minimum Manhattan distances from boxes to goals
        """
        if not isinstance(state, SokobanState):
            raise TypeError("SokobanManhattanHeuristic only works with SokobanState")
        
        # Check cache
        state_hash = state.get_state_hash()
        if state_hash in self._cache:
            
            return self._cache[state_hash]
        
        
        
        # Calculate minimum matching between boxes and goals
        total_distance = 0
        boxes = list(state.boxes)
        goals = list(state.goals)
        
        # Simple greedy matching: for each box, find nearest goal
        # This is admissible but not optimal matching
        used_goals = set()
        
        for box in boxes:
            min_dist = float('inf')
            best_goal = None
            
            for goal in goals:
                if goal not in used_goals:
                    dist = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
                    if dist < min_dist:
                        min_dist = dist
                        best_goal = goal
            
            if best_goal is not None:
                used_goals.add(best_goal)
                total_distance += min_dist
        
        # Cache the result
        self._cache[state_hash] = total_distance
        
        # Limit cache size
        if len(self._cache) > 10000:
            keys_to_remove = list(self._cache.keys())[:1000]
            for key in keys_to_remove:
                del self._cache[key]
        
        return total_distance
    
    def is_admissible(self) -> bool:
        """
        Check if this heuristic is admissible.
        
        Returns:
            True (Manhattan distance is admissible for Sokoban)
        """
        return True
    
    def get_name(self) -> str:
        """
        Get the name of this heuristic.
        
        Returns:
            Name of the heuristic
        """
        return "Sokoban Manhattan Distance"
    
    
    
    

class SokobanSimpleHeuristic(HeuristicFunction):
    """
    Simple heuristic for Sokoban: count boxes not on goals.
    
    This is similar to misplaced tiles for sliding puzzles.
    """
    
    def __init__(self):
        """Initialize the simple Sokoban heuristic."""
        self._cache = {}

    
    def calculate(self, state: PuzzleState) -> int:
        """
        Calculate the simple heuristic: boxes not on goals.
        
        Args:
            state: The Sokoban state to evaluate
            
        Returns:
            Number of boxes not on goal positions
        """
        if not isinstance(state, SokobanState):
            raise TypeError("SokobanSimpleHeuristic only works with SokobanState")
        
        # Check cache
        state_hash = state.get_state_hash()
        if state_hash in self._cache:
            
            return self._cache[state_hash]
        
      
        
        # Count boxes not on goals
        boxes_on_goals = state.boxes & state.goals
        boxes_not_on_goals = len(state.boxes) - len(boxes_on_goals)
        
        # Cache the result
        self._cache[state_hash] = boxes_not_on_goals
        
        # Limit cache size
        if len(self._cache) > 10000:
            keys_to_remove = list(self._cache.keys())[:1000]
            for key in keys_to_remove:
                del self._cache[key]
        
        return boxes_not_on_goals
    
    def is_admissible(self) -> bool:
        """
        Check if this heuristic is admissible.
        
        Returns:
            True (counting misplaced boxes is admissible)
        """
        return True
    
    def get_name(self) -> str:
        """
        Get the name of this heuristic.
        
        Returns:
            Name of the heuristic
        """
        return "Sokoban Simple (Misplaced Boxes)"
    
   
