from multiprocessing import Process, Queue


def run_process(fn):
    q = Queue()

    def run():
        print "START"
        q.put(fn())
        print "FINISH"


    p = Process(target=run)
    p.start()
    print "STARTED"
    p.join(timeout=2)
    print "OH?"
    if not q.empty():
        return q.get()
    else:
        return (False, {})
