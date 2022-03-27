import logging
import logging.handlers
import multiprocessing
import requests
import uuid
from random import choice, random, randint
import json
from time import time, sleep


MAX_USERS = 10
START_NUM = 101
END_NUM = 200 # MAX_USERS

HOST=''
HEADERS = {
    'content-type': 'application/json',
}

REQ_WORKER_NUM = multiprocessing.cpu_count() - 2

def listener_configurer():
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('preparation.log', 'a', 3000)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)


def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                print("end log listener")
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def generate_id_process(queue):
    for i in range(START_NUM, END_NUM+1, 2):
        uuid_ = str(uuid.uuid5(uuid.NAMESPACE_OID, str(i)))

        if randint(1,10) == 1:
            id_n = randint(35, 50)
        else:
            id_n = randint(1, 10)
        queue.put((uuid_, id_n, i))
    print("done generate_id_process")


def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)
    root= logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(h)


def worker_process(log_queue, id_queue, configurer):
    configurer(log_queue)
    while True:
        item = id_queue.get()
        if item is None:
            print("end worker process")
            break

        cid = f"{item[0]}=1"
        for i in range(1, item[1]+1):
            ccid = f"{item[0]}={i}:{item[1]}"
            logger = logging.getLogger('worker_process')
            path, payload = {} # 省略
            r = requests.post(HOST + path, headers=HEADERS, data=json.dumps(payload))
            if r.status_code >= 400:
                message = f"[{r.status_code}] {item[2]} {ccid} {r.text}"
                logger.log(logging.WARNING, message)
            else:
                message = f"[{r.status_code}] {item[2]} {ccid}"
                logger.log(logging.INFO, message)


def main():
    log_q = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=listener_process, args=(log_q, listener_configurer))
    listener.start()

    id_q = multiprocessing.Queue(-1)
    workers = []
    for _ in range(REQ_WORKER_NUM):
        worker = multiprocessing.Process(target=worker_process, args=(log_q, id_q, worker_configurer))
        workers.append(worker)
        worker.start()

    id_listener = multiprocessing.Process(target=generate_id_process, args=(id_q, ))
    id_listener.start()
    id_listener.join()

    for _ in range(REQ_WORKER_NUM):
        id_q.put_nowait(None)
    for w in workers:
        w.join()

    log_q.put_nowait(None)
    listener.join()


if __name__ == "__main__":
    s = time()
    main()
    print(time() - s)