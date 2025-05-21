import numpy as np
from collections import deque
import sys
import re
import heapq
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from parser import MazeRouterInput

@dataclass
class Point:
    layer: int
    x: int
    y: int

    def __hash__(self):
        return hash((self.layer, self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.layer, self.x, self.y) == (other.layer, other.x, other.y)
    
    def __lt__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.layer, self.x, self.y) < (other.layer, other.x, other.y)

    def to_tuple(self):
        return (self.layer, self.x, self.y)

class Grid:
    def __init__(self, width: int, height: int, num_layers: int = 2):
        self.width = width
        self.height = height
        self.num_layers = num_layers + 1  
        self.grid = [
            [
                [{'obstacle': False, 'cost': 0} for _ in range(width)]
                for _ in range(height)
            ] for _ in range(self.num_layers)
        ]

    def is_valid_point(self, point: Point) -> bool:
        return (1 <= point.layer <= self.num_layers - 1 and
                0 <= point.x < self.width and
                0 <= point.y < self.height)

    def is_obstacle(self, point: Point) -> bool:
        if not self.is_valid_point(point):
            return True
        return self.grid[point.layer][point.y][point.x]['obstacle']

    def set_obstacle(self, point: Point, is_obstacle: bool = True):
        if self.is_valid_point(point):
            self.grid[point.layer][point.y][point.x]['obstacle'] = is_obstacle

class PathFinder:
    def __init__(self, grid: Grid, via_penalty: int, wrong_direction_penalty: int):
        self.grid = grid
        self.via_penalty = via_penalty
        self.wrong_direction_penalty = wrong_direction_penalty

    def get_neighbors(self, point: Point) -> List[Tuple[Point, int]]:
        neighbors = []
        
        # Layer-specific preferred directions
        if point.layer == 1:  # M1 - Prefer horizontal
            directions = [
                (1, 0, point.layer),    # Right
                (-1, 0, point.layer),   # Left
                (0, 0, 2),             # Via to M2
                (0, 1, point.layer),    # Up
                (0, -1, point.layer)    # Down
            ]
        else:  # M2 - Prefer vertical
            directions = [
                (0, 1, point.layer),    # Up
                (0, -1, point.layer),   # Down
                (0, 0, 1),             # Via to M1
                (1, 0, point.layer),    # Right
                (-1, 0, point.layer)    # Left
            ]

        for dx, dy, new_layer in directions:
            neighbor = Point(new_layer, point.x + dx, point.y + dy)
            
            if not self.grid.is_valid_point(neighbor):
                continue

            cost = 1
            if new_layer != point.layer:
                cost += self.via_penalty
            elif (point.layer == 1 and dy != 0) or (point.layer == 2 and dx != 0):
                cost += self.wrong_direction_penalty

            neighbors.append((neighbor, cost))

        return neighbors

    def find_path(self, start: Point, end: Point, net_pins: Set[Point], all_pins: Set[Point]) -> Optional[List[Point]]:
        heap = [(0, start)]
        visited = {start: 0}
        parent = {}

        while heap:
            current_cost, current = heapq.heappop(heap)
            
            if current == end:
                path = []
                while current:
                    path.append(current)
                    current = parent.get(current)
                return path[::-1]

            for neighbor, move_cost in self.get_neighbors(current):
                if (neighbor in all_pins and neighbor not in net_pins) or self.grid.is_obstacle(neighbor):
                    continue

                new_cost = current_cost + move_cost
                if neighbor not in visited or new_cost < visited[neighbor]:
                    visited[neighbor] = new_cost
                    parent[neighbor] = current
                    heapq.heappush(heap, (new_cost, neighbor))

        return None

