"""This script launches a window in which the procedure of the robot is explained"""

import os
import random
import tkinter as tk
from PIL import ImageTk, Image

class Exp:
    """This class launches a window on which is displayed and explained how the robot paints"""

    def __init__(self):
        # COLORS #########################
        # the background colors of the color palette backgrounds
        self.color_bgds = [[None, None, None], [None, None, None]]
        # the colors of the color palette
        self.colors = [["#E84427", "#FF801C", "#F5EC1B"], ["#477D32", "#246CEA", "#000000"]]
        # the colors used for designing the application window
        # background color, outline color, default color
        self.design_colors = ["#E6FAFF", "#A0E1FF", "#FFFFFF"]
        # the color being used right now
        self.current_color = self.design_colors[2]

        # font used
        self.normal_font = ("Engel", 16, "bold")
        self.big_font = ("Engel", 20, "bold")

        # TAGS #####################
        self.field_tag = "field"
        self.bkd_tag = "bgd"

        # FIELDS #########################
        self.fields = [] # the draw fields
        # the dimensions of the different grids
        self.grid_dimensions = [16, 10, 3, 2] # draw col, draw rol, pal col, pal row

        # LAST ELEMENTS USED #########################
        self.last_bgd = None # last background changed
        self.last_field = [-1, -1] # last painted field
        self.last_color = [-1, -1] # last used color
        self.last_loaded_img = "" # path to the last loaded image

        # MAIN WIDGETS #################################
        self.window = tk.Tk() # application window
        self.left_frame = tk.Frame(master=self.window) # left frame
        self.right_frame = tk.Frame(master=self.window) # right frame

        # LEFT WIDGETS ###############################
        self.img_label = tk.Label(master=self.left_frame) # label displaying current painting
        # grid on which the robot's painting is shown
        self.canvas = tk.Canvas(master=self.left_frame)

        # RIGHT WIDGETS ###############################
        # canvas containing the upper part of the explanations displayed
        self.top_exp = tk.Canvas(master=self.right_frame)
        # label with the pointer image
        self.pointer_label = tk.Label(master=self.right_frame)
        # textarea displaying what the robot is processing
        self.inst_textarea = tk.Text(master=self.right_frame)
        # canvas containing the lower part of the explanations displayed
        self.bottom_exp = tk.Canvas(master=self.right_frame)

        # IMAGES #####################################
        # images must be stored in attributes or else they will disappear
        self.img = "" # the image being displayed right now
        self.pointer = "./ressources/nopointer.png" # the pointer image
        self.logo = "./ressources/logo.png" # the scienteens lab logo

        self.instructions = "" # the instructions the robot receives

        self.exp_pos_x = 0 # reference position for the layout of the explanation text

        # the different text widgets
        # they need to be stored because clearing the canvas and reputting
        # everything again when switching langage looks is visible
        # just adding the text in a different langage is no solution either
        # because the previous text will still be visible
        # this solution stores the text fields and goes modify the content during runtime so
        # that no visible blink happens or that no text stacking happens
        self.text_fields = []

        # LANGAGES ###############################
        self.langs = ["en","fr","de"] # available langages
        # one label for each langage on which the corresponding flag will be placed
        self.lang_labels = [tk.Label(self.right_frame), tk.Label(self.right_frame),
                            tk.Label(self.right_frame)]
        # the flag (image) of the different langages will be stored here
        self.lang_imgs = [None, None, None]
        self.curr_lang = self.langs[0] # the langage currently displayed
        self.prev_lang = "" # the langage previously used (necessary for layout)

        # EXECUTE ################################
        self.init_window() # initialise window
        self.init_widgets() # initialise widgets
        # get the minimal dimension of the application window
        self.min_dim = min(self.canvas.winfo_width(), self.canvas.winfo_height())
        self.draw_grids() # draw the different grids
        self.add_langs() # add the flags to the application
        self.update_explanations() # add the explanation
        self.start_new_sim() # load image into application and start running simulation

        self.window.mainloop() # initiates and keeps window alive (necessary)

    # LANGAGE + EXPLANATIONS #################################

    def add_langs(self):
        """adds the flags of available langages to the application and sets them up"""
        ratio = 0.06 # used to turn the images smaller
        # do the following once for each langage
        for i, _ in enumerate(self.lang_imgs):
            # open the flag of the current langage
            self.lang_imgs[i] = Image.open("./ressources/" + self.langs[i] + "_icon.png")
            # take the image's current size
            old_img_size = self.lang_imgs[i].size[0], self.lang_imgs[i].size[1]
            # calculate the size it gets when the ratio is applied
            size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)
            # resize the image
            self.lang_imgs[i] = ImageTk.PhotoImage(self.lang_imgs[i].resize(size, Image.ANTIALIAS))
            # add image to corresponding label
            self.lang_labels[i].configure(image=self.lang_imgs[i])
            # change the label's background color to the global background color
            self.lang_labels[i].configure(bg=self.design_colors[0])
            # add mouse event to switch langage when flag is clicked
            self.lang_labels[i].bind("<ButtonPress-1>",
                lambda event, lang=self.langs[i]: self.switch_lang(event, lang))
            # place the label
            self.lang_labels[i].place(x=630 + i * 50, y=0)

    def switch_lang(self, event, lang):
        """switch langage"""
        # event is not needed but the parameter is necessary because this function is a mouse event
        del event
        # check if the current langage is not the langage being switch to
        if self.curr_lang != lang:
            self.prev_lang = self.curr_lang # remember the last langage
            self.curr_lang = lang # update the current langages
            self.update_explanations() # update explanations

    def update_explanations(self):
        """adds or updates the displayed explanations to a new langage"""
        # here no for loop is being used because there is a slight difference between the different
        # explanation fields
        # paths to the files containing the explanations in current langage
        exp_p1 = "./exp_src/explanations/part1-" + self.curr_lang + ".txt"
        exp_p21 = "./exp_src/explanations/part2-1-" + self.curr_lang + ".txt"
        exp_p22 = "./exp_src/explanations/part2-2-" + self.curr_lang + ".txt"
        exp_p3 = "./exp_src/explanations/part3-" + self.curr_lang + ".txt"
        # content of the files containing the explanations
        p1_content = ""
        # the last line of the first part is stored because it needs to have its own style
        p1_last_line = ""
        p21_content = ""
        p22_content = ""
        p3_content = ""
        # open files and store content
        with open(exp_p1, "r") as txt_file:
            p1_content = txt_file.read()
            p1_last_line = p1_content.split("\n")[-1] # store last line
        with open(exp_p21, "r") as txt_file:
            p21_content = txt_file.read()
        with open(exp_p22, "r") as txt_file:
            p22_content = txt_file.read()
        with open(exp_p3, "r") as txt_file:
            p3_content = txt_file.read()
        # checks if the text fields have already been initialised -> update
        if self.text_fields:
            # the text widgets may need to be moved as the text is not equally big in each langage
            # here en is shorter than fr and de. fr and de are approximately the same
            # switching from or to eng -> move text
            # switching fr <-> de -> no move text
            move_x = 0
            if self.prev_lang == "en":
                move_x = 80
            if self.curr_lang == "en":
                move_x = -80
            # update the text
            self.top_exp.itemconfig(self.text_fields[0], text=p1_content)
            self.top_exp.itemconfig(self.text_fields[1], text=p1_last_line)
            self.top_exp.itemconfig(self.text_fields[2], text=p21_content)
            self.top_exp.move(self.text_fields[2], move_x, 0) # move text horizontally
            self.top_exp.itemconfig(self.text_fields[3], text=p22_content)
            self.bottom_exp.itemconfig(self.text_fields[4], text=p3_content)
        else:
            # create and add the explanation text to the text_fields list
            # being able to access them eases later modification
            # some text fields are tagged to modify their style during runtime
            # the x and y coordinates are relative to the label the text is in
            self.text_fields.append(
                self.top_exp.create_text(self.exp_pos_x, 100, text=p1_content, font=self.big_font))
            self.text_fields.append(
                self.top_exp.create_text(self.exp_pos_x, 136, text=p1_last_line,
                font=self.big_font, fill="#FF0000", tag="lastline"))
            self.text_fields.append(
                self.top_exp.create_text(int(self.exp_pos_x/2)+10, 240,
                text=p21_content, font=self.normal_font, tag="fill"))
            self.text_fields.append(
                self.top_exp.create_text(int(self.exp_pos_x*1.5), 215,
                text=p22_content, font=self.normal_font, tag="paint"))
            self.text_fields.append(self.bottom_exp.create_text(self.exp_pos_x, 80,
                text=p3_content, font=self.big_font))

    # WINDOW + WIDGETS ###########################

    def init_window(self):
        """initialise application window"""
        self.window.wm_attributes('-fullscreen','true') # set application to fullscreen
        self.window.resizable(width=False, height=False) # disable resizing
        self.window.title(string="Scienteens Pipetting") # change title
        self.window.update() # update internal values

    def init_widgets(self):
        """initialises most of the widgets and defines their layout"""
        pady = 15 # height padding
        height = self.window.winfo_height() - pady*2 # height (padding incl.)
        left_width = int (self.window.winfo_width() / 2.2) # width of left frame
        right_width = int (self.window.winfo_width() - left_width) # width of right frame

        # change the background of the different widgets to the same color
        self.window.configure(bg=self.design_colors[0])
        self.left_frame.configure(bg=self.design_colors[0])
        self.canvas.configure(bg=self.design_colors[0])
        self.right_frame.configure(bg=self.design_colors[0])
        self.top_exp.configure(bg=self.design_colors[0])
        self.bottom_exp.configure(bg=self.design_colors[0])

        # configure and place the widgets on the left side (left frame)
        self.left_frame.configure(width=left_width, height=self.window.winfo_height(), pady=pady)
        self.left_frame.grid(column=0,row=0)
        self.img_label.configure(bd=0)
        self.img_label.grid(column=0, row=0)
        self.canvas.configure(highlightthickness=0)
        self.canvas.grid(column=0, row=1)

        # configure and place the widgets on the right side (right frame)
        self.right_frame.configure(width=right_width, height=self.window.winfo_height())
        self.right_frame.grid(column=1,row=0)
        self.top_exp.configure(width=right_width, highlightthickness=0,
            height=int(self.window.winfo_height()/3))
        self.top_exp.pack()
        self.inst_textarea.configure(highlightthickness=0, width=20, height=15,
                                    font=self.big_font)
        self.inst_textarea.pack(pady=5)
        self.bottom_exp.configure(width=right_width, highlightthickness=0)
        self.bottom_exp.pack(pady=5)

        # load pointer and set up label containing image
        self.pointer = Image.open("./ressources/nopointer.png")
        old_img_size = self.pointer.size[0], self.pointer.size[1]
        ratio = 0.12
        size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)
        self.pointer = ImageTk.PhotoImage(self.pointer.resize(size, Image.ANTIALIAS))
        self.pointer_label.configure(image=self.pointer)
        self.pointer_label.configure(width=size[0], height=size[1])
        self.pointer_label.place(x=int(right_width*0.415),y=160)
        self.pointer_label.configure(bg=self.design_colors[0])

        # update the text reference x-coordinate
        self.exp_pos_x = int (right_width / 2)

        # load placeholder painting without displaying it
        # the dimensions of the painting are used to to create the different grids
        # a painting must be loaded to get the necessary values but displaying it is not necessary
        self.img = Image.open("./exp_src/placeholder.jpg")
        old_img_size = self.img.size[0], self.img.size[1]
        ratio = 0.6
        size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)

        # change the dimensions of the canvas containing the grids
        self.canvas.configure(width=left_width, height=height-size[1])

        self.window.update() # update widget values

        # load scienteen lab logo and place it on the bottom rights
        self.logo = Image.open(self.logo)
        old_img_size = self.logo.size[0], self.logo.size[1]
        ratio = 0.12
        size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)
        self.logo = ImageTk.PhotoImage(self.logo.resize(size, Image.ANTIALIAS))
        logo_canvas = tk.Canvas(self.window)
        logo_canvas.place(x=0, y=self.left_frame.winfo_height())
        logo_canvas.configure(bg=self.design_colors[0], highlightthickness=0)
        logo_label = tk.Label(logo_canvas)
        self.window.update()
        logo_canvas_width = logo_canvas.winfo_width()
        logo_canvas.configure(width=logo_canvas_width*0.7)
        logo_label.configure(bg=self.design_colors[0])
        logo_label.configure(image=self.logo)
        logo_label.place(x=size[0]/2.8, y=size[1]/2)

        self.window.update() # update internal values

    def draw_grids(self):
        """creates and draws the different grids and its widgets"""
        # DRAW GRID #####################################
        padding = 5 # padding used to create space between the different fields
        # side length of one field
        side_length = self.min_dim  / max(self.grid_dimensions[0], self.grid_dimensions[1]) - 3.7
        # calculate how to center the draw grid
        canvas_middle = int (self.canvas.cget("width")) / 2
        fields_width = self.grid_dimensions[0] * side_length
        start_left = canvas_middle - fields_width / 2 - padding

        # index the columns of draw grid
        stary_y = padding + 0.5 * side_length
        for i in range(self.grid_dimensions[0]):
            start_x = start_left + (i+1+0.5) * side_length + padding
            self.canvas.create_text(start_x, stary_y, text=str(i), tag="dcol"+str(i),
                font=self.normal_font)

        # index the rows of draw grid
        start_x = start_left + 0.5 * side_length + padding
        for i in range(self.grid_dimensions[1]):
            stary_y = padding + (i+1+0.5) * side_length
            self.canvas.create_text(start_x, stary_y, text=str(i), tag="drow"+str(i),
                font=self.normal_font)

        # draw and create the draw grid
        end_y = 0 # will be used to define the start of the color palette
        # iterate through each row of the draw grid
        for row in range(self.grid_dimensions[1]):
            fields_row = [] # the row will be stored in the fields matrix
            # the y-coordinates just need to be calculated once per row
            start_y = (row+1) * side_length + padding
            end_y = start_y + side_length - padding
            # iterate through each column of the draw grid
            for col in range(self.grid_dimensions[0]):
                # the x-coordinates need to be calculated with each column
                start_x = start_left + (col+1) * side_length + padding
                end_x = start_x + side_length - padding
                # create, draw, and store current field in current row
                fields_row.append(self.canvas.create_oval(start_x, start_y, end_x, end_y, \
                    fill=self.design_colors[2], tag=self.field_tag))
            # add row to fields matrix
            self.fields.append(fields_row)

        # COLOR PALETTE #############################################
        side_length = int (0.1 * self.min_dim) # define the lenght of one fields
        padding = 7 # padding used to create space between the different fields
        # calculate how to center color palette
        palette_width = self.grid_dimensions[2] * side_length
        start_left = canvas_middle - palette_width / 2

        # index the rows of draw grid
        start_x = start_left + 0.5 * side_length + padding
        for i in range(self.grid_dimensions[3]):
            stary_y = end_y + padding + (i+0.5) * side_length
            self.canvas.create_text(start_x, stary_y, text=str(i), tag="crow"+str(i),
                font=self.normal_font)

        # iterate through each row of the color palette
        for row in range(self.grid_dimensions[3]):
            start_y = end_y + padding
            end_y = start_y + side_length
            # iterate through each column of the color palette
            for col in range(self.grid_dimensions[2]):
                start_x = start_left + (col+1) * side_length
                end_x = start_x + side_length
                # add the color background
                self.color_bgds[row][col] = self.round_rectangle(s_x=start_x, s_y=start_y,\
                    e_x=end_x, e_y=end_y, radius=35, tag=self.bkd_tag)
                start_x += padding
                end_x -= padding
                # add the color field
                field = self.canvas.create_oval(start_x, start_y + padding, end_x, end_y - padding)
                self.canvas.itemconfig(field, fill=self.colors[row][col],
                                    outline=self.design_colors[1])

        # index the columns of draw grid
        stary_y = end_y + 0.3 * side_length
        for i in range(self.grid_dimensions[2]):
            start_x = start_left + (i+1.4) * side_length + padding
            self.canvas.create_text(start_x, stary_y, text=str(i), tag="ccol"+str(i),
                font=self.normal_font)

    # OTHER #######################################

    def round_rectangle(self, s_x, s_y, e_x, e_y, radius=25, color="", tag="", **kwargs):
        """creates and returns rounded rectangles"""
        # https://stackoverflow.com/questions/44099594/how-to-make-a-tkinter-canvas-rectangle-with-rounded-corners
        points = [s_x+radius, s_y,
                s_x+radius, s_y,
                e_x-radius, s_y,
                e_x-radius, s_y,
                e_x, s_y,
                e_x, s_y+radius,
                e_x, s_y+radius,
                e_x, e_y-radius,
                e_x, e_y-radius,
                e_x, e_y,
                e_x-radius, e_y,
                e_x-radius, e_y,
                s_x+radius, e_y,
                s_x+radius, e_y,
                s_x, e_y,
                s_x, e_y-radius,
                s_x, e_y-radius,
                s_x, s_y+radius,
                s_x, s_y+radius,
                s_x, s_y]
        # if no color has been passed, use default color
        if color == "":
            color = self.design_colors[2]
        return self.canvas.create_polygon(points, **kwargs, smooth=True, \
            outline=self.design_colors[1], fill=color, tags=tag)

    def start_new_sim(self):
        """loads a new painting and starts the simulation on that painting"""
        # reset the draw grid and the color palette backgrounds
        self.canvas.itemconfig(self.bkd_tag, fill=self.design_colors[2])
        self.canvas.itemconfig(self.field_tag, fill=self.design_colors[2])
        # pick a random painting
        items = os.listdir("./exp_src/pics") # go to the painting directory
        done = False # flag to know when a new painting has been found
        while not done: # repeat until new painting has been found
            # pick random painting in directory and check if it is different
            # from the one that was simulated just now
            rand_index = random.randrange(len(items))
            done = bool (self.last_loaded_img != items[rand_index])
        self.last_loaded_img = items[rand_index] # remember the path to the current painting
        code = self.last_loaded_img[:-4] # pick the code of the painting (remove extension)
        picture = "./exp_src/pics/" + str(code) + ".jpg" # path to picture
        instructions = "./exp_src/instructions/" + str(code) + ".txt" # path to instructions
        with open(instructions, "r") as txt_file: # open instructions
            self.instructions = txt_file.read() # store instructions
            self.inst_textarea.insert(tk.END, self.instructions) # display instructions
        # load image into the painting label
        self.img = Image.open(picture)
        old_img_size = self.img.size[0], self.img.size[1]
        ratio = 0.67
        size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)
        self.img = ImageTk.PhotoImage(self.img.resize(size, Image.ANTIALIAS))
        self.img_label.configure(image=self.img)
        self.run_sim() # start highlighting the instructions (start simulation)

    def run_sim(self):
        """starts highlighting the instructions and show how the robot reacts to them"""
        lines = self.instructions.split("\n") # split the instructions
        self.top_exp.itemconfig("lastline", fill="#FF0000") # turn last line red
        for line in lines: # iterate through each instructions
            if len(line) == 0: # if empty line -> eof
                continue # can be replaced with break
            # add a tag to every character in the first line
            self.inst_textarea.tag_add("highlight", "1.0", "2.0")
            # highlight every previously tagged character
            self.inst_textarea.tag_configure("highlight", background="#D3F527",
               foreground="black")
            if "fill" in line: # if command = fill
                self.top_exp.itemconfig("paint", fill="#000000") # disable the paint exp coloring
                self.top_exp.itemconfig("fill", fill="#FF0000") # color the fill explanation
                self.pointer = "./ressources/left.png" # path to left-pointer image
            if "paint" in line: # if command = paint
                self.top_exp.itemconfig("fill", fill="#000000") # disable the fill exp coloring
                self.top_exp.itemconfig("paint", fill="#FF0000") # color the paint explanation
                self.pointer = "./ressources/right.png" # path to right-pointer image
            # load pointer image only if current pointer is different
            if self.pointer_label.cget("image") != self.pointer:
                self.pointer = Image.open(self.pointer)
                old_img_size = self.pointer.size[0], self.pointer.size[1]
                ratio = 0.12
                size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)
                self.pointer = ImageTk.PhotoImage(self.pointer.resize(size, Image.ANTIALIAS))
                self.pointer_label.configure(image=self.pointer)
            self.read_line(line) # simulate current instruction
            if "fill" in line: # if instruction = fill, sleep a bit longer
                self.tksleep(1)
            self.tksleep(1) # sleep a bit
            self.inst_textarea.delete("1.0", "2.0")
        # disable explanation coloring
        self.top_exp.itemconfig("lastline", fill="#000000")
        self.top_exp.itemconfig("fill", fill="#000000")
        self.top_exp.itemconfig("paint", fill="#000000")
        # reset pointer
        self.pointer = Image.open("./ressources/nopointer.png")
        old_img_size = self.pointer.size[0], self.pointer.size[1]
        ratio = 0.12
        size = int(old_img_size[0] * ratio), int(old_img_size[1] * ratio)
        self.pointer = ImageTk.PhotoImage(self.pointer.resize(size, Image.ANTIALIAS))
        self.pointer_label.configure(image=self.pointer)
        self.tksleep(2) # sleep / pause 2 seconds
        self.start_new_sim()

    # https://stackoverflow.com/questions/10393886/tkinter-and-time-sleep
    def tksleep(self, seconds):
        """emulates time.sleep(seconds)"""
        milli_seconds = int(seconds*1000)
        root = tk._get_default_root('sleep')
        var = tk.IntVar(root)
        root.after(milli_seconds, var.set, 1)
        root.wait_variable(var)

    def read_line(self, line):
        """simulate robot following instruction"""
        words = line.split(" ") # split the words in a list
        # remove coloring of column/row highlighting
        self.canvas.itemconfig("dcol"+str(self.last_field[0]), fill="#000000")
        self.canvas.itemconfig("drow"+str(self.last_field[1]), fill="#000000")
        self.canvas.itemconfig("ccol"+str(self.last_color[0]), fill="#000000")
        self.canvas.itemconfig("crow"+str(self.last_color[1]), fill="#000000")
        if len(words) >= 3: # check if line is valid
            command = words[0]
            row = int (words[1])
            col = int (words[2])
            if command == "fill": # if command = fill
                if self.last_bgd: # reset color palette background if one background changed
                    self.canvas.itemconfig(self.last_bgd, fill=self.design_colors[2])
                self.current_color = self.colors[row][col] # update current color
                # change color palette background
                self.canvas.itemconfig(self.color_bgds[row][col], fill=self.current_color)
                self.last_bgd = self.color_bgds[row][col] # remember last background
                # highlight corresponding color palette indexes
                self.canvas.itemconfigure("ccol"+str(col), fill="#FF0000")
                self.canvas.itemconfigure("crow"+str(row), fill="#FF0000")
                self.last_color = [col, row] # remember last color used
            if command == "paint": # if command = paint
                # highlight corresponding draw grid indexes
                self.canvas.itemconfigure("dcol"+str(col), fill="#FF0000")
                self.canvas.itemconfigure("drow"+str(row), fill="#FF0000")
                # fill field
                self.canvas.itemconfig(self.fields[row][col], fill=self.current_color)
                self.last_field = [col, row] # remember last field painted

exp = Exp()
