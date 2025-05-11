# Maze Router - MS1 Implementation

This is the first milestone implementation of a maze router using Lee's algorithm. This version supports single-layer routing with basic functionality.

## Project Structure
- `router.py`: Main router implementation
- `test_cases/`: Directory containing test cases
- `requirements.txt`: Python dependencies

## Setup
1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the router:
```bash
python router.py <input_file> <output_file>
```

## Current Limitations (MS1)
- Single-layer routing only
- Basic Lee's algorithm implementation
- No via support

## Test Cases
Three test cases are provided in the `test_cases` directory:
1. `test1.txt`: Simple 2-pin net
2. `test2.txt`: Multiple nets with obstacles
3. `test3.txt`: Complex routing scenario

## Input Format
The input file should follow this format:
```
<grid_width>x<grid_height>
OBS (x, y)
net1 (layer, x1, y1) (layer, x2, y2)
net2 (layer, x1, y1) (layer, x2, y2)
...
```

## Output Format
The output file will contain the routed paths:
```
net1 (layer, x1, y1) (layer, x2, y2) ...
net2 (layer, x1, y1) (layer, x2, y2) ...
...
```
