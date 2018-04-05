import threading


class myThread(threading.Thread):
    def __init__(self, thread_name, func, begin, end):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.func = func
        self.begin = begin
        self.end = end;

    def run(self):
        print("开启线程： " + self.name)
        self.func(self.begin, self.end)
