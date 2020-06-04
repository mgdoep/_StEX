import tkinter as tk
from time import time, sleep
import arduinohelper

sublevel = -1
root = tk.Tk()

#Dimensionen bestimmen
cw = root.winfo_screenwidth() #Breite der Diagrammfläche
ch = root.winfo_screenheight()-50 # Höhe der Diagrammfläche

#Kalibrierungsdatei lesen und Werte festlegen
noe = -1 #Wie viele Einheiten auf y-Achse
scalemin = -1 #Ort des 0-Punkts der Skala vor dem Sensor
scalemax = -1 #Ort des Maximal-Punkts auf der Skala vor dem Sensor
arduinoport = "" #Portname des Arduinoports

file = open("calib.cal", "r")
for line in file.readlines():
    l = line.split(" ")
    if l[0] == "port":
        arduinoport = l[1].split(":")[0]
    elif l[0] == "steps":
        noe = int(l[1])
    elif l[0] == "min":
        scalemin = int(l[1])
    elif l[0] == "max":
        scalemax = int(l[1])
t = 10 #Zeit in s
ey = round(ch-100)/noe-5 #Länge einer Einheit auf der y-Achse
ex = round(cw-100)/t-2 #Länge einer Einheit auf der x-Achse

arduino = arduinohelper.ArduinoHelper(arduinoport, noe, scalemin, scalemax)

def disable_event(): #Wird aufgerufen, wenn der Schließen-Button gedrückt wird, verhindert den Abbruch des Experiments
    pass

def close_program(event): #Bricht Experiment ab
    root.destroy()

def getFunktion(name): #holt die Funktion aus der Datei <name>.txt, die kritische Punkte enthält
    file = open(name+".txt", "r")
    rv = []
    for line in file.readlines():
        ll = line.split(",")
        rv.append((float(ll[0]), float(ll[1])))
    return rv

def getFktValue(locp, x): #gibt den Wert der Zielfunktion für einen bestimmten x-Wert aus. locp: List of critical points
    getmn = False
    for i in range(len(locp)-1):
        if (locp[i][0] <= x) and (locp[i+1][0] > 0):
            m = (locp[i+1][1]-locp[i][1])/(locp[i+1][0]-locp[i][0])
            n = locp[i+1][1]-m*locp[i+1][0]
            getmn = True
    if not getmn:
        return -1
    return m*x+n

def getError(locp, point, maxy): #Berechnet die derzeitige Abweichung und die maximal mögliche Abweichung von der Zielfunktion
    fy = getFktValue(locp, point[0])
    if fy > maxy/2:
        maxe = fy
    else:
        maxe = maxy - fy
    return(round(abs(fy-point[1]),8), round(maxe, 8))

def calculateScore(maximal_possible_score): #Berechnet die Score
    global positions
    accumulated_error = 0
    maximal_error = 0
    for p in positions:
        fehler = getError(targetfunction, p, noe)
        accumulated_error += fehler[0]
        maximal_error += fehler[1]
    return (1-accumulated_error/maximal_error)*maximal_possible_score

def drawTargetFunction(name): #Holt und zeichnet die Zielfunktion
    global tarfunc_graph
    rv=getFunktion(name)
    for i in range(0, len(tarfunc_graph)):
        canvas.delete(tarfunc_graph[i])
    for i in range(len(rv)-1):
        p1 = getKoord(rv[i], False)
        p2 = getKoord(rv[i+1], False)
        tarfunc_graph.append(canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill="#BBBBBB", width=4))
    return rv

def getKoord(k, protocol): #Errechnet die Koordinaten zur Darstellung, bei protocol=True werden die Ergebnisse protokolliert
    if protocol:
        positions.append(k)
    return (50+round(k[0]*ex), ch-50-round(k[1]*ey))

def updatePosition(op, xval=0,protocol=False): #Holt die derzeitige Position vom Arduino, bewegt den Punkt und zeichnet (bei Protokollierung) auch den Strich
    global pos, canvas, graph
    nk=getKoord((xval, arduino.getDistance()), protocol)
    canvas.move(pos, nk[0]-op[0], nk[1]-op[1])
    if protocol:
        graph.append(canvas.create_line(op[0], op[1], nk[0], nk[1], fill="blue", width=3))
    canvas.pack()
    canvas.update()
    return nk

def countdown(l): #Zeigt Countdown der Länge l (in sek) an
    global canvas, pos
    secs = canvas.create_text(cw/2, ch/2, text=str(l), font=("Arial", 80, "bold"), fill="red")
    op = (0,0)
    pos = canvas.create_oval(op[0] - 8, op[1] - 8, op[0] + 8, op[1] + 8, fill="blue")
    canvas.update()
    for i in range(0, l):
        canvas.itemconfigure(secs, text=str(l-i))
        canvas.update()
        stime = time()
        ctime = time()
        while ctime-stime < 1:
            op = updatePosition(op)
            ctime = time()
    canvas.delete(secs)
    sleep(0.2)
    return op

def lauflos(): #Hier wird die Funktion gelaufen
    global pos
    koord = countdown(5)
    starttime = time()
    currenttime = time()
    while currenttime - starttime < t:
        currenttime = time()
        koord = updatePosition(koord, xval=currenttime-starttime, protocol=True)
        sleep(0.01)
    canvas.delete(pos)

