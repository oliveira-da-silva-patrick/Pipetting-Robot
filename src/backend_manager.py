"""This script contains functions that primarily manage the output files
and send the necessary files to the robot"""

import os
import subprocess
import random
import numpy as np
from PIL import Image as im

class Manager:
    """handles file manipulation and sends instructions to robot"""

    def __init__(self, painting=None, colors=None):

        # folders used for file manipulation
        self.output_folder = "./creations/"
        self.save_folder = "./examples/"

        # necessary information for the file creation
        self.painting = painting
        self.colors = colors

        # dimensions of color palette
        self.pal_dimensions = [3, 2] # col, row

        # the last loaded image
        self.last_loaded = ""

    def create_folder(self, path):
        """creates a new folder in the provided location if it does not exist yet"""
        if not os.path.exists(path):
            os.makedirs(path)

    def get_next_code(self, folder_path):
        """returns the code that will be generated next for a specific folder"""
        code = 0
        # update code if previous files have already been already generated in this folder
        if os.path.exists(folder_path):
            code = len(os.listdir(folder_path))
        return code

    def hex_to_rgb(self, hex_code):
        """converts a hex code to rgb"""
        r_value = int(hex_code[1:3], 16)
        g_value = int(hex_code[3:5], 16)
        b_value = int(hex_code[5:], 16)
        return r_value, g_value, b_value

    def create_jpg(self, jpg_path):
        """creates a jpg file of the painting drawn"""
        pixels = [] # matrix that will be turned to a jpg
        repeat = 40 # used to turn the image (40x10)x(40x16) -> 400x640
        # iterate through each row of the painting
        for row in self.painting:
            inner = [] # current row of the output matrix
            # for each field in current row add 40 times the same colour
            for field_color in row:
                color_in_hex = self.hex_to_rgb(field_color)
                for _ in range(repeat):
                    inner.append(color_in_hex)
            # add the current output row 40 times to the output matrix (1 row -> 40 rows)
            for _ in range(repeat):
                pixels.append(inner)
        pixels = np.array(pixels) # convert output matrix to array
        data = im.fromarray(pixels.astype(np.uint8), "RGB") # get image from array
        data.save(jpg_path) # save output image

    def count_color(self, color):
        """returns for how many fields a color is used"""
        max_count = 0
        # iterate through each row in the painting
        for i, _ in enumerate(self.painting):

            for j, _ in enumerate(self.painting[i]):
                curr_field_color = self.painting[i][j]
                # if current field has colour we are looking for, add 1 to the counter
                if curr_field_color == color:
                    max_count += 1
        return max_count

    def get_instructions(self):
        """returns the instructions"""
        commands = ""
        # iterate through each color
        for i, color in enumerate(self.colors):
            # transform (1x6) matrix to (2x3) matrix
            row = int (i / self.pal_dimensions[0])
            col = int (i % self.pal_dimensions[0])
            # get the nbr of occurences of current color
            max_count = self.count_color(color)
            # check if color has been used
            if max_count != 0:
                # add instruction to fill pipette
                commands += f"fill {row} {col} {max_count} \n"
                # iterate through each field of the painting
                for j, _ in enumerate(self.painting):
                    for k, _ in enumerate(self.painting[row]):
                        # if current field is colored with current color, add instruction
                        if self.painting[j][k] == color:
                            commands += f"paint {j} {k} \n"
        return commands

    def create_txt(self, txt_path, content):
        """creates a txt file at the given path with the given content"""
        with open(txt_path, "w") as file:
            # write method overwrites content of file if file already exists
            file.write(content)

    def send_to_robot(self, txt_path):
        """executes the bash script to send the instructions"""
        # execute shell script that sends instructions to robot
        subprocess.run([f"./bash_scripts/send.sh {txt_path}"], shell=True, check=False)

    def create_and_send_output(self):
        """creates the output files and sends txt file to robot"""
        self.create_folder(self.output_folder) # check and maybe create output folder
        code = self.get_next_code(self.output_folder) # get next expected code
        sub_path = self.output_folder + str(code) + "/" # create sub-folder path of output
        self.create_folder(sub_path) # create sub-folder (will contain output)
        jpg_path = sub_path + str(code) + ".jpg" # create .jpg output path
        self.create_jpg(jpg_path) # create .jpg output
        txt_path = sub_path + str(code) + ".txt" # create .txt output path
        commands = self.get_instructions() # create instructions
        self.create_txt(txt_path, commands) # create .txt output
        self.send_to_robot(txt_path) # send instructions (.txt) to robot

    def save(self):
        """saves an how-to paint this painting .txt file in the examples folder"""
        folder_path = "./examples/" # save output path
        self.create_folder(folder_path) # check and maybe create save folder
        code = self.get_next_code(folder_path) # get next code
        txt_path = folder_path + "/" + str(code) + ".txt" # create .txt path
        output = "" # empty output
        # iterate through fields of painting
        for row in self.painting:
            for color in row:
                # check if the color is a color of the palette or not
                if color in self.colors:
                    # if yes, add location of color to output
                    output += str(self.colors.index(color)) + "\n"
                # only non-palette color is white (non-filled fields)
                else:
                    # add -1 to output
                    output += str(-1) + "\n"
        # create a .txt file with the output content
        self.create_txt(txt_path, output)

    def load(self):
        """loads a random image into the draw grid"""
        # if the examples folder does not exist, return nothing
        if not os.path.exists("./examples/"):
            return None
        # get the files in the examples directory
        items = os.listdir("./examples/")
        done = False
        # take a random file until the new file is different from the last file
        while not done:
            rand_index = random.randrange(len(items))
            done = bool (self.last_loaded != items[rand_index])
        self.last_loaded = items[rand_index] # remember the last used file
        filepath = "./examples/" + self.last_loaded # create the path to the new file
        # create a matrix with the loaded instruction
        colors_used = []
        with open(filepath, "r", encoding="utf8", errors='ignore') as file:
            colors_used = file.read().split("\n")
        return colors_used
