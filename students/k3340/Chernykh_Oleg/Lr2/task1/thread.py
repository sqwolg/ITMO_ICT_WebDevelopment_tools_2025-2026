import threading
import time

TOTAL = 1_000_000_000
NUM_THREADS = 4
CHUNK_SIZE = TOTAL // NUM_THREADS
result = 0
lock = threading.Lock()


def range_sum(start, end):
    return sum(range(start, end))


def partial_sum(start, end):
    global result
    local_sum = range_sum(start, end)
    with lock:
        result += local_sum


def calculate_sum():
    global result
    result = 0
    threads = []
    for i in range(NUM_THREADS):
        start = i * CHUNK_SIZE
        end = TOTAL if i == NUM_THREADS - 1 else (i + 1) * CHUNK_SIZE
        t = threading.Thread(target=partial_sum, args=(start, end))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return result


def main():
    start_time = time.time()
    total = calculate_sum()
    print(f"Threading result: {total}, Time: {time.time() - start_time:.4f}s")


if __name__ == "__main__":
    main()
