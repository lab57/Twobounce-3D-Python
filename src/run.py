from twobounce import *

'''
 ___  ____                                   ____  _____
|__ \|  _ \                                 |___ \|  __ \
   ) | |_) | ___  _   _ _ __   ___ ___       __) | |  | |
  / /|  _ < / _ \| | | | '_ \ / __/ _ |      |__ <| |  | |
 / /_| |_) | (_) | |_| | | | | (_|  __/      ___) | |__| |
|____|____/ \___/ \__,_|_| |_|\___\___|     |____/|_____/
                  labarrett@umass.edu
'''

N = 10_000_000

if __name__ == "__main__":
    initalize()
    
    print("Loading geometry")
    load = ObjLoader("./")
    objs, tris = load.load("untitled.obj")
    print(f"Done")
    print(f"{len(objs)} objects, {len(tris)} polygons\n")
    
    t1 = time.time()
    print()
    print("Starting twobounce")
    ans = multicoreIterateMap(objs, n=N)
    print("Finished")
    print(f"Simulared {N} rays using {CPU_COUNT} cores in {time.time() - t1: .2f}s")
    # print(len(ans))
