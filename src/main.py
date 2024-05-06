#-------------------------------------------------------------------------------
# Name:        Image Editor
# Purpose:     Learn Tkinter GUI
#
# Author:      Nikola Jovanovic
#
# Created:     05/05/2024
# Copyright:   (c) etfovac 2024
# Licence:     <MIT>
#-------------------------------------------------------------------------------

import sys
import os
import datetime
import time
from tkinter import filedialog
from tkinter import ttk
import tkinter
from PIL import Image, ImageTk
sys.path.append(os.path.abspath(".."))
import img.config

class ImageEditorGUI():
    def __init__(self, title):
        self.root = tkinter.Tk()
        self.root.title(title)
        self.root.protocol('WM_DELETE_WINDOW', self.Stop)
        self.root.eval('tk::PlaceWindow . center')
        self.frame = ttk.Frame(self.root)

        self.input_filepath = os.path.expandvars("%userprofile%\\Pictures")
        self.prop = img.config.Prop()
        self.root.minsize(self.prop.ImgSize.Small[0],self.prop.ImgSize.Small[1])
        self.root.maxsize(self.prop.ImgSize.Large[0],self.prop.ImgSize.Large[1])

        self.menubar = tkinter.Menu()

        self.file_menu = tkinter.Menu(tearoff=False)
        self.file_menu.add_command(
            label="Open",
            accelerator="Ctrl+O",
            command=self.Open)
        self.root.bind_all("<Control-o>", lambda e: self.Open())
        self.root.bind_all("<Control-O>", lambda e: self.Open())
        self.file_menu.add_command(
            label="Save As...",
            state=tkinter.DISABLED,
            #command=self.Save_as
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Exit",
            accelerator="Ctrl+Q",
            command=self.Stop)
        self.root.bind_all("<Control-q>", lambda e: self.Stop())
        self.root.bind_all("<Control-Q>", lambda e: self.Stop())
        self.menubar.add_cascade(menu=self.file_menu, label="File")

        self.edit_menu = tkinter.Menu(tearoff=False)
        self.edit_menu.add_command(
            label="Resize...",
            command=self.ResizeOutputImage)
        self.menubar.add_cascade(menu=self.edit_menu, label="Edit")

        self.sett_menu = tkinter.Menu(tearoff=False)

        self.center_sel = tkinter.BooleanVar()
        self.center_sel.set(False)
        self.sett_menu.add_checkbutton(
            label="Center",
            variable = self.center_sel,
            command=self.Center
        )
        self.window_menu = tkinter.Menu(tearoff=False)
        self.win_size_sel = tkinter.IntVar()
        self.window_menu.add_radiobutton(
            label="Small",
            value=1,
            variable = self.win_size_sel,
            command=self.ResizeWindow)
        self.window_menu.add_radiobutton(
            label="Medium",
            value=2,
            variable = self.win_size_sel,
            command=self.ResizeWindow)
        self.window_menu.add_radiobutton(
            label="Large",
            value=3,
            variable = self.win_size_sel,
            command=self.ResizeWindow)
        self.sett_menu.add_cascade(menu=self.window_menu, label="Window")
        self.menubar.add_cascade(menu=self.sett_menu, label="Settings")

        self.root.config(menu=self.menubar)

        # canvas
        self.DispImage = None
        self.canvas = tkinter.Canvas(self.frame,
                                     width=self.prop.ImgSize.Medium[0],
                                     height=self.prop.ImgSize.Medium[1],
                                     #bg='white'
                                     )
        self.preview_size = (self.canvas.winfo_width(), self.canvas.winfo_height())

        # pack order: last item is first lost on resize
        self.status = StatusBar(self.frame)
        self.frame.pack(fill=tkinter.BOTH, expand=True)
        self.canvas.pack(anchor=tkinter.CENTER, fill=tkinter.BOTH, expand=True)

        self.UpdateStatusStrip("Load an image file")
        self.UpdateStatusInfo("File >> Open (Ctrl+O)")

        # Last: Center root window with eval (works only here)
        self.root.eval('tk::PlaceWindow . center')
        self.root.bind_all('<Configure>', self.On_Resize)

    def On_Resize(self,event):
        self.win_size_sel.set(0) # keeps size radiobuttons unchecked
        if self.preview_size != (self.canvas.winfo_width(), self.canvas.winfo_height()):
            self.preview_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
            #print(self.preview_size)
            self.GetPhotoImage()
            self.Display()
        if self.center_sel.get() and self.root.state()=="normal":
            geometries = Get_Window_Geometries(self.root)
            if geometries[0] != geometries[1]:
                self.Center()

    def ResizeWindow(self):
        #print("win_size sel {0}".format(self.win_size_sel.get()))
        match self.win_size_sel.get():
            case 1:
                win_size = self.prop.ImgSize.Small
            case 2:
                win_size = self.prop.ImgSize.Medium
            case 3:
                win_size = self.prop.ImgSize.Large
            case default:
                win_size = self.prop.ImgSize.Medium
        self.root.state("normal")
        self.root.geometry("{0}x{1}".format(win_size[0],win_size[1]))

    def Center(self):
        if self.center_sel.get():
            if self.root.state()!="normal":
                self.root.state("normal")
            self.root.geometry(Get_Window_Geometries(self.root)[1])

    def SelectFile(self):
        self.input_filepath = filedialog.askopenfilename(
            initialdir=self.input_filepath,
            parent=self.root,
            title="Browse File",
            filetypes=(
                ("JPEG Files", (self.prop.ImgType.JPEG, ".jpg")),
                ("All Files", "*.*")
            )
        )
        #print(self.input_filepath)
        # display original file name
        self.UpdateStatusStrip('{0}'.format(os.path.split(self.input_filepath)[1]))

    def GetPhotoImage(self):
        try:
            if os.path.isfile(self.input_filepath):
                img_ref = Image.open(self.input_filepath)
                self.root.title(self.input_filepath)
                # Shows original size
                self.UpdateStatusInfo('{0}×{1}'.format(img_ref.width, img_ref.height))
                # Resized to fit the canvas size
                img_ref.thumbnail(self.preview_size)
                self.prop.PreviewFile = "tmp"+os.path.splitext(self.input_filepath)[1]
                img_ref.save(self.prop.PreviewFile)
                img_ref.close()
                disp_file = self.prop.PreviewFile
                self.DispImage = ImageTk.PhotoImage(file=disp_file)
        except IOError as ioe:
            errlog='Unable to get: {0} ({1})'.format(self.input_filepath, str(ioe))
            self.UpdateStatusStrip(errlog)

    def Display(self):
        self.canvas.create_image(
            self.preview_size[0]/2, self.preview_size[1]/2,
            #anchor=tkinter.NW,
            image=self.DispImage)

    def Open(self):
        self.SelectFile()
        self.GetPhotoImage()
        self.Display()

    def ResizeOutputImage(self):
        self.root.update()
        print(self.canvas.winfo_width(), self.canvas.winfo_height())
        # TODO: Popup window

    def UpdateStatusStrip(self,line):
        self.status.left.config(text=line)
        #print("Status: {}".format(line))
    def UpdateStatusInfo(self,line):
        self.status.right.config(text=line)

    def Start(self):
        self.root.mainloop()

    def Stop(self):
        self.root.destroy()

