from threading import Thread

class ThreadManager(Thread):
    def __init__(self, mUserId):
        self.UserId = mUserId
        Thread.__init__(self)

    def run(self):
        print("Старт потока # " + self.mUserId)