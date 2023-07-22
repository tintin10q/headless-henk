import random

def weighted_shuffle(items, weights):
    if len(items) != len(weights):
        raise ValueError("Unequal lengths")

    n = len(items)
    nodes = [None for _ in range(n)]

    def left_index(i):
        return 2 * i + 1

    def right_index(i):
        return 2 * i + 2

    def total_weight(i=0):
        if i >= n:
            return 0
        this_weight = weights[i]
        if this_weight <= 0:
            raise ValueError("weight can't be zero or negative")
        left_weight = total_weight(left_index(i))
        right_weight = total_weight(right_index(i))
        nodes[i] = [this_weight, left_weight, right_weight]
        return this_weight + left_weight + right_weight

    def sample(i=0):
        this_w, left_w, right_w = nodes[i]
        total = this_w + left_w + right_w
        r = total * random.random()
        if r < this_w:
            nodes[i][0] = 0
            return i
        elif r < this_w + left_w:
            chosen = sample(left_index(i))
            nodes[i][1] -= weights[chosen]
            return chosen
        else:
            chosen = sample(right_index(i))
            nodes[i][2] -= weights[chosen]
            return chosen

    total_weight()  # build nodes tree

    return (items[sample()] for _ in range(n - 1))