class MazeRouter:
    def __init__(self, router_input: MazeRouterInput, via_penalty: Optional[int] = None, wrong_direction_penalty: Optional[int] = None):
        self.input = router_input
        self.grid = Grid(router_input.grid_width, router_input.grid_height)
        
        # Use provided penalties or fall back to input file values
        self.via_penalty = via_penalty if via_penalty is not None else router_input.via_penalty
        self.wrong_direction_penalty = wrong_direction_penalty if wrong_direction_penalty is not None else router_input.wrong_direction_penalty
        
        self.path_finder = PathFinder(self.grid, self.via_penalty, self.wrong_direction_penalty)
        self.initialize_grid()

    def initialize_grid(self):
        # Mark obstructions
        for layer, x, y in self.input.obstructions:
            self.grid.set_obstacle(Point(layer, x, y))

    def convert_to_points(self, pins: List[Dict]) -> List[Point]:
        return [Point(pin['layer'], pin['x'], pin['y']) for pin in pins]

    def route_net(self, net: Dict) -> Optional[Tuple[List[Tuple[int, int, int]], int, int]]:
        pins = self.convert_to_points(net['pins'])
        if len(pins) < 2:
            raise ValueError(f"Net '{net['name']}' does not have enough pins to route.")

        # Convert all pins to sets for efficient lookup
        net_pins = set(pins)
        all_pins = {Point(pin['layer'], pin['x'], pin['y']) for net in self.input.nets for pin in net['pins']}

        full_path = []
        total_wire_length = 0
        number_of_vias = 0

        for i in range(len(pins) - 1):
            path_segment = self.path_finder.find_path(pins[i], pins[i + 1], net_pins, all_pins)
            if not path_segment:
                return None

            # Calculate metrics
            for j in range(1, len(path_segment)):
                prev, curr = path_segment[j - 1], path_segment[j]
                total_wire_length += abs(curr.x - prev.x) + abs(curr.y - prev.y)
                if curr.layer != prev.layer:
                    number_of_vias += 1

            # Skip first point if not first segment to avoid duplicates
            if i > 0:
                path_segment = path_segment[1:]

            full_path.extend(path_segment)

            # Mark path as obstacles (except pins)
            for point in path_segment[:-1]:
                if point not in net_pins:
                    self.grid.set_obstacle(point)

        # Convert points back to tuples for compatibility
        path_tuples = [point.to_tuple() for point in full_path]
        return path_tuples, total_wire_length, number_of_vias

def parse_input_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # First line: grid dimensions and costs
    dimensions = list(map(int, lines[0].strip().split(',')))
    width, height = dimensions[0], dimensions[1]  # First two numbers are width and height
    via_cost = dimensions[2]  # Third number is via cost
    wrong_direction_cost = dimensions[3]  # Fourth number is wrong direction cost
    
    router = MazeRouter(width, height, via_cost=via_cost, wrong_direction_cost=wrong_direction_cost)
    
    nets = []
    all_pins = []
    
    for line in lines[1:]:  # Start from second line
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('OBS'):
            # Parse obstacle format: OBS (layer, x, y)
            obs_match = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            if obs_match:
                layer, x, y = map(int, obs_match[0])
                router.grid.set_obstacle(Point(layer-1, x, y))  # Convert 1-based layer to 0-based
        else:
            parts = line.split()
            net_name = parts[0]
            pins = []
            pin_matches = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            for match in pin_matches:
                layer, x, y = map(int, match)
                pin = (layer, x, y)
                pins.append(pin)
                all_pins.append((layer-1, x, y))  # Store 0-based layer
            if pins:
                nets.append((net_name, pins))
    
    router.grid.all_pins = all_pins
    return router, nets

def write_output_file(filename, routed_nets):
    with open(filename, 'w') as f:
        for net_name, paths in routed_nets:
            if paths:
                path_str = ' '.join(f'({layer}, {x}, {y})' for layer, x, y in paths)
                f.write(f"{net_name} {path_str}\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python router.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    router, nets = parse_input_file(input_file)
    print(f"Parsed nets: {nets}")
    
    routed_nets = []
    total_wire_length = 0
    total_vias = 0
    
    for net_name, pins in nets:
        print(f"Routing net: {net_name} with pins: {pins}")
        
        # Route all pins together
        result = router.route_net(pins)
        
        if result:
            path, wire_length, via_count = result
            routed_nets.append((net_name, path))
            total_wire_length += wire_length
            total_vias += via_count
            print(f"Successfully routed {net_name}")
            print(f"Wire length: {wire_length}, Vias: {via_count}")
        else:
            print(f"Warning: Could not route {net_name}")
            routed_nets.append((net_name, []))
    
    write_output_file(output_file, routed_nets)
    
    # Print summary
    print("\nRouting Summary:")
    print(f"Total nets routed: {len([n for n, p in routed_nets if p])}")
    print(f"Total wire length: {total_wire_length}")
    print(f"Total vias used: {total_vias}")
    
    # Print detailed net information
    print("\nDetailed Net Information:")
    for net_name, paths in routed_nets:
        if paths:
            path_str = ' '.join(f'({layer}, {x}, {y})' for layer, x, y in paths)
            print(f"{net_name}: {path_str}")

def route_all_nets(router_input: MazeRouterInput) -> Dict[str, Tuple[List[Tuple[int, int, int]], int, int]]:
    router = MazeRouter(router_input)
    routing_results = {}

    for net in router_input.nets:
        result = router.route_net(net)
        if result:
            routing_results[net['name']] = result

    return routing_results

if __name__ == "__main__":
    main() 