import sys
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import Frame, Label
from PIL import ImageTk, Image
import datetime
import jpgcollectinfo

EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"
DEFAULTDIR = "D:\\temp\\kepek\\"

CANVAS_WIDTH = 500
CANVAS_HIGHT = 500

# Horizontal SIZE of GRID
GRID_HSIZE = 5

# Google Geocoding API key
GOOGLE_API_KEY = ""
# google_api_key_file = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\keyfile.txt"
GOOGLE_API_KEY_FILE = "D:\\temp\\keyfile.txt"

current_tag = 0
processed_tag_list = ()


def cb_file():
    global rootwindow
    global DEFAULTDIR
    print("cb file")
    # rootwindow.filename = filedialog.askopenfilename(initialdir = DEFAULTDIR,title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    rootwindow.filename = filedialog.askdirectory(initialdir=DEFAULTDIR, title="Select folder")
    print(rootwindow.filename)
    DEFAULTDIR = rootwindow.filename
    update_all_widgets()

    messagebox.showinfo("Information","Go and select a DB file then scan")

    return


def cb_datafile():
    global rootwindow
    global EXIF_DB_FILE
    print("cb data file")
    rootwindow.dbfilename = filedialog.askopenfilename(initialdir=rootwindow.filename, title="Select file",
                                                       filetypes=(("EXIF db pickle", "*.db"), ("all files", "*.*")))

    if (rootwindow.dbfilename == ""):
        EXIF_DB_FILE = DEFAULTDIR + "/" + "exif_db.db"

    else:
        EXIF_DB_FILE = rootwindow.dbfilename

    print(EXIF_DB_FILE)
    update_all_widgets()

    messagebox.showinfo("Information", "Check settings below and run scan...")

    return


def cb_scan():
    print("cb scan")
    global GOOGLE_API_KEY
    global processed_tag_list
    global scl_quicknavi

    GOOGLE_API_KEY = jpgcollectinfo.read_api_key_from_file()

    # List the files in JPG_DIR
    filelist = jpgcollectinfo.findjpg(DEFAULTDIR)
    number_of_files_found = len(filelist)
    print("Found {} files to scan".format(number_of_files_found))

    # Load the database file
    # We have data in this DB from the files scanned
    # earlier
    processed_tag_list = jpgcollectinfo.read_list_from_file(EXIF_DB_FILE)

    # We will narrow down the list of files
    # so we will check only new files not found in our DB
    jpgcollectinfo.remove_processed_files(filelist, processed_tag_list)
    print("Number of files to process after filtering: {}".format(len(filelist)))

    # Collect EXIF info from all JPG images
    taglist = jpgcollectinfo.gettags(filelist)

    # Filter down this list a bit, since I do not need this many info
    # Might want to skip this step
    smalllist = jpgcollectinfo.filtertags(taglist)

    # Add decimal GPS info to the list items
    # the new tags will be mylat and mylon
    jpgcollectinfo.add_decimal_GPS(smalllist)
    # Log on to google geomap API
    # to collect "address" information based on GPS coordinates
    jpgcollectinfo.add_google_maps_info(smalllist, GOOGLE_API_KEY)

    # Check
    jpgcollectinfo.printtags(smalllist)

    # We will have to concatenate
    # the list of fresh files
    # with the list of already processed files
    if (len(processed_tag_list) == 0):
        new_processed_list = smalllist
    else:
        new_processed_list = processed_tag_list + smalllist

    # Sort by date
    jpgcollectinfo.sort_tags_byexifdate(new_processed_list)

    # We are working with globals, so we need to have the result in a global var
    processed_tag_list = new_processed_list

    scl_quicknavi["to"] = len(processed_tag_list)
    # Display the first pic
    cb_start()
    return


def cb_updatedb():
    print("cb updatedb")
    return


def cb_save():
    print("cb save")
    jpgcollectinfo.sort_tags_byexifdate(processed_tag_list)
    jpgcollectinfo.save_list_to_file(processed_tag_list, EXIF_DB_FILE)
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

    update_all_widgets()

    return


