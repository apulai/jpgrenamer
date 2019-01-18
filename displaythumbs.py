from PIL import Image, ImageTk
from tkinter import Tk
from tkinter.ttk import Frame, Label
import sys
import jpgcollectinfo

EXIF_DB_FILE = "D:\\temp\\kepek\\exif_db.db"
DEFAULTPIC = "D:\\temp\\kepek\\default.jpg"
class Example(Frame):

    def __init__(self):
        super().__init__()

        self.loadImage()
        self.initUI()

    def __init__(self,filename):
        super().__init__()

        self.loadImage(filename)
        self.initUI()

    def loadImage(self):
        try:
            self.img = Image.open(DEFAULTPIC)

        except IOError:
            print("Unable to load image")
            sys.exit(1)

    def loadImage(self,filename):
        try:
            self.img = Image.open(filename)

        except IOError:
            print("Unable to load image")
            sys.exit(1)


    def initUI(self):

        self.master.title("Label")

        tatras = ImageTk.PhotoImage(self.img)
        label = Label(self, image=tatras)

        # reference must be stored
        label.image = tatras

        label.pack()
        self.pack()

    def setGeometry(self):

        w, h = self.img.size
        self.master.geometry(("%dx%d+300+300") % (w, h))

    def resize(self,percent):
        w, h = self.img.size
        size = ( (int)(w*percent), (int)(h*percent) )
        self.img = self.img.resize(size,Image.BILINEAR)
        self.initUI()

def main():

    processed_tag_list = jpgcollectinfo.read_list_from_file(EXIF_DB_FILE)
    print(processed_tag_list[1]["myfilename"])
    filename = processed_tag_list[1]["myfilename"]

    root = Tk()
    ex = Example(filename)
    ex.resize(0.2)
    ex.setGeometry()

    root.mainloop()





if __name__ == '__main__':
    main()