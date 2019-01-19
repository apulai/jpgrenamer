import sys
from tkinter import *
from tkinter.ttk import Frame, Label
from PIL import ImageTk, Image
import jpgcollectinfo

EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"
DEFAULTPIC = "D:\\temp\\kepek\\default.jpg"

CANVAS_WIDTH = 500
CANVAS_HIGHT = 500

current_tag=0
processed_tag_list = ()

def cb_file():
    print("cb file")
    return

def cb_scan():
    print("cb scan")
    return

def cb_updatedb():
    print("cb updatedb")
    return

def cb_save():
    print("cb save")
    return

def cb_rename():
    print("cb rename")
    return

def cb_start():
    print("cb start")
    global current_tag
    global processed_tag_list
    global can_maincanvas


    current_tag = 0
    im = load_image(processed_tag_list[current_tag]["myfilename"])
    can_maincanvas.image = ImageTk.PhotoImage(im)
    can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")

    update_address_labels()


    return

def cb_left():
    global current_tag
    global processed_tag_list
    global can_maincanvas
    print("cb left")

    if (current_tag>0):
        current_tag = current_tag -1
        im = load_image(processed_tag_list[current_tag]["myfilename"])
        can_maincanvas.image = ImageTk.PhotoImage(im)
        can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")
        update_address_labels()

    return


def cb_right():
    global current_tag
    global processed_tag_list
    print("cb right")

    if len(processed_tag_list)-1 > current_tag:
        current_tag = current_tag + 1
        im = load_image(processed_tag_list[current_tag]["myfilename"])
        can_maincanvas.image = ImageTk.PhotoImage(im)
        can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")
        update_address_labels()
    return


def cb_last():
    global current_tag
    global processed_tag_list
    print("cb last")

    if len(processed_tag_list) != current_tag:
        current_tag = len(processed_tag_list)-1
        im = load_image(processed_tag_list[current_tag]["myfilename"])
        can_maincanvas.image = ImageTk.PhotoImage(im)
        can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")
        update_address_labels()
    return

def update_address_labels():
    """
    Will update all google labels
    :return: nothing
    """
    global lbl_google0, lbl_google1, lbl_google2, lbl_google3

    print("Google0 {}".format(processed_tag_list[current_tag]["formatted_address_list"][0]))
    lbl_google0["text"] = processed_tag_list[current_tag]["formatted_address_list"][0]

    print("Google1 {}".format(processed_tag_list[current_tag]["formatted_address_list"][1]))
    lbl_google1["text"] = processed_tag_list[current_tag]["formatted_address_list"][1]

    print("Google2 {}".format(processed_tag_list[current_tag]["formatted_address_list"][2]))
    lbl_google2["text"] = processed_tag_list[current_tag]["formatted_address_list"][2]

    print("Google3 {}".format(processed_tag_list[current_tag]["formatted_address_list"][3]))
    lbl_google3["text"] = processed_tag_list[current_tag]["formatted_address_list"][3]

    return

def load_image(filename):
    """
    Will try to load an image and return a PIL object
    Currently will also resize the image to 20% of orig
    :param filename: name of the file to load
    :return: PIL image
    """
    try:
        fp = open(filename,"rb")
        im = Image.open(fp,"r")
        w = im.width
        h = im.height
        r1 = w / CANVAS_WIDTH
        r2 = h / CANVAS_HIGHT


        if( r1 > r2):
            if( r1 > 1 ):
                w = w * (1/r1)
                h = h * (1/r1)
        else:
            if( r2 > 1):
                w = w * (1 / r2)
                h = h * (1 / r2)

        size = int(w),int(h)
        print(size)
        im.thumbnail(size)
        return im
    except IOError:
        print("cannot create thumbnail for", filename)



def main():
    global processed_tag_list
    global current_tag
    global can_maincanvas
    global lbl_google0,lbl_google1,lbl_google2,lbl_google3

    currentrow = 0

    processed_tag_list = jpgcollectinfo.read_list_from_file(EXIF_DB_FILE)

    # Is list OK, or is empty? Quit if empty
    if(len(processed_tag_list) < 1):
        exit(1)

    print(processed_tag_list[current_tag]["myfilename"])

    abl1 = Tk()

    # Creating first row of UI
    btn_file = Button(abl1, text="File", command=cb_file)
    btn_scan = Button(abl1, text="Scan", command=cb_scan)
    btn_update = Button(abl1, text="Update Metadata DB", command=cb_updatedb)
    btn_save = Button(abl1,text="Save Metadata DB", command=cb_save)
    btn_rename = Button(abl1,text="Rename file", command=cb_rename)
    btn_file.grid   ( row=currentrow, column =0, sticky = W)
    btn_scan.grid   ( row=currentrow, column =1, sticky = W)
    btn_update.grid ( row=currentrow, column =2, sticky = W)
    btn_save.grid   ( row=currentrow, column =3, sticky = W)
    btn_rename.grid ( row=currentrow, column =4, sticky = W)
    currentrow = currentrow + 1

    # Creating next row of UI
    # This is a frame and a canvas in the frame
    frame_main = Frame(abl1)

    filename = processed_tag_list[current_tag]["myfilename"]
    im = load_image(filename)

    can_maincanvas = Canvas(frame_main, width=CANVAS_WIDTH, height=CANVAS_HIGHT, bg='white')
    can_maincanvas.image = ImageTk.PhotoImage(im)
    can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")

    frame_main.grid(row =currentrow, column = 0 , rowspan = 5, columnspan = 5, padx =10, pady =5)
    can_maincanvas.grid(row =0, column = 0 , rowspan = 1, columnspan = 1, padx =10, pady =5 )
    currentrow=currentrow+5

    # Creating next row of UI
    # next and previous buttons
    btn_start = Button(abl1, text="|<", command=cb_start)
    btn_left  = Button(abl1, text="<<", command=cb_left)
    btn_right = Button(abl1, text=">>", command=cb_right)
    btn_last = Button(abl1, text=">|", command=cb_last)
    btn_start.grid(row=currentrow, column=0)
    btn_left.grid (row=currentrow, column=1)
    btn_right.grid(row=currentrow, column=2)
    btn_last.grid (row=currentrow, column=3)
    currentrow = currentrow + 1


    # Creating next row of UI
    lbl_a = Label( abl1, text = " A ")
    lbl_a.grid( row = currentrow, column = 0)
    scl_withintime = Scale( abl1, orient=HORIZONTAL, showvalue=15 )
    scl_withintime.grid( row = currentrow, column = 1)
    lbl_numberofpic = Label (abl1, text = " belül készült képek száma  xxxx db")
    lbl_numberofpic.grid( row = currentrow, column = 2)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_renameto =     Label (abl1, text = "Rename to")
    lbl_renameto.grid( row =currentrow, column = 0 )
    entry_renameto =   Entry (abl1, text = "default rename to")
    entry_renameto.grid( row = currentrow, column = 1)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_google0 = Label (abl1, text = "Google0")
    lbl_google0.grid(row=currentrow, columnspan = 5)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_google1 = Label(abl1, text="Google1")
    lbl_google1.grid(row=currentrow, columnspan = 5)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_google2 = Label(abl1, text="Google2")
    lbl_google2.grid(row=currentrow, columnspan = 5)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_google3 = Label(abl1, text="Google3")
    lbl_google3.grid(row=currentrow, columnspan = 5)
    currentrow = currentrow + 1

    cb_start()

    abl1.mainloop()





if __name__ == '__main__':
    main()