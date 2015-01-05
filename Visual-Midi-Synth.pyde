# first of all, you should execute this command 
# to create a virtual midi device in the system
# sudo modprobe snd-virmidi
from themidibus import MidiBus

#add_library('video')
from processing.video import Capture

webcamlist = Capture.list()

for j, i in enumerate(webcamlist):
    print("{} {}".format(j, i))
cam = Capture(this, webcamlist[1])

width = 640
height = 320
x = 0
fps = 30
minim = 83
threshold = 0
deltax = 11
tempo = 1
octave = 4
nobg = False

filename = "imagen.jpg"
#filename = "webcam"
log = []

miditones = [1, 3, 6, 8, 10]  #pentatonic scale
miditones70 = [1,3,6,8,10,13,15,18,20,22,25, 27,30,32,34,37,39,42,44,46,49,51,54,56,58,61,63,66,68,70]
graytones = {}          # dict containing {miditone: graytone}
colordict = {}          # dict containing {color: nthresholder of pixels with this color}
sendnotesdict = {}      # dict containing {notes: velocity}
oldsendnotesdict = {}   # a copy of previous frame calculation
oldcolordict = {}       # a copy of previous frame calculation
cdict = {}

MidiBus.list()
myBus = MidiBus(this, "VirMIDI [hw:2,0,0]", "VirMIDI [hw:2,0,0]")

def drawbackground(filename):
    if filename == "webcam":
        if cam.available() == True:
            cam.read()
            cam.filter(GRAY)
            cam.filter(POSTERIZE, 5)
            image(cam, 0, -142)
    else:
        img = loadImage(filename)
        img.filter(GRAY)
        img.filter(POSTERIZE, 5)
        #background(img)
        image(img, 0, 0, 640, 320)

def generate_a():
    global oldcolordict
    global colordict
    global graytones
    global log
    global cdict

    if x == 0:
        log = []

    colorlist = []
    oldcolordict = {}
    # generate color list
    for x1 in range(width):
        for y1 in range(height):
            c = int(brightness(get(x + x1 - 1, y1)))
            if c not in colorlist:
                colorlist.append(c)

    # generate oldcolordict and cdict
    cdict = {}
    oldcolordict == {}
    for c in colorlist:
        oldcolordict[c] = 0
        cdict[c] = 0

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
    sorted_colors = colorlist
    sorted_colors.sort()
    # generate graytones
    for i, j in enumerate(sorted_colors):
        try:
            graytones[miditones[i]] = j
        except IndexError:
            print("Except", sorted_colors)

    print("colorlist --------------{}".format(sorted_colors))
    print("graytones --------------{}".format(graytones))

def generate_c():
    global x
    global cdict

    #colordict = {}

    colorlist = colordict.keys()
    # generate colordict
    for i in range(tempo):
        for y1 in range(height):
            c = int(brightness(get(x + tempo, y1)))   # change x :   x + i
            if c not in colordict.keys():
                colordict[c] = 1
            else:
                colordict[c] += 1
    # adding unfounded colors to dict
    for c in oldcolordict.keys():
        if c not in colordict.keys():
            colordict[c] = 0
   
