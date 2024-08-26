import time

class ProgressManager:

    def __init__(self, handler, on_step_callback=None, on_complete_callback=None):
        self.handler = handler
        self.on_step_callback = on_step_callback
        self.on_complete_callback = on_complete_callback
        self.is_completed = False
        self.on_step_return = None
        self.on_completed_return = None

    def step_callback(self, x):
        self.on_step_return = x
        self.on_step_callback(x)

    def complete_callback(self, x):
        self.on_completed_return = x
        self.on_complete_callback(x)
        self.is_completed = True

    def start(self):
        self.handler(on_step_callback=self.step_callback, on_complete_callback=self.complete_callback)

    def wait_until_complete(self, delay=1):

        while not self.is_completed:
            self.on_step_callback(self.on_step_return)
            time.sleep(delay)
        
        self.on_complete_callback(self.on_completed_return)


manager_dict = dict()
        