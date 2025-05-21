import sys
import os
import argparse
from parser import MazeRouterInput
from router import MazeRouter
from visualization import plot_routed_nets

def parse_arguments():
    parser = argparse.ArgumentParser(description='Maze Router with configurable costs')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--via-penalty', type=int, default=None,
                      help='Cost penalty for vias (layer changes). If not specified, uses value from input file.')
    parser.add_argument('--wrong-direction-penalty', type=int, default=None,
                      help='Cost penalty for routing in non-preferred direction. If not specified, uses value from input file.')
    return parser.parse_args()

def write_routing_results(output_file: str, routing_results: dict):
    with open(output_file, 'w') as f:
        for net_name, result in routing_results.items():
            if result:
                path, wire_length, via_count = result
                path_str = ' '.join(f"({layer}, {x}, {y})" for layer, x, y in path)
                f.write(f"{net_name} {path_str}\n")
                print(f"Successfully routed {net_name}")
                print(f"Wire length: {wire_length}, Vias: {via_count}")
            else:
                print(f"Warning: Could not route {net_name}")

def main():
    args = parse_arguments()

    # Parse input file and create router input
    router_input = MazeRouterInput.from_file(args.input_file)

    # Create router with optional penalty overrides
    router = MazeRouter(
        router_input,
        via_penalty=args.via_penalty,
        wrong_direction_penalty=args.wrong_direction_penalty
    )
    
    # Print penalty values being used
    print(f"\nUsing penalties:")
    print(f"Via penalty: {router.via_penalty}")
    print(f"Wrong direction penalty: {router.wrong_direction_penalty}\n")
    
    routing_results = {}
    for net in router_input.nets:
        result = router.route_net(net)
        if result:
            routing_results[net['name']] = result

    # Write output file
    write_routing_results(args.output_file, routing_results)
    
    # Generate visualizations
    output_dir = os.path.dirname(args.output_file)
    plot_routed_nets(routing_results, router_input, output_dir)
    print(f"\nVisualizations saved in {output_dir}")

if __name__ == "__main__":
    main()