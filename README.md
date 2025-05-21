# Maze Router Implementation

A maze router implementation supporting multi-layer routing with advanced visualization capabilities. The router uses an enhanced A* algorithm with layer-aware pathfinding and direction preferences.

## Features
- Two-layer routing (M1 and M2)
- Layer-specific direction preferences:
  * M1 (Layer 1): Horizontal preferred
  * M2 (Layer 2): Vertical preferred
- Smart via placement
- Comprehensive visualization:
  * Separate layer views (M1 and M2)
  * 3D visualization
  * Color-coded nets and obstacles
- Cost-aware routing:
  * Via cost penalties
  * Wrong direction penalties
- Multiple pin support
- Obstacle avoidance

## Project Structure
- `src/`
  * `main.py`: Main entry point
  * `router.py`: Core routing implementation
  * `visualization.py`: Visualization tools
  * `test_cases/`: Directory containing test cases (1-21)

## Setup
1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the router:
```bash
python3 main.py <input_file> <output_file>
```

The router will generate:
- Routing solution in the output file
- Visualization files:
  * `layer_views.png`: Shows Layer 1 (M1), Layer 2 (M2), and 3D view

## Input Format
The input file should follow this format:
```
<width>,<height>,<via_cost>,<wrong_direction_cost>
OBS (layer, x, y)
net1 (layer1, x1, y1) (layer2, x2, y2)
net2 (layer1, x1, y1) (layer2, x2, y2)
...
```

Where:
- `layer`: 1 for M1 (horizontal preferred), 2 for M2 (vertical preferred)
- `via_cost`: Cost penalty for switching layers
- `wrong_direction_cost`: Cost penalty for routing against layer preference

## Output Format
The output file contains the routed paths:
```
net1 (layer, x1, y1) (layer, x2, y2) ...
net2 (layer, x1, y1) (layer, x2, y2) ...
...
```

## Visualization
The router generates comprehensive visualizations:
- Layer 1 (M1) View: Shows horizontal preferred routing
- Layer 2 (M2) View: Shows vertical preferred routing
- 3D View: Shows complete routing in 3D space

Visualization features:
- Red obstacles
- Color-coded nets
- Via points (red circles)
- Pin points (green squares)
- Grid lines
- Layer-specific routing preferences

## Performance
The router uses several optimization techniques:
- A* pathfinding with Manhattan distance heuristic
- Smart direction prioritization
- Efficient layer transitions
- Cost-based routing decisions

## Test Cases
The project includes 25 test cases of varying complexity, demonstrating:
- Multi-net routing
- Obstacle avoidance
- Layer transitions
- Complex pin configurations
- Different grid sizes
