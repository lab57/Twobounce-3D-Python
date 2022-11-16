from twobounce import TriObject
from src.utilities import Triangle, Vector
from utilities import Vector2

TEXTURE_SIZE = 25  # px


class ObjLoader:
    """
    Loader for .obj files
    """
    
    def __init__(self, path):
        """
        :param path: Path to folder containing object files. Ex: "./"
        """
        self.path = path
    
    def makeMtlFiles(self, objs: list[TriObject], filename):
        with open(self.path + filename + "_textured.mtl", "w") as file:
            for obj in objs:
                file.write(f"newmtl {obj.name}_mtl\n")
                st = f"""Ns 250.000000
Ka 1.000000 1.000000 1.000000
Kd 0.097925 0.065680 0.800000
Ks 0.500000 0.500000 0.500000
Ke 0.000000 0.000000 0.000000
Ni 1.450000
d 1.000000
illum 2
map_Kd {self.path}textures/{obj.name}_mtl.png
"""
                file.write(st)
    
    def load(self, filename) -> tuple[list[TriObject], list[Triangle]]:
        """
        :param filename: Name of file in path, ex: test_file.obj
        :return: Tuple containing list of objects and full list of triangles
        """
        verticies = []
        objects = []
        triangles = []
        normals = []
        textures = []
        with open(self.path + filename + ".obj", "r") as f:
            with open(self.path + filename + "_textured.obj", "w") as f_new:  # TODO add mtl linker
                f_new.write(f"mtlib {filename}_textured.mtl\n")
                curObject = None
                for line in f.readlines():
                    if line[0] in ['o', 'g']:
                        name = line.split(" ")[1].strip("\n")
                        args = name.split("-")
                        
                        # print(f"Loading {name}")
                        curObject = TriObject(name, [], [], "crit" in args)
                        curObject.initTexture(TEXTURE_SIZE)
                        objects.append(curObject)
                    if line[0:6] == "mtllib":
                        continue
                    if line[0] == "#":
                        continue
                    if line[0] == "v" and line[1] == " ":  # verticies
                        split = line.split(" ")
                        verticies.append(Vector(float(split[1]), float(split[2]), float(split[3])))
                        curObject.points.append(Vector(float(split[1]), float(split[2]), float(split[3])))
                    if line[0] == "v" and line[1] == "n":  # normals
                        split = line.split(" ")
                        normals.append(Vector(float(split[1]), float(split[2]), float(split[3])))
                    if line[0] == "v" and line[1] == "t":  # textures
                        split = line.split(" ")
                        textures.append(Vector2(float(split[1]), float(split[2])))
                    if line[0] == 'f':
                        f_new.write(f"usemtl {name}_mtl\n")
                        split = line.split(" ")
                        v1 = split[1].split("/")
                        v2 = split[2].split("/")
                        v3 = split[3].split("/")
                        triangle = Triangle((
                            verticies[int(v1[0]) - 1],
                            verticies[int(v2[0]) - 1],
                            verticies[int(v3[0]) - 1]
                        ))
                        
                        # texture verticies
                        triangle.at = textures[int(v1[1]) - 1]
                        triangle.bt = textures[int(v2[1]) - 1]
                        triangle.ct = textures[int(v3[1]) - 1]
                        
                        triangle.normal = normals[int(v1[2]) - 1]
                        curObject.triangles.append(triangle)
                        triangles.append(triangle)
                    f_new.write(line)
        # print(f"{len(triangles)} polygons loaded")
        
        self.makeMtlFiles(objects, filename)
        
        return objects, triangles