def cb_left():
    global current_tag
    global processed_tag_list
    global can_maincanvas
    print("cb left")

    if (current_tag > 0):
        current_tag = current_tag - 1
        im = load_image(processed_tag_list[current_tag]["myfilename"])
        can_maincanvas.image = ImageTk.PhotoImage(im)
        can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")
        update_all_widgets()

    return


def cb_right():
    global current_tag
    global processed_tag_list
    print("cb right")

    if len(processed_tag_list) - 1 > current_tag:
        current_tag = current_tag + 1
        im = load_image(processed_tag_list[current_tag]["myfilename"])
        can_maincanvas.image = ImageTk.PhotoImage(im)
        can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")
        update_all_widgets()
    return


def cb_last():
    global current_tag
    global processed_tag_list
    print("cb last")

    if len(processed_tag_list) != current_tag:
        current_tag = len(processed_tag_list) - 1
        im = load_image(processed_tag_list[current_tag]["myfilename"])
        can_maincanvas.image = ImageTk.PhotoImage(im)
        can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")
        update_all_widgets()
    return


def cb_quicknavi(position):
    global current_tag
    current_tag = int(position) - 1
    cb_right()
    return

def cb_btn_google0():
    global btn_google0, entry_renameto
    entry_renameto.delete(0,END)
    entry_renameto.insert(0,btn_google0["text"])
    return

def cb_btn_google1():
    global btn_google1, entry_renameto
    entry_renameto.delete(0, END)
    entry_renameto.insert(0, btn_google1["text"])
    return

def cb_btn_google2():
    global btn_google2, entry_renameto
    entry_renameto.delete(0, END)
    entry_renameto.insert(0, btn_google2["text"])
    return

def cb_btn_google3():
    global btn_google3, entry_renameto
    entry_renameto.delete(0, END)
    entry_renameto.insert(0, btn_google3["text"])
    return

def cb_scale_withintime(position):
    update_all_widgets()

def number_of_pics_in_range():
    """
    Will return the number of pictures
    from currently showing pic
    to the value of
    :return:
    """
    global scl_withintime
    count = 0
    maxdelta = int(scl_withintime.get())
    maxdelta = datetime.timedelta(minutes=maxdelta)
    for tag in processed_tag_list[current_tag:]:
        delta = jpgcollectinfo.timedifference(tag, processed_tag_list[current_tag])
        #print(delta, maxdelta)
        if( delta < maxdelta ):
            count = count + 1
        if( delta > maxdelta):
            break
    return count

def update_all_widgets():
    """
    Will update all google labels, picture name, slider, settings info
    :return: nothing
    """
    global btn_google0, btn_google1, btn_google2, btn_google3
    global lbl_currentpicname, lbl_numberofpic
    global scl_quicknavi

    # Let's get the date of the picture
    try:
        a_date = "   " + processed_tag_list[current_tag]["EXIF DateTimeOriginal"].printable[:10]
    except KeyError:
        a_date = "1970:01:01 01:01:01"

    a_date2 = re.sub(":", "", a_date)
    a_date2 = a_date2+"_"

    # Let's update the name of the picture
    lbl_currentpicname["text"] = processed_tag_list[current_tag]["myfilename"] + "   " + str(
        current_tag) + " of " + str(len(processed_tag_list))

    # Let's update the setting labale
    txt = "Source folder: " + DEFAULTDIR + "           Exif DB file: " + EXIF_DB_FILE
    lbl_currentsettings["text"]=txt

    # Let's move the quick_navi slider to the right location
    # Maybe on a wrong place since can be moved with buttons
    scl_quicknavi.set(current_tag)

    #
    # Calculate the number of pic within range
    #
    lbl_numberofpic["text"] = " percen belül készült képek száma " + str(number_of_pics_in_range()) + " db"

    # Try to display the address
    # Can get both Key and Index error
    try:
        print("Google0 {}".format(processed_tag_list[current_tag]["formatted_address_list"][0]))
        btn_google0["text"] = a_date2 + processed_tag_list[current_tag]["formatted_address_list"][0]
    except KeyError:
        btn_google0["text"] = a_date2 + ""
    except IndexError:
        btn_google0["text"] = a_date2 + ""


    try:
        print("Google1 {}".format(processed_tag_list[current_tag]["formatted_address_list"][1]))
        btn_google1["text"] = a_date2 + processed_tag_list[current_tag]["formatted_address_list"][1]
    except KeyError:
        btn_google1["text"] = a_date2 + ""
    except IndexError:
        btn_google1["text"] = a_date2 + ""

    try:
        print("Google2 {}".format(processed_tag_list[current_tag]["formatted_address_list"][2]))
        btn_google2["text"] = a_date2 + processed_tag_list[current_tag]["formatted_address_list"][2]
    except KeyError:
        btn_google2["text"] = a_date2 + ""
    except IndexError:
        btn_google2["text"] = a_date2 + ""

    try:
        print("Google3 {}".format(processed_tag_list[current_tag]["formatted_address_list"][3]))
        btn_google3["text"] = a_date2 + processed_tag_list[current_tag]["formatted_address_list"][3]
    except KeyError:
        btn_google3["text"] = a_date2 + ""
    except IndexError:
        btn_google3["text"] = a_date2 + ""

    return


