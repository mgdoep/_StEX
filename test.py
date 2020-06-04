#Test, ob Modul vorhanden ist
try:
    import aripel
except ImportError:
    print("Doh!")
print("Jetzt kann es weiter gehen.")

def foo(bar=2):
    if bar == 2:
        print(bar)
        return
    print(bar)

a = [0.2, 1.0, 1.1, 1.2, 1.5, 1.6, 2.0, 2.5]
aa = ["a0", "a", "b", "c", "d", "e", "f", "g"]
b = [0.5, 0.9, 0.98, 1.01, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
ba = ["bq", "b0", "bx", "ba", "bb", "bc", "bd", "be", "bf", "bg"]
bc = []

#a: Sys_Time in self
#b : Sys_Time in val
index_lastimport = -1
maxindex = len(b)
for x in range(len(a)):
    candidates = []
    cont = True
    i = index_lastimport+1
    while cont and i < len(b):
        difference = b[i]-a[x]
        if difference < -0.09:
            i += 1
        elif difference > -0.09 and difference < 0.09:
            candidates.append((i, difference))
            i += 1
        else:
            cont = False
        if cont and i == maxindex:
            cont = False
    if len(candidates) == 0:
        bc.append(None)
    elif len(candidates) == 1:
        bc.append(ba[candidates[0][0]])
        index_lastimport = candidates[0][0]
    else:
        nearest = 0
        for i in range(1, len(candidates)):
            if abs(candidates[nearest][1]) > abs(candidates[i][1]):
                nearest = i
        bc.append(ba[candidates[nearest][0]])
        index_lastimport = candidates[nearest][0]
print(bc)
print(ba[-1])
d = {"a": 1, "b": 5, "c":[1, 2, 3]}
dk = d.keys()
dkl = []
for v in dk:
    dkl.append(v)
dkl.pop(dkl.index("b"))
print(dkl)
from copy import deepcopy
dc = deepcopy(d)
d["a"] = 1000
print(d)
print(dc)

dn1 = 1
dn2 = 2
dn = [dn1, dn2]
for dnv in dn:
    dnv = None
dn2 = None
print(dn1, dn2)


from os import path
def _getavailableFileName(string, ext, getlatest=False):
    running = 0
    while path.exists(string + str(running) + ext):
        running += 1
    if getlatest:
        return string+str(running - 1)
    return string + str(running)


"""string = "<datafile>myolddata.dat</datafile>"
fn = _getavailableFileName("proj10_data-", ".meta", getlatest=True)
print(fn)
print(string.split("<datafile>")[1].split("</datafile>")[0])
"""
from time import localtime, strftime
print(path.getctime("proj1_data-0.meta"), path.getmtime("proj1_data-0.meta"))

def paratest(p, **kwargs):
    if "a" in kwargs:
        p = "olala"+str(kwargs["a"])
    print(p)

paratest(9)
paratest(10, a=4)



d ={"a": 0, "b": 3, "c": 7}

string = "t [ s ];s [ m ]; tl [s]\n"
line = string.strip().split(";")
variables = []
units = []
for element in line:
    fs = element.split("[")
    variables.append(fs[0].strip())
    units.append(fs[1].split("]")[0].strip())
print(variables)
print(units)

test = {1: "vari1", 2: "vari2"}
print(test[1])

tst = "ol"
print(tst.split("["))

stack=[1]
a = stack.pop()
stack.append(2)
print(stack)
print(float("3.9"))
import numpy as np
print(np.exp(1.0))
print(np.pi)


t = 0.6
l = 10

print([t]*l)


def _checkProperVariableDeclaration(vardecl):
    checkfor = ["name", "unit", "errorrule"]
    rv = True
    k = vardecl.keys()
    for i in checkfor:
        if rv:
            rv = i in k
    return rv

d1 = {"name": 0, "unit": 2, "errorrule": 3}
d2 = {"name2": 0, "unit": 2, "errorrule": 3}

print(_checkProperVariableDeclaration(d1))
print(_checkProperVariableDeclaration(d2))