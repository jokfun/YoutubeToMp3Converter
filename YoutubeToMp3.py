from __future__ import unicode_literals
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import *
from tkinter import ttk
import queue 
import threading
import time
import youtube_dl

class GUI:
    def __init__(self, master):

        #The root of the application
        self.master = master

        #Link of the video/playlist
        frame = Frame(self.master)
        frame.pack(side=TOP)
        name = Label(frame, text="Link video/playlist :")
        name.pack( side = LEFT)
        self.link = Entry(frame, bd =2)
        self.link.pack(side = LEFT)

        #Codec used to saved the music
        frame = Frame(self.master)
        frame.pack(side=TOP)
        #List of the different used in youtube_dl
        vals = ['aac', 'flac', 'mp3', 'ogg', 'opus','m4a']
        self.codec = StringVar()
        #Set the codec to the most used one : mp3
        self.codec.set(vals[2])
        for i in range(len(vals)):
            b = Radiobutton(frame, variable=self.codec, text=vals[i], value=vals[i])
            b.pack(side='left', expand=1)

        #Audio rate
        frame = Frame(self.master)
        frame.pack(side=TOP)
        #List of the classic audio rates
        vals = ['16', '32', '96', '128', '192', '320']
        self.audioRate = StringVar()
        #Set the audio to the best possible quality
        self.audioRate.set(vals[len(vals)-1])
        for i in range(len(vals)):
            b = Radiobutton(frame, variable=self.audioRate, text=vals[i]+" kbs", value=vals[i])
            b.pack(side='left', expand=1)

        #Folder where the music(s) will be saved
        self.folder = ""
        self.frame_folder = Frame(self.master)
        self.frame_folder.pack(side=TOP)
        #Button to open the folder selection
        self.folder_button = Button(self.frame_folder, command=self.select_folder)
        self.folder_button.configure(text="Select folder", background="White")
        self.folder_button.grid(row=0,column=0)
        #Label where we show the folder choosen
        self.name_folder = Label( self.frame_folder, text="Select a folder")
        self.name_folder.grid( row=0,column=1)

        #Start Button
        self.start_button = Button(self.master, command=self.start)
        self.start_button.configure(
            text="Start", background="White",
            padx=50
            )
        self.start_button.pack(side=TOP)

        #Error / Bar/ Validate part, in the same place
        self.frame_errorBar = Frame(self.master)
        self.frame_errorBar.pack(side=TOP)
        self.content_errorBar = Label(self.frame_errorBar, text="Ready To Launch")
        self.content_errorBar.pack(side=TOP)

        #Termes and use button
        frame = Frame(self.master)
        frame.pack(side=TOP)
        Button(text='Termes of use', command=self.termes).pack(side=TOP)

        #Go is connected to the start button
        self.Go = True

    def termes(self):
        """
            Classics termes and uses shown in a pop-up 
        """
        showinfo("","You may not infringe the copyright, trademark or \
            other proprietary informational rights of any party.\
            The creators are not responsible for your use of the software.")

    def select_folder(self):
        """
            Choose a folder with a dialog box
        """
        self.folder = filedialog.askdirectory()
        text_folder= self.folder
        if len(self.folder)>30:
            #If the path is too long to show, we remove the first part
            text_folder="..."+self.folder[-30:]
        #Update the content of the folder shown in the app
        self.name_folder.destroy()
        self.name_folder = Label( self.frame_folder, text= text_folder)
        self.name_folder.grid( row=0,column=1)

    def progress(self):
        """
            A progress bar is used to show the loading of the sounds on the computer
        """
        self.content_errorBar.destroy()
        self.content_errorBar = ttk.Progressbar(
            self.frame_errorBar, orient="horizontal",
            length=200, mode="indeterminate"
            )
        self.content_errorBar.pack(side=TOP)

    def start(self):
        """
            Can launch the app only if it's not already working
        """
        if self.Go:
            self.Go = False
            #Start the progress bar
            self.progress()
            self.content_errorBar.start()
            #Create the queue
            self.queue = queue.Queue()
            #start the Thread with the global parameters
            ThreadedTask(self.queue,self.link.get(),self.codec.get(),self.audioRate.get(),self.folder).start()
            #Call a function after a will
            self.master.after(100, self.process_queue)

    def process_queue(self):
        """
            Update the app if the download is completed
        """
        try:
            #The queue must have an end or it will raise an error here
            msg = self.queue.get(0)
            self.Go = True
            self.content_errorBar.destroy()
            self.content_errorBar = Label(self.frame_errorBar, text=msg)
            self.content_errorBar.pack(side=TOP)
        except queue.Empty:
            #Call the function again after a will
            self.master.after(100, self.process_queue)

class ThreadedTask(threading.Thread):
    def __init__(self, queue,link,codec,audioRate,folder):
        """
            Creating a new Thread
            Tkinter can crash if it's waiting too long, so the download must be done in a thread
        """
        threading.Thread.__init__(self)
        self.queue = queue
        self.link = link
        self.codec = codec
        self.audioRate = audioRate
        self.folder = folder

    def run(self):
        """
            Make the download with youtube_dl and the parameters of the user
        """
        try:
            ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.codec,
                'preferredquality': self.audioRate,
                }],
            'outtmpl':self.folder + '/%(title)s.%(ext)s',
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link])

            self.queue.put("Task finished")
        except Exception as e:
            self.queue.put(e)

if __name__ == "__main__":
    #Create the application
    root = Tk()
    root.title("Youtube Downloader")
    gui = GUI(root)
    root.mainloop()