from typing import List, Dict, Tuple
import re

class MazeRouterInput:
    def __init__(self, grid_width: int, grid_height: int, via_penalty: int, wrong_direction_penalty: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.via_penalty = via_penalty
        self.wrong_direction_penalty = wrong_direction_penalty
        self.nets: List[Dict] = []
        self.obstructions: List[Tuple[int, int, int]] = []

    @classmethod
    def from_file(cls, filename: str) -> 'MazeRouterInput':
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Parse first line: grid dimensions and costs
        dimensions = list(map(int, lines[0].strip().split(',')))
        width, height = dimensions[0], dimensions[1]
        via_penalty = dimensions[2]
        wrong_direction_penalty = dimensions[3]

        router_input = cls(width, height, via_penalty, wrong_direction_penalty)

        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('OBS'):
                # Parse obstacle format: OBS (layer, x, y)
                obs_match = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
                if obs_match:
                    layer, x, y = map(int, obs_match[0])
                    router_input.obstructions.append((layer, x, y))
            else:
                # Parse net format: netN (layer1, x1, y1) (layer2, x2, y2) ...
                parts = line.split()
                net_name = parts[0]
                pins = []
                pin_matches = re.findall(r'\((\d+),\s*(\d+),\s*(\d+)\)', line)
                for match in pin_matches:
                    layer, x, y = map(int, match)
                    pins.append({'layer': layer, 'x': x, 'y': y})
                if pins:
                    router_input.nets.append({
                        'name': net_name,
                        'pins': pins
                    })

        return router_input 