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

N = 100_000


def printResults(stats: list[dict]) -> None:
    """
    Print the statistical results from the run
    Currently prints precetnage of rays that hit critical geometry at either of their two contact points
    and precent that hit any geometry
    :param stats: list of statistic dictionarys returned by twobounce
    :return: None
    """
    totalRays = 0
    hitCrit = 0
    hitObj = 0
    for stat in stats:
        totalRays += stat['num_rays']
        hitCrit += stat['hit_critical']
        hitObj += stat['hit_obj']
    
    print(f"Hit critical geometry: {hitCrit}, {hitCrit / totalRays * 100: .3f}%")
    print(f"Hit any geometry: {hitObj / totalRays * 100: .1f}%")


def main() -> None:
    """
    Main function for running sim
    :return: None
    """
    
    t1 = time.time()
    print()
    print("Starting twobounce")
    ans = multicoreIterateMap(objs, N)
    printResults(ans)
    print("Finished")
    deltat = time.time() - t1
    print(f"Simulated {N} rays using {CPU_COUNT} cores in {deltat: .2f}s")
    print(f"Time per 1k rays: {deltat/(N/1000) : .2g}s")
    print(f"Time per 1k rays per core: {deltat / ((N/1000)/mp.cpu_count()) : .2g}s")
    # check individual vector


def oneVec() -> None:
    """
    Debugging, look more closely at one particular vector
    :return: None
    """
    st = Vector(0, 0, 50)
    dir = Vector(-1, 0, 0)
    r = twobounce(objs, st, dir)
    pprint(r[0].hitDict)
    pprint(r[1].hitDict)


if __name__ == "__main__":
    initalize()
    print("Loading geometry")
    loader = ObjLoader("./")
    objs, tris = loader.load("MOLLER-TestGeo.obj")
    # objs, tris = loader.load("untitled.obj")
    print(f"Done")
    print(f"{len(objs)} objects, {len(tris)} polygons\n")
    # oneVec()
    main()
    # print(len(ans))
