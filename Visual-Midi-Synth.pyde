# first of all, you should execute this command 
# to create a virtual midi device in the system
# sudo modprobe snd-virmidi
from themidibus import MidiBus

width = 640
height = 320
x = 0
fps = 30
minim = 0
umb = 1
deltax = 2
tempo = 200
octave = 4
nobg = False

filename = "imagen.jpg"

miditones = [1, 3, 6, 8, 10]  #pentatonic scale
graytones = {}     # dict containing {miditone: graytone}
colordict = {}          # dict containing {color: number of pixels with this color}
sendnotesdict = {} # dict containing notes: velocity
oldcolordict = {}   # a copy of previous frame calculation

MidiBus.list()
myBus = MidiBus(this, "VirMIDI [hw:2,0,0]", "VirMIDI [hw:2,0,0]")

def drawbackground(filename):
    img = loadImage(filename)
    img.filter(GRAY)
    img.filter(POSTERIZE, 5)
    #background(img)
    image(img, 0, 0, 640, 320)

def generate_a():
    global oldcolordict
    global colordict
    global graytones

    colorlist = []
    oldcolordict = {}
    # generate color list
    for x1 in range(width):
        for y1 in range(height):
            c = int(brightness(get(x + x1 - 1, y1)))
            if c not in colorlist:
                colorlist.append(c)
    # generate oldcolordict 
    if oldcolordict == {}:
        for c in colorlist:
            oldcolordict[c] = 0

    # generate colordict
    # counting pixels and save data in color dict
    colordict = {}
    for x1 in range(deltax):
        for y1 in range(height):
            c = int(brightness(get(x + x1 - 1, y1)))
            if c not in colordict.keys():
                colordict[c] = 1
            else:
                colordict[c] += 1
    # adding unfounded colors to dict
    for c in colorlist:
        if c not in colordict.keys():
            colordict[c] = 0

    # generate graytones
    gtones = {}
    sorted_colors = colorlist
    sorted_colors.sort()
    # generate graytones
    for i, j in enumerate(sorted_colors):
        graytones[j] = miditones[i]

def generate_b():
    global colordict

    colorlist = colordict.keys()
    # generate colordict
    # counting pixels and save data in color dict
    colordict = {}
    for x1 in range(deltax):
        for y1 in range(height):
            c = int(brightness(get(x + x1 - 1, y1)))
            if c not in colordict.keys():
                colordict[c] = 1
            else:
                colordict[c] += 1
    # adding unfounded colors to dict
    for c in colorlist:
        if c not in colordict.keys():
            colordict[c] = 0

    
def printdata():
    global colordict
    global sendnotesdict
    global miditones
    global graytones
    global nobg
    print("**********")
    print(nobg)
    print("oldcolordict: "+sorted_dict2(oldcolordict))
    print("colordict: "+sorted_dict2(colordict))
    print("graytones: "+sorted_dict2(graytones))
    print("sendnotesdict: "+sorted_dict(sendnotesdict))

def sorted_dict(colordict):
    lista = colordict.keys()
    lista.sort()
    label = ""
    for i in lista:
        label += "{} ".format(colordict[i])
    return label

def sorted_dict2(colordict):
    lista = colordict.keys()
    lista.sort()
    label = ""
    for i in lista:
        label += "{}:{} ".format(i,colordict[i])
    return label


def sendnote(chan, pitch, vel):
    myBus.sendNoteOff(chan, pitch, vel)
    myBus.sendNoteOn(chan, pitch, vel)