def printdata():
    global colordict
    global sendnotesdict
    global miditones
    global graytones
    global nobg
    print("________________:"+str(nobg)+" "+str(tempo))
    print("    oldcolordict: "+sorted_dict2(oldcolordict))
    print("       colordict: "+sorted_dict2(colordict))
    print("___sendnotesdict: "+sorted_dict2(sendnotesdict))
    print("oldsendnotesdict: "+sorted_dict2(oldsendnotesdict))
    print("____   graytones: "+sorted_dict2(graytones))
    print("____   cdict: "+sorted_dict2(cdict))
    i = len(log)-1
    if i > -1:
        print("x:{} octave:{} miditones:{}".format(log[i][0], log[i][1], log[i][2]))

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
    global cdict
    
    cdict = {}
    # copy colordict for calculations
    for i in colordict.keys():
        cdict[i] = colordict[i]
    
    # apply bg rule
    if nobg == True:
        cdict[255] = 0

    #detect higher value color
    maximum = 0
    for i in colordict.values():
        if i > maximum:
            maximum = i
    #
    lista = cdict.keys()
    lista.sort()
    # map values in colordict to 0-127            
    for j, i in enumerate(lista):
        try:
            nota = miditones[j]
        except IndexError:
            #print("es un error", lista)
            nota = 1
            pass
        gray = graytones[nota]
        #print(nota,gray, colordict[i], maximum)
        try:
            cdict[i] = int(map(colordict[i], 0, maximum, 0, 127))
        except ValueError:
            cdict[i] = 0
        # apply minim and threshold filters
        if cdict[i] < minim:
            cdict[i] = 0
        #print(".......", i)
        #print(abs(colordict[gray]-oldcolordict[gray]))
        if abs(colordict[gray]-oldcolordict[gray]) < threshold:
            cdict[i] = 0

    # generate new dict with tones to send midi
    lista = cdict.keys()
    lista.sort()
    for j, i in enumerate(lista):
        try:
            nota = miditones[j]
        except IndexError:
            nota = 1
            #print("exception", lista)
            pass
        sendnotesdict[nota] = cdict[i]
    
    for k, v in sendnotesdict.iteritems():
        if v != 0:
            sendnote(0, k + 12 * octave, v)
            #print("NOTAAAAAAAAA", k, v)

#............................................SETUP
def setup():
    # setup
    size(width, height+137)
    frameRate(fps)
    # draw
    drawbackground(filename)
    # calculate color dicts
    generate_a()

#............................................DRAW
def draw():
    global oldcolordict
    global oldsendnotesdict
    global x
    global log
    
    # draw
    #if len(log) == 0:
    #    drawbackground(filename)
    
    drawtimeline()
    #printdata()
    drawgui()
    # calculate selected notes with rules
    if x%deltax == 0:
        print("---------{}---------------".format(filename))
        drawbackground(filename)
        # calculate new color dict
        generate_c()
        calculate_sendnotesdict()
        # store old send notes and log
        for i in sendnotesdict.keys():
            oldsendnotesdict[i] = sendnotesdict[i]
        # create a notedictator to store
        notedict = {}
        for i in miditones:
            notedict[i] = sendnotesdict[i]
        log.append((x, octave ,notedict))
        # store old colordict and reset colordict
        for i in colordict.keys():
            oldcolordict[i] = colordict[i]
        #printdata()
        drawlog()

    # move to next pixel column
    x = x + 1*tempo
    if x > width - width%deltax:
        x = 0
        log = []

    #print(x, x/deltax, (x/deltax)*deltax)



def drawtimeline():
    #
    # labels background
    noStroke()
    fill(60,22,0)
    rect(0,322, 640, 15)
    # current frame marker
    fill(240,90,0)
    rect(x-1,322, 3, 15)

    # draw variables labels
    fill(220)
    textSize(14)
    label1 = "min(v/b):" + str(minim) + " threshold(n/m): " + str(threshold)
    label2 = " octave(up/down): " + str(octave)
    label3 = " deltax (left/right):" + str(deltax)
    text(label1, 10, 333)
    text(label2, 320, 333)
    text(label3, 480, 333)
    

