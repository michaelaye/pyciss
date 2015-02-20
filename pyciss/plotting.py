def lookup_rcparam(rcParams, pattern):
    return [i for i in rcParams.keys() if pattern in i]
