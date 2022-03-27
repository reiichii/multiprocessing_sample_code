# 複数のプロセスからの単一ファイルへのログ記録
# Queue と QueueHandler を使って一つのプロセスに全てのloggingイベントを送る

import logging
import logging.handlers
import multiprocessing

from random import choice, random
import time


def listener_configurer():
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('step3.log', 'a', 3000)
    f = logging.Formatter('%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)


def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:
                print('end listener')
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
    root.addHandler(h)


def worker_process(queue, configurer):
    configurer(queue)
    name = multiprocessing.current_process().name
    print(f'Worker started: {name}')
    for _ in range(10):
        time.sleep(random())
        logger = logging.getLogger(choice(['red', 'blue', 'green']))
        level = choice([logging.DEBUG, logging.INFO, logging.WARNING])
        message = choice(['message1', 'message2', 'message3'])
        logger.log(level, message)
    print(f'Worker finished: {name}')


def main():
    q = multiprocessing.Queue(-1)

    listener = multiprocessing.Process(target=listener_process, args=(q, listener_configurer))
    listener.start()

    workers = []
    NUMBER_OF_PROCESSES = multiprocessing.cpu_count() - 1
    for _ in range(NUMBER_OF_PROCESSES):
        worker = multiprocessing.Process(target=worker_process, args=(q, worker_configurer))
        workers.append(worker)
        worker.start()
    for w in workers:
        w.join()

    q.put_nowait(None)
    listener.join()


if __name__ == "__main__":
    main()