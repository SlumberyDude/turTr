import tkinter as tk
from utils import create_left_device_pick, create_ui, create_left_device_frame
from micro_gens import get_rms

import time
import collections
import threading

import speech_recognition.speech_recognition as sr

import os
# from reverso_context_api import Client
import requests
import json

def get_translation(text):
    # return list(client.get_translations(text))[0]
    url = "https://api.mymemory.translated.net/get?q={}!&langpair=en|ru".format(text)
    headers = {"key": "00f28d84e77bd94072a4",}
    response = requests.request("GET", url, headers=headers)
    res = json.loads(response.text)
    return (res['responseData']['translatedText'][:-1]).encode('utf-8').decode('utf-8')

# add flac directory to the path to allow speech_recognition to find the flac.exe there
os.environ['PATH'] = os.environ['PATH'] + os.pathsep + os.path.join(os.getcwd(), "flac") 

class TurTrApp:
    def __init__(self):
        self.elements = dict()

        # current device section variances
        self.cur_device = None # in future it will be Device
    
        # end
        self.pb_list_stop_event = threading.Event()
        self.pb_cur_stop_event = threading.Event()

        self.r = sr.Recognizer()
        self.data_to_process = collections.deque()
        
        self.stopListening = None
        self._cutPhrase = None
        self.prevDeviceName = None
        self.micro = None
        self.currentLineNum = 0
        
        # init root window and sound panel
        self.root = tk.Tk()
        create_ui(self.root, self.elements) # creating init components
        self.bind_events()

        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        # launch one thread to work everytime and looking for data processing
        self.stopAudioProcessing = None
        self.stopAudioProcessing = self.process_in_background()
        
    def cut_phrase(self):
        if self._cutPhrase != None:
            print('calling _cutPhrase()')
            self._cutPhrase()

    def add_text(self, textWidget, text):
        assert isinstance(textWidget, tk.Text) # textWidget must be tk.Text
        textWidget.tag_remove("last_insert", 1.0, "end")
        textWidget.insert(tk.END, f"{self.currentLineNum:>3}| {text}\n", ('last_insert',))
        textWidget.see(tk.END)
    
    def process_in_background(self):
        """
            Process audio for recognition in separate thread

            It checks `self.data_to_process` deque for a new audio fragments
        """
        # translate_client = Client("en", "ru")
        running = [True]
        def threaded_processAudio():
            while running[0]:
                # check data for processing every second
                if self.data_to_process: # if deque is not empty
                    recognizer, audio = self.data_to_process.popleft()
                    self.currentLineNum += 1
                    try:
                        text = recognizer.recognize_google(audio)
                        self.add_text(self.elements['original_text'], text)
                    except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio")
                        self.add_text(self.elements['original_text'], "Google Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google Speech Recognition service; {e}")
                        self.add_text(self.elements['original_text'], "Could not request results from Google Speech Recognition service")
                    except Exception as e:
                        print(f"Unknown error from Google Speech Recognition service; {e}")
                        self.add_text(self.elements['original_text'], "Unknown error from Google Speech Recognition service")
                    
                    try:
                        tr_text = get_translation(text)
                        self.add_text(self.elements['translated_text'], tr_text)
                        pass
                    except Exception as e:
                        print(f"Translator TextBlob API raised an error {e}")
                        self.add_text(self.elements['translated_text'], "Translator TextBlob API raised an error")
                    finally:
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
            
    def start_listen(self):
        device = sr.Microphone(self.device_id)
        self.pb_cur_stop_event.set() # let's stop listening for bp
        time.sleep(1)
        # start to listen micro device in background
        self.stopListening, self._cutPhrase = self.r.listen_in_background(device, self.processAudio)

    def onClose(self):
        print("[INFO] closing application")
        if self.stopListening != None:
            self.stopListening(wait_for_stop=False)
        if self.stopAudioProcessing != None:
            self.stopAudioProcessing()

        # stop progressbar threads
        print("Stop progressbar threads in thread {}".format(threading.current_thread()))
        if hasattr(self, 'pb_list_stop_event'):
            self.pb_list_stop_event.set()
            # erase threading objects
            self.pb_threads = dict()
        if hasattr(self, 'pb_cur_stop_event'):
            self.pb_cur_stop_event.set()
        self.root.quit()
        self.root.destroy()

    def bind_events(self):
        self.elements['f1_cur_device_btn'].config(command = self.to_device_list)
        self.elements['f2_cur_device_btn'].config(command = self.set_device)
        self.elements['start_btn'].config(command = self.start_listen)
        self.elements['cut_btn'].config(command = self.cut_phrase)

    def pb_thread_list(self, device_idx, stop_event):
        '''Method for processing in separate thread
        '''
        pyaudio_module = sr.Microphone.get_pyaudio()
        audio = pyaudio_module.PyAudio()
        device_info = audio.get_device_info_by_index(device_idx)
        device_name = device_info.get("name")

        gen = get_rms(audio, device_idx) # creating generator

        while not stop_event.is_set():
            rms, db = next(gen)
            vol = -int(db)
            try:
                pb = self.elements['f2_devices'][device_name]['progress']
                pb['value'] = vol
            except:
                print("Can't set value for progressbar")
            print(f'{device_name}: RMS = {rms}, DB = {db}')
            time.sleep(0.5)
        print("Exit from thread method for device {}".format(device_name))

    def pb_thread_current(self, stop_event):
        '''
        Method for current thread signal processing and 
        '''
        pyaudio_module = sr.Microphone.get_pyaudio()
        audio = pyaudio_module.PyAudio()

        gen = get_rms(audio, self.device_id) # creating generator

        while not stop_event.is_set():
            rms, db = next(gen)
            vol = -int(db)
            try:
                pb = self.elements['f1_cur_device_pb']
                pb['value'] = vol
            except:
                print("Can't set value for progressbar")
            print(f'{self.device_name}: RMS = {rms}, DB = {db}')
            time.sleep(0.5)
        print("Exit from thread method for current device {}".format(self.device_name))

    """
    Button to 2nd left frame state
    """
    def to_device_list(self):
        print('[turTr.py]::to_device_list')
        # need to stop current thread
        self.pb_cur_stop_event.set()
        time.sleep(0.1)
        if hasattr(self, 'cur_pb_thread'): # meant that early device already was picked
            print( f"Current thread is alive?: {self.cur_pb_thread.is_alive()}")
        # end

        pyaudio_module = sr.Microphone.get_pyaudio()
        audio = pyaudio_module.PyAudio()

        # check that state is valid 
        if hasattr(self, 'pb_threads'):
            if type(self.pb_threads) == dict and len(self.pb_threads) > 0:
                threads_text = " ".join(self.pb_threads)
                print("We have progressbar threads for devices {}".format(threads_text))
                assert False, f'There are {len(self.pb_threads)} pb threads already, should be 0'
        else:
            self.pb_threads = dict()
        
        # map device names
        self.devices_map = dict() # map device names on device ids
        for device_index in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(device_index)

            device_name = device_info.get("name")
            max_channels = device_info.get('maxInputChannels')

            if max_channels >= 1: # only input devices
                self.devices_map[device_name] = device_index

        create_left_device_frame(self.elements['f2_devices_frame'], self.elements, list(self.devices_map))
        
        
        self.pb_list_stop_event.clear() # start threads
        for name, id in self.devices_map.items():
            # key is a device index
            self.pb_threads[id] = threading.Thread(target=self.pb_thread_list, args=(id, self.pb_list_stop_event))   
            self.pb_threads[id].start()
            # self.generate_rms(key)
        
        
        # change frame
        self.elements['left_frame_2']['element'].grid(**self.elements['left_frame_2']['grid_kwargs'])
        self.elements['left_frame_2']['element'].grid_propagate(False)
        self.elements['left_frame_current'].grid_forget()
        self.elements['left_frame_current'] = self.elements['left_frame_2']['element']


    def to_left_init(self):
        """
        Gui change functionality and also element changing
        """
        print('[turTr.py]::to_left_init')            
        # change frame
        self.elements['left_frame_1']['element'].grid(**self.elements['left_frame_1']['grid_kwargs'])
        self.elements['left_frame_1']['element'].grid_propagate(False)
        self.elements['left_frame_current'].grid_forget()
        self.elements['left_frame_current'] = self.elements['left_frame_1']['element']

    def set_device(self):
        """
            Button at 'device list frame' was pressed
        """
        print('[turTr::set_device()]')
        
        # stop progressbar threads
        self.pb_list_stop_event.set()
        time.sleep(0.2)
        for _, th in self.pb_threads.items():
            print(f'Thread {th} is alive?: {th.is_alive()}')
        
        # erase threading objects
        self.pb_threads = dict()


        # get current device id
        self.device_name = self.elements['f2_active_device'].get()
        self.device_id = self.devices_map[self.device_name]
        print(f'{self.device_name} with id={self.device_id} was picked!')
        
        self.pb_cur_stop_event.clear()
        # setup currect device thread
        self.cur_pb_thread = threading.Thread(target=self.pb_thread_current, args=(self.pb_cur_stop_event,))
        self.cur_pb_thread.start()

        # Set label
        self.elements['f1_cur_device_label'].config(text=self.device_name)

        # Create new gui elements
        self.to_left_init()

turTr = TurTrApp()
turTr.root.mainloop()