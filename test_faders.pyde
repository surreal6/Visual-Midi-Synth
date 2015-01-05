from controlP5 import ControlP5
from controlP5 import Slider


s1 = 20
s2 = 100

def a_listener(e):
    print(str(e))

def b_listener(e):
    print(e)


def setup():
    cp5 = ControlP5(this)
    size(700,400)
    smooth()
    noStroke()
    cp5.addSlider("s1",10,200).linebreak().addListener(a_listener)
    cp5.addSlider("s2").setPosition(100,50).setRange(0,150).addListener(b_listener)
    cp5.end()
    cp5.getTooltip().setDelay(500)
    cp5.getTooltip().register("s1","Changes the size of the ellipse.")
    cp5.getTooltip().register("s2","Changes the Background")

def draw():
    background(s2)
    fill(255,100)
    ellipse(width/2, height/2, s1,s1)