from twobounce import *
from texturing import *

load = ObjLoader("/Users/lucb/Desktop/Research/3D_twobounce/PythonTest/")

objs, tris = load.load("textureTest")
st = Vector(0, -5, 0)
dir = Vector(0, 1, .1)
twobounce(objs, st, dir)
for ob in objs:
    print(ob.texture)
