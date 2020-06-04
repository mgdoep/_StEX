def getFunktion(name):
    file = open(name+".txt", "r")
    rv = []
    for line in file.readlines():
        ll = line.split(",")
        rv.append((float(ll[0]), float(ll[1])))
    return rv

def getFktValue(locp, x):
    getmn = False
    for i in range(len(locp)-1):
        if (locp[i][0] <= x) and (locp[i+1][0] > 0):
            m = (locp[i+1][1]-locp[i][1])/(locp[i+1][0]-locp[i][0])
            n = locp[i+1][1]-m*locp[i+1][0]
            getmn = True
    if not getmn:
        return -1
    return m*x+n

def getError(locp, point, maxy):
    fy = getFktValue(locp, point[0])
    if fy > maxy/2:
        maxe = fy
    else:
        maxe = maxy - fy
    return(round(abs(fy-point[1]),8), round(maxe, 8))