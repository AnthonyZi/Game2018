import sys

def dict_function_call():

    def addition(a,b):
        return a+b

    d = dict()
    d["a"] = addition

    d2 = {"a": lambda a,b : addition(a,b) }

    out1 = d["a"](3,5)
    out2 = d["a"](21,4)

    print(out1)
    print(out2)

def default_dict_default_function():
    from collections import defaultdict

    def default_function():
        print("default function print")
        return 0

    def test():
        print("test function")

    def test2(x):
        print("test function, val: {}".format(x))


    d = defaultdict(lambda : default_function)

    d["test"] = test
    d["test2"] = test2

    d["bla"]()
    d["test"]()
    d["test2"](42)

def norm_vector():

    def get_norm_vectors(dx,dy):
        if dx != 0:
            dx = int(dx/ abs(dx))
        if dy != 0:
            dy = int(dy/ abs(dy))

        return dx,dy

    dx,dy = -32, 2
    dx,dy = get_norm_vectors(dx,dy)
    print(dx,dy)


if __name__ == "__main__":
    arg = sys.argv[1]

    if arg == "dict_function_call":
        dict_function_call()

    if arg == "default_dict_default_function":
        default_dict_default_function()

    if arg == "norm_vector":
        norm_vector()
