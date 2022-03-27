import random
import time
from multiprocessing import Process, Queue, current_process, cpu_count


def mul(a, b):
    time.sleep(0.5*random.random())
    return a * b


def calculate(func, args):
    result = func(*args)
    return '%s says that %s%s = %s' % (current_process().name, func.__name__, args, result)


def worker(q):
    for func, args in iter(q.get, "STOP"):
        result = calculate(func, args)
        print(result)


def main():
    NUMBER_OF_PROCESSES = cpu_count()
    TASKS1 = [(mul, (i, 2)) for i in range(10+1)]

    queue = Queue()

    for task in TASKS1:
        queue.put(task)

    processes = []
    for _ in range(NUMBER_OF_PROCESSES):
        p = Process(target=worker, args=(queue,))
        processes.append(p)
        p.start()

    for task in TASKS1:
        queue.put("STOP")
    for p in processes:
        p.join()


if __name__ == "__main__":
    main()