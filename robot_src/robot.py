#!/usr/bin/env pybricks-micropython
"""This script controls the robot"""

import os
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor)
from pybricks.parameters import Port, Color, Button
from pybricks.tools import wait

class EV3Robot:
    """Manages the robot in movement (visible) and files manipulation (invisible)"""

    def __init__(self):

        # coordinates and dimensions of color palette and output paper
        self.pal_radius = 140 # distance (in degrees) between each color fields
        self.jump_dist = 33 # distance (in degrees) between each draw field
        self.draw_sy = 800 # start y-coordinate of draw grid
        self.draw_sx = 350 # start x-coordinate of draw grid

        # number of rows and columns
        self.pal_rows = 2
        self.pal_cols = 3
        self.draw_rows = 10
        self.draw_cols = 16

        # pipette properties
        self.pip_remains = 0 # how many draw fields the pipette can fill before being empty
        # degrees to spit for one draw field
        # 700 = max number of fields that can be drawn with one pipette
        # 600 = max number of fields that should be drawn with one pipette
        # increasing 600 to 700 turns the ejection so small that the result on paper is no longer ok
        self.pip_per_field = 700 / 600

        self.speed = 700 # moving speed
        self.next_code = 0 # code of next expected image
        self.last_color = [-1, -1] # column and row of last color used

        # ev3brick, motors, and sensors
        self.ev3 = EV3Brick() # ev3brick
        self.motor_a = Motor(Port.A) # motor moving whole body (vertical movement)
        self.motor_b = Motor(Port.B) # motor filling/emptying pipette
        self.motor_c = Motor(Port.C) # motor moving upper body (horizontal movement)
        self.motor_d = Motor(Port.D) # motor moving pipette up/down
        self.gear_s1 = ColorSensor(Port.S1) # color sensor for motor b and d
        self.gear_s2 = TouchSensor(Port.S2) # touch sensor for motor a
        self.gear_s4 = TouchSensor(Port.S4) # touch sensor for motor c

        # short term capacity before having to start drawing
        self.max_capacity = 2 # max painting that can be done serially
        self.curr_capacity = 0 # number of paintings in short memory
        # y-distance between each painting
        self.cap_jump_y = self.draw_rows * self.jump_dist + 200
        self.instructions = "" # can contain instruction for up to capacity (2) paintings
        # the codes of the different paintings to be printed are stored
        self.codes_being_printed = []

    # start position #######################################################

    def reset_coordinates(self):
        """moves the robot to the upper right corner and defines
        this position as starting position"""
        # best order of resetting is D > A > C > B
        # first reset pipette and syringe afterwards move robot
        # the other way around can cause the robot to get stuck
        # somewhere because the pipette is too low

        # Motor D
        self.motor_d.run(-self.speed)
        while self.gear_s1.color() != Color.YELLOW:
            wait(1)
        self.motor_d.hold()
        self.motor_d.reset_angle(0)
        self.motor_d.run_target(self.speed, 40)
        self.motor_d.reset_angle(0)

        # Motor A
        self.motor_a.run(-self.speed)
        while not self.gear_s2.pressed():
            wait(1)
        self.motor_a.hold()
        self.motor_a.reset_angle(0)

        # Motor B
        self.motor_b.run(self.speed)
        while self.gear_s1.color() != Color.BLUE:
            wait(1)
        self.motor_b.hold()
        self.motor_b.reset_angle(0)
        self.motor_b.run_target(self.speed, 15, wait=True)
        self.motor_b.reset_angle(0)

        # Motor C
        self.motor_c.run(self.speed)
        while not self.gear_s4.pressed():
            wait(1)
        self.motor_c.hold()
        self.motor_c.reset_angle(0)

    def go_start_pos(self):
        """robot goes back to starting point"""
        # the order is important. moving the pipette up first prevents it getting stuck somewhere
        self.motor_d.run_target(self.speed, 0)
        self.motor_a.run_target(self.speed, 0)
        self.motor_c.run_target(self.speed, 0)
        self.motor_b.run_target(self.speed, 0)

    # color palette #######################################################

    def go_to_color(self, col, row):
        """moves the robot to the color at the provided coordinates"""
        # col needs to be mirrored because robot starts painting from the right and not the left
        target_col = self.pal_cols - col - 1
        # calculate degrees it takes to go to color
        target_x = -(2*target_col+1) * self.pal_radius
        target_y = (2*row+1) * self.pal_radius
        self.motor_d.run_target(self.speed, 50, wait=True) # move pipette high enough to not collide
        # move body over color
        self.motor_a.run_target(self.speed, target_y, wait=True)
        self.motor_c.run_target(self.speed, target_x, wait=True)

    def take_color(self, nbr_fields):
        """fills the pipette with enough color for the provided
        number of fields"""
        self.motor_d.run_target(self.speed, 240, wait=True) # move pipette down
        target = -self.pip_per_field * nbr_fields # calc how many degrees to do
        self.motor_b.run_target(self.speed, target, wait=True) # fill pipette
        self.pip_remains = nbr_fields # remember for how many fields color was taken

    def fill(self, col, row, nbr_fields):
        """takes pipette to color and fills pipette"""
        # empty pipette. there is probably leftover color from before
        if self.last_color[0] != -1 and self.last_color[1] != -1:
            self.go_to_color(self.last_color[0], self.last_color[1])
            self.motor_d.run_target(self.speed, 240, wait=True)
            self.eject_color(self.pip_remains)
        self.go_to_color(col, row) # go to color
        self.take_color(nbr_fields + 200) # take more color than needed
        self.eject_color(170) # spits out the air with some color
        self.last_color = [col, row] # store last color used
        self.motor_d.run_target(self.speed, 0, wait=True) # lift pipette
        self.eject_color(1) # spits out the air with some color
        self.eject_color(1) # spits out the air with some color

    # draw grid #######################################################

    def go_to_drawing(self, col, row):
        """moves the robot to the coordinates provided. coordinates belong to drawing"""
        # counting starts on the left, but robot counts from the right
        # col needs to be mirrored
        target_col = self.draw_cols - col - 1
        target_row = row - 1 # not necessary, but better result
        # calc degrees to get to field (col, row)
        target_x = -(self.draw_sx + target_col * self.jump_dist)
        target_y = self.draw_sy + target_row * self.jump_dist \
            + self.curr_capacity * self.cap_jump_y
        # move body to draw field (col, row)
        self.motor_a.run_target(self.speed, target_y, wait=True)
        self.motor_c.run_target(self.speed, target_x, wait=True)

    def eject_color(self, nbr_fields):
        """pipettes enough color out to color the number of fields provided"""
        # calc degrees to spit right amount
        target = self.motor_b.angle() + self.pip_per_field * nbr_fields
        self.motor_b.run_target(self.speed, target, wait=True) # eject
        self.pip_remains = self.pip_remains - nbr_fields # update pip remains

    def color_field(self, col, row):
        """takes robot to drawing position and draws"""
        self.go_to_drawing(col, row) # go to draw field
        self.motor_d.run_target(self.speed, 260, wait=True) # move pipette down
        self.eject_color(1) # eject color
        self.motor_d.run_target(self.speed, 200, wait=True) # move pipette up

    # file management #######################################################

    def load_code(self):
        """prepares everything file management"""
        os.chdir("/home/robot") # go to home dir
        if "queue" not in os.listdir(): # check if queue dir does not exist
            os.mkdir("queue") # create queue dir
        save_read = False # flag to know if save file has been read
        queue = os.listdir("./queue") # get queue
        if queue: # check if there is a queue
            save_read = True # no need to read the save file
            # the next code is the first item in queue without extension
            self.next_code = queue[0][:-4]
            for item in queue: # iterate through items in queue
                item = item[:-4] # remove the extension of the filename (.txt)
                item = int(item) # convert filename to integer (filename = number)
                # compare with other items what item is the next in queue (asc order)
                self.next_code = min(item, int(self.next_code))
        while not save_read: # if queue is empty, wait for save.txt
            if "save.txt" in os.listdir(): # check if save.txt arrived
                # open save.txt through os, because python script can not read with built-in
                # file reader files received during runtime
                # workaround, because usual does not work
                next_code = os.popen("cat save.txt").read()
                self.next_code = int (next_code) # update next code
                save_read = True # update flag to continue program

    def add_instructions(self):
        """combines different instructions together to print more 
        than one painting at the same time"""
        filepath = "/home/robot/queue/" + str(self.next_code) + ".txt" # path to instructions
        # read + store instructions in global instructions
        self.instructions = self.instructions + os.popen("cat " + filepath).read()
        # add current code to the ones being printed
        self.codes_being_printed.append(self.next_code)
        self.next_code += 1 # update expecting code
        # add an in-between note to distinguish the paintings being printed
        self.instructions = self.instructions + "\nnext\n"
        self.curr_capacity += 1 # increment current capacity
        # check if robot has reached max capacity
        # prepare for printing
        if self.curr_capacity == self.max_capacity:
            self.go_start_pos() # go back to start position
            self.display_instructions() # display the user instructions before printing
            self.draw_paintings() # start printing
            self.codes_being_printed = [] # empty list with codes being printed

    def display_instructions(self):
        """edits the robots display with instructions.
        waits for instructions to be followed"""
        self.ev3.screen.clear() # clears the display
        # prints the code(s) being printed right now
        codes_printing = ""
        for code in self.codes_being_printed:
            codes_printing = codes_printing + str(code) + " "
        self.ev3.screen.print("code(s): " + codes_printing, sep='', end='\n')
        # asks user if material for printing is ready
        self.ev3.screen.print("check material", sep='', end='\n')
        # asks user to press the center button when ready
        self.ev3.screen.print("press center \nbutton when\n ready ", sep='', end='\n')
        # waits until button is pressed
        while Button.CENTER not in self.ev3.buttons.pressed():
            wait(1)
        self.ev3.screen.clear() # clears display
        # displays what painting is currently being done
        self.ev3.screen.print("current: " + codes_printing, sep=' ', end='\n')
        # calcs how many paintings follow the current one
        queue = len(os.listdir()) - self.curr_capacity
        # displays the queues length
        self.ev3.screen.print("queue: " + str(queue), sep=' ', end='\n')

    def draw_paintings(self):
        """opens next painting(s) in queue and paints them"""
        self.curr_capacity = 0 # resets capacity to 0
        # splits the global instructions into an iterable list
        instructions = self.instructions.split("\n")
        # iterates through each instruction
        for instruction in instructions:
            # if current line is "next", the next painting in short memory is starting
            if instruction == "next":
                # we already know that the next painting is being done by the robot
                # but curr_capacity is used to paint on the upper or lower plate
                self.curr_capacity += 1
                # remove current painting from queue and from printing list
                os.remove("/home/robot/queue/"+str(self.codes_being_printed[0])+".txt")
                self.codes_being_printed[0] = self.codes_being_printed[1]
            words = instruction.split(" ") # split the elements of each instruction
            # check if the instruction is valid.
            # instruction: command row col nbr_fields
            # nbr_fields is only there for the fill command
            if len(words) >= 3:
                command = words[0] # take the command
                row = int (words[1]) # take the row to act on
                col = int (words[2]) # take the col to act on
                if command == "fill": # command is fill
                    nbr_fields = int (words[3]) # take nbr_fields
                    self.fill(col, row, nbr_fields) # go fill pipette
                elif command == "paint": # command is paint
                    self.color_field(col, row) # go paint field
        if self.last_color[0] != -1 and self.last_color[1] != -1:
            self.go_to_color(self.last_color[0], self.last_color[1])
            self.motor_d.run_target(self.speed, 240, wait=True)
            self.eject_color(self.pip_remains)
        self.go_start_pos()
        self.curr_capacity = 0

    def run(self):
        """starts and runs the robot"""
        self.load_code() # load the expected code
        self.reset_coordinates() # define starting position
        os.chdir("/home/robot/queue") # go to queue directory
        update_display = True
        while True: # run forever (or until manually stopped)
            if str(self.next_code) + ".txt" in os.listdir():
                self.add_instructions() # add instructions of new painting
                update_display = True # set flag to true -> updates text on display
            if update_display: # if the display needs to be updated
                self.ev3.screen.clear() # clear display
                # display what robot is waiting for
                self.ev3.screen.print("waiting for " + str(self.next_code), sep='', end='\n')
                self.ev3.screen.print("waiting for " + str(2-self.curr_capacity)
                    + " more paintings", sep='', end='\n')
                update_display = False

robot = EV3Robot()
robot.run()
