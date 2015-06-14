from multiprocessing import Process, Queue


def run_process(fn):
    q = Queue()

    def run():
        q.put(fn())

    p = Process(target=run)
    p.start()
    p.join(timeout=60)
    if not q.empty():
        return q.get()
    else:
        return (False, {})
