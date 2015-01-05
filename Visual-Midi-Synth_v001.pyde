# first of all, you should execute this command 
# to create a virtual midi device in the system
# sudo modprobe snd-virmidi
from themidibus import MidiBus

from processing.video import Capture

webcamlist = Capture.list()
for j, i in enumerate(webcamlist):
    print("{} {}".format(j, i))
cam = Capture(this, webcamlist[1])

#MidiBus.list()
myBus = MidiBus(this, "VirMIDI [hw:4,0,0]", "VirMIDI [hw:4,0,0]")

width = 640
height = 320
x = 0
fps = 30
minim = 0
threshold = 0
deltax = 11
tempo = 1.00
poster = 5
octave = 4
nobg = False

filename = "imagen.jpg"
#filename = "webcam"
log = []

#miditones = [1, 3, 6, 8, 10]  #pentatonic scale
miditones = [1,3,6,8,10,13,15,18,20,22,25, 27,30,32,34,37,39,42,44,46,49,51,54,56,58,61,63,66,68,70]
graytones = {}          # dict containing {miditone: graytone}
colordict = {}          # dict containing {color: nthresholder of pixels with this color}
sendnotesdict = {}      # dict containing {notes: velocity}
oldcolordict = {}       # a copy of previous frame calculation
cdict = {}
colors = {} # colors[i]: colordict[i]-oldcolordict[i]

def drawbackground(filename):
    if filename == "webcam":
        if cam.available() == True:
            cam.read()
            cam.filter(GRAY)
            cam.filter(POSTERIZE, poster)
            image(cam, 0, -142)
    else:
        img = loadImage(filename)
        img.filter(GRAY)
        img.filter(POSTERIZE, poster)
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
    graytones = {}
    sorted_colors = colorlist
    sorted_colors.sort()
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
    global colordict

    colorlist = colordict.keys()
    # generate colordict
    
    for i in range(tempo):
        for y1 in range(height):
            c = int(brightness(get(x + i, y1)))   # change x :   x + i
            if c not in colordict.keys():
                colordict[c] = 1
            else:
                colordict[c] += 1
    # adding unfounded colors to dict
    for c in graytones.values():
        if c not in colordict.keys():
            colordict[c] = 0
   
def printdata():
    global colordict
    global sendnotesdict
    global miditones
    global graytones
    global nobg
    print("________________x"+str(x)+" "+str(nobg)+" "+str(tempo))
    print("    oldcolordict[gray]: "+sorted_dict(oldcolordict))
    print("       colordict[gray]: "+sorted_dict(colordict))
    print("_______   colors[gray]: "+sorted_dict(colors))
    print("___sendnotesdict[note]: "+sorted_dict2(sendnotesdict))
    print("graytones[note]:[gray]: "+sorted_dict2(graytones))
    print("           cdict[gray]: "+sorted_dict(cdict))
    
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

def calculate_colors():
    global colors

    lista = colordict.keys()
    lista.sort()

    colors = {}
    for i in lista:
        try:
            colors[i] = abs(colordict[i] - oldcolordict[i])
        except KeyError:
            pass

    # apply bg rule
    if nobg == True:
        #detect maximum gray
        maxgray = 0
        for i in colors.values():
            if i > maxgray:
                maxgray = i
        colors[maxgray] = 0

def calculate_sendnotesdict():
    global cdict
    global sendnotesdict

    calculate_colors()
    
    cdict = {}
    # copy colordict for calculations
    for i in colors.keys():
        cdict[i] = colors[i]

    #detect maximum (higher pixels values)
    maximum = 1
    for i in colors.values():
        if i > maximum:
            maximum = i
    
    lista = colors.keys()
    lista.sort()
    # map values in colordict to 0-127            
    for j, i in enumerate(lista):
        gray = i
        nota = miditones[j]
        colordif = colors[gray]
        #print(nota,gray, colordict[i], maximum)
        cdict[i] = int(map(colordif, 0, maximum, 0, 127))
        
        # apply minim and threshold filters
        if colordif < minim:
            cdict[i] = 0
        if colordif < threshold:
            cdict[i] = 0

    # generate new dict with tones to send midi
    lista = colors.keys()
    lista.sort()
    sendnotesdict = {}
    for j, i in enumerate(lista):
        if cdict[i] != 0:
            nota = miditones[j]
            sendnotesdict[nota] = cdict[i]
    
    for k, v in sendnotesdict.iteritems():
        if v != 0 and x != 0:
            sendnote(0, k + 12 * octave, v)
            #print("notaaaa-----{} {}".format(k + 12 * octave, v))

def createlog():
    global log
    # create a log
    notedict = {}
    for i in sendnotesdict.keys():
        notedict[i] = sendnotesdict[i]
    log.append((x, octave ,notedict))

def updatedicts():
    global oldcolordict
    # store old colordict and reset colordict
    for i in colordict.keys():
        oldcolordict[i] = colordict[i]

#............................................SETUP
def setup():
    # setup
    size(width, height+137)
    frameRate(fps)
    drawbackground(filename)
    generate_a()



