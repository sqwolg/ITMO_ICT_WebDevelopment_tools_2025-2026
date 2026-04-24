import multiprocessing
import time

TOTAL = 1_000_000_000
NUM_PROCESSES = 4
CHUNK_SIZE = TOTAL // NUM_PROCESSES


def range_sum(start, end):
    return sum(range(start, end))


def calculate_sum():
    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        ranges = [
            (i * CHUNK_SIZE, TOTAL if i == NUM_PROCESSES - 1 else (i + 1) * CHUNK_SIZE)
            for i in range(NUM_PROCESSES)
        ]
        results = pool.starmap(range_sum, ranges)
    return sum(results)


def main():
    start_time = time.time()
    total = calculate_sum()
    print(f"Multiprocessing result: {total}, Time: {time.time() - start_time:.4f}s")

if __name__ == "__main__":
    main()
