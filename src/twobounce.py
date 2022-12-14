import copy
import math
import multiprocessing as mp
import time
from functools import partial
from pprint import pprint
import random as r
from math import sin, cos

# import numpy as np

CPU_COUNT = mp.cpu_count() - 1

# pprint("")

printf = print


def print(s=""):
    """
    Perhaps bad practice, but I do not care. Override print() function to print timestamp at the front.
    :param s: String to print
    :return: void
    """
    st = time.gmtime(time.time())
    st = time.strftime("%H:%M:%S", st)
    printf(f"{st} - {s}")


def initalize():
    printf(r'''
 ___  ____                                   ____  _____
|__ \|  _ \                                 |___ \|  __ \
   ) | |_) | ___  _   _ _ __   ___ ___       __) | |  | |
  / /|  _ < / _ \| | | | '_ \ / __/ _ |      |__ <| |  | |
 / /_| |_) | (_) | |_| | | | | (_|  __/      ___) | |__| |
|____|____/ \___/ \__,_|_| |_|\___\___|     |____/|_____/
Luc Barrett, Nov. 2022
        ''')
    print(f"CPU Core Count: {CPU_COUNT}\n")


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.arr = [self.x, self.y, self.z]
    
    def norm(self):
        """
        :return: Normalized copy of self
        """
        return self / abs(self)
    
    def dot(self, other: 'Vector') -> float:
        """
        :param other: Vector
        :return: Dot product of self and other
        """
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vector') -> 'Vector':
        """
        :param other: Vector
        :return: Cross product of self and other
        """
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vector(x, y, z)
    
    def calcCoord(self, st: 'Vector', t: float):
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
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)


class Triangle:
    """
    Object representing a triangle made up of 3 Vectors: a, b, and c

    """
    
    def __init__(self, coords):
        self.a = coords[0]
        self.b = coords[1]
        self.c = coords[2]
        self.normal = None
    
    def intersect(self, ray_start, ray_vec) -> tuple[bool, Vector]:
        """
        Detect intersection between this triangle and ray_vec originating from ray_start
        
        :param ray_start: Vector indicating the origin of the ray
        :param ray_vec: Vector indicating direction of the ray
        :return: bool indicating if it was a hit, and vector indicating parameterized t, and local coordinates u, v
        """
        # define a null intersection
        #null_inter = [None, None, None]  # np.array([np.nan, np.nan, np.nan])
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
    def __init__(self, name: str, triangles: list[Triangle], points: list[Vector], critical: bool):
        self.name = name
        self.triangles = triangles
        self.points = points
        self.bounding_box = None
        self.critial = critical
    
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


class ObjLoader:
    def __init__(self, path):
        """
        :param path: Path to folder containing object files. Ex: "./"
        """
        self.path = path
    
    def load(self, filename) -> tuple[list[TriObject], list[Triangle]]:
        """
        :param filename: Name of file in path, ex: test_file.obj
        :return: Tuple containing list of objects and full list of triangles
        """
        verticies = []
        objects = []
        triangles = []
        normals = []
        with open(self.path + filename, "r") as f:
            curObject = None
            for line in f.readlines():
                if line[0] in ['o', 'g']:
                    name = line.split(" ")[1].strip("\n")
                    args = name.split("-")
                    
                    # print(f"Loading {name}")
                    curObject = TriObject(name, [], [], "crit" in args)
                    objects.append(curObject)
                if line[0] == "#":
                    continue
                if line[0] == "v" and line[1] == " ":
                    split = line.split(" ")
                    verticies.append(Vector(float(split[1]), float(split[2]), float(split[3])))
                    curObject.points.append(Vector(float(split[1]), float(split[2]), float(split[3])))
                if line[0] == "v" and line[1] == "n":
                    split = line.split(" ")
                    normals.append(Vector(float(split[1]), float(split[2]), float(split[3])))
                if line[0] == 'f':
                    split = line.split(" ")
                    v1 = split[1].split("/")
                    v2 = split[2].split("/")
                    v3 = split[3].split("/")
                    triangle = Triangle((
                        verticies[int(v1[0]) - 1],
                        verticies[int(v2[0]) - 1],
                        verticies[int(v3[0]) - 1]
                    ))
                    triangle.normal = normals[int(v1[2]) - 1]
                    curObject.triangles.append(triangle)
                    triangles.append(triangle)
        # print(f"{len(triangles)} polygons loaded")
        return objects, triangles


class Hit:
    def __init__(self, start: Vector, vec: Vector, t: float, tri: Triangle, obj: TriObject, didHit: bool):
        self.start = start
        self.vec = vec
        self.t = t
        self.tri = tri
        self.obj = obj
        self.hit = didHit
        self.n = None
        self.hitDict = {
            "Start point"     : self.start,
            "Direction Vector": self.vec,
            "t"               : self.t,
            "Hit object"      : self.obj,
            # "Hit triangle"    : self.tri
        }
        if self.obj:
            self.hitDict['Collison'] = self.coord()
    
    def coord(self):
        return self.vec.calcCoord(self.start, self.t)
    
    def __bool__(self):
        if self.hit is None:
            return False
        return self.hit
    
    def __repr__(self):
        if (self.obj):
            return f"<HitInfo - hit {self.obj.name}>"
        else:
            return f"<HitInfo - hit None>"


