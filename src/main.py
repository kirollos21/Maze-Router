import sys
import os
import re
from router import MazeRouter

def parse_dimensions(line):
    match = re.match(r'(\d+)x(\d+)', line.strip())
    if not match:
        raise ValueError(f"Invalid dimensions format: {line}")
    return int(match.group(1)), int(match.group(2))

def parse_net(line):
    net_name = line.split()[0]
    coords = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
    
    if len(coords) < 2:
        raise ValueError(f"Invalid net format: {line}")
    
    layer = int(coords[0][0])
    start = tuple(map(int, coords[0][1:]))
    end = tuple(map(int, coords[1][1:]))
    return net_name, layer, start, end

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    width, height = parse_dimensions(lines[0])
    router = MazeRouter(width, height)
    
    nets = []
    current_line = 1
    while current_line < len(lines) and lines[current_line].strip():
        line = lines[current_line].strip()
        if line and not line.startswith('#'):
            try:
                net_name, layer, start, end = parse_net(line)
                nets.append((net_name, layer, start, end))
            except ValueError as e:
                print(f"Warning: Skipping invalid net: {e}")
        current_line += 1
    
    obstacles = []
    while current_line < len(lines):
        line = lines[current_line].strip()
        if line and not line.startswith('#'):
            if line.startswith('OBS'):
                match = re.search(r'\((\d+),\s*(\d+)\)', line)
                if match:
                    x, y = map(int, match.groups())
                    obstacles.append((x, y))
                    router.add_obstacle(x, y)
        current_line += 1

    routed_nets = []
    for net_name, layer, start, end in nets:
        path = router.route_net(start, end)
        if path:
            path_with_layer = [(layer, x, y) for x, y in path]
            routed_nets.append((net_name, path_with_layer))

    if routed_nets:
        with open(output_file, 'w') as f:
            for net_name, path in routed_nets:
                if path:
                    path_str = ' '.join(f"({layer}, {x}, {y})" for layer, x, y in path)
                    f.write(f"{net_name} {path_str}\n")
    else:
        open(output_file, 'w').close()

if __name__ == "__main__":
    main()