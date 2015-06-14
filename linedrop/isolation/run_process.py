from multiprocessing import Process, Queue
import os
import sys


def run_process(fn):
    q = Queue()

    def run():
        sys.stdout = open(str(os.getpid()) + ".out", "a", buffering=0)
        sys.stderr = open(str(os.getpid()) + "_error.out", "a", buffering=0)
        res = fn()
        stdout = open(str(os.getpid()) + ".out", "r").read()
        stderr = open(str(os.getpid()) + "_error.out", "r", buffering=0)
        q.put((res, stdout, stderr))
        os.remove(str(os.getpid()) + ".out")
        os.remove(str(os.getpid()) + "_error.out")

    p = Process(target=run)
    p.start()
    p.join(timeout=60)
    if not q.empty():
        return q.get()
    else:
        return ((False, {}), "no stdio", "no error")
