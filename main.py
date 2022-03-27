import logging
import logging.handlers
import multiprocessing
from random import choice
from time import time


START_NUM = 1
END_NUM = 10
WORKER_NUM = multiprocessing.cpu_count() - 1


def listener_configurer():
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('main.log', 'a', 3000)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)


def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                print("Done log listener")
                break

            logger = logging.getLogger(record.name)
            logger.handle(record)
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def worker_configurer(queue):
    h = logging.handlers.QueueHandler(queue)
    root= logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(h)


def worker_process(log_queue, id_queue, configurer):
    configurer(log_queue)
    logger = logging.getLogger('worker_process')
    while True:
        item = id_queue.get()
        if item is None:
            print("End worker")
            break

        print(f"item: {item}")
        if choice([True, True, False]):
            message = f"{item}"
            logger.log(logging.INFO, message)
        else:
            message = f"{item}"
            logger.log(logging.WARNING, message)


def generate_data(queue):
    for i in range(START_NUM, END_NUM+1):
        id_ = i
        queue.put(id_)
    print("Done generate data")


def main():
    log_q = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=listener_process, args=(log_q, listener_configurer))
    listener.start()

    id_q = multiprocessing.Queue(-1)
    workers = []
    for _ in range(WORKER_NUM):
        worker = multiprocessing.Process(target=worker_process, args=(log_q, id_q, worker_configurer))
        workers.append(worker)
        worker.start()

    generate_data(id_q)

    for _ in range(WORKER_NUM):
        id_q.put_nowait(None)
    for w in workers:
        w.join()

    log_q.put_nowait(None)
    listener.join()


if __name__ == "__main__":
    s = time()
    main()
    print(time() - s)