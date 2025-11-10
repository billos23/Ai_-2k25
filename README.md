# A* Sokoban Solver

An implementation of the A* search algorithm for solving Sokoban puzzles.

## What is Sokoban?

Sokoban is a classic puzzle game where you push boxes to goal locations in a warehouse. The player can only push boxes (not pull them), and only one box at a time. The goal is to get all boxes onto the goal positions.

## Features

- **A* Search Algorithm**: Optimal pathfinding with admissible heuristics
- **Two Heuristics**:
  - Manhattan Distance: Sum of distances from boxes to nearest goals
  - Simple: Count of boxes not on goals
- **Level Loader**: Parses standard .sok format files
- **10 Sokoban Levels**: Aymeric du Peloux's Medium collection
- **Interactive Interface**: Select levels, choose heuristics, view solutions

## Installation

No external dependencies required - uses only Python standard library.

```bash
# Clone or download this repository
cd AiAskisi1

# Run the solver
python main.py
```

## Usage

```bash
python main.py
```

Then:
1. Select a level number (1-10)
2. Choose a heuristic (1 for Manhattan Distance, 2 for Simple)
3. Wait for the solver to find a solution
4. Optionally view the step-by-step solution path

## Sokoban Notation

- `#` = Wall
- `@` = Player
- `$` = Box
- `.` = Goal
- `*` = Box on goal
- `+` = Player on goal
- ` ` = Empty space

## Project Structure

```
AiAskisi1/
├── main.py                          # Main application entry point
├── test_sokoban.py                  # Simple test script
├── levels/
│   └── Aymeric_Medium.sok          # 10 Sokoban levels
└── a_star_solver/
    ├── puzzles/
    │   ├── base_puzzle.py          # Abstract puzzle interface
    │   ├── sokoban_puzzle.py       # Sokoban state representation
    │   └── sokoban_loader.py       # Level file parser
    └── solver/
        ├── a_star.py               # Core A* algorithm
        ├── sokoban_heuristics.py   # Sokoban-specific heuristics
        └── solution_result.py      # Result data structure
```

## Testing

Run the simple test to verify the implementation:

```bash
python test_sokoban.py
```

This tests a trivial 2-move puzzle to ensure everything works correctly.

## Performance Notes

The included levels are medium-difficulty puzzles requiring 69-178 optimal moves. These are challenging for basic A* with simple heuristics:

- **Current limits**: 50,000 states, 30 second timeout
- **Expected behavior**: May hit state limit before finding solutions
- **Why**: Sokoban is PSPACE-complete with enormous search spaces

The implementation is correct and finds optimal solutions for simpler puzzles. To solve the included levels, you would need:
- More sophisticated heuristics (pattern databases, goal room detection)
- Better deadlock detection (freeze deadlocks, corral deadlocks)
- Larger state limits (100,000+)
- More time (minutes instead of seconds)

## Algorithm Details

### A* Search
- Uses priority queue to explore states with lowest f(n) = g(n) + h(n)
- g(n) = actual cost from start
- h(n) = heuristic estimate to goal
- Guarantees optimal solution when heuristic is admissible

### Heuristics
Both heuristics are admissible (never overestimate):
- **Manhattan Distance**: More informed, usually faster
- **Simple**: Less informed, explores more states

### Deadlock Detection
Prevents pushing boxes into unsolvable positions:
- Corner deadlocks: Box in corner not on goal
- Conservative approach to avoid false positives

## Levels

The 10 included levels from Aymeric du Peloux's collection:

1. Nabokosmos 15 (97 moves)
2. Nabokosmos 20 (148 moves)
3. Nabokosmos 14 (104 moves)
4. Nabokosmos 30 (113 moves)
5. Nabokosmos 40 (171 moves)
6. Nabokosmos 29 (136 moves)
7. Nabokosmos 35 (178 moves)
8. Nabokosmos 38 (69 moves)
9. Nabokosmos 33 (110 moves)
10. Nabokosmos 31 (113 moves)

## License

This is an educational project. The Sokoban levels are © Aymeric du Peloux.

## References

- Sokoban levels: https://github.com/medovina/Sokoban4J
- A* Algorithm: Hart, P. E.; Nilsson, N. J.; Raphael, B. (1968)
- Sokoban: Created by Hiroyuki Imabayashi (1981)