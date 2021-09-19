from datetime import datetime, timedelta
import heapq


# just holds a function, its arguments, and when we want it to execute.
class TimeoutFunction:
    def __init__(self, function, timeout, *args):
        self.function = function
        self.args = args
        self.startTime = datetime.now() + timedelta(0, 0, 0, timeout)

    def execute(self):
        self.function(*self.args)


# A "todo" list for all the TimeoutFunctions we want to execute in the future
# They are sorted in the order they should be executed, thanks to heapq
class TodoList:
    def __init__(self):
        self.todo = []

    def add_to_list(self, tFunction):
        heapq.heappush(self.todo, (tFunction.startTime, tFunction))

    def execute_ready_functions(self):
        if len(self.todo) > 0:
            t_function = heapq.heappop(self.todo)[1]
            while t_function and datetime.now() > t_function.startTime:
                # execute all the functions that are ready
                t_function.execute()
                if len(self.todo) > 0:
                    t_function = heapq.heappop(self.todo)[1]
                else:
                    t_function = None
            if t_function:
                # this one's not ready yet, push it back on
                heapq.heappush(self.todo, (t_function.startTime, t_function))