def drawgui():

    #printdata()
    #    
    # draw circles with notes:
    lista = colordict.keys()
    lista.sort()
    
    maxim = 0
    for i in lista: 
        if colordict[i] > maxim: 
            maxim = colordict[i]
    if maxim == 0:
        maxim = 1
    #print("maximo", maxim)

    rectwidth = width / len(lista)
    rectheight = 335 + (127/2)

    lista = colordict.keys()
    lista.sort()
        
    for j, i in enumerate(lista):
        # draw gray scale boxes
        fill(i+20,i+20,i+20)
        noStroke()
        rect(rectwidth*j, 335, 640/5, 127)
        # draw each circle
        stroke(0)
        radius = int(map(colordict[i], 0, maxim, 0, rectwidth))
        if i==255 and nobg==True:
            radius = 0
        fill(i)
        stroke(255-i)
        ellipse(rectwidth*j+rectwidth/2, rectheight, radius, radius)
        # if radius == 0:
        if colordict[i] == 0 or (i==255 and nobg==True): 
            stroke(240,90,0)
            fill(0)
            line((rectwidth*j+rectwidth/2)-10, rectheight-10,(rectwidth*j+rectwidth/2)+10, rectheight+10)
            line((rectwidth*j+rectwidth/2)+10, rectheight-10,(rectwidth*j+rectwidth/2)-10, rectheight+10)
        
        try:
            try:
                nota = miditones[j]
            except IndexError:
                nota = 1
            label1 = "{}:".format(str(nota + 12 * octave))
            label2 = " {}".format(sendnotesdict[nota])
            if sendnotesdict[nota] == 0:
                label2 = ""
                label1 = ""
        except KeyError:
            label1 = "@"
            label2 = "@@"
        #shadow
        fill(0, 0, 0)
        textSize(15)
        text(label1, rectwidth*j+2, rectheight+2)
        textSize(28)
        text(label2, rectwidth*j+2, rectheight+52)
        #yellow titles
        fill(255, 190, 0)
        textSize(15)
        text(label1, rectwidth*j, rectheight+0)
        textSize(28)
        text(label2, rectwidth*j, rectheight+50)

def drawlog():
    
    #
    # fade left side
    noStroke()
    fill(120,45,0,80)
    rect(0, -1, (x/deltax)*deltax - 2, 337)
    # # fade right side
    rect((x/deltax)*deltax+deltax + 2, 0, width-(x/deltax)*deltax + 3, 337)
    
    # draw log notes
    if log != []:
        for i in log:
            ix = i[0]
            ioctave = i[1]
            imiditones = i[2]
            lista = sendnotesdict.keys()
            lista.sort()
            for k, j in enumerate(lista):
                nota = miditones[k]
                try:
                    value = imiditones[j]
                except IndexError:
                    value = 0
                for color in graytones.keys():
                    if color == nota:
                        fill(graytones[color]) 
                
                base = ix - deltax - 3
                basey = k + 12 * ioctave
                val = int(map(value, 0, 127, 0, deltax))
                noStroke()
                rect(base, basey + 12 * k, val, 12)
    


def keyPressed():
    # global colordict
    # global oldcolordict
    # global graytones
    global deltax
    global x
    global minim
    global threshold
    global tempo
    global octave
    global filename
    global nobg
    global log
    
    if keyPressed:
        if key == "1":
            filename = "imagen.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "2":
            filename = "viso_del_marques_peque.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "3":
            filename = "prueba_vacio.jpg"
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "4":
            filename = "webcam"
            cam.start()
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
            threshold += 1
            if threshold > 127:
                threshold = 127
        if key == "n":
            threshold -= 1
            if threshold < 0:
                threshold = 0
        if key == "b":
            minim += 1
            if minim > 127:
                minim = 127
        if key == "v":
            minim -= 1
            if minim < 0:
                minim = 0
        if key == ".":
            tempo += 1
        if key == ",":
            tempo -= 1
            if tempo < 1:
                tempo = 1

    if key == CODED:
        if keyCode == RIGHT:
            x = 0
            deltax += 1
            if deltax > width / 2:
                deltax = width / 2
        if keyCode == LEFT:
            x = 0
            deltax -= 1
            if deltax < 1:
                deltax = 1
        if keyCode == LEFT or keyCode == RIGHT:
            log = []
        if keyCode == UP:
            octave += 1
            if octave > 8:
                octave = 8
        if keyCode == DOWN:
            octave -= 1
            if octave < 0:
                octave = 0

