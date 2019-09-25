
def build_index(query_dicts, *keys):
    index = {}
    for q in query_dicts:
        key = hash(''.join(q[k] for k in keys if k in q))
        index[key] = 1
    return index


def in_index(index, *keys):
    key = hash(''.join(k for k in keys))
    return key in index
