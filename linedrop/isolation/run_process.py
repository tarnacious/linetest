import sys
from multiprocessing import Process, Queue, Pool
from linedrop.isolation.logger import Logger
from linedrop.isolation.run_function import RunFunction


def run(fn, q):
    logger = Logger()
    sys.stdout = logger
    sys.stderr = logger
    res = fn()
    q.put((res, logger.log, ""))


def run_processes(funs, cb, run_function):
    results = []
    pool = Pool(processes=4, maxtasksperchild=1)

    def callback(result):
        results.append(result)
        cb(result)

    for mutation in funs:
        pool.apply_async(run_function(*mutation), callback=callback)

    pool.close()
    pool.join()
    return results


def run_process(fn):
    q = Queue()

    p = Process(target=run, args=(fn, q,))
    p.start()
    p.join(timeout=6)
    if not q.empty():
        return q.get()
    else:
        return ((False, {}), "no stdio", "no error")
