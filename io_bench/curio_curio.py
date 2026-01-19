import curio
import os
import time

DIR = "test_files"

async def read_file(path):
    async with curio.aopen(path, "r") as f:
        await f.read()

async def write_file(path, data):
    async with curio.aopen(path, "w") as f:
        await f.write(data)

async def main():
    start = time.perf_counter()
    paths = [os.path.join(DIR, f) for f in os.listdir(DIR)]

    # --- Reading files concurrently ---
    async with curio.TaskGroup() as g:
        for p in paths:
            await g.spawn(read_file, p)
    await g.join()  # Wait for all to finish

    # --- Writing files concurrently ---
    async with curio.TaskGroup() as g:
        for p in paths:
            await g.spawn(write_file, p + "_out", "Test data")
    await g.join()

    end = time.perf_counter()
    print(f"curio: file I/O in {end - start:.4f} seconds")
    return end - start

if __name__ == "__main__":
    res = []
    for _ in range(10):
        res.append(curio.run(main))

    mean = sum(res) / len(res)
    stddev = (sum((x - mean)**2 for x in res) / len(res))**0.5

    print(f"mean: {mean:.4f} seconds")
    print(f"min: {min(res):.4f} seconds")
    print(f"max: {max(res):.4f} seconds")
    print(f"stddev: {stddev:.4f} seconds")
    print(f"total: {sum(res):.4f} seconds")

    # Cleanup output files
    for f in os.listdir(DIR):
        out_file = os.path.join(DIR, f + "_out")
        if os.path.exists(out_file):
            os.remove(out_file)
