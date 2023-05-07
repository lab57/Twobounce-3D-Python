import os
from GeometricObjects import Vector2
#f"{hit.obj.name}\t{i}\t{hit.u}\t{hit.v}\t{hit.tri.at.u}\t{hit.tri.at.v}\t{hit.tri.bt.u}\t{hit.tri.bt.v}\t{hit.tri.ct.u}\t{hit.tri.ct.v}\n")

DIR = "./output"


def fileParser(f, objDict=None):
    if objDict is None:
        objDict = { }
    for line in f:
        spl = line.split("\t")
        # print(spl)
        a = Vector2(float(spl[4]), float(spl[5]))
        b = Vector2(float(spl[6]), float(spl[7]))
        c = Vector2(float(spl[8]), float(spl[9]))
        res_vec = a * (1 - float(spl[2]) - float(spl[3])) + b * float(spl[2]) + c * float(spl[3])
        
        print("res", res_vec)


# iterate over files in
# that directory


# for filename in os.scandir(DIR):
#     if filename.name[0] == ".":
#         continue
#     with open(f"{DIR}/{filename.name}", "r") as f:
#         print(filename.name)
#         res = fileParser(f)
with open(f"./output/output_test.txt", "r") as f:

    fileParser(f)