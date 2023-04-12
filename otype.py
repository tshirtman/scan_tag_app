class oType:
    def __init__(self, name, props = None):
        self.id = name
        if props is not None:
            self.props = props # dict with runes as keys
        else:
            print("TODO fetch data from database")


    def items(self):
        return  (
            ('key0', 'value0'),
            ('key1', 'value1'),
        )

    def get(self, x,y):
        #print(f"oType.get({x},{y})")
        return y