def chooseLvlClick(event): #Event-Handler LevelChooser
    global lvlc, cl, sublevel
    p1=(cw/2-200, ch/2-75)
    p2=(cw/2+50, ch/2-75)
    if cl and (event.x >= p1[0]) and (event.x <= p1[0]+150) and (event.y >=p1[1]) and (event.y <= p1[1]+150):
        sublevel += 1
        lvlc = "f1"+str(sublevel%3)
    if cl and (event.x >= p2[0]) and (event.x <= p2[0]+150) and (event.y >=p2[1]) and (event.y <= p2[1]+150):
        sublevel += 1
        lvlc = "f2"+str(sublevel%3)

def chooseLevel(): #Level-Chooser
    global lvlc, cl
    cl = True
    headline = canvas.create_text(cw/2, ch/2-200, text="Level wählen", font=("Arial", 40, "bold"), fill="black")
    #easybutton = tk.Button(text="1", command=chooseLvlClick1, anchor="w")
    #easybutton.configure(width=150, activebackground="#106010")
    #easybutton.window = canvas.create_window(cw/2-200, ch/2-20, anchor="nw", window=easybutton)
    easybutton = canvas.create_rectangle(cw/2-200, ch/2-75, cw/2-50, ch/2+75, fill="#106010", tags=('easy'))
    easytext = canvas.create_text(cw/2-125, ch/2, text="1", font=("Arial", 30, "bold"), fill="white")
    diffbutton = canvas.create_rectangle(cw/2+50, ch/2-75, cw/2+200, ch / 2 + 75, fill="#6e0e10", tags=('diff'))
    difftext = canvas.create_text(cw / 2 + 125, ch / 2, text="2", font=("Arial", 30, "bold"), fill="white")
    canvas.bind("<Button-1>", chooseLvlClick)
    canvas.pack()
    while lvlc not in ["f10", "f11", "f12", "f20", "f21", "f22"]:
        canvas.update()
    rv = lvlc
    lvlc = 0
    cl = False
    canvas.delete(headline)
    canvas.delete(easybutton)
    canvas.delete(easytext)
    canvas.delete(diffbutton)
    canvas.delete(difftext)
    canvas.update()
    return rv

def startbutton(event): #Event-Handler Startbutton
    global showscore
    showscore = False

def loescheVerlauf(): #Löscht den Verlauf des Trials
    global graph, positions, tarfunc_graph, targetfunction
    positions = []
    for i in range(len(graph)):
        canvas.delete(graph[i])
        if i in range(len(tarfunc_graph)):
            canvas.delete(tarfunc_graph[i])
    canvas.update()
    targetfunction = []

def showscoreText(): #Zeigt den Punktwert an
    global showscore
    t = canvas.create_text(cw/2, ch/2, text="Berechne die Punktzahl", font=("Arial", 60, "bold"))
    canvas.update()
    sleep(1)
    canvas.delete(t)
    canvas.update()
    t = canvas.create_text(cw / 2, ch / 2-80, text="Punkte: "+str(int(calculateScore(10000))), font=("Arial", 60, "bold"))
    t2 = canvas.create_text(cw / 2, ch / 2+80, text="Zum Fortfahren Leertaste drücken!", font=("Arial", 40, "bold"), fill = "red")
    showscore = True
    while showscore:
        canvas.update()
    canvas.delete(t)
    canvas.delete(t2)
    canvas.update()


root.title("Funktionen laufen")

canvas = tk.Canvas(root, bg="white", width=cw, height=ch)
canvas.pack()


# Diagramm initialisieren
sysItems = []
sysItems.append(canvas.create_line(50, 50, 50, ch-50, fill="black", width=2))
sysItems.append(canvas.create_line(50, ch-50, cw-50, ch-50, fill="black", width=2))

#Grid zeichnen
for i in range(1,noe+1):
    sysItems.append(canvas.create_line(cw-50, ch-50-i*ey, 45, ch-50-i*ey, fill="#aaaaaa", width=1, dash=(2,2)))
    sysItems.append(canvas.create_text(30, ch-50-i*ey, text=str(i), font=("Arial", 20)))

for i in range(1,t+1):
    sysItems.append(canvas.create_line(50+i*ex, 50, 50+i*ex, ch-50, fill="#aaaaaa", width=1, dash=(2, 2)))
    sysItems.append(canvas.create_text(50+i*ex, ch-30, text=str(i), font=("Arial", 20)))

#Einstellen, dass das Programm nur mit der Tastenkombination <F10><q><x> geschlossen werden kann
root.protocol("WM_DELETE_WINDOW", disable_event)
root.bind("<F10><q><x>", close_program)

#Event-Bindings für Level-Chooser und Startbutton
root.bind("<space>", startbutton)
canvas.bind("<Button-1>", chooseLvlClick)

#Loslaufen
positions = [] #gemessene Funktionswerte
graph = [] #gelaufene Funktion, Canvas-Objekte

tarfunc_graph = [] #Zielfunktion, Canvas-Objekte
pos = "" #später wird darauf der Punkt initialisiert

lvlc = "" #Variable für Level-Choose-Handler
cl = True #gibt an, ob gerade ein Level ausgewählt werden kann (für Level-Choose-Event-Handler)
showscore = False #gibt an, ob gerade ein Punktwert angezeigt wird (für Punktanzeige-Event-Handler)

while True:
    targetfunction = drawTargetFunction(chooseLevel())
    lauflos()
    showscoreText()
    loescheVerlauf()
root.mainloop()
