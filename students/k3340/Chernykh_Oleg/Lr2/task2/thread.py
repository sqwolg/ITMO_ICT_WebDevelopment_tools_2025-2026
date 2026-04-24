import threading
import requests
import time
from database import SessionLocal, Todo, init_db

URLS = [f"https://dummyjson.com/todos?skip={i}&limit=25" for i in range(0, 251, 25)]


def parse_and_save(url):
    response = requests.get(url)
    todos = response.json()["todos"]
    
    session = SessionLocal()
    for todo in todos:
        t = Todo(id=todo["id"], title=todo["todo"], completed=todo["completed"])
        session.merge(t)
    session.commit()
    session.close()
    print(f"Thread saved {len(todos)} items from {url}")


def run():
    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    init_db()
    start = time.time()
    run()
    print(f"Threading completed in {time.time() - start:.2f}s")