def load_image(filename):
    """
    Will try to load an image and return a PIL object
    Currently will also resize the image to 20% of orig
    :param filename: name of the file to load
    :return: PIL image
    """
    try:
        fp = open(filename, "rb")
        im = Image.open(fp, "r")
        w = im.width
        h = im.height
        r1 = w / CANVAS_WIDTH
        r2 = h / CANVAS_HIGHT

        if (r1 > r2):
            if (r1 > 1):
                w = w * (1 / r1)
                h = h * (1 / r1)
        else:
            if (r2 > 1):
                w = w * (1 / r2)
                h = h * (1 / r2)

        size = int(w), int(h)
        print(size)
        im.thumbnail(size)
        return im
    except IOError:
        print("cannot create thumbnail for", filename)


def main():
    global processed_tag_list
    global current_tag
    global can_maincanvas
    global rootwindow
    global btn_google0, btn_google1, btn_google2, btn_google3
    global lbl_currentpicname, lbl_renameto, lbl_currentsettings, lbl_numberofpic
    global entry_renameto
    global scl_quicknavi, scl_withintime

    currentrow = 0

    processed_tag_list = jpgcollectinfo.read_list_from_file(EXIF_DB_FILE)

    # Is list OK, or is empty? Quit if empty
    if (len(processed_tag_list) < 1):
        exit(1)

    print(processed_tag_list[current_tag]["myfilename"])

    rootwindow = Tk()

    # Creating first row of UI
    # This will be the menubar
    menubar = Menu(rootwindow)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Select folder ...", command=cb_file)
    filemenu.add_command(label="Select db file...", command=cb_datafile)
    filemenu.add_command(label="Save db ...", command=cb_save)
    filemenu.add_command(label="Quit", command=exit)

    menubar.add_cascade(label="File", menu=filemenu)
    menubar.add_cascade(label="Scan folder", command=cb_scan)
    menubar.add_cascade(label="Rename source files", command=cb_rename)
    menubar.add_cascade(label="Help")

    rootwindow.config(menu=menubar)

    # Creating next row of UI
    # This is a frame and a canvas in the frame
    frame_main = Frame(rootwindow)

    filename = processed_tag_list[current_tag]["myfilename"]
    im = load_image(filename)

    can_maincanvas = Canvas(frame_main, width=CANVAS_WIDTH, height=CANVAS_HIGHT, bg='white')
    can_maincanvas.image = ImageTk.PhotoImage(im)
    can_maincanvas.create_image(0, 0, image=can_maincanvas.image, anchor="nw")

    frame_main.grid(row=currentrow, column=0, rowspan=5, columnspan=GRID_HSIZE, padx=5, pady=5)
    can_maincanvas.grid(row=0, column=0, rowspan=1, columnspan=GRID_HSIZE, padx=5, pady=5)
    currentrow = currentrow + 5

    # Creating next row of UI
    # slider for quick navi
    # next and previous buttons
    frame_navi = Frame(rootwindow)
    btn_start = Button(frame_navi, text="|<", command=cb_start, anchor="e")
    btn_left = Button(frame_navi, text="<<", command=cb_left, anchor="e")

    scl_quicknavi = Scale(frame_navi, orient=HORIZONTAL, length=300, to=len(processed_tag_list), command=cb_quicknavi)
    scl_quicknavi.set(current_tag)

    btn_right = Button(frame_navi, text=">>", command=cb_right, anchor="w")
    btn_last = Button(frame_navi, text=">|", command=cb_last, anchor="w")

    btn_start.grid(row=0, column=0)
    btn_left.grid(row=0, column=1)
    scl_quicknavi.grid(row=0, column=2)
    btn_right.grid(row=0, column=3)
    btn_last.grid(row=0, column=4)
    frame_navi.grid(row=currentrow, column=0, columnspan=GRID_HSIZE, padx=5, pady=5)
    currentrow = currentrow + 1

    # Creating next row of UI
    # which picture we are looking at
    lbl_currentpicname = Label(rootwindow, text="currentpicname")
    lbl_currentpicname.grid(row=currentrow, column=0, columnspan=GRID_HSIZE)
    currentrow = currentrow + 1



    # Creating next row of UI
    # slider for how many to pics display at once
    lbl_a = Label(rootwindow, text=" A ")
    lbl_a.grid(row=currentrow, column=0)
    scl_withintime = Scale(rootwindow, orient=HORIZONTAL, length=300, to=300, command=cb_scale_withintime)
    scl_withintime.set(15)
    scl_withintime.grid(row=currentrow, column=1, columnspan=1)
    lbl_numberofpic = Label(rootwindow, text=" percen belül készült képek száma  xxxx db")
    lbl_numberofpic.grid(row=currentrow, column=2)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_renameto = Label(rootwindow, text="Rename to")
    lbl_renameto.grid(row=currentrow, column=0)
    entry_renameto = Entry(rootwindow, text="default rename to", width=100)
    entry_renameto.grid(row=currentrow, column=1, columnspan=GRID_HSIZE - 1)
    currentrow = currentrow + 1

    # Creating next row of UI
    btn_google0 = Button(rootwindow, text="Google0", command=cb_btn_google0)
    btn_google0.grid(row=currentrow, columnspan=GRID_HSIZE)
    currentrow = currentrow + 1

    # Creating next row of UI
    btn_google1 = Button(rootwindow, text="Google1", command=cb_btn_google1)
    btn_google1.grid(row=currentrow, columnspan=GRID_HSIZE)
    currentrow = currentrow + 1

    # Creating next row of UI
    btn_google2 = Button(rootwindow, text="Google2", command=cb_btn_google2)
    btn_google2.grid(row=currentrow, columnspan=GRID_HSIZE)
    currentrow = currentrow + 1

    # Creating next row of UI
    btn_google3 = Button(rootwindow, text="Google3", command=cb_btn_google3)
    btn_google3.grid(row=currentrow, columnspan=GRID_HSIZE)
    currentrow = currentrow + 1

    # Creating next row of UI
    # Name of working folder and DB
    txt = "Source folder: " + DEFAULTDIR + "       Exif DB file: " + EXIF_DB_FILE
    lbl_currentsettings = Label(rootwindow, text=txt)
    lbl_currentsettings.grid(row=currentrow, column=0, columnspan=GRID_HSIZE)
    currentrow = currentrow + 1

    cb_start()

    messagebox.showinfo("Information", "You can select a different working directory. \n Select a DB file. \n Run Scan ")

    rootwindow.mainloop()


if __name__ == '__main__':
    main()
