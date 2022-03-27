import logging
import logging.handlers
import multiprocessing
import requests
import uuid
from random import choice, random, randint
import json
from time import time, sleep


REQ_WORKER_NUM = 3


def generate_id_process(queue):
    print("start generate_id_process")
    for i in range(1,100+1):
        print(f"put: {i}")
        queue.put(i)
    print("end generate_id_process")


def worker_process(id_queue):
    print("start worker_process")
    while True:
        item = id_queue.get()
        print(f'get: {item}')
        if item is None:
            print("end worker process")
            break
        print(f"requests: {item}")
    print("end worker_process")


def main():
    print('start')
    id_q = multiprocessing.Queue(-1)
    workers = []
    for _ in range(REQ_WORKER_NUM):
        worker = multiprocessing.Process(target=worker_process, args=(id_q,))
        workers.append(worker)
        worker.start()

    id_listener = multiprocessing.Process(target=generate_id_process, args=(id_q, ))
    id_listener.start()
    id_listener.join()

    print('--- id_q.put_nowait(None) ---')
    for _ in range(REQ_WORKER_NUM):
        id_q.put_nowait(None)

if __name__ == "__main__":
    s = time()
    main()
    print(time() - s)