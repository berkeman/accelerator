from collections import defaultdict

def analysis(sliceno):
    c = defaultdict(lambda: defaultdict(set))
    c[0][2].add(sliceno)
    return c

def synthesis(analysis_res):
    print(analysis_res.merge_auto())
