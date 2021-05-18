class Scope():
    def __init__(self, index, parent):
        self.index = index
        self.parent = parent
        self.open = True

    def __str__(self):
        return "Index:{} Parent:{} Open:{}".format(self.index, self.parent, self.open)

    def close(self):
        self.open = False
