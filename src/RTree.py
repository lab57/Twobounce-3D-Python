import math


class BoundingBox:
    def __init__(self, min_point, max_point):
        self.min_point = min_point
        self.max_point = max_point

    def intersects(self, origin, direction):
        t1 = (self.min_point[0] - origin[0]) / direction[0]
        t2 = (self.max_point[0] - origin[0]) / direction[0]
        t3 = (self.min_point[1] - origin[1]) / direction[1]
        t4 = (self.max_point[1] - origin[1]) / direction[1]
        t5 = (self.min_point[2] - origin[2]) / direction[2]
        t6 = (self.max_point[2] - origin[2]) / direction[2]

        tmin = max(min(t1, t2), min(t3, t4), min(t5, t6))
        tmax = min(max(t1, t2), max(t3, t4), max(t5, t6))

        return tmax > max(tmin, 0)


class RTreeNode:
    def __init__(self, bounding_box, triangles=None, children=None):
        self.bounding_box = bounding_box
        self.triangles = triangles if triangles is not None else []
        self.children = children if children is not None else []


class RTree:
    def __init__(self, triangles, max_triangles_per_leaf=8):
        self.root = self.build_tree(triangles, max_triangles_per_leaf)

    def build_tree(self, triangles, max_triangles_per_leaf):
        if len(triangles) <= max_triangles_per_leaf:
            min_point, max_point = self.compute_bounds(triangles)
            bounding_box = BoundingBox(min_point, max_point)
            return RTreeNode(bounding_box, triangles=triangles)

        # Choose an axis to split along
        axis = self.choose_split_axis(triangles)

        # Sort triangles along the chosen axis
        triangles.sort(key=lambda t: t.a.arr[axis])

        # Split triangles into two halves
        mid = len(triangles) // 2
        left_triangles = triangles[:mid]
        right_triangles = triangles[mid:]

        left_child = self.build_tree(left_triangles, max_triangles_per_leaf)
        right_child = self.build_tree(right_triangles, max_triangles_per_leaf)

        min_point = [
            min(
                left_child.bounding_box.min_point[i],
                right_child.bounding_box.min_point[i],
            )
            for i in range(3)
        ]
        max_point = [
            max(
                left_child.bounding_box.max_point[i],
                right_child.bounding_box.max_point[i],
            )
            for i in range(3)
        ]
        bounding_box = BoundingBox(min_point, max_point)

        return RTreeNode(bounding_box, children=[left_child, right_child])

    def compute_bounds(self, triangles):
        min_point = [math.inf] * 3
        max_point = [-math.inf] * 3

        for triangle in triangles:
            for vertex in [triangle.a, triangle.b, triangle.c]:
                for i in range(3):
                    min_point[i] = min(min_point[i], vertex.arr[i])
                    max_point[i] = max(max_point[i], vertex.arr[i])

        return min_point, max_point

    def choose_split_axis(self, triangles):
        extents = []
        for axis in range(3):
            min_coord, max_coord = zip(
                *[(t.a.arr[axis], t.c.arr[axis]) for t in triangles]
            )
            extents.append(max(max_coord) - min(min_coord))
        return extents.index(max(extents))

    def query_ray(self, origin, direction):
        return self._query_ray_recursive(self.root, origin, direction)

    def _query_ray_recursive(self, node, origin, direction):
        if not node.bounding_box.intersects(origin, direction):
            return []

        if node.children:
            result = []
            for child in node.children:
                result.extend(self._query_ray_recursive(child, origin, direction))
            return result
        else:
            return node.triangles


if __name__ == "__main__":
    triangles = []  # List of Triangle objects
    rtree = RTree(triangles)
    origin = [0, 0, 0]
    direction = [1, 1, 1]
    intersected_triangles = rtree.query_ray(origin, direction)
    intersected_triangles
