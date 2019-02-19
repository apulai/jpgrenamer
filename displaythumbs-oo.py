import sys
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tkinter.ttk import Frame, Label
from PIL import ImageTk, Image
import datetime
import jpgcollectinfo
from functools import partial

#EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"
#DEFAULTDIR = "D:\\temp\\kepek\\"

EXIF_DB_FILE = "D:\\kepek\\2017\\201708_Montenegro\\exif_db.db"
DEFAULTDIR = "D:\\kepek\\2017\\201708_Montenegro"

# EXIF_DB_FILE = "C:\\Users\\PatrikJelinko\\PycharmProjects\\jpgrenamer\\exif_db.db"
# DEFAULTDIR = "C:\\Users\\PatrikJelinko\\PycharmProjects\\kepatnevezo\\kepek\\"

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400
CANVAS_BG_COLOUR = 'white'

UI_LEFT = 0
UI_RIGHT = 1
# Horizontal SIZE of GRID
GRID_HSIZE = 5

GOOGLE_RECOMMENDATIONS = 4

class Publisher:
    # We use the observer pattern. notifier is the Subject where
    # observer object register
    def __init__(self, events):
        """
        This is the Subject or the central object which others observe
        We call it publisher here
        :param events: list of string for which you can register yourself and a callback
        """
        self.observer_subscribers = {event: dict()
                                     for event in events}

    def observer_get_subscribers(self, event):
        """ Returns the list of observers (subscribers) for a particular event """
        return self.observer_subscribers[event]

    def observer_register(self, event, who, callback=None):
        """
        :param event: Name of the event
        :param who: which instance is registering to this callback
        :param callback: what function to call in case of dispatch, if none is give we will try to call receive_message
        :return:
        """
        print("registering observer for {}, who {}, for event {}".format(self, who, event))
        if callback is None:
            callback = getattr(who, 'receive_message')
        self.observer_get_subscribers(event)[who] = callback

        print("\nShowing current registrations")
        for subscriber, callback in self.observer_get_subscribers(event).items():
            print("Event:{} Subscriber:{} Callback:{}".format(event, subscriber, callback))

    def observer_unregister(self, event, who):
        """ Unregisters an observer for an event """

        del self.observer_get_subscribers(event)[who]

    def observer_dispatch(self, sender, event, message):
        """ Dispatches the message to the observers about an event using the appropriate callback function """

        for subscriber, callback in self.observer_get_subscribers(event).items():
            if subscriber != sender:
                print("Dispatching message from {} to {}".format(sender, subscriber))
                callback(message)
            else:
                print("Not sending message when sender and subscriber are the same")


