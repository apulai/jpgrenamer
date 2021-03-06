import sys
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import Frame, Label
from PIL import ImageTk, Image
import datetime
import jpgcollectinfo
from functools import partial

EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"
DEFAULTDIR = "D:\\temp\\kepek\\"

#EXIF_DB_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\exif_db.db"
#DEFAULTDIR = "C:\\Users\\PatrikJelinko\\PycharmProjects\\kepatnevezo\\kepek\\"

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
CANVAS_BG_COLOUR = 'white'

# Horizontal SIZE of GRID
GRID_HSIZE = 5

GOOGLE_RECOMMENDATIONS = 4

# TODO: slider goes to 0 to n-1, text says 0 of n
# TODO: hunglish interface doesn't look good




class RenameUI:
    def __init__(self, canvas_width, canvas_height, canvas_bg_colour, grid_hsize, num_recommendations, dir, db_file):
        self.root_window = Tk()
        self.dir = dir
        self.db_file = db_file
        self.current_row = 0
        self.processed_tag_list = jpgcollectinfo.read_list_from_file(db_file)

        self.current_tag = 0
        # self.create_widgets()
        self.menu_bar = Menu()
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.filename = self.processed_tag_list[self.current_tag]["myfilename"]
        self.im = load_image(self.filename)
        self.main_frame = Frame()
        self.main_canvas = Canvas(self.main_frame, width=canvas_width, height=canvas_height, bg=canvas_bg_colour)
        self.grid_hsize = grid_hsize
        self.create_canvas()
        self.navi_frame = Frame()
        self.scl_quicknavi = Scale(self.navi_frame, orient=HORIZONTAL, length=300,
                                   from_=1, to=len(self.processed_tag_list), command=self.cb_quicknavi)
        self.lbl_currentpicname = Label(self.root_window, text="currentpicname")
        self.scl_withintime = Scale(self.root_window, orient=HORIZONTAL, length=300, to=300,
                                    command=self.cb_scale_withintime)
        self.lbl_numberofpic = Label(self.root_window, text=" percen belül készült képek száma  xxxx db")
        self.entry_renameto = Entry(self.root_window, text="default rename to", width=100)
        self.google_buttons = []
        self.lbl_current_settings = Label(self.root_window,
                                          text="Source folder: {}       Exif DB file: {}".format(dir, db_file))
        self.create_widgets(num_recommendations)



    def create_widgets(self, num_recommendations):
        self.create_menu()
        self.create_picture_slider()
        self.create_filename_area()
        self.create_google_buttons(num_recommendations)
        self.create_bottom_info_area()

    def create_menu(self):
        # Creating first row of UI
        # This will be the menubar
        self.file_menu.add_command(label="Select folder ...", command=self.cb_file)
        self.file_menu.add_command(label="Select db file...", command=self.cb_datafile)
        self.file_menu.add_command(label="Save db ...", command=self.cb_save)
        self.file_menu.add_command(label="Quit", command=exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Scan folder", command=self.cb_scan)
        self.menu_bar.add_cascade(label="Rename source files", command=self.cb_rename)
        self.menu_bar.add_cascade(label="Help")
        self.root_window.config(menu=self.menu_bar)

    def create_canvas(self):
        # Creating next row of UI
        # This is a frame and a canvas in the frame
       
        self.main_canvas.image = ImageTk.PhotoImage(self.im)
        self.main_canvas.create_image(0, 0, image=self.main_canvas.image, anchor="nw")

        self.main_frame.grid(row=self.current_row, column=0, rowspan=5, columnspan=self.grid_hsize, padx=5, pady=5)
        self.main_canvas.grid(row=0, column=0, rowspan=1, columnspan=self.grid_hsize, padx=5, pady=5)
        self.current_row = self.current_row + 5

    def create_picture_slider(self):
        # Creating next row of UI
        # slider for quick navi
        # next and previous buttons

        btn_start = Button(self.navi_frame, text="|<", command=self.cb_start, anchor="e")
        btn_left = Button(self.navi_frame, text="<<", command=self.cb_left, anchor="e")
        self.scl_quicknavi.set(self.current_tag)
        btn_right = Button(self.navi_frame, text=">>", command=self.cb_right, anchor="w")
        btn_last = Button(self.navi_frame, text=">|", command=self.cb_last, anchor="w")

        btn_start.grid(row=0, column=0)
        btn_left.grid(row=0, column=1)
        self.scl_quicknavi.grid(row=0, column=2)
        btn_right.grid(row=0, column=3)
        btn_last.grid(row=0, column=4)
        self.navi_frame.grid(row=self.current_row, column=0, columnspan=self.grid_hsize, padx=5, pady=5)
        self.current_row += 1

    def create_filename_area(self):
        # Creating next row of UI
        # which picture we are looking at
        self.lbl_currentpicname.grid(row=self.current_row, column=0, columnspan=self.grid_hsize)
        self.current_row += 1

        # Creating next row of UI
        # slider for how many to pics display at once
        lbl_a = Label(self.root_window, text=" A ")
        lbl_a.grid(row=self.current_row, column=0)

        self.scl_withintime.set(15)
        self.scl_withintime.grid(row=self.current_row, column=1, columnspan=1)
        self.lbl_numberofpic.grid(row=self.current_row, column=2)
        self.current_row += 1

        # Creating next row of UI
        lbl_renameto = Label(self.root_window, text="Rename to")
        lbl_renameto.grid(row=self.current_row, column=0)
        self.entry_renameto.grid(row=self.current_row, column=1, columnspan=self.grid_hsize-1)

        btn_ok = Button(self.root_window, text=" OK ", command=self.cb_rename)
        btn_ok.grid(row=self.current_row, column=4)
        self.current_row += 1

    def create_google_buttons(self, num_recommendations):
        for i in range(num_recommendations):
            self.google_buttons.append(Button(self.root_window, text="Google{}".format(i),
                                              command=partial(self.cb_btn_google, i)))
            self.google_buttons[i].grid(row=self.current_row, columnspan=self.grid_hsize)
            self.current_row += 1

    def create_bottom_info_area(self):
        # Creating next row of UI
        # Name of working folder and DB
        self.lbl_current_settings.grid(row=self.current_row, column=0, columnspan=self.grid_hsize)
        self.current_row += 1

    def cb_start(self):
        print("cb start")
        self.current_tag = 0
        self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
        self.main_canvas.image = ImageTk.PhotoImage(self.im)
        self.main_canvas.create_image(0, 0, image=self.main_canvas.image, anchor="nw")
        self.update_all_widgets()

    def cb_scale_withintime(self, position):
        self.update_all_widgets()

    def update_all_widgets(self):
        """
        Will update all google labels, picture name, slider, settings info
        :return: nothing
        """

        # Let's get the date of the picture
        try:
            a_date = "  " + self.processed_tag_list[self.current_tag]["EXIF DateTimeOriginal"].printable[:10]
        except KeyError:
            a_date = "1970:01:01 01:01:01"

        a_date2 = re.sub(":", "", a_date)
        a_date2 = a_date2 + "_"

        # Let's update the name of the picture
        self.lbl_currentpicname["text"] = self.processed_tag_list[self.current_tag]["myfilename"] + "   " \
                                          + str(self.current_tag+1) + " of " + str(len(self.processed_tag_list))

        # Let's update the bottom info area
        self.lbl_current_settings["text"] = "Source folder: " + self.dir + "           Exif DB file: " + self.db_file

        # Let's move the quick_navi slider to the right location
        # Maybe on a wrong place since can be moved with buttons
        self.scl_quicknavi.set(self.current_tag+1)

        #
        # Calculate the number of pic within range
        #
        self.lbl_numberofpic["text"] = " percen belül készült képek száma " + str(self.number_of_pics_in_range()) \
                                       + " db"

        # Try to display the address
        # Can get both Key and Index error
        for i, b in enumerate(self.google_buttons):
            try:
                print("Google{} {}".format(i, self.processed_tag_list[self.current_tag]["formatted_address_list"][i]))
                b["text"] = a_date2 + self.processed_tag_list[self.current_tag]["formatted_address_list"][i]
            except (KeyError, IndexError) as e:
                b["text"] = a_date2 + ""

    def number_of_pics_in_range(self):
        """
        Will return the number of pictures
        from currently showing pic
        to the value of
        :return:
        """
        count = 0
        max_delta = int(self.scl_withintime.get())

        max_delta = datetime.timedelta(minutes=max_delta).total_seconds()
        for tag in self.processed_tag_list[self.current_tag:]:
            delta = jpgcollectinfo.timedifference(tag, self.processed_tag_list[self.current_tag])
            if abs(delta.total_seconds()) < max_delta:
                count = count + 1

# TODO: APULAI, I don't think your implementation works reliably, check proposed mod above
# TODO: Also should it return 0 or 1 if we found only 1 picture (itself)???
# TODO: And why don't you consider pictures before the current one?
#        max_delta = datetime.timedelta(minutes=max_delta)
#        for tag in self.processed_tag_list[self.current_tag:]:
#            delta = jpgcollectinfo.timedifference(tag, self.processed_tag_list[self.current_tag])
#            # print(delta, max_delta)
#            if delta < max_delta:
#                count = count + 1
#            if delta > max_delta:
#                break
        return count

    def cb_file(self):
        print("cb file")
        self.root_window.filename = filedialog.askdirectory(initialdir=self.dir, title="Select folder")
        print(self.root_window.filename)
        self.dir = self.root_window.filename
        self.update_all_widgets()
        messagebox.showinfo("Information", "Go and select a DB file then scan")

    def cb_datafile(self):
        print("cb data file")
        self.root_window.dbfilename = filedialog.askopenfilename(initialdir=self.root_window.filename,
                                                                 title="Select file",
                                                                 filetypes=(("EXIF db pickle", "*.db"),
                                                                            ("all files", "*.*")))
        if self.root_window.dbfilename == "":
            self.db_file = self.dir + "/" + "exif_db.db"
        else:
            self.db_file = self.root_window.dbfilename
        print(self.db_file)
        self.update_all_widgets()

        messagebox.showinfo("Information", "Check settings below and run scan...")

    def cb_scan(self):
        print("cb scan")

        google_api_key = jpgcollectinfo.read_api_key_from_file()

        # List the files in JPG_DIR
        filelist = jpgcollectinfo.findjpg(self.dir)
        number_of_files_found = len(filelist)
        print("Found {} files to scan".format(number_of_files_found))

        # Load the database file
        # We have data in this DB from the files scanned
        # earlier
        self.processed_tag_list = jpgcollectinfo.read_list_from_file(self.db_file)

        # We will narrow down the list of files
        # so we will check only new files not found in our DB
        jpgcollectinfo.remove_processed_files(filelist, self.processed_tag_list)
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
        jpgcollectinfo.add_google_maps_info(smalllist, google_api_key)

        # Check
        jpgcollectinfo.printtags(smalllist)

        # We will have to concatenate
        # the list of fresh files
        # with the list of already processed files
        if len(self.processed_tag_list) == 0:
            new_processed_list = smalllist
        else:
            new_processed_list = self.processed_tag_list + smalllist

        # Sort by date
        jpgcollectinfo.sort_tags_byexifdate(new_processed_list)

        # We are working with globals, so we need to have the result in a global var
        self.processed_tag_list = new_processed_list

        self.scl_quicknavi["to"] = len(self.processed_tag_list)
        # Display the first pic
        self.cb_start()

    def cb_update_db(self):
        print("cb updatedb")
        # TODO: complete this

    def cb_save(self):
        print("cb save")
        jpgcollectinfo.sort_tags_byexifdate(self.processed_tag_list)
        jpgcollectinfo.save_list_to_file(self.processed_tag_list, self.db_file)

    def cb_rename(self):
        print("cb rename")
        # TODO: complete this

    def cb_left(self):
        print("cb left")
        if self.current_tag > 0:
            self.current_tag -= 1
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.main_canvas.image = ImageTk.PhotoImage(self.im)
            self.main_canvas.create_image(0, 0, image=self.main_canvas.image, anchor="nw")
            self.update_all_widgets()

    def cb_right(self):
        print("cb right")
        if len(self.processed_tag_list) - 1 > self.current_tag:
            self.current_tag += 1
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.main_canvas.image = ImageTk.PhotoImage(self.im)
            self.main_canvas.create_image(0, 0, image=self.main_canvas.image, anchor="nw")
            self.update_all_widgets()

    def cb_last(self):
        print("cb last")
        if len(self.processed_tag_list) != self.current_tag:
            self.current_tag = len(self.processed_tag_list) - 1
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.main_canvas.image = ImageTk.PhotoImage(self.im)
            self.main_canvas.create_image(0, 0, image=self.main_canvas.image, anchor="nw")
            self.update_all_widgets()

    def cb_quicknavi(self, position):
        self.current_tag = int(position) - 1
        self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
        self.main_canvas.image = ImageTk.PhotoImage(self.im)
        self.main_canvas.create_image(0, 0, image=self.main_canvas.image, anchor="nw")
        self.update_all_widgets()
        # self.cb_right()

    def cb_btn_google(self, button):
        self.entry_renameto.delete(0, END)
        self.entry_renameto.insert(0, self.google_buttons[button]["text"].lstrip())


def load_image(filename):
    """
    Will try to load an image and return a PIL object
    Currently will also resize the image to 20% of orig
    :param filename: name of the file to load
    :return: PIL image
    """
    # TODO: APULAI to move this into the class
    try:
        fp = open(filename, "rb")
        im = Image.open(fp, "r")
        w = im.width
        h = im.height
        r1 = w / CANVAS_WIDTH
        r2 = h / CANVAS_HEIGHT

        if r1 > r2:
            if r1 > 1:
                w = w * (1 / r1)
                h = h * (1 / r1)
        else:
            if r2 > 1:
                w = w * (1 / r2)
                h = h * (1 / r2)

        size = int(w), int(h)
        print(size)
        im.thumbnail(size)
        return im
    except IOError:
        print("cannot create thumbnail for", filename)
        return None


def main():
    c = RenameUI(CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG_COLOUR, GRID_HSIZE, GOOGLE_RECOMMENDATIONS, DEFAULTDIR,
                EXIF_DB_FILE)
    if len(c.processed_tag_list) < 1:
        exit(1)

    print(c.processed_tag_list[c.current_tag]["myfilename"])

    messagebox.showinfo("Information", "You can select a different working directory. \n Select a DB file. "
                                       "\n Run Scan ")
    c.root_window.mainloop()


if __name__ == '__main__':
    main()
