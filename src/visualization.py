import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from typing import Dict, List, Tuple

def plot_single_layer(routing_results: Dict[str, Tuple[List[Tuple[int, int, int]], int, int]], 
                     router_input, layer: int, ax, title: str):
    """Plot a single layer view."""
    ax.set_title(title)
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")

    # Set the grid limits
    ax.set_xlim(-0.5, router_input.grid_width - 0.5)
    ax.set_ylim(-0.5, router_input.grid_height - 0.5)

    # Draw grid
    for x in range(router_input.grid_width):
        ax.axvline(x - 0.5, color='gray', linewidth=0.5, linestyle=':')
    for y in range(router_input.grid_height):
        ax.axhline(y - 0.5, color='gray', linewidth=0.5, linestyle=':')
    ax.grid(False)

    # Plot obstacles for this layer
    for obs in router_input.obstructions:
        if obs[0] == layer + 1:  # Convert 0-based layer to 1-based
            ax.add_patch(
                patches.Rectangle(
                    (obs[1] - 0.4, obs[2] - 0.4), 0.8, 0.8,
                    facecolor='red',
                    alpha=0.3
                )
            )

    colors = ['blue', 'green', 'purple', 'orange', 'brown', 'pink']
    
    # Plot nets
    for idx, (net_name, result) in enumerate(routing_results.items()):
        if not result:
            continue
            
        path, _, _ = result
        color = colors[idx % len(colors)]
        
        # Filter segments for this layer
        layer_segments = []
        for i in range(len(path)-1):
            curr = path[i]
            next_point = path[i+1]
            
            # If either point is on this layer, draw the segment
            if curr[0] == layer + 1 or next_point[0] == layer + 1:  # Convert 0-based layer to 1-based
                layer_segments.append((curr, next_point))
                
                # Draw via points
                if curr[0] != next_point[0]:  # Layer change
                    if curr[0] == layer + 1:
                        ax.plot(curr[1], curr[2], 'ro', markersize=8, alpha=0.6)
                    else:
                        ax.plot(next_point[1], next_point[2], 'ro', markersize=8, alpha=0.6)
        
        # Draw segments
        for start, end in layer_segments:
            if start[0] == layer + 1 and end[0] == layer + 1:  # Same layer segment
                ax.plot([start[1], end[1]], [start[2], end[2]], 
                       color=color, linewidth=2, label=net_name if idx == 0 else "")
            else:  # Via connection
                ax.plot([start[1], end[1]], [start[2], end[2]], 
                       color=color, linewidth=2, linestyle=':', alpha=0.5)
        
        # Mark start/end points on this layer
        for point in [path[0], path[-1]]:
            if point[0] == layer + 1:
                ax.plot(point[1], point[2], 'gs', markersize=10, alpha=0.8)

    # Create legend
    legend_elements = [
        patches.Patch(facecolor='red', alpha=0.3, label='Obstacle'),
        Line2D([0], [0], color='blue', label='Net Path'),
        Line2D([0], [0], marker='o', color='r', label='Via',
               markersize=8, linestyle='None'),
        Line2D([0], [0], marker='s', color='g', label='Pin',
               markersize=8, linestyle='None')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

def plot_3d_view(routing_results: Dict[str, Tuple[List[Tuple[int, int, int]], int, int]], 
                router_input, ax):
    """Plot 3D view of the routing."""
    ax.set_title('3D View')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Layer')

    # Set the axis limits
    ax.set_xlim(0, router_input.grid_width)
    ax.set_ylim(0, router_input.grid_height)
    ax.set_zlim(1, 2)
    ax.set_zticks([1, 2])

    # Plot obstacles
    for obs in router_input.obstructions:
        ax.scatter(obs[1], obs[2], obs[0], color="red", s=100, alpha=0.5)

    colors = ['blue', 'green', 'purple', 'orange', 'brown', 'pink']

    # Plot routed nets
    for idx, (net_name, result) in enumerate(routing_results.items()):
        if not result:
            continue
            
        path, _, _ = result
        color = colors[idx % len(colors)]
        x_coords = [p[1] for p in path]
        y_coords = [p[2] for p in path]
        z_coords = [p[0] for p in path]
        
        # Plot path
        ax.plot(x_coords, y_coords, z_coords, color=color, linewidth=2, label=net_name)
        
        # Mark start and end points
        ax.scatter(x_coords[0], y_coords[0], z_coords[0], color=color, s=100, marker='o')
        ax.scatter(x_coords[-1], y_coords[-1], z_coords[-1], color=color, s=100, marker='s')

    ax.legend()

def plot_routed_nets(routing_results: Dict[str, Tuple[List[Tuple[int, int, int]], int, int]], 
                    router_input, output_dir: str):
    """Create separate layer views and 3D view."""
    # Create figure with 3 subplots side by side
    fig = plt.figure(figsize=(15, 5))
    
    # Layer 1 view
    ax1 = fig.add_subplot(131)
    plot_single_layer(routing_results, router_input, 0, ax1, "Layer 1 (M1)")
    
    # Layer 2 view
    ax2 = fig.add_subplot(132)
    plot_single_layer(routing_results, router_input, 1, ax2, "Layer 2 (M2)")
    
    # 3D view
    ax3 = fig.add_subplot(133, projection='3d')
    plot_3d_view(routing_results, router_input, ax3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "layer_views.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)
  
def plot_2d_routed_nets(routing_results, router, ax):
    """Plot 2D view with all layers combined."""
    # Set the grid limits
    ax.set_xlim(-0.5, router.width - 0.5)
    ax.set_ylim(-0.5, router.height - 0.5)

    # Draw grid
    for x in range(router.width):
        ax.axvline(x - 0.5, color='gray', linewidth=0.5, linestyle=':')
    for y in range(router.height):
        ax.axhline(y - 0.5, color='gray', linewidth=0.5, linestyle=':')
    ax.grid(False)

    # Plot obstacles
    for layer in range(router.num_layers):
        for y in range(router.height):
            for x in range(router.width):
                if router.grid[layer][y][x]['obstacle']:
                    ax.add_patch(
                        patches.Rectangle(
                            (x - 0.3, y - 0.3), 0.6, 0.6,
                            edgecolor='red',
                            facecolor='red',
                            alpha=0.5
                        )
                    )

    # Define color and style dictionaries
    colors = {
        "M1": "blue",
        "M2": "yellow",
        "VIA12": "red",
        "ENDPOINT": "green"
    }
    hatch_styles = {
        "M1": "x",
        "M2": "//"
    }

    via_size = 0.4
    horizontal_height = 0.2
    vertical_width = 0.2

    for net_name, path in routing_results.items():
        if not path:
            continue
            
        for i, (layer, x, y) in enumerate(path):
            layer_name = "M1" if layer == 0 else "M2"

            if i == 0 or i == len(path) - 1:
                ax.add_patch(
                    patches.Rectangle(
                        (x - 0.3, y - 0.3), 0.6, 0.6,
                        edgecolor=colors["ENDPOINT"],
                        facecolor="none",
                        linewidth=2
                    )
                )

            if i > 0:
                prev_layer, prev_x, prev_y = path[i - 1]

                if y == prev_y:  # Horizontal segment
                    x_min, x_max = sorted([x, prev_x])
                    seg_width = x_max - x_min
                    seg_color = colors[layer_name] if layer == prev_layer else colors["VIA12"]
                    seg_hatch = hatch_styles[layer_name] if layer == prev_layer else None

                    rect = patches.Rectangle(
                        (x_min, y - horizontal_height/2),
                        seg_width,
                        horizontal_height,
                        edgecolor=seg_color,
                        facecolor='none' if seg_hatch else seg_color,
                        hatch=seg_hatch,
                        linewidth=2 if layer == prev_layer else 1
                    )
                    ax.add_patch(rect)

                    if layer != prev_layer:
                        via_rect = patches.Rectangle(
                            (x - via_size/2, y - via_size/2), via_size, via_size,
                            edgecolor=colors["VIA12"],
                            facecolor=colors["VIA12"],
                            linewidth=1
                        )
                        ax.add_patch(via_rect)

                elif x == prev_x:  # Vertical segment
                    y_min, y_max = sorted([y, prev_y])
                    seg_height = y_max - y_min
                    seg_color = colors[layer_name] if layer == prev_layer else colors["VIA12"]
                    seg_hatch = hatch_styles[layer_name] if layer == prev_layer else None

                    rect = patches.Rectangle(
                        (x - vertical_width/2, y_min),
                        vertical_width,
                        seg_height,
                        edgecolor=seg_color,
                        facecolor='none' if seg_hatch else seg_color,
                        hatch=seg_hatch,
                        linewidth=2 if layer == prev_layer else 1
                    )
                    ax.add_patch(rect)

                    if layer != prev_layer:
                        via_rect = patches.Rectangle(
                            (x - via_size/2, y - via_size/2), via_size, via_size,
                            edgecolor=colors["VIA12"],
                            facecolor=colors["VIA12"],
                            linewidth=1
                        )
                        ax.add_patch(via_rect)

    # Create legend handles
    legend_elements = [
        Line2D([0], [0], color='blue', lw=2, label='Layer 1 (M1)'),
        Line2D([0], [0], color='yellow', lw=2, label='Layer 2 (M2)'),
        patches.Rectangle((0,0),1,1, edgecolor='red', facecolor='red', label='VIA'),
        patches.Rectangle((0,0),1,1, edgecolor='green', facecolor='none', lw=2, label='Net Points'),
        patches.Rectangle((0,0),1,1, facecolor='red', alpha=0.5, label='Obstacle')
    ]

    ax.legend(handles=legend_elements, loc='upper right')
    plt.grid(False)