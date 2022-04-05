import tkinter as tk

from textblob import TextBlob

import time
import collections
import threading

import speech_recognition as sr

import os
# add flac directory to the path to allow speech_recognition to find the flac.exe there
os.environ['PATH'] = os.environ['PATH'] + os.pathsep + os.path.join(os.getcwd(), "flac") 

class TurTrApp:
    def __init__(self):
        self.r = sr.Recognizer()
        self.data_to_process = collections.deque()
        
        self.stopListening = None
        self._cutPhrase = None
        self.prevDeviceName = None
        self.micro = None
        self.currentLineNum = 0
        
        # init root window and sound panel
        self.root = tk.Tk()
        self.root.iconphoto(False, tk.PhotoImage(file='turtle.png'))
        
        self.root.wm_title("Turtle Translator~")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        
        # Elements
 
        self.updateBtn = tk.Button(self.root, text="Update device list -->", command=self.updateMics, width=10)
        self.updateBtn.grid(row=0,column=0, rowspan=2, sticky=tk.E+tk.W)
        
        self.cutBtn = tk.Button(self.root, text="Cut the Phrase", command=self.cutPhrase, width=10)
        self.cutBtn.grid(row=0,column=2, rowspan=2, columnspan=2, sticky = tk.W+tk.E)

        self.currentDevice = tk.StringVar(self.root)
        self.currentDevice.trace("w", self.device_changed)
        self.devs = []
        
        self.om = tk.OptionMenu(self.root, self.currentDevice, value='', command=self.device_changed)
        self.om.config(width=30)
        self.om.grid(row=0, column=1, sticky = tk.W+tk.E)
        
        self.updateMics()
        
        self.originalText = tk.Text(self.root, height=10, width=100, wrap=tk.WORD)
        self.originalText.grid(row=2, column=0, columnspan=3)
        self.translatedText = tk.Text(self.root, height=10, width=100, wrap=tk.WORD)
        self.translatedText.grid(row=3, column=0, columnspan=3)
        
        self.originalText.tag_configure("last_insert", background="#E5EFC1")
        self.translatedText.tag_configure("last_insert", background="#E5EFC1")
        
        self.stopAudioProcessing = None
        self.stopAudioProcessing = self.process_in_background()

    def cutPhrase(self):
        if self._cutPhrase != None:
            self._cutPhrase()
        
    def updateMics(self):
        _devices = sr.Microphone.list_working_microphones()
        self.devices = {}
        for key, value in _devices.items():
            self.devices[value] = key
        menu = self.om["menu"]
        menu.delete(0, "end")
        dev_names = list(self.devices.keys())
        prev_name = self.currentDevice.get()
        if not prev_name and len(dev_names) != 0:
            prev_name = dev_names[0]
        self.currentDevice.set(prev_name)
        for string in dev_names: 
            menu.add_command(label=string, command=tk._setit(self.currentDevice, string))

    def add_text(self, textWidget, text):
        assert isinstance(textWidget, tk.Text) # textWidget must be tk.Text
        textWidget.tag_remove("last_insert", 1.0, "end")
        textWidget.insert(tk.END, f"{self.currentLineNum:>3}| {text}\n", ('last_insert',))
        textWidget.see(tk.END)
            
    def process_in_background(self):
        running = [True]
        def threaded_processAudio():
            while running[0]:
                # check data for processing every second
                if self.data_to_process: # if deque is not empty
                    recognizer, audio = self.data_to_process.popleft()
                    self.currentLineNum += 1
                    try:
                        text = recognizer.recognize_google(audio)
                        self.add_text(self.originalText, text)
                    except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio")
                        self.add_text(self.originalText, "Google Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        self.add_text(self.originalText, "Could not request results from Google Speech Recognition service")
                    except Exception as e:
                        print(f"Unknown error from Google Speech Recognition service; {e}")
                        self.add_text(self.originalText, "Unknown error from Google Speech Recognition service")
                    
                    try:
                        blob = TextBlob(text)
                        tr_text = blob.translate(to='ru')
                        self.add_text(self.translatedText, tr_text)
                    except Exception as e:
                        print(f"Translator TextBlob API raised an error {e}")
                        self.add_text(self.translatedText, "Translator TextBlob API raised an error")
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)
                    
        def stopper(wait_for_stop=True):
            running[0] = False
            if wait_for_stop:
                processer_thread.join()  # block until the background thread is done, which can take around 1 second

        processer_thread = threading.Thread(target=threaded_processAudio)
        processer_thread.daemon = True
        processer_thread.start()
        return stopper
            
    def processAudio(self, recognizer, audio):
        # need to process Audio async
        self.data_to_process.append((recognizer, audio)) 
            
    def device_changed(self, *args):
        device_name = self.currentDevice.get()
        if device_name in self.devices and device_name != self.prevDeviceName:
            self.prevDeviceName = device_name
            print(f"We picked {device_name} device with id = {self.devices[device_name]}")
            # check if the listening was already started into different background thread
            if self.stopListening != None:
                self.stopListening(wait_for_stop=False)
            # create a new micro
            self.micro = sr.Microphone(int(self.devices[device_name]))
            # start to listen micro device in background
            self.stopListening, self._cutPhrase = self.r.listen_in_background(self.micro, self.processAudio)
            
    def onClose(self):
        print("[INFO] closing application")
        if self.stopListening != None:
            self.stopListening(wait_for_stop=False)
        if self.stopAudioProcessing != None:
            self.stopAudioProcessing()
        self.root.quit()
        self.root.destroy()

turTr = TurTrApp()
turTr.root.mainloop()