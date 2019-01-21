import sys
from tkinter import filedialog

from tkinter import *
from tkinter.ttk import Frame, Label
from PIL import ImageTk, Image
import jpgcollectinfo

EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"
DEFAULTDIR = "D:\\temp\\kepek\\"

CANVAS_WIDTH = 500
CANVAS_HIGHT = 500

# Google Geocoding API key
GOOGLE_API_KEY = ""
#GOOGLE_API_KEY_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\keyfile.txt"
GOOGLE_API_KEY_FILE = "D:\\temp\\keyfile.txt"


current_tag=0
processed_tag_list = ()

def cb_file():
    global abl1
    global DEFAULTDIR
    print("cb file")
    #abl1.filename = filedialog.askopenfilename(initialdir = DEFAULTDIR,title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    abl1.filename = filedialog.askdirectory(initialdir=DEFAULTDIR, title="Select folder")
    print (abl1.filename)
    DEFAULTDIR=abl1.filename
    return

def cb_datafile():
    global abl1
    global EXIF_DB_FILE
    print("cb data file")
    abl1.dbfilename = filedialog.askopenfilename(initialdir = abl1.filename,title = "Select file",filetypes = (("EXIF db pickle","*.db"),("all files","*.*")))

    if( abl1.dbfilename == ""):
        EXIF_DB_FILE=DEFAULTDIR+"/"+"exif_db.db"

    else:
        EXIF_DB_FILE=abl1.dbfilename

    print(EXIF_DB_FILE)
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

    # quick sort by date
    jpgcollectinfo.sort_tags_byexifdate(new_processed_list)

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

def cb_quicknavi(position):
    global current_tag
    current_tag = int(position)-1
    cb_right()
    return


def update_address_labels():
    """
    Will update all google labels
    :return: nothing
    """
    global lbl_google0, lbl_google1, lbl_google2, lbl_google3, lbl_currentpicname
    global scl_quicknavi

    a_date = "   "+ processed_tag_list[current_tag]["EXIF DateTimeOriginal"].printable[:10]

    lbl_currentpicname["text"] = processed_tag_list[current_tag]["myfilename"] + "   " + str(current_tag) + " of " + str(len(processed_tag_list))


    scl_quicknavi.set(current_tag)

    try:
        print("Google0 {}".format(processed_tag_list[current_tag]["formatted_address_list"][0]))
        lbl_google0["text"] = processed_tag_list[current_tag]["formatted_address_list"][0] + a_date
    except KeyError:
        lbl_google0["text"] = "" + a_date
    except IndexError:
        lbl_google0["text"] = "" + a_date

    try:
        print("Google1 {}".format(processed_tag_list[current_tag]["formatted_address_list"][1]))
        lbl_google1["text"] = processed_tag_list[current_tag]["formatted_address_list"][1] + a_date
    except KeyError:
        lbl_google1["text"] = "" + a_date
    except IndexError:
        lbl_google1["text"] = "" + a_date

    try:
        print("Google2 {}".format(processed_tag_list[current_tag]["formatted_address_list"][2]))
        lbl_google2["text"] = processed_tag_list[current_tag]["formatted_address_list"][2] + a_date
    except KeyError:
        lbl_google2["text"] = "" + a_date
    except IndexError:
        lbl_google2["text"] = "" + a_date

    try:
        print("Google3 {}".format(processed_tag_list[current_tag]["formatted_address_list"][3]))
        lbl_google3["text"] = processed_tag_list[current_tag]["formatted_address_list"][3] + a_date
    except KeyError:
        lbl_google3["text"] = "" + a_date
    except IndexError:
        lbl_google3["text"] = "" + a_date



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
    global abl1
    global lbl_google0,lbl_google1,lbl_google2,lbl_google3
    global lbl_currentpicname
    global scl_quicknavi

    currentrow = 0

    processed_tag_list = jpgcollectinfo.read_list_from_file(EXIF_DB_FILE)

    # Is list OK, or is empty? Quit if empty
    if(len(processed_tag_list) < 1):
        exit(1)

    print(processed_tag_list[current_tag]["myfilename"])

    abl1 = Tk()

    # Creating first row of UI
    menubar = Menu(abl1)
    filemenu = Menu(menubar,tearoff = 0 )
    filemenu.add_command(label="Select folder ...", command=cb_file)
    filemenu.add_command(label="Select db file...", command=cb_datafile)
    filemenu.add_command(label="Save db ...", command=cb_save)
    filemenu.add_command(label="Quit", command=exit)

    menubar.add_cascade(label = "File", menu = filemenu)
    menubar.add_cascade(label = "Scan folder", command=cb_scan)
    menubar.add_cascade(label = "Rename source files", command=cb_rename)
    menubar.add_cascade(label="Help")

    abl1.config(menu=menubar)

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
    # slider for quick navi
    scl_quicknavi = Scale(abl1, orient=HORIZONTAL, length=300, to=len(processed_tag_list), command = cb_quicknavi)
    scl_quicknavi.set(current_tag)
    scl_quicknavi.grid(row=currentrow, column=1, columnspan=5)
    currentrow = currentrow + 1

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
    # which picture we are looking at
    lbl_currentpicname = Label (abl1, text = "currentpicname")
    lbl_currentpicname.grid(row=currentrow, column=0,columnspan=5)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_a = Label( abl1, text = " A ")
    lbl_a.grid( row = currentrow, column = 0)
    scl_withintime = Scale( abl1, orient=HORIZONTAL, length = 300, to=300 )
    scl_withintime.set(15)
    scl_withintime.grid( row = currentrow, column = 1, columnspan = 3)
    lbl_numberofpic = Label (abl1, text = " percen belül készült képek száma  xxxx db")
    lbl_numberofpic.grid( row = currentrow, column = 4)
    currentrow = currentrow + 1

    # Creating next row of UI
    lbl_renameto =     Label (abl1, text = "Rename to")
    lbl_renameto.grid( row =currentrow, column = 0 )
    entry_renameto =   Entry (abl1, text = "default rename to", width = 100)
    entry_renameto.grid( row = currentrow, column = 1, columnspan = 3 )
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