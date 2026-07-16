
import numpy as np
import matplotlib.pyplot as plt


class TernaryDiagram:
    """Simple ternary diagram plotter for 3-component compositions."""

    def __init__(self, labels):
        """Create a ternary diagram with 3 axis labels.
        
        labels: list of 3 strings for the vertex labels
        """
        if len(labels) != 3:
            raise ValueError('TernaryDiagram requires exactly 3 labels')
        self.labels = labels
        self._setup_axes()

    def _setup_axes(self):
        """Set up the ternary diagram axes."""
        self.ax = plt.gca()
        # Equilateral triangle vertices
        # Vertex 0 (top), Vertex 1 (bottom-left), Vertex 2 (bottom-right)
        self.vertices = np.array([
            [0.5, np.sqrt(3) / 2],   # top
            [0.0, 0.0],               # bottom-left
            [1.0, 0.0],               # bottom-right
        ])
        
        # Draw the 20%-spaced composition grid before the border and data.
        # A constant value for each of the three barycentric coordinates gives
        # one of the horizontal/diagonal families in the ternary triangle.
        self._add_gridlines()

        # Draw triangle border
        triangle = plt.Polygon(self.vertices, fill=False, edgecolor='black', linewidth=1.5,
                               zorder=1)
        self.ax.add_patch(triangle)
        
        # Set axis limits and aspect
        self.ax.set_xlim(-0.05, 1.05)
        self.ax.set_ylim(-0.05, np.sqrt(3) / 2 + 0.05)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        # Add vertex labels
        self.ax.text(self.vertices[0][0], self.vertices[0][1] + 0.03, self.labels[0],
                     ha='center', va='bottom', fontsize=12, fontweight='bold')
        self.ax.text(self.vertices[1][0] - 0.05, self.vertices[1][1], self.labels[1],
                     ha='right', va='center', fontsize=12, fontweight='bold')
        self.ax.text(self.vertices[2][0] + 0.05, self.vertices[2][1], self.labels[2],
                     ha='left', va='center', fontsize=12, fontweight='bold')
        
        # Add tick marks and labels along edges
        self._add_ticks()

    def _add_gridlines(self):
        """Draw horizontal and diagonal grid lines at 20% composition intervals."""
        self.gridlines = []
        n_intervals = 5
        for component in range(3):
            other_components = [index for index in range(3) if index != component]
            for i in range(1, n_intervals):
                fraction = i / n_intervals
                start = np.zeros(3)
                end = np.zeros(3)
                start[component] = fraction
                end[component] = fraction
                start[other_components[0]] = 1 - fraction
                end[other_components[1]] = 1 - fraction
                start_cart = self._to_cartesian(start)
                end_cart = self._to_cartesian(end)
                line, = self.ax.plot(
                    [start_cart[0], end_cart[0]],
                    [start_cart[1], end_cart[1]],
                    color='0.8', linewidth=0.6, zorder=0,
                )
                self.gridlines.append(line)

    def _add_ticks(self):
        """Add tick marks along each edge."""
        n_ticks = 5
        for edge in range(3):
            v_start = self.vertices[edge]
            v_end = self.vertices[(edge + 1) % 3]
            for i in range(1, n_ticks):
                t = i / n_ticks
                point = v_start + t * (v_end - v_start)
                # Tick mark
                perp = np.array([-(v_end[1] - v_start[1]), v_end[0] - v_start[0]])
                perp = perp / np.linalg.norm(perp) * 0.015
                self.ax.plot([point[0] - perp[0], point[0] + perp[0]],
                            [point[1] - perp[1], point[1] + perp[1]],
                            'k-', linewidth=0.5)

    def _to_cartesian(self, point):
        """Convert ternary (barycentric) coordinates to Cartesian."""
        a, b, c = point[0], point[1], point[2]
        x = a * self.vertices[0][0] + b * self.vertices[1][0] + c * self.vertices[2][0]
        y = a * self.vertices[0][1] + b * self.vertices[1][1] + c * self.vertices[2][1]
        return np.array([x, y])

    def plot(self, points, **kwargs):
        """Draw a line between two points on the ternary diagram.
        
        points: list of two 3-tuples [point1, point2]
        """
        if len(points) != 2:
            raise ValueError('plot() requires exactly 2 points')
        p1_cart = self._to_cartesian(points[0])
        p2_cart = self._to_cartesian(points[1])
        self.ax.plot([p1_cart[0], p2_cart[0]], [p1_cart[1], p2_cart[1]], **kwargs)

    def annotate(self, text, position, **kwargs):
        """Add a text annotation at a position on the ternary diagram.
        
        position: list containing a 3-tuple of ternary coordinates (e.g., [norm([a,b,c])])
        """
        # Handle list-wrapped position (as used by phase plugins)
        if isinstance(position, list) and len(position) == 1 and isinstance(position[0], (list, tuple, np.ndarray)):
            position = position[0]
        cart = self._to_cartesian(position)
        default_kwargs = {'ha': 'center', 'va': 'center', 'fontsize': 10}
        default_kwargs.update(kwargs)
        offset_points = default_kwargs.pop('offset_points', None)
        if offset_points is not None:
            return self.ax.annotate(
                text, (cart[0], cart[1]), xytext=offset_points,
                textcoords='offset points', **default_kwargs,
            )
        self.ax.text(cart[0], cart[1], text, **default_kwargs)

    def scatter(self, points_list, **kwargs):
        """Plot scatter points on the ternary diagram.
        
        points_list: list of 3-tuples (ternary coordinates)
        """
        if not points_list:
            return
        xs = []
        ys = []
        for point in points_list:
            cart = self._to_cartesian(point)
            xs.append(cart[0])
            ys.append(cart[1])
        self.ax.scatter(xs, ys, **kwargs)
