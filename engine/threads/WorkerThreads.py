import threading


class WorkerThread(threading.Thread):
    def __init__(self, function, once=False, daemon=False, *args, **kwargs):
        super(WorkerThread, self).__init__(daemon=daemon)
        self.stop = False
        self.my_args = args
        self.my_kwargs = kwargs
        self.my_func = function
        self.once = once

    def run(self):
        if self.stop:
            return

        self.my_func(*self.my_args, **self.my_kwargs)
        if self.once:
            self.stop = True
