import math, copy
import numpy as np


class Vector2:
    """
    2D vector, used mainly for texture coordiantes (U V)
    """

    def __init__(self, u: float, v: float):
        self.u = u
        self.v = v
        self.w = 1 - self.u - self.v

    def norm(self):
        """
        :return: Normalized copy of self
        """
        return self / abs(self)

    def dot(self, other: "Vector2") -> float:
        """
        :param other: Vector2
        :return: Dot product of self and other
        """
        return self.u * other.u + self.v * other.v

    def __repr__(self):
        return f"<{self.u : .1f}, {self.v : .1f}>"

    def __str__(self):
        return f"<{self.u : .1f}, {self.v : .1f}>"

    def __sub__(self, other: "Vector2"):
        return Vector2(self.u - other.u, self.v - other.v)

    def __add__(self, other: "Vector2"):
        return Vector2(self.u + other.u, self.v + other.v)

    def __mul__(self, other: float):
        new = copy.copy(self)
        new.u *= other
        new.v *= other
        return new

    def __truediv__(self, other: float):
        new = copy.copy(self)
        new.u /= other
        new.v /= other
        return new

    def __abs__(self):
        """
        :return: Norm of self
        """
        return math.sqrt(self.u**2 + self.v**2)


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.t = self.x
        self.u = self.y
        self.v = self.z
        self.arr = [self.x, self.y, self.z]

    def norm(self):
        """
        :return: Normalized copy of self
        """
        return self / abs(self)

    def dot(self, other: "Vector") -> float:
        """
        :param other: Vector
        :return: Dot product of self and other
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector") -> "Vector":
        """
        :param other: Vector
        :return: Cross product of self and other
        """
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector(x, y, z)

    def calcCoord(self, st: "Vector", t: float):
        """
        :param st: Starting point
        :param t: Parameterization
        :return: 3D coordinates corresponding to parameterization t if self starts at st
        """
        parallel = self - st
        coord = st + self * t
        return coord

    def __repr__(self):
        return f"<{self.x : .1f}, {self.y : .1f}, {self.z : .1f}>"

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other):
        new = copy.copy(self)
        new.x *= other
        new.y *= other
        new.z *= other
        return new

    def __truediv__(self, other):
        new = copy.copy(self)
        new.x /= other
        new.y /= other
        new.z /= other
        return new

    def __abs__(self):
        """
        :return: Norm of self
        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


class Triangle:
    """
    Object representing a triangle made up of 3 Vectors: a, b, and c

    """

    def __init__(self, coords):
        self.a = coords[0]
        self.b = coords[1]
        self.c = coords[2]
        self.at = None
        self.bt = None
        self.ct = None
        self.normal = None
        self.collisions = []
        self.textureCoords = []

    def intersect(self, ray_start, ray_vec) -> tuple[bool, Vector]:
        """
        Detect intersection between this triangle and ray_vec originating from ray_start

        :param ray_start: Vector indicating the origin of the ray
        :param ray_vec: Vector indicating direction of the ray
        :return: bool indicating if it was a hit, and vector indicating parameterized t, and local coordinates u, v
        """
        # define a null intersection
        # null_inter = [None, None, None]  # np.array([np.nan, np.nan, np.nan])
        null_inter = Vector(None, None, None)
        # ray_start = np.asarray(ray_start)
        # ray_vec = np.asarray(ray_vec)

        # break down triangle into the individual points
        v1, v2, v3 = self.a, self.b, self.c
        eps = 0.000001

        # compute edges
        edge1 = v2 - v1
        edge2 = v3 - v1
        # pvec = np.cross(ray_vec, edge2)
        pvec = ray_vec.cross(edge2)
        det = edge1.dot(pvec)

        if abs(det) < eps:  # no intersection
            # print('fail1')
            return False, null_inter
        inv_det = 1.0 / det
        tvec = ray_start - v1
        u = tvec.dot(pvec) * inv_det
        # print(u)
        if u < 0.0 or u > 1.0:  # if not intersection
            # print('fail2')
            return False, null_inter

        qvec = tvec.cross(edge1)
        v = ray_vec.dot(qvec) * inv_det
        if v < 0.0 or u + v > 1.0:  # if not intersection
            #  print('fail3')
            return False, null_inter

        t = edge2.dot(qvec) * inv_det
        if t < eps:
            #   print('fail4')
            return False, null_inter

        return True, Vector(t, u, v)

    def __repr__(self):
        return f"Tri[{self.a}, {self.b}, {self.c}]"


class TriObject:
    def __init__(
        self, name: str, triangles: list[Triangle], points: list[Vector], critical: bool
    ):
        self.name = name
        self.triangles = triangles
        self.points = points
        self.bounding_box = None
        self.critial = critical
        self.texture = None

    def initTexture(self, size):
        self.texture = [[(0, 0, 0, 0) for i in range(size)] for j in range(size)]

    def calcBoundingBox(self):
        minX = min([vec.x for vec in self.points])
        minY = min([vec.y for vec in self.points])
        minZ = min([vec.z for vec in self.points])
        maxX = max([vec.x for vec in self.points])
        maxY = max([vec.y for vec in self.points])
        maxZ = max([vec.z for vec in self.points])
        minPt = Vector(minX, minY, minZ)
        maxPt = Vector(maxX, maxY, maxZ)
        self.bounding_box = [minPt, maxPt]

    def __repr__(self):
        return f"[{self.name.upper()}: {len(self.triangles)} tris]"
