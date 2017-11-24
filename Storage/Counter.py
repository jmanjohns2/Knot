
class Counter(object):

    def __init__(self):
        self.count = 0

    def get_Count(self):
        return self.count

    def advance_Count(self):
        self.count = self.count+1