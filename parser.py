import re

class MazeRouterInput:
    def __init__(self):
        self.grid_width = 0
        self.grid_height = 0
        self.bend_penalty = 0
        self.via_penalty = 0
        self.obstructions = []
        self.nets = []

def parse_maze_router_input(file_path):
    router_input = MazeRouterInput()

    with open(file_path, 'r') as file:
        lines = file.readlines()

    grid_line = lines[0].strip()
    grid_data = list(map(int, grid_line.split(',')))
    router_input.grid_width, router_input.grid_height, router_input.bend_penalty, router_input.via_penalty = grid_data

    for line in lines[1:]:
        line = line.strip()

        if line.startswith("OBS"):
            match = re.match(r"OBS \((\d+), (\d+), (\d+)\)", line)
            if match:
                layer, x, y = map(int, match.groups())
                router_input.obstructions.append((layer, x, y))

        elif line.startswith("net"):
            parts = re.split(r'\s+', line, maxsplit=1)
            if len(parts) == 2:
                net_name, pin_data = parts
                pins = []
                matches = re.findall(r"\((\d+), (\d+), (\d+)\)", pin_data)
                for match in matches:
                    layer, x, y = map(int, match)
                    pins.append({'layer': layer, 'x': x, 'y': y})
                router_input.nets.append({'name': net_name, 'pins': pins})

    return router_input

def validate_router_input(router_input):
    if router_input.grid_width <= 0 or router_input.grid_height <= 0:
        raise ValueError("Grid dimensions must be positive integers.")
    
    if router_input.bend_penalty < 0 or router_input.via_penalty < 0:
        raise ValueError("Penalties must be non-negative.")
    
    for obs in router_input.obstructions:
        layer, x, y = obs
        if x < 0 or y < 0 or x >= router_input.grid_width or y >= router_input.grid_height:
            raise ValueError(f"Invalid obstruction position: ({layer}, {x}, {y}).")
        
    for net in router_input.nets:
        if len(net['pins']) < 2:
            raise ValueError(f"Net '{net['name']}' must have at least two pins.")
        for pin in net['pins']:
            if pin['x'] < 0 or pin['y'] < 0 or pin['x'] >= router_input.grid_width or pin['y'] >= router_input.grid_height:
                raise ValueError(f"Invalid pin position in net '{net['name']}': ({pin['layer']}, {pin['x']}, {pin['y']}).")