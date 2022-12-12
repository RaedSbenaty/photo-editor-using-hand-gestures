import operator
from collections import Counter
class Queue:
    def __init__(self,size):
        self.q = []
        self.size = size
    def append(self,value):
        if len(self.q) > self.size:
            self.q.pop(0)
        self.q.append(value)
    def max_value(self):
        c = {}
        for value in self.q:
            c[value] = c.get(value,0)+1
        return max(c.items(), key=operator.itemgetter(1))[0]
    def first_last_diff(self):
        return self.q[0] - self.q[-1]
q = Queue(20)
for j in range(15):
    q.append(j)
q.append(14)
print(q.max_value())
print(q.q)