import numpy as np
from collections import deque
import sys
import re

class MazeRouter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.obstacles = set()
        
    def add_obstacle(self, x, y):
        self.obstacles.add((x, y))
        self.grid[y][x] = -1
        
    def is_valid_position(self, x, y):
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                (x, y) not in self.obstacles)
    
    def get_neighbors(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                neighbors.append((new_x, new_y))
        return neighbors
    
    def route_net(self, start, end):
        start_x, start_y = start
        end_x, end_y = end
        
        wave_grid = np.full((self.height, self.width), -1)
        wave_grid[start_y][start_x] = 0
        queue = deque([(start_x, start_y)])
        
        while queue and wave_grid[end_y][end_x] == -1:
            x, y = queue.popleft()
            current_wave = wave_grid[y][x]
            
            for nx, ny in self.get_neighbors(x, y):
                if wave_grid[ny][nx] == -1:
                    wave_grid[ny][nx] = current_wave + 1
                    queue.append((nx, ny))
        
        if wave_grid[end_y][end_x] == -1:
            return None
        
        path = []
        x, y = end_x, end_y
        while (x, y) != (start_x, start_y):
            path.append((x, y))
            current_wave = wave_grid[y][x]
            
            for nx, ny in self.get_neighbors(x, y):
                if wave_grid[ny][nx] == current_wave - 1:
                    x, y = nx, ny
                    break
        
        path.append((start_x, start_y))
        return path[::-1]

def parse_input_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    width, height = map(int, lines[0].strip().split('x'))
    router = MazeRouter(width, height)
    
    nets = []
    current_net = None
    
    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('OBS'):
            obs_match = re.search(r'\((\d+),\s*(\d+)\)', line)
            if obs_match:
                x, y = map(int, obs_match.groups())
                router.add_obstacle(x, y)
        else:
            parts = line.split()
            net_name = parts[0]
            pins = []
            pin_matches = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
            for match in pin_matches:
                layer, x, y = map(int, match)
                pins.append((layer, x, y))
            if pins:
                nets.append((net_name, pins))
    
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
    for net_name, pins in nets:
        print(f"Routing net: {net_name} with pins: {pins}")
        layer = pins[0][0]
        
        paths = []
        for i in range(len(pins) - 1):
            start = (pins[i][1], pins[i][2])
            end = (pins[i+1][1], pins[i+1][2])
            
            paths.append((layer, start[0], start[1]))
            
            route = router.route_net(start, end)
            if route:
                for x, y in route[1:]:
                    paths.append((layer, x, y))
            else:
                print(f"Warning: Could not route {net_name} between pins {i} and {i+1}")
        
        routed_nets.append((net_name, paths))
    
    write_output_file(output_file, routed_nets)

    for net_name, paths in routed_nets:
        if paths:
            path_str = ' '.join(f'({layer}, {x}, {y})' for layer, x, y in paths)
            print(f"{net_name} {path_str}")

if __name__ == "__main__":
    main() 