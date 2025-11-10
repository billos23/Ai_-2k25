"""
A* algorithm implementation for puzzle solving.
"""

import heapq
import time
from typing import Dict, List, Optional, Set, Tuple
from a_star_solver.puzzles.base_puzzle import PuzzleState
from a_star_solver.solver.heuristic_base import HeuristicFunction
from a_star_solver.solver.solution_result import SolutionResult


class AStarSolver:
    """
    A* algorithm implementation for solving state-space search problems.
    
    This class implements the complete A* search algorithm with support for
    custom heuristic functions and comprehensive performance tracking.
    """
    
    def __init__(self, heuristic_function: HeuristicFunction, max_states: int = 100000, timeout_seconds: float = 60.0, memory_limit_mb: int = 512):
        """
        Initialize the A* solver with a heuristic function.
        
        Args:
            heuristic_function: The heuristic function to use for guiding the search
            max_states: Maximum number of states to explore before terminating (default: 100000)
            timeout_seconds: Maximum time in seconds before terminating (default: 60.0)
            memory_limit_mb: Maximum memory usage in MB before cleanup (default: 512)
            
        Raises:
            TypeError: If heuristic_function is not a HeuristicFunction instance
            ValueError: If heuristic_function is not admissible or limits are invalid
        """
        if not isinstance(heuristic_function, HeuristicFunction):
            raise TypeError("heuristic_function must be an instance of HeuristicFunction")
        
        if not heuristic_function.is_admissible():
            raise ValueError("heuristic_function must be admissible for optimal solutions")
        
        if max_states <= 0:
            raise ValueError("max_states must be positive")
        
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        
        if memory_limit_mb <= 0:
            raise ValueError("memory_limit_mb must be positive")
        
        self.heuristic_function = heuristic_function
        self.max_states = max_states
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        
        # Initialize data structures for search
        self._open_list: List[Tuple[int, int, PuzzleState]] = []  # (f_score, counter, state)
        self._open_set: Set[str] = set()  # Set of state hashes in open list
        self._closed_set: Set[str] = set()  # Set of explored state hashes
        self._came_from: Dict[str, PuzzleState] = {}  # Parent tracking for path reconstruction
        self._g_scores: Dict[str, int] = {}  # Actual cost from start to each state
        self._f_scores: Dict[str, int] = {}  # f(n) = g(n) + h(n) for each state
        
        # Performance tracking
        self._states_explored = 0
        self._states_generated = 0
        self._counter = 0  # For breaking ties in priority queue
        self._search_start_time = 0.0
        self._termination_reason = ""
        self._memory_cleanups = 0
        self._last_timeout_check = 0.0
    
    def solve(self, initial_state: PuzzleState) -> SolutionResult:
        """
        Solve the puzzle using A* algorithm.
        
        Args:
            initial_state: The starting state of the puzzle
            
        Returns:
            SolutionResult containing the solution path and performance metrics
            
        Raises:
            TypeError: If initial_state is not a PuzzleState instance
        """
        if not isinstance(initial_state, PuzzleState):
            raise TypeError("initial_state must be an instance of PuzzleState")
        
        # Reset all data structures for new search
        self._reset_search_state()
        
        # Start timing
        start_time = time.time()
        
        try:
            # Check if initial state is already the goal
            if initial_state.is_goal_state():
                end_time = time.time()
                self._termination_reason = "Initial state is goal"
                return SolutionResult(
                    solution_found=True,
                    solution_path=[initial_state],
                    states_explored=0,
                    states_generated=1,
                    execution_time=end_time - start_time,
                    solution_length=0
                )
            
            # Initialize search with initial state
            initial_hash = initial_state.get_state_hash()
            initial_h = self.heuristic_function.calculate(initial_state)
            initial_f = initial_h  # g(initial) = 0
            
            self._g_scores[initial_hash] = 0
            self._f_scores[initial_hash] = initial_f
            self._add_to_open_list(initial_state, initial_f)
            self._states_generated = 1
            
            # Main A* search loop
            result = self._search_loop()
            
            end_time = time.time()
            result.execution_time = end_time - start_time
            
            return result
            
        except Exception as e:
            end_time = time.time()
            self._termination_reason = f"Exception: {str(e)}"
            # Return failure result with timing information
            return SolutionResult(
                solution_found=False,
                solution_path=None,
                states_explored=self._states_explored,
                states_generated=self._states_generated,
                execution_time=end_time - start_time,
                solution_length=0
            )
    
    def _calculate_f_score(self, state: PuzzleState, g_score: int) -> int:
        """
        Calculate the f-score for a state: f(n) = g(n) + h(n).
        
        Args:
            state: The puzzle state to evaluate
            g_score: The actual cost from start to this state
            
        Returns:
            The f-score (estimated total cost through this state)
        """
        h_score = self.heuristic_function.calculate(state)
        return g_score + h_score
    
    def _reset_search_state(self) -> None:
        """Reset all data structures for a new search."""
        self._open_list.clear()
        self._open_set.clear()
        self._closed_set.clear()
        self._came_from.clear()
        self._g_scores.clear()
        self._f_scores.clear()
        self._states_explored = 0
        self._states_generated = 0
        self._counter = 0
        self._search_start_time = 0.0
        self._termination_reason = ""
    
    def _add_to_open_list(self, state: PuzzleState, f_score: int) -> None:
        """
        Add a state to the open list (priority queue).
        
        Args:
            state: The state to add
            f_score: The f-score of the state
        """
        state_hash = state.get_state_hash()
        self._counter += 1
        heapq.heappush(self._open_list, (f_score, self._counter, state))
        self._open_set.add(state_hash)
    
    def _get_next_state(self) -> Optional[PuzzleState]:
        """
        Get the next state to explore from the open list.
        
        Returns:
            The state with the lowest f-score, or None if open list is empty
        """
        while self._open_list:
            f_score, counter, state = heapq.heappop(self._open_list)
            state_hash = state.get_state_hash()
            
            # Remove from open set
            self._open_set.discard(state_hash)
            
            # Check if this state is still valid (not superseded by better path)
            if state_hash in self._f_scores and self._f_scores[state_hash] == f_score:
                return state
        
        return None
    
    def _search_loop(self) -> SolutionResult:
        """
        Main A* search loop implementation with termination conditions.
        
        Returns:
            SolutionResult with the search outcome
        """
        self._search_start_time = time.time()
        
        while self._open_list:
            # Check termination conditions
            if self._should_terminate():
                break
            
            # Get the state with lowest f-score
            current_state = self._get_next_state()
            if current_state is None:
                self._termination_reason = "Open list exhausted"
                break
            
            current_hash = current_state.get_state_hash()
            
            # Move current state to closed set
            self._closed_set.add(current_hash)
            self._states_explored += 1
            
            # Check if we reached the goal
            if current_state.is_goal_state():
                # Reconstruct and return solution
                solution_path = self._reconstruct_path(current_state)
                self._termination_reason = "Solution found"
                return SolutionResult(
                    solution_found=True,
                    solution_path=solution_path,
                    states_explored=self._states_explored,
                    states_generated=self._states_generated,
                    execution_time=0.0,  # Will be set by caller
                    solution_length=len(solution_path) - 1
                )
            
            # Generate and evaluate successor states
            self._process_successors(current_state)
        
        # No solution found
        if not self._termination_reason:
            self._termination_reason = "Open list exhausted"
        
        return SolutionResult(
            solution_found=False,
            solution_path=None,
            states_explored=self._states_explored,
            states_generated=self._states_generated,
            execution_time=0.0,  # Will be set by caller
            solution_length=0
        )
    
    def _should_terminate(self) -> bool:
        """
        Check if the search should terminate due to limits.
        
        Returns:
            True if search should terminate, False otherwise
        """
        # Check state limit
        if self._states_explored >= self.max_states:
            self._termination_reason = f"State limit reached ({self.max_states})"
            return True
        
        # Check timeout (optimize by checking less frequently)
        current_time = time.time()
        if current_time - self._last_timeout_check > 0.1:  # Check every 100ms
            self._last_timeout_check = current_time
            elapsed_time = current_time - self._search_start_time
            if elapsed_time >= self.timeout_seconds:
                self._termination_reason = f"Timeout reached ({self.timeout_seconds}s)"
                return True
        
        # Check memory usage periodically
        if self._states_explored % 1000 == 0:
            if self._check_memory_usage():
                return True
        
        return False
    
    def _check_memory_usage(self) -> bool:
        """
        Check memory usage and perform cleanup if needed.
        
        Returns:
            True if search should terminate due to memory issues, False otherwise
        """
        try:
            import psutil
            import os
            
            # Get current process memory usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.memory_limit_mb:
                # Try to free some memory by cleaning up old states
                self._cleanup_memory()
                self._memory_cleanups += 1
                
                # Check again after cleanup
                memory_mb = process.memory_info().rss / 1024 / 1024
                if memory_mb > self.memory_limit_mb * 1.2:  # 20% tolerance
                    self._termination_reason = f"Memory limit exceeded ({memory_mb:.1f}MB > {self.memory_limit_mb}MB)"
                    return True
            
        except ImportError:
            # psutil not available, skip memory checking
            pass
        except Exception:
            # Any other error, continue without memory checking
            pass
        
        return False
    
    def _cleanup_memory(self) -> None:
        """
        Clean up memory by removing old states from tracking dictionaries.
        """
        # Keep only the most recent states in closed set
        if len(self._closed_set) > 50000:
            # Convert to list and keep only the last 25000
            closed_list = list(self._closed_set)
            self._closed_set = set(closed_list[-25000:])
        
        # Clean up g_scores and f_scores for states no longer needed
        states_to_keep = self._open_set | self._closed_set
        
        # Clean g_scores
        g_keys_to_remove = [k for k in self._g_scores.keys() if k not in states_to_keep]
        for key in g_keys_to_remove:
            del self._g_scores[key]
        
        # Clean f_scores
        f_keys_to_remove = [k for k in self._f_scores.keys() if k not in states_to_keep]
        for key in f_keys_to_remove:
            del self._f_scores[key]
        
        # Clean came_from (keep only states that might be in solution path)
        came_from_keys_to_remove = [k for k in self._came_from.keys() if k not in states_to_keep]
        for key in came_from_keys_to_remove:
            del self._came_from[key]
    
    def _process_successors(self, current_state: PuzzleState) -> None:
        """
        Process all successor states of the current state.
        
        Args:
            current_state: The current state being expanded
        """
        current_hash = current_state.get_state_hash()
        current_g = self._g_scores[current_hash]
        
        # Get all possible moves from current state
        possible_moves = current_state.get_possible_moves()
        
        for move in possible_moves:
            # Apply move to create successor state
            try:
                successor_state = current_state.apply_move(move)
                successor_hash = successor_state.get_state_hash()
                self._states_generated += 1
                
                # Skip if already in closed set
                if successor_hash in self._closed_set:
                    continue
                
                # Calculate tentative g-score (cost from start to successor)
                tentative_g = current_g + 1  # Assuming unit cost for each move
                
                # Check if this is a better path to the successor
                if (successor_hash not in self._g_scores or 
                    tentative_g < self._g_scores[successor_hash]):
                    
                    # Update path tracking
                    self._came_from[successor_hash] = current_state
                    self._g_scores[successor_hash] = tentative_g
                    
                    # Calculate f-score
                    f_score = self._calculate_f_score(successor_state, tentative_g)
                    self._f_scores[successor_hash] = f_score
                    
                    # Add to open list if not already there
                    if successor_hash not in self._open_set:
                        self._add_to_open_list(successor_state, f_score)
                    
            except Exception:
                # Skip invalid moves or states
                continue
    
    def _reconstruct_path(self, goal_state: PuzzleState) -> List[PuzzleState]:
        """
        Reconstruct the solution path from initial state to goal state.
        
        Args:
            goal_state: The goal state reached by the search
            
        Returns:
            List of states representing the complete solution path
        """
        path = []
        current_state = goal_state
        
        # Trace back through parent states
        while current_state is not None:
            path.append(current_state)
            current_hash = current_state.get_state_hash()
            current_state = self._came_from.get(current_hash)
        
        # Reverse to get path from initial to goal
        path.reverse()
        return path
    
    def get_search_statistics(self) -> Dict[str, any]:
        """
        Get detailed statistics about the current search state.
        
        Returns:
            Dictionary containing search statistics
        """
        stats = {
            'states_explored': self._states_explored,
            'states_generated': self._states_generated,
            'open_list_size': len(self._open_list),
            'closed_set_size': len(self._closed_set),
            'g_scores_tracked': len(self._g_scores),
            'f_scores_tracked': len(self._f_scores),
            'termination_reason': self._termination_reason,
            'max_states_limit': self.max_states,
            'timeout_limit': self.timeout_seconds,
            'memory_limit_mb': self.memory_limit_mb,
            'memory_cleanups': self._memory_cleanups
        }
        
        # Add heuristic cache stats if available
        if hasattr(self.heuristic_function, 'get_cache_stats'):
            heuristic_stats = self.heuristic_function.get_cache_stats()
            stats['heuristic_cache'] = heuristic_stats
        
        return stats
    
    def get_heuristic_name(self) -> str:
        """
        Get the name of the heuristic function being used.
        
        Returns:
            Name of the heuristic function
        """
        return self.heuristic_function.get_name()
    
    def get_termination_reason(self) -> str:
        """
        Get the reason why the search terminated.
        
        Returns:
            String describing why the search ended
        """
        return self._termination_reason