# Task 1
def my_range(*args):
    assert len(args) != 0, "my_range expected at least 1 argument, 0 given"
    if len(args) > 3:
        raise TypeError("range expected at most 3 arguments")
    if len(args) == 3:
        start = args[0]
        stop = args[1]
        step = args[2]
        assert step != 0, "my_range() arg 3 must not be zero"
        if stop >= 0 and step > 0:
            i = 0
            while start + step * i < stop:
                yield start + step * i
                i += 1
        elif stop <= 0 and step < 0:
            i = 0
            while start + step * i > stop:
                yield start + step * i
                i += 1
    if len(args) == 2:
        start = args[0]
        stop = args[1]
        step = 1
        if stop >= 0 and step > 0:
            i = 0
            while start + step * i < stop:
                yield start + step * i
                i += 1
        elif stop <= 0 and step < 0:
            i = 0
            while start + step * i > stop:
                yield start + step * i
                i += 1
    if len(args) == 1:
        stop = args[0]
        start = 0
        step = 1
        if stop >= 0 and step > 0:
            i = 0
            while start + step * i < stop:
                yield start + step * i
                i += 1
        elif stop <= 0 and step < 0:
            i = 0
            while start + step * i > stop:
                yield start + step * i
                i += 1


print(list(my_range(1,3,1)), list(range(1,3,1)))