class ImageShowUI:

    def __init__(self, renameui_instance, pub):
        """
        :param renameui_instance: this is our parent object, we use it's variables
        :param pub: publisher we will send our messages to this guy
        """

        self.processed_tag_list = renameui_instance.processed_tag_list
        self.current_tag = 0
        self.myside=UI_LEFT
        self.current_row = 0
        self.grid_hsize = renameui_instance.grid_hsize
        self.num_recommendations = renameui_instance.num_recommendations
        self.canvas_width = renameui_instance.canvas_width
        self.canvas_height = renameui_instance.canvas_height
        self.canvas_bg_colour = renameui_instance.canvas_bg_colour
        # We use the observer pattern. Publisher is the central object
        # which will dispatch messages
        self.publisher = pub
        # Main global frame
        self.img_frame = Frame()
        # Canvas to draw into
        self.img_canvas = Canvas()
        # Picture name
        self.lbl_currentpicname = Label()

        # Navi frame
        self.navi_frame = Frame()
        # Google buttons
        self.google_buttons = []
        self.create_widgets()

    def create_widgets(self):
        self.create_image_area()
        self.create_pictitle()
        self.create_picture_slider()
        self.create_google_buttons()

    def create_image_area(self):
        """
        This is simply a canvas we will draw here the image
        :return:
        """
        self.img_canvas = Canvas(self.img_frame, width=self.canvas_width, height=self.canvas_height,
                                 bg=self.canvas_bg_colour)
        self.img_canvas.grid(row=0, column=0, rowspan=1, columnspan=self.grid_hsize, padx=5, pady=5)
        self.current_row = self.current_row + 5

    def create_pictitle(self):
        self.lbl_currentpicname = Label(self.img_frame, text="currentpicname")
        self.lbl_currentpicname.grid(column=0, row=self.current_row, columnspan=self.grid_hsize )
        self.current_row = self.current_row + 1

    def create_picture_slider(self):
        # Creating next row of UI
        # slider for quick navi
        # next and previous buttons

        self.navi_frame = Frame(self.img_frame)

        btn_start = Button(self.navi_frame, text="|<", command=self.cb_start, anchor="e")
        btn_left = Button(self.navi_frame, text="<<", command=self.cb_left, anchor="e")
        self.scl_quicknavi = Scale(self.navi_frame, orient=HORIZONTAL, length=300,
                                   from_=1, to=len(self.processed_tag_list), command=self.cb_quicknavi)
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

    def create_google_buttons(self):
        for i in range(self.num_recommendations):
            btn = Button(self.img_frame, text="Google{}".format(i),
                         command=partial(self.cb_btn_google, i))
            btn.grid(row=i + 1, columnspan=self.grid_hsize, sticky="NSEW",)
            self.google_buttons.append(btn)

    def set_processed_tag_list(self, processed_tag_list):
        self.processed_tag_list = processed_tag_list
        self.scl_quicknavi["to"] = len(self.processed_tag_list)

    def cb_btn_google(self, button):
        print("Google button pushed, dispatching message to observer:", self.google_buttons[button]["text"].lstrip())
        self.publisher.observer_dispatch(self, 'google_button_pushed', self.google_buttons[button]["text"].lstrip())

    def draw_image_to_canvas(self, im):
        self.img_canvas.image = ImageTk.PhotoImage(im)
        self.img_canvas.create_image(0, 0, image=self.img_canvas.image, anchor="nw")

    def cb_start(self):
        # print("cb start")
        self.current_tag = 0
        self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
        self.draw_image_to_canvas(self.im)
        self.update_all_widgets()

    def cb_left(self):
        # print("cb left")
        if self.current_tag > 0:
            self.current_tag -= 1
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.draw_image_to_canvas(self.im)
            self.update_all_widgets()

    def cb_right(self):
        # print("cb right")
        if len(self.processed_tag_list) - 1 > self.current_tag:
            self.current_tag += 1
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.draw_image_to_canvas(self.im)
            self.update_all_widgets()

    def cb_last(self):
        # print("cb last")
        if len(self.processed_tag_list) != self.current_tag:
            self.current_tag = len(self.processed_tag_list) - 1
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.draw_image_to_canvas(self.im)
            self.update_all_widgets()

    def cb_quicknavi(self, position):
        if self.current_tag == int(position) - 1:
            # we are at the right position
            pass
        else:
            self.current_tag = int(position) - 1
            try:
                self.publisher.observer_dispatch(self, 'picture_slider_moved',self.current_tag)
            except KeyError:
                print("No observer for current object, do nothing")
                pass
            self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
            self.draw_image_to_canvas(self.im)
            self.update_all_widgets()
            # If there is an observer for the slider movement, we have to dispatch a message

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
                                          + str(self.current_tag + 1) + " of " + str(len(self.processed_tag_list))


        # Try to display the address
        # Can get both Key and Index error
        for i, b in enumerate(self.google_buttons):
            try:
                # print("Google{} {}".format(i, self.processed_tag_list[self.current_tag]["formatted_address_list"][i]))
                b["text"] = a_date2 + self.processed_tag_list[self.current_tag]["formatted_address_list"][i]
            except (KeyError, IndexError) as e:
                b["text"] = a_date2 + ""

        # Let's check if we need to move the slider
        if self.scl_quicknavi.get() != self.current_tag+1:
            # Let's move the quick_navi slider to the right location
            # Maybe on a wrong place since can be moved with buttons
            self.scl_quicknavi.set(self.current_tag + 1)
            # We changed slider position, so we need to send an update
            try:
                self.publisher.observer_dispatch(self, 'picture_slider_moved',self.current_tag)
            except KeyError:
                print("No observer for current object, do nothing")
                pass

    def observer_picture_slider_moved(self, peers_position):
        """ If the left picture slider was moved, this call back function repositions the right slider to picture n+1,
        if possible. Reminder: position == currant_tag+1 """

        print("Picture slider moved, message received by observer:", peers_position)
        if self.myside == UI_LEFT:
            # I am left side, I have to be smaller
            if self.current_tag  < int(peers_position):
                print("Left is more to the left: do nothing")
                pass
            else:
                print("Left needs to move {} {} ".format(self.current_tag, int(peers_position)))
                self.current_tag = int(peers_position)-1
                self.current_tag = max( self.current_tag, 0 )

        elif self.myside == UI_RIGHT:
            # I am the right side, I have to be bigger
            if self.current_tag > int(peers_position):
                print("Right is more to the right")
                pass
            else:
                print("Right needs to move {} {} ".format(self.current_tag, int(peers_position)))
                self.current_tag = int(peers_position)+1
                self.current_tag = min(self.current_tag, len(self.processed_tag_list)-1)


        self.im = load_image(self.processed_tag_list[self.current_tag]["myfilename"])
        self.draw_image_to_canvas(self.im)
        self.update_all_widgets()

    def receive_message(self, message):
        """
        Default observer callback function
        :return:
        """
        print("{} :received {}".format(self, message))

    def get_currenttag(self):
        return self.current_tag

    def goto_tag(self,position):
        self.current_tag=position
        self.update_all_widgets()


