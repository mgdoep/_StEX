import numpy as np

file = open("f23.txt", "w")
i = 0
while i < 8:
    s = str(round(i,2))
    s += ","+str(round(0.0625*i*i, 2))+"\n"
    file.write(s)
    i += 0.3
file.close()