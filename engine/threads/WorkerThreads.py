import threading


class WorkerThread(threading.Thread):
    def __init__(self, function, daemon=False, *args, **kwargs):
        super(WorkerThread, self).__init__(daemon=daemon)
        self.stop = False
        self.my_args = args
        self.my_kwargs = kwargs
        self.my_func = function

    def run(self):
        if self.stop:
            return

        print(self.my_args, self.my_kwargs)
        self.my_func(*self.my_args, **self.my_kwargs)
