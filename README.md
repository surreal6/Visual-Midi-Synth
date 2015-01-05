Visual-Midi-Synth
=================

This is a visual midi synthetizer, it takes an image and returns midi signals... 

This is programmed in py-processing, a pythonic version of processing, you need to install: 

http://py.processing.org/

Here you will find instructions on how to install and how to install libraries:
https://github.com/jdf/processing.py

You also need to install some libraries in your py-processing installation:

https://processing.org/reference/libraries/video/index.html
http://www.smallbutdigital.com/themidibus.php

How to make it sound!!
===============

This app only generate MIDI pulses, if you want to hear it, you need to plug the output into a sound synthetizer...

In linux, you need to run this command to create a virtual midi device (Virtual-Raw-MIDI):

sudo modprobe snd-virmidi

Then you can run Qjackctl and connect Virtual-Raw-MIDI OUT to MidiThrough IN and MidiThrough OUT to your preferred synth (ie: amsynth, qsynth, zynaddsubfx). 

You can connect more than one devices...

When running the app for the forst time, two device lists will be printed to let you choose how to configure midi and webcam 

--> Change values in line 11 and 14.


Visual to Midi Synth
------------------
Keys:

Change Image
1,2,3 : load images
4:		load webcam

Background mode
9: no bg mode off
0: no bg mode (exclude brigther color)

Change variables
x/c 		tempo
v/b 		minimum value
n/m 		threshold
,/. 		posterize
up/down 	octave
left/right 	deltax

if you change tempo you can expect lots of inestability...