class StatusBar(ttk.Frame):
    def __init__(self, root):
        ttk.Frame.__init__(self, root,
            #relief=tkinter.SUNKEN
            )
        self.left = ttk.Label(self, text = "")
        self.left.pack(side = tkinter.LEFT)
        self.right = ttk.Label(self, text = "")
        self.right.pack(side = tkinter.RIGHT)
        self.pack(fill = tkinter.X, side = tkinter.BOTTOM)

def Get_Window_Geometries(win):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    curr_win_x = win.winfo_x()
    curr_win_y = win.winfo_y()
    frm_width = win.winfo_rootx() - curr_win_x
    titlebar_height = win.winfo_rooty() - curr_win_y
    #print(frm_width, titlebar_height)
    window_width = win.winfo_width()  + 2*0
    window_height = win.winfo_height() + 0 + 0
    curr_geom_string = "{0}x{1}+{2}+{3}".format(
        window_width, window_height, curr_win_x, curr_win_y)
    #print(curr_geom_string)
    center_x = screen_width //2 - (window_width + 2*frm_width)//2
    center_y = screen_height//2 - (window_height + frm_width + titlebar_height)//2
    center_geom_string = "{0}x{1}+{2}+{3}".format(
        window_width, window_height, center_x, center_y)
    #print(center_geom_string)
    return (curr_geom_string, center_geom_string)

def TStamp():
    tstring=datetime.datetime.fromtimestamp(time.time())
    return tstring.strftime("%Y%m%d_%H%M%S")

def main():
    gui = ImageEditorGUI("Preview Image")
    gui.Start()

if __name__ == "__main__":
    main()
