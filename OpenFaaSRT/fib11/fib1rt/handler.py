def handle(req):
    nterms = 100000
    n1, n2 = 0, 1
    count = 0
    while count < nterms:
        nth = n1 + n2
        n1 = n2
        n2 = nth
        count += 1
    #print(nth)
    return nth
