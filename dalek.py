import os
import sys
import termios
import fcntl

import platform
import time
import socket
import urllib
import re
import json

import pygame

import usb.core
import usb.util


# Protocol command bytes
DOWN    = 0x01
UP      = 0x02
LEFT    = 0x04
RIGHT   = 0x08
FIRE    = 0x10
STOP    = 0x20

DEVICE = None

exterminate = "ext1.wav"
dalekGun  = "dalekgun.wav"


def usage():
    print ""
    print "Commands:"
    print "  W          - move up"
    print "  S          - move down"
    print "  D          - move right"
    print "  A          - move left"
    print "  Space      - stop"
    print "  F          - fire"
    print "  R          - reset to center position"
    print "  K          - kill program"    
    print ""


def setup_usb():
    # Tested only with the Cheeky Dream Thunder
    global DEVICE 
    DEVICE = usb.core.find(idVendor=0x2123, idProduct=0x1010)

    if DEVICE is None:
        raise ValueError('Missile device not found')

    # On Linux we need to detach usb HID first
    if "Linux" == platform.system():
        try:
            DEVICE.detach_kernel_driver(0)
        except Exception, e:
            pass # already unregistered    

    DEVICE.set_configuration()


def send_cmd(cmd):
    DEVICE.ctrl_transfer(0x21, 0x09, 0, 0, [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])


def play_sound(wavFile):
	if os.path.isfile(wavFile):
		pygame.init()
		sound = pygame.mixer.Sound(wavFile)
		sound.play()

		    
def getch():
	fd = sys.stdin.fileno()
	
	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)

	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

	try:
		while 1:
			try:
				c = sys.stdin.read(1)
				break
			except IOError: pass
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
	return c


def listen():
	while 1:
		x = getch()
		if x == 'w':
			send_cmd(UP)
		if x == 'a':
			send_cmd(LEFT)	
		if x == 's':
			send_cmd(DOWN)
		if x == 'd':
			send_cmd(RIGHT)
		if x == ' ':
			send_cmd(STOP)
		if x == 'f':
			send_cmd(FIRE)
			play_sound(dalekGun)
			time.sleep(5)
			termios.tcflush(sys.stdin, termios.TCIOFLUSH)
		if x == 'r':
			send_cmd(LEFT)
			time.sleep(6)
			send_cmd(DOWN)
			time.sleep(1)
			send_cmd(RIGHT)
			time.sleep(3)
			send_cmd(UP)
			time.sleep(.5)
			send_cmd(STOP)
			termios.tcflush(sys.stdin, termios.TCIOFLUSH)
		if x == 'k':
			print""
			print "SHUT DOWN SEQUENCE INITIATED"
			break
			


def main(args):
	play_sound(exterminate)	
	usage()
        setup_usb()
	listen()
	sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
