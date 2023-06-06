"""This script mainly manages the ui part of this application"""
import tkinter as tk
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk
import backend_manager as bm

class UI:
    """This class runs the interface of the pipetting robot painting app"""

    def __init__(self):
        self.manager = bm.Manager() # responsible for backend operations
        # used to shift the mouse event point and make cursor more accurate. [x, y]
        self.shift_mouse = [0, 0]
        # colors used in the frontend design
        # default, background, outline, button, active button, send button
        self.design_colors = ["#FFFFFF", "#E6FAFF", "#A0E1FF", "#05AADC", "#9DCEC7", "#FF140B"]
        # colors in the color palette
        self.color_palette = ["#E84427", "#FF801C", "#F5EC1B", "#477D32", "#246CEA", "#000000"]
        self.curr_clr = self.design_colors[0] # the selected color
        # dimension of the different grids
        # cols of draw grid, rows of draw grid, cols of color palette, rows of color palette
        self.dimensions = [16, 10, 6, 1]
        # tags used to identify the different widgets and buttons
        self.tags = ["field", "color", "clr_bkg", "eraser", "erase_all",
                     "generate", "send", "save", "load", "text"]

        self.window = tk.Tk() # the application window
        self.canvas = tk.Canvas(master=self.window) # the canvas containing every widget

        # cursors used in this application
        self.cursors = ["@./ressources/brush_c1.png", "@./ressources/brush_c2.png",
                        "@./ressources/brush_c3.png", "@./ressources/brush_c4.png",
                        "@./ressources/brush_c5.png", "@./ressources/brush_c6.png",
                        "@./ressources/brush.png", "@./ressources/eraser.png"]
        self.curr_cur = self.cursors[-2] # the current cursor
        # application uses the default brush as cursor. does only work on mac
        self.window.config(cursor=self.curr_cur)
        self.shift_mouse = [-50, -50]

        self.setup_application_window()
        # layout and design values used throughout the application
        # minimum dimension, vertical margin, left margin, right margin, image size, font
        self.layout = [min(self.canvas.winfo_width(), self.canvas.winfo_height()),
                       int (0.06 * self.canvas.winfo_height()),
                       int (0.03 * self.canvas.winfo_width()),
                       int (0.125 * self.canvas.winfo_width()),
                       -1, ("Engel", 18, "bold")]
        self.layout[4] = int (0.23 * self.layout[0])
        # some widgets that need to be stored to avoid getting garbage collected
        self.widgets = [self.load_logo(), None, None]

        self.create_art_area()
        self.create_buttons()

        self.window.mainloop() # keeps the window alive and running. it is necessary

    def setup_application_window(self):
        """configures the application window and its canvas"""
        self.window.wm_attributes('-fullscreen','true') # set application to fullscreen
        # application is non-resizable. it being resizable may cause problems
        self.window.resizable(width=False, height=False)
        # application title is changed
        self.window.title(string="Scienteens Pipetting")
        # update the internal values of window and its widgets so that
        # other widgets can work with them
        self.window.update()
        # canvas uses 100% of window's height and width
        self.canvas.configure(width=self.window.winfo_width(), height=self.window.winfo_height())
        # the surrounding border is removed
        self.canvas.configure(highlightthickness=0)
        # change background color of canvas
        self.canvas.configure(bg=self.design_colors[1])
        # put the canvas on the application window (turn visible)
        self.canvas.pack()
        # update the internal values of window and its widgets so that
        # other widgets can work with them
        self.window.update()
        # bind mouse events to canvas
        self.canvas.bind(sequence="<B1-Motion>", func=self.mouse_drag_event)
        self.canvas.bind(sequence="<B1-ButtonRelease>", func=self.mouse_click_event)

    def create_round_rect(self, coords, radius=25, color="", tag="", **kwargs):
        """creates rounded rectangles"""
        s_x = coords[0]
        s_y = coords[1]
        e_x = coords[2]
        e_y = coords[3]
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
        # if no color is passed, the default button color is used
        if color == "":
            color = self.design_colors[0]
        # the rounded rectangle is put on the canvas
        self.canvas.create_polygon(points, **kwargs, smooth=True, \
            outline=self.design_colors[2], fill=color, tags=tag)

    def create_art_area(self):
        """creates the draw grid and the color palette"""
        # draw grid
        # a padding is applied on the draw fields.
        # this padding turns the in between fields space more natural.
        padding = 4
        # calculate how big a draw fields needs to be. the smaller dimension between
        # height and width must be considered
        side_length = self.layout[0] / max(self.dimensions[0], self.dimensions[1])
        # iterate through each row of draw grid
        for row in range(self.dimensions[1]):
            # the y-coordinates remain the same in the same row
            start_y = row * side_length + self.layout[1] + padding + 15
            end_y = start_y + side_length - padding
            # iterate through each column of draw grid
            for col in range(self.dimensions[0]):
                # the x-coordinates change with each column
                start_x = col * side_length + self.layout[2] + padding
                end_x = start_x + side_length - padding
                # add the field to the canvas
                self.canvas.create_oval(start_x, start_y, end_x, end_y,
                    tags=self.tags[0], fill= self.design_colors[0])

        # color palette
        draw_grid_width = self.dimensions[0] * side_length # width of draw grid
        side_length = int (0.15 * self.layout[0]) # size of color field in color palette
        padding = 10 # padding to make the color palette look more like a real color palette
        palette_width = self.dimensions[2] * side_length # width of color palette
        # left margin is recalculated. centers the color palette under the draw grid
        left_mar = int (self.layout[2] + (draw_grid_width - palette_width) / 2)
        # normally, you need to iterate through each row of the color palette.
        # but there is only one row. no loop is needed
        # the y-coordinates stay the same for the whole color palette
        start_y = self.canvas.winfo_height() - self.layout[1] - side_length * 1.2
        end_y = start_y + side_length
        # iterate through each column of the color palette
        for col in range(self.dimensions[2]):
            # the x-coordinates change with each column
            start_x = col * side_length + left_mar
            end_x = start_x + side_length
            # add a rounded rectangle as color palette background
            coords = [start_x, start_y, end_x, end_y]
            self.create_round_rect(coords=coords, tag=self.tags[2], radius=50)
            # add the color field to the color palette
            field = self.canvas.create_oval(start_x+padding, start_y+padding,
                end_x-padding, end_y-padding)
            # apply color to that color field
            self.canvas.itemconfig(field, fill=self.color_palette[col],
                                   outline=self.design_colors[2])
            # give that field a tag. necessary for mouse events
            self.canvas.itemconfig(field, tag=self.tags[1])

    def load_logo(self):
        """loads and places the scienteens lab logo"""
        # load the logo
        logo = Image.open("./ressources/logo.png")
        # resize the image
        logo = logo.resize((self.layout[4], self.layout[4]), Image.ANTIALIAS)
        # convert the image for Tkinter compatibility
        logo_img = ImageTk.PhotoImage(logo)
        # place the image
        pos_y = self.layout[1]
        pos_x = self.canvas.winfo_width() - self.layout[3] - self.layout[4] + 20
        self.canvas.create_image(pos_x, pos_y, image=logo_img, anchor="nw")
        # return image to prevent it from being garbage collected
        return logo_img

    def create_buttons(self, save=False):
        """creates the different buttons"""
        # button enabling eraser
        row = 0
        erase_text = "Erase / Entfernen / Effacer"
        self.create_button(row=row, text=erase_text, tag=self.tags[3])
        # button clearing draw grid
        row += 1
        erase_all_text = "Erase all / Alles entfernen / Effacer tout"
        self.create_button(row=row, text=erase_all_text, tag=self.tags[4])
        # button loading random image into draw grid
        row += 1
        load_text = "Random image / Zufälliges Bild / Image aléatoire"
        self.create_button(row=row, text=load_text, tag=self.tags[8])
        # button storing current draw grid. optional
        if save:
            row += 1
            save_text = "Save"
            self.create_button(row=row, text=save_text, tag=self.tags[7])
        # button sending draw grid to robot
        row += 1
        send_text = "Send to robot\nZum Roboter senden\nEnvoyer au robot"
        self.create_button(row=row+1.5, text=send_text, tag=self.tags[6])

    def create_button(self, row, text, tag):
        """creates one button"""
        # button design values
        btn_height = int (0.06 * self.canvas.winfo_height())
        btn_width = 2.1 * self.layout[4] # mac
        vertical_between = 10
        # buttons are centered with logo
        start_x = int (self.canvas.winfo_width() - self.layout[3] - self.layout[4] \
            - (btn_width - self.layout[4])/2) + 30
        end_x = start_x + btn_width
        center_x = start_x + btn_width / 2

        start_y = 2 * self.layout[1] + self.layout[4] + row * (btn_height + vertical_between)
        end_y = start_y + btn_height
        center_y = start_y + btn_height / 2
        # if the button is not the send button, a normal button is done
        if tag != self.tags[6]:
            coords = [start_x, start_y, end_x, end_y]
            # create the button
            self.create_round_rect(coords=coords, color=self.design_colors[3], tag=tag)
        # else, a special button is done
        else :
            # coordinates base off the ones of a normal button
            btn_width = end_x - start_x
            start_x = start_x + btn_width / 4
            end_x = end_x - btn_width / 4
            btn_size = end_x - start_x
            end_y = start_y + btn_size
            center_y = start_y + btn_size / 2
            center_x = start_x + btn_size / 2
            # create the button
            self.canvas.create_oval(start_x, start_y, end_x, end_y, \
                                fill=self.design_colors[5], tag=tag)
        # add text to button
        self.canvas.create_text(center_x, center_y, \
                tag=[tag, self.tags[9]], text=text, fill=self.design_colors[0], \
                font=self.layout[-1], justify="center")

    def mouse_drag_event(self, event):
        """acts when the mouse is dragged in the application"""
        # changes the cursor back to custom cursor
        # must be done because when application loses focus cursor is not loaded again automatically
        self.window.config(cursor="")
        self.window.config(cursor=self.curr_cur)
        # event location is shifted. necessary for custom cursors
        xpos = event.x + self.shift_mouse[0]
        ypos = event.y + self.shift_mouse[1]
        # takes every widget interacted with
        event_widgets = self.canvas.find_overlapping(xpos, ypos, xpos, ypos)
        # iterates through every widget interacted with
        for widget in event_widgets:
            # if the widget is a draw field, the field is filled the current color
            if self.tags[0] in self.canvas.itemcget(widget, "tag"):
                self.fill_field(widget)

    def mouse_click_event(self, event):
        """acts when the mouse is clicked in the application"""
        # changes the cursor back to custom cursor
        # must be done because when application loses focus cursor is not loaded again automatically
        self.window.config(cursor="")
        self.window.config(cursor=self.curr_cur)
        # event location is shifted. necessary for custom cursors
        xpos = event.x + self.shift_mouse[0]
        ypos = event.y + self.shift_mouse[1]
        # takes every widget interacted with
        event_widgets = self.canvas.find_overlapping(xpos, ypos, xpos, ypos)
        # iterates through every widget interacted with
        for widget in event_widgets:
            # if the widget is a draw field, the field is filled the current color
            if self.tags[0] in self.canvas.itemcget(widget, "tag"):
                self.fill_field(widget)
            # if the widget is a color field, the current color is changed
            elif self.tags[1] in self.canvas.itemcget(widget, "tag"):
                self.change_color(event_widgets[0], widget)
            # the following events have a break, because these events
            # should happen alone and only one
            # checks if the eraser has been enabled
            elif self.tags[3] in self.canvas.itemcget(widget, "tag"):
                self.enable_eraser()
                break
            # checks if the erase all button has been pressed
            elif self.tags[4] in self.canvas.itemcget(widget, "tag"):
                self.erase_all()
                break
            # checks if the send button has been pressed
            elif self.tags[6] in self.canvas.itemcget(widget, "tag"):
                self.confirm_send()
                break
            # checks if the save button has been pressed
            elif self.tags[7] in self.canvas.itemcget(widget, "tag"):
                self.save()
                break
            # checks if the load button has been pressed
            elif self.tags[8] in self.canvas.itemcget(widget, "tag"):
                self.load()
                break

    def reset_widget_bkgs(self):
        """resets the widget bkgs to default"""
        # picks every color palette field background
        bkgs = self.canvas.find_withtag(self.tags[2])
        # iterates through each background
        for bkg in bkgs:
            # resets the color of each color palette field background to default
            self.canvas.itemconfig(bkg, fill=self.design_colors[0])
        # picks every eraser button
        erasers = self.canvas.find_withtag(self.tags[3])
        # iterates through each eraser
        for eraser in erasers:
            # resets the color of each eraser button background to default
            self.canvas.itemconfig(eraser, fill=self.design_colors[3])
            # the text's color is changed to if not stopped
            break

    def change_color(self, background, color_field):
        """change the current color to the color of the passed color field"""
        # resets the widget backgrounds
        self.reset_widget_bkgs()
        # changes the current color to the selected color
        self.curr_clr = self.canvas.itemcget(color_field, "fill")
        # changes the background of that color field
        self.canvas.itemconfig(background, fill=self.curr_clr)
        # changes the current cursor and applies shift values
        for i, color in enumerate(self.color_palette):
            if color == self.curr_clr:
                self.curr_cur = self.cursors[i]
                break
        self.shift_mouse = [-50, -50]
        self.window.config(cursor=self.curr_cur)

    def fill_field(self, field):
        """fill the passed field with the current color"""
        self.canvas.itemconfig(field, fill=self.curr_clr)

    def enable_eraser(self):
        """enables the eraser"""
        # reset the widget backgrounds
        self.reset_widget_bkgs()
        # changes the color of the eraser button and its text
        self.canvas.itemconfig(self.tags[3], fill=self.design_colors[4])
        self.canvas.itemconfig(self.tags[9], fill=self.design_colors[0])
        # the eraser is enabled. the current color is set to the default color (white)
        self.curr_clr = self.design_colors[0]
        # changes the cursor and applies the shift values
        self.curr_cur = self.cursors[-1]
        self.shift_mouse = [-50, -40]
        self.window.config(cursor=self.curr_cur)

    def erase_all(self):
        """erases the drawing fields"""
        # prompts the user if the draw grid can be cleared
        answer = askyesno(title='Confirmation',
                          message='Are you sure that you want to erase your whole painting?')
        # if yes, clears the draw grid
        if answer:
            for widget in self.canvas.find_withtag(self.tags[0]):
                self.canvas.itemconfig(widget, fill=self.design_colors[0])

    def confirm_send(self):
        """prompts whether the user wants to send the painting or not"""
        # prompts the user if the drawing is done
        answer = askyesno(title='Confirmation',
                          message='Are you sure that you want to send your painting?')
        # if yes, continues
        if answer:
            self.__create_info_window()

    def __create_info_window(self):
        """creates a window informing the user what number (s)he's getting"""
        # create a new window for the product details
        self.widgets[1] = tk.Tk()
        # give dimensions and center window
        width = 370
        height = 180
        center_x = int(self.window.winfo_screenwidth()/2 - width/2)
        center_y = int(self.window.winfo_screenheight()/2 - height/2)
        geometry = f"{width}x{height}+{center_x}+{center_y}"
        self.widgets[1].geometry(newGeometry=geometry)
        # change title of window
        self.widgets[1].title(string="Info")
        # set title to non resizable
        self.widgets[1].resizable(width=False, height=False)
        # create the label for the info window
        info = "Code: " + str(self.manager.get_next_code("./creations/")) + "\n\n" \
            "The painting will be sent to robot." + "\n" \
            "Das Bild wird zum Roboter geschickt." + "\n" \
            "Le dessin va être envoyé au robot." + "\n"
        self.widgets[2] = tk.Label(master=self.widgets[1], text=info, font=self.layout[-1])
        self.widgets[2].pack()
        # create a button
        ok_btn = tk.Button(master=self.widgets[1], text="OK",
            command=self.__send)
        ok_btn.pack()
        # run and keep alive the info window
        self.widgets[1].mainloop()

    def __send(self):
        """kills info window and sends painting to robot"""
        # kill info window
        self.widgets[1].destroy()
        self.widgets[2] = None
        self.widgets[1] = None
        # send painting to robot
        manager = bm.Manager(self.get_matrix(), self.color_palette)
        manager.create_and_send_output()

    def save(self):
        """tells the manager to save the current painting"""
        manager = bm.Manager(self.get_matrix(), self.color_palette)
        manager.save()

    def load(self):
        """"loads one of the saved paintings"""
        # loads what colour each field of a painting has
        colors_used = self.manager.load()
        # if load returned nothing -> stop
        if not colors_used:
            return
        # counts how many fields have been dealt with
        count = 0
        # iterates through every draw field widget
        for widget in self.canvas.find_withtag(self.tags[0]):
            # stops at end-of-file (should the painting resolution be
            # smaller than the draw grid's resolution)
            if colors_used[count] == "":
                break
            # convert the text to a number
            color_index = int (colors_used[count])
            # pick the default color because the field has maybe not been filled
            color = self.design_colors[0]
            # if the position is not -1, the field has been filled
            if color_index != -1:
                # pick the color from the color palette at the given position
                color = self.color_palette[color_index]
            count += 1
            # fill the current draw field with the picked color
            self.canvas.itemconfig(widget, fill=color)

    def get_matrix(self):
        """returns how the painting has been coloured"""
        # picks every widget in the canvas
        widgets = self.canvas.find_all()
        # list with the painting in matrix form
        draw_grid = []
        # counts how many draw fields have been gone through
        count = 0
        # list with the colors used in the current row
        row = []
        # iterate through every widget
        for widget in widgets:
            # if current widget is a draw field
            if self.tags[0] in self.canvas.itemcget(widget, "tag"):
                count += 1
                # add color of this field to row list
                row.append(self.canvas.itemcget(widget, "fill"))
                # check if row is complete
                if count % self.dimensions[0] == 0:
                    # add row to draw grid matrix
                    draw_grid.append(row)
                    # empty current row
                    row = []
        # return draw grid matrix
        return draw_grid

ui = UI()