#............................................DRAW
def draw():
    global colordict
    global x
    global log

    if x == 0:
    	drawbackground(filename)
    generate_c()
    drawtimeline()    

    if x%deltax == 0:
    	print("---{}------{}------{}".format(x, filename, sorted_dict(sendnotesdict)))
        
        drawbackground(filename)
        calculate_sendnotesdict()
        drawgui()
        
        createlog()
        drawlog()
        printdata()

    drawfastgui()
    drawknobs()
    if x%deltax == 0:
        for i in colordict.keys():
            colordict[i] = 0
    updatedicts()
    # move to next pixel column
    x = x + 1*tempo
    if x > width - width%deltax:
        x = 0
        log = []
    max_x = deltax*(width/deltax)
    if x > max_x:
    	x = 0
    	log = []
    #print("----------",x, x/deltax, (x/deltax)*deltax)

def drawknobs():
    #print("Knobs y sliders!!!!")
    pass

def drawtimeline():
    # labels background
    noStroke()
    fill(60,22,0)
    rect(0,322, 640, 30)
    # current frame marker
    fill(240,90,0)
    rect(x-1,322, 3, 15)

    # draw variables labels
    fill(220)
    textSize(14)
    label1 = "min(v/b):" + str(minim) + "  threshold(n/m): " + str(threshold)
    label1 += "   tempo(x/c): " + str(tempo) + "  octave(up/down): " + str(octave)
    label1 += "   deltax (left/right):" + str(deltax)
    text(label1, 10, 333)
    
def drawfastgui():
    lista = graytones.values()
    lista.sort()

    rectwidth = width / len(lista)
    rectheight = 335 + (127/2)
    
    for j, i in enumerate(lista):
        # draw gray scale boxes
        gray = i
        nota = miditones[j]
        try:
            colordif = abs(colordict[gray]-oldcolordict[gray])
        except KeyError:
            colordif = 0
        
        fill(255,255,0)
        stroke(255,225,0)
        label1 = "{}".format(colordif, colordict[i])
        textSize(15)
        text(label1, rectwidth*j, rectheight-50) 

    fill(255,0,0,75)
    stroke(255,0,0,75)
    line(x, 0, x, height)

def drawgui():
    calculate_colors()

    lista = colors.keys()
    lista.sort()

    rectwidth = width / len(lista)
    rectheight = 335 + (127/2)

    maxim = 1
    for i in lista:
        try:
            if colors[i] > maxim: 
                maxim = colors[i]
        except KeyError:
            pass
        
    for j, i in enumerate(lista):
        # draw gray scale boxes
        gray = i
        nota = miditones[j]
        
        try:
            lastvel = sendnotesdict[nota]
            colordif = colors[gray]
        except KeyError:
            colordif = 0
            lastvel = 0
        
        
        if gray == 255:
        	fill(gray-80,gray-120,gray-150)
        	border = 0
        else:
        	fill(gray+40,gray+20,gray-20)
        	border = 255
        noStroke()
        rect(rectwidth*j, 335, 640/len(lista), 127)
        
        # draw each circle
        stroke(border)
        radius = int(map(colordif, 0, maxim, 0, rectheight/4))
        fill(gray)
        ellipse(rectwidth*j+rectwidth/2, rectheight, radius, radius)
        # if radius == 0:
        if radius == 0: 
            stroke(240,90,0)
            fill(0)
            line((rectwidth*j+rectwidth/2)-10, rectheight-10,(rectwidth*j+rectwidth/2)+10, rectheight+10)
            line((rectwidth*j+rectwidth/2)+10, rectheight-10,(rectwidth*j+rectwidth/2)-10, rectheight+10)
        
        label1 = "{}:{}".format(nota, str(nota + 12 * octave))
        label2 = "{}".format(lastvel)

        if lastvel == 0:
            fill(100,0,0)
        else:
            fill(255, 190, 0)
        textSize(15)
        text(label1, rectwidth*j, rectheight+0)
        textSize(28)
        text(label2, rectwidth*j, rectheight+50)
        fill(0, 190, 0)

def drawlog():
    # fade left side
    noStroke()
    fill(120,45,0,80)
    rect(0, 0, (x/deltax)*deltax, 337)

    # # fade right side
    dx = (x/deltax)*deltax + deltax*tempo + 2
    size = width-dx
    rect(dx, 0, size, 337)
    
    # draw log notes
    if log != []:
        for i in log:
            ix = i[0]
            ioctave = i[1]
            imiditones = {}
            imiditones = i[2]
            lista = imiditones.keys()
            lista.sort()
            for k, j in enumerate(lista):
                nota = j
                value = imiditones[j]
                basex = ix - deltax - 3
                basey = nota + 12 * ioctave
                val = int(map(value, 0, 127, 0, deltax))
                if val > 0: val += 1
                try:
                    fill(graytones[nota]) 
                    noStroke()
                    rect(basex, basey + 12 * nota, val, 12)
                except KeyError:
                    print("keyerror en draw log... {}".format(nota, graytones))
                    pass
    


def keyPressed():
    global deltax
    global x
    global minim
    global threshold
    global tempo
    global poster
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
            generate_a()
        if key == "2":
            filename = "viso_del_marques_peque.jpg"
            x = 0
            drawbackground(filename)
            generate_a()
        if key == "3":
            filename = "prueba_vacio.jpg"
            x = 0
            drawbackground(filename)
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
            poster += 1
            if poster > 50:
                poster = 50
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == ",":
            poster -= 1
            if poster < 2:
                poster = 2
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "c":
            tempo = tempo*2
            x = 0
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()
        if key == "x":
            tempo = tempo/2
            # draw
            drawbackground(filename)
            # calculate color dicts
            generate_a()

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

