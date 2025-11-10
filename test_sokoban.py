"""Quick test of Sokoban implementation."""

from a_star_solver.puzzles.sokoban_puzzle import SokobanState
from a_star_solver.solver.a_star import AStarSolver
from a_star_solver.solver.sokoban_heuristics import SokobanManhattanHeuristic

# Very simple test level - box next to goal, player can push it
level_str = """
#####
#.$ #
#  @#
#####
"""

print("Testing Sokoban implementation...")
print("="*50)

# Create state
state = SokobanState.from_string(level_str)
print("\nInitial state:")
print(state.display())
print(f"Player: {state.player}")
print(f"Boxes: {state.boxes}")
print(f"Goals: {state.goals}")
print(f"Is goal: {state.is_goal_state()}")

# Test moves
print("\nPossible moves:", state.get_possible_moves())

# Debug move generation
player_row, player_col = state.player
print(f"\nDebug move generation:")
print(f"Player at ({player_row}, {player_col})")
print(f"Left position: ({player_row}, {player_col - 1}) - ", end="")
left_pos = (player_row, player_col - 1)
if left_pos in state.walls:
    print("WALL")
elif left_pos in state.boxes:
    print(f"BOX - can push to ({player_row}, {player_col - 2})?")
    box_new = (player_row, player_col - 2)
    if box_new in state.walls:
        print(f"  No - wall at {box_new}")
    elif box_new in state.boxes:
        print(f"  No - another box at {box_new}")
    else:
        print(f"  Yes - empty at {box_new}")
        if state._is_deadlock_position(box_new):
            print(f"  But it's a deadlock position!")
else:
    print("EMPTY")

# Try manual solution
print("\n" + "="*50)
print("Manual solution attempt:")
current = state

# Step 1: Move UP
print("\nStep 1: Move UP")
current = current.apply_move('U')
print(current.display())
print(f"Possible moves: {current.get_possible_moves()}")

# Step 2: Move LEFT (should push box left onto goal)
print("\nStep 2: Move LEFT (pushing box)")
current = current.apply_move('L')
print(current.display())
print(f"Is goal state: {current.is_goal_state()}")

# Test solver
print("\n" + "="*50)
print("Testing A* solver...")
heuristic = SokobanManhattanHeuristic()
print(f"Initial heuristic value: {heuristic.calculate(state)}")

solver = AStarSolver(heuristic, max_states=1000, timeout_seconds=5.0)
result = solver.solve(state)

print(f"\nSolution found: {result.solution_found}")
print(f"Solution length: {result.solution_length}")
print(f"States explored: {result.states_explored}")
print(f"States generated: {result.states_generated}")

if result.solution_found and result.solution_path:
    print("\nSolution path:")
    for i, s in enumerate(result.solution_path):
        print(f"\nStep {i}:")
        print(s.display())
else:
    print(f"Termination reason: {solver.get_termination_reason()}")