class RenameUI:
    def __init__(self, canvas_width, canvas_height, canvas_bg_colour, grid_hsize, num_recommendations, dir, db_file,
                 publisher):
        self.root_window = Tk()
        self.dir = dir
        self.db_file = db_file
        self.current_row = 0
        self.grid_hsize = grid_hsize
        self.num_recommendations = num_recommendations
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.canvas_bg_colour = canvas_bg_colour
        self.lbl_currentpicname = Label()
        # This is a message dispatcher object
        self.publisher = publisher

        self.processed_tag_list = jpgcollectinfo.read_list_from_file(db_file)

        self.current_tag = 0

        self.create_widgets()

        self.left_img.cb_start()
        self.right_img.cb_right()  # displaying the next picture by default on the right hand side

    def create_widgets(self):
        self.create_menu()
        self.create_left_and_right_images()
        self.create_timeslider_rename_area()
        self.create_bottom_info_area()

    def create_menu(self):
        # Creating first row of UI
        # This will be the menubar
        self.menu_bar = Menu()
        self.file_menu = Menu(self.menu_bar, tearoff=0)

        self.file_menu.add_command(label="Select folder ...", command=self.cb_file)
        self.file_menu.add_command(label="Select db file...", command=self.cb_datafile)
        self.file_menu.add_command(label="Save db ...", command=self.cb_save)
        self.file_menu.add_command(label="Quit", command=exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Scan folder", command=self.cb_scan)
        self.menu_bar.add_cascade(label="Rename source files", command=self.cb_rename)
        self.menu_bar.add_cascade(label="Help")
        self.root_window.config(menu=self.menu_bar)

    def create_left_and_right_images(self):
        self.left_img = ImageShowUI(self, self.publisher)
        self.left_img.myside = UI_LEFT
        self.publisher.observer_register("picture_slider_moved", self.left_img,
                                         self.left_img.observer_picture_slider_moved)

        self.right_img = ImageShowUI(self, self.publisher)
        self.right_img.myside = UI_RIGHT
        self.publisher.observer_register('picture_slider_moved', self.right_img,
                                         self.right_img.observer_picture_slider_moved)

        self.left_frame = self.left_img.img_frame
        self.right_frame = self.right_img.img_frame

        self.left_frame.grid(row=0, column=0)
        self.right_frame.grid(row=0, column=1)
        self.current_row = self.current_row + 5

    def create_timeslider_rename_area(self):

        frame_slider = Frame(self.root_window)

        # Creating next row of UI
        # slider for how many to pics display at once
        lbl_a = Label(frame_slider, text=" Pictures taken within ")

        self.scl_withintime = Scale(frame_slider, orient=HORIZONTAL, length=300, to=300,
                                    command=self.cb_scale_withintime)
        self.scl_withintime.set(15)

        self.lbl_numberofpic = Label(frame_slider, text=" minutes is xxxx.")

        lbl_a.pack(side=LEFT)
        self.scl_withintime.pack(side=LEFT)
        self.lbl_numberofpic.pack(side=LEFT)
        frame_slider.grid(row=self.current_row, columnspan=self.grid_hsize)
        self.current_row += 1



        # Creating next row of UI
        # Rename to part
        frame_rename = Frame(self.root_window)

        lbl_renameto = Label(frame_rename, text="Rename to")


        self.entry_renameto = Entry(frame_rename, text="default rename to", width=100)
        #self.entry_renameto.grid(row=self.current_row, column=1, columnspan=self.grid_hsize - 1)

        btn_ok = Button(frame_rename, text=" OK ", command=self.cb_rename)
        #btn_ok.grid(row=self.current_row, column=4)

        lbl_renameto.pack(side=LEFT)
        self.entry_renameto.pack(side=LEFT)
        btn_ok.pack(side=LEFT)
        frame_rename.grid(row=self.current_row, columnspan=self.grid_hsize)
        self.current_row += 1

    def create_bottom_info_area(self):
        # Creating next row of UI
        # Name of working folder and DB
        self.lbl_current_settings = Label(self.root_window,
                                          text="Source folder: {}       Exif DB file: {}".format(self.dir, self.db_file))

        self.lbl_current_settings.grid(row=self.current_row, column=0, columnspan=self.grid_hsize)
        self.current_row += 1

    def cb_scale_withintime(self, position):
        self.update_all_widgets()

    def update_all_widgets(self):
        """
        Will update all google labels, picture name, slider, settings info
        :return: nothing
        """
        count = self.number_of_pics_in_range()
        print("Number of pics in range {}".format(count))
        a_txt = "minutes is " + str(count) + "."
        self.lbl_numberofpic["text"] = a_txt
        #TODO: uncomment this:
        #cur_pos = self.left_img.get_currenttag()
        #self.right_img.goto_tag(cur_pos + count)

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
        self.current_tag=self.left_img.get_currenttag()
        for tag in self.processed_tag_list[self.current_tag:]:
            delta = jpgcollectinfo.timedifference(tag, self.processed_tag_list[self.current_tag])
            if abs(delta.total_seconds()) < max_delta:
                count = count + 1
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

        # update their copy of the working list
        self.left_img.set_processed_tag_list(self.processed_tag_list)
        self.right_img.set_processed_tag_list(self.processed_tag_list)
        # Display the first pic
        self.left_img.cb_start()
        self.right_img.cb_right()

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

    def observer_google_button_pushed(self, button_text):
        """ If a google button was pushed, this callback function updates the renameto entry field """

        print("Google button pushed, message received by observer:", button_text)
        self.entry_renameto.delete(0, END)
        self.entry_renameto.insert(0, button_text)
        self.update_all_widgets()

    def observer_picture_slider_moved(self, position):
        self.update_all_widgets()

    def receive_message(self, message):
        """
        Default observer callback function
        :return:
        """
        print("{} :received {}".format(self, message))


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
        # print(size)
        im.thumbnail(size)
        return im
    except IOError:
        print("cannot create thumbnail for", filename)
        return None


def main():
    # We are creating a publisher, where you can subscibe to these events
    pub = Publisher(("google_button_pushed", "picture_slider_moved"))

    c = RenameUI(CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_BG_COLOUR, GRID_HSIZE, GOOGLE_RECOMMENDATIONS, DEFAULTDIR,
                 EXIF_DB_FILE, pub)
    if len(c.processed_tag_list) < 1:
        exit(1)
    pub.observer_register('google_button_pushed', c, c.observer_google_button_pushed)
    pub.observer_register('picture_slider_moved', c, c.observer_picture_slider_moved)

    print(c.processed_tag_list[c.current_tag]["myfilename"])

    messagebox.showinfo("Information", "You can select a different working directory. \n Select a DB file. "
                                       "\n Run Scan ")

    # Init the pictures
    # c.left_img.cb_start()
    # c.right_img.cb_right()

    c.root_window.mainloop()


if __name__ == '__main__':
    main()
