from multiprocessing import cpu_count, Process
import os


def work(identifier):
    print(f"num: {identifier}, pid: {os.getpid()}")


def main():
    print(f"parent pid: {os.getpid()}")
    processes = []
    cpu = cpu_count()
    for i in range(cpu):
        process = Process(target=work, args=(i, ))
        processes.append(process)
        process.start()
    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