def checkIntersections(objects: list[TriObject], st: Vector, ray: Vector) -> Hit:
    """
    Finds first intersection of ray starting at st with any object
    
    Future optimization options:
        - Check for bounding box intersection first
        - Organize objects into tree (?)
    :param objects: list of Objects
    :param st: starting Vector
    :param ray: direction Vector
    :return: Hit class containing hit info
    """
    min_t = math.inf
    hitInfo = [st, ray, None, None, None, None]
    for obj in objects:
        for tri in obj.triangles:
            hit, vec = tri.intersect(st, ray)
            if hit and vec.x < min_t:
                min_t = vec.x
                hitInfo[2] = min_t
                hitInfo[3] = tri
                hitInfo[4] = obj
                hitInfo[5] = hit
    
    return Hit(*hitInfo)


def twobounce(objects: list[TriObject], st: Vector, ray: Vector) -> tuple[Hit, Hit]:
    """
    :param objects: List of objects
    :param st: Start of ray
    :param ray: Direction of ray
    :return: (res1, res2) where res1 is Hit information of first collision, res2 is Hit information of second collision
    """
    objects = copy.copy(objects)
    # One bounce
    result = checkIntersections(objects, st, ray)
    if not result.hit:
        return (result, Hit(None, None, None, None, None, False))
    coords = result.coord()  # coords becomes new start
    
    # two bounce
    n = result.tri.normal  # normal vector to triangle
    # new_r = ray - n * 2 * (ray.dot(n))  # new direction vector from reflection
    new_r = ray - n * ((ray * 2).dot(n) / (abs(n) * abs(n)))
    # objects.remove(result.obj)  # remove originating structure from objects to avoid floating point error causing hit
    result2 = checkIntersections(objects, coords, new_r)
    return result, result2


def linspace(start, stop, n):
    """
    Copy of numpys linspace, with integer divide
    :param start: start value
    :param stop: end value
    :param n: how many divisions between start and end
    :return: generator for values (can be casted to list)
    """
    if n == 1:
        yield stop
        return
    h = (stop - start) // (n - 1)
    for i in range(n):
        yield start + h * i


def writeToFile(file, res):
    for i, hit in enumerate(res):
        if not hit.hit:
            return
        else:
            file.write(f"{hit.n}\t{i}\t{hit.obj.name :>20}\t{hit.start}\t{hit.coord()}\n")


def iterateStartVecs(n0, n, N, objs, results=None, shouldPrint=False, pid=0) -> dict:
    """
    Iterate over source vectors from n0 to n
    :param n0: starting n
    :param n: ending n
    :param objs: list of objects
    :param results: deprecated? (default: none)
    :param shouldPrint: should print precentage (default: false)
    :param pid: process id (default: 0)
    :return: void?
    """
    LENGTH = 500  # length of "pencil"
    if (results is None):
        results = []
    
    stats = {
        "num_rays"    : 0,
        "hit_obj"     : 0,
        "hit_critical": 0,
    }
    
    prec = 0  # percent tracker
    print(f"PID {pid} starting (n -> {n0}-{n})")
    outFile = open(f"./output/output_{pid}.txt", "w")
    for t in range(n0, n):
        if pid == 0:  # percentage, not the most accurate and should change at some point
            if t % (n // 20) == 0 and t != 0:
                prec += 1
                print(f"{prec * 5}%")
        
        #start = Vector(0, 250 - t * LENGTH / N, 50)
        start = Vector(0, 0, 50)
        theta = r.random() * 2 * math.pi
        phi = r.random() * math.pi
        
        #dir = Vector(sin(phi) * cos(theta), sin(phi) * sin(theta), cos(phi))  # TODO fix
        dir = Vector(cos(theta), sin(theta), 0)
        res = twobounce(objs, start, dir)
        res[0].n = t
        res[1].n = t
        ##########################################################
        # Get stats
        # Track rays that hit critical geometry at any point in their path
        # or that hit objects at any point in their path
        thisHits = 0
        thisCrits = 0
        for hit in res:
            if hit.obj and hit.obj.critial:
                thisCrits += 1
            if hit.hit:
                thisHits += 1
        stats["hit_critical"] += 1 if thisCrits else 0
        stats["hit_obj"] += 1 if thisHits else 0
        stats["num_rays"] += 1
        
        results += res
        if thisCrits:
            writeToFile(outFile, res)

    outFile.close()
    print(f"PID {pid} done")
    if results is not None:
        return stats


def multicoreIterateMap(objs, N) -> list[dict]:
    division = N // CPU_COUNT
    divisionList = [(i * division, (i + 1) * division, N, objs, None, None, i) for i in range(CPU_COUNT)]
    with mp.Pool(CPU_COUNT) as pool:
        res = pool.starmap(iterateStartVecs, divisionList)
    return res


def _multicoreIterate(objs, n=1_000_000):
    """
    DEPRECATED, use multicoreIterateMap instead
    Create CPU_COUNT processes that will work on a division of the n events, calls iterateStartVecs
    :param objs: List of objects
    :param n: Number of events
    :return: void
    """
    division = n // CPU_COUNT
    processes = []
    results = []
    
    otherArgs = (objs, None)
    for i in range(CPU_COUNT):
        shouldPrint = not i  # only true on i=0
        p = mp.Process(target=iterateStartVecs, args=(i * division, (i + 1) * division, objs, results, shouldPrint, i))
        processes.append(p)
        p.start()
    for proc in processes:
        proc.join()
    
    # for process in processes:
    # process.join()
    return results


'''
TODO checklist:
_ Bounding box? -> May not be needed, unsure until more complex geometry is implemented
_ Change ObjLoader -> in progress -> Done
_ Make hit information class -> Done
_ Make method to check interesctions and calculate reflections -> in progress -> Done
_ Impelment emitter and number of vectors -> in progress -> Done
_ Multiprocessing? -> Done

'''
