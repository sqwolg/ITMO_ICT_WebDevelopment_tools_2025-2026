import asyncio
import time

TOTAL = 1_000_000_000
NUM_TASKS = 4
CHUNK_SIZE = TOTAL // NUM_TASKS


def range_sum(start, end):
    return sum(range(start, end))


async def partial_sum(start, end):
    return range_sum(start, end)


async def calculate_sum():
    tasks = []
    for i in range(NUM_TASKS):
        start = i * CHUNK_SIZE
        end = TOTAL if i == NUM_TASKS - 1 else (i + 1) * CHUNK_SIZE
        tasks.append(partial_sum(start, end))
    results = await asyncio.gather(*tasks)
    return sum(results)


def main():
    start_time = time.time()
    total = asyncio.run(calculate_sum())
    print(f"Asyncio result: {total}, Time: {time.time() - start_time:.4f}s")


if __name__ == "__main__":
    main()
