import operator

class FramesQueue:
    def __init__(self, size, default_value=None):
        self.q = []
        self.size = size
        self.default_value = default_value

    def append(self, value):
        if len(self.q) > self.size:
            self.q.pop(0)
        self.q.append(value)

    def max_value(self):
        if len(self.q) == 0:
            return self.default_value
        c = {}
        for value in self.q:
            c[value] = c.get(value, 0) + 1
        return max(c.items(), key=operator.itemgetter(1))[0]

    def get_first_last(self):
        if len(self.q) == 0:
            return self.default_value,self.default_value
        return self.q[0], self.q[-1]

    def pop(self):
        return self.q.pop()

    def len(self):
        return len(self.q)