def calculate_sendnotesdict():
    global colordict
    global graytones
    global oldcolordict
    global sendnotesdict

    maximum = 0
    # detect higher value color
    for i in colordict.keys():
        if nobg == False:
            if colordict[i] > maximum:
                maximum = colordict[i]
        else:
            if colordict[i] > maximum:
                maximum = colordict[i]
    
    # map values in colordict to 0-127            
    for i in colordict.keys():
        if nobg == False:
            colordict[i] = int(map(colordict[i], 0, maximum, 0, 127))
        else:
            if i == 255:
                colordict[i] = 0
            else:
                colordict[i] = int(map(colordict[i], 0, maximum, 0, 127))

    # generate new dict with tones to send midi
    # acording to umb (threshold) and min rules
    sendnotesdict = {}
    print(colordict.keys())
    for j, i in enumerate(colordict.keys()):
        nota = miditones[j]
        if abs(colordict[i] - oldcolordict[i]) < umb:
            sendnotesdict[nota] = 0
        elif colordict[i] < minim:
            sendnotesdict[nota] = 0
        else:
            sendnotesdict[nota] = colordict[i]
    oldcolordict = colordict

    printdata()
    
#............................................SETUP
def setup():
    # setup
    size(width, height+127)
    frameRate(fps)
    # draw
    drawbackground(filename)
    # calculate color dicts
    generate_a()


#............................................DRAW
def draw():
    global colordict
    global oldcolordict
    global sendnotesdict
    global graytones
    global x
    global deltax
    # draw
    drawbackground(filename)
    
    # calculate new color dict
    generate_b()
    
    # calculate selected notes with rules
    calculate_sendnotesdict()

    #
    # draw line
    fill(60,60,30)
    noStroke()
    rect(1, 321, 640, 127)
    fill(0, 0, 0, 0)
    strokeWeight(1)
    stroke(255, 0, 0, 180)
    rect(x - 1, 0, deltax + 1, height)
    # draw labels
    fill(255, 255, 0)
    label1 = "min(v/b):" + str(minim) + "       umbral(n/m): " + str(umb) + \
        "\ntempo (,/.): " + str(tempo) + "          octave(up/down): " + str(octave)
    label1 += "           deltax (left/right):" + str(deltax)
    text(label1, 10, 340)

    # draw notes:
    lista = colordict.keys()
    lista.sort()
    rectwidth = width / 5
    rectheight = 320 + (127/2)
    print("...........",lista)
    for j, i in enumerate(lista):
        fill(i)
        noStroke()
        rect(rectwidth*j, 321, 640/5, 127)
        print(graytones[i], colordict[i])
        radius = colordict[i]
        if radius == 0: 
            radius = 10
            noFill()
            stroke(255,255,0)
        ellipse(rectwidth*j+rectwidth/2, rectheight, radius, radius)
    # move to next pixel column
    x = x + deltax
    if x > width:
        x = 0
    delay(tempo)


def keyPressed():
    global colordict
    global oldcolordict
    global graytones
    global deltax
    global x
    global minim
    global umb
    global tempo
    global octave
    global filename
    global nobg
    
    if keyPressed:
        if key == "1":
            print("------------------image1--------------------")
            filename = "imagen.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "2":
            print("--------------------image2------------------------")
            filename = "viso_del_marques_peque.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "3":
            print("--------------------------------------------------")
            filename = "prueba_vacio.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "4":
            print("--------------------------------------------------")
            filename = "viso_del_marques_peque.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "9":
            nobg = False
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "0":
            nobg = True
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "m":
            umb += 1
            if umb > 100:
                umb = 100
        if key == "n":
            umb -= 1
            if umb < 0:
                umb = 0
        if key == "b":
            minim += 1
            if minim > 100:
                minim = 100
        if key == "v":
            minim -= 1
            if minim < 0:
                minim = 0
        if key == ".":
            tempo += 25
        if key == ",":
            tempo -= 25
            if tempo < 1:
                tempo = 1

    if key == CODED:
        if keyCode == RIGHT:
            deltax += 1
            if deltax > width / 2:
                deltax = width / 2
        if keyCode == LEFT:
            deltax -= 1
            if deltax < 1:
                deltax = 1
        if keyCode == UP:
            octave += 1
            if octave > 8:
                octave = 8
        if keyCode == DOWN:
            octave -= 1
            if octave < 0:
                octave = 0


def delay(time):
    current = millis()
    while millis() < current + time:
        millis()

