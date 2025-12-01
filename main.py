"""
Main entry point for the A* Sokoban solver application.
"""

import sys
from a_star_solver.solver.a_star import AStarSolver
from a_star_solver.solver.sokoban_heuristics import SokobanManhattanHeuristic, SokobanSimpleHeuristic
from a_star_solver.puzzles.sokoban_loader import SokobanLevelLoader


def main():
    """Main application entry point."""
    print("="*60)
    print("A* SOKOBAN PUZZLE SOLVER")
    print("="*60)

    print("\nAvailable level files:")
    print("  1. Aymeric Medium (10 levels)")
    print("  2. Aymeric Hard (10 levels)")

    #Menu
     while True:
        file_choice = input("\nSelect level file (1 or 2): ").strip()
        if file_choice == '1':
            level_file = 'levels/Aymeric_Medium.sok'
            break
        elif file_choice == '2':
            level_file = 'levels/Aymeric_Hard.sok'
            break
        else:
            print("Please enter 1 or 2")
    
    # Load levels
    try:
        levels = SokobanLevelLoader.load_from_file(level_file)   
        print(f"\nLoaded {len(levels)} from {level_file}")
    except FileNotFoundError:
        print("\nError: Could not find {level_file}")
        print("Please ensure the level file is in the levels directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError loading levels: {e}")
        sys.exit(1)
    
    # Display available levels
    print("\nAvailable levels:")
    for level in levels:
        print(f"  {level.number}. {level.title} ({level.moves} optimal moves)")
    
    # Select level
    while True:
        try:
            level_num = input("\nEnter level number (or 'q' to quit): ").strip()
            if level_num.lower() == 'q':
                print("Goodbye!")
                sys.exit(0)
            
            level_num = int(level_num)
            level = SokobanLevelLoader.get_level_by_number(levels, level_num)
            break
        except ValueError:
            print("Please enter a valid level number")
        except Exception as e:
            print(f"Error: {e}")
    
    # Display level
    print(f"\nLevel {level.number}: {level.title} ({level.moves} optimal moves)")
    print("\nInitial state:")
    print(level.state.display())
    print(f"\nBoxes: {len(level.state.boxes)}, Goals: {len(level.state.goals)}")
    
    # Select heuristic
    print("\nAvailable heuristics:")
    print("  1. Manhattan Distance (recommended)")
    print("  2. Simple (Misplaced Boxes)")
    
    while True:
        choice = input("\nSelect heuristic (1 or 2): ").strip()
        if choice == '1':
            heuristic = SokobanManhattanHeuristic()
            break
        elif choice == '2':
            heuristic = SokobanSimpleHeuristic()
            break
        else:
            print("Please enter 1 or 2")
    
    print(f"\nUsing heuristic: {heuristic.get_name()}")
    
    # Create solver
    solver = AStarSolver(heuristic, max_states=2000000, timeout_seconds=60.0)
    
    # Solve
    print("\nSolving...")
    result = solver.solve(level.state)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    if result.solution_found:
        print(f"✓ Solution found!")
        print(f"\nSolution length: {result.solution_length} moves")
        print(f"Optimal moves: {level.moves}")
        if result.solution_length == level.moves:
            print("★ OPTIMAL SOLUTION! ★")
        elif result.solution_length < level.moves:
            print("★ BETTER THAN OPTIMAL! ★")
        else:
            print(f"(+{result.solution_length - level.moves} moves over optimal)")
        
        print(f"\nStates explored: {result.states_explored}")
        print(f"States generated: {result.states_generated}")
        print(f"Execution time: {result.execution_time:.3f} seconds")
        
        # Show solution path
        show_path = input("\nShow solution path? (y/n): ").strip().lower()
        if show_path == 'y':
            print("\nSolution path:")
            for i, state in enumerate(result.solution_path):
                print(f"\nStep {i}:")
                print(state.display())
                if i < len(result.solution_path) - 1:
                    input("Press Enter for next step...")
    else:
        print(f"✗ No solution found")
        print(f"\nStates explored: {result.states_explored}")
        print(f"States generated: {result.states_generated}")
        print(f"Execution time: {result.execution_time:.3f} seconds")
        print(f"Termination reason: {solver.get_termination_reason()}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
    

        sys.exit(1)




