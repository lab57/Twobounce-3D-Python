from tqdm import tqdm

total = 1
p = 0
N = 100_000_000
for i in range(N):
    total *= i
    if i % (N / 20) == 0:
        print(f"{p}%")
        p += 5
