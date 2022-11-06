import pyaudio
import time
import audioop
from math import log10

def get_rms(p: pyaudio.PyAudio, inp_dev_idx: int):
    # Creates a generator that can iterate rms values
    CHUNK = 8
    WIDTH = 2
    CHANNELS = 1
    RATE = 44100

    try:
        stream = p.open(format=p.get_format_from_width(WIDTH),
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=False,
                        frames_per_buffer=CHUNK,
                        input_device_index=inp_dev_idx)
        # wait a second to allow the stream to be setup
        time.sleep(1)
        print(f'[get_rms] Creating a new stream for {inp_dev_idx} device')
        while True:
            # read the data
            stream.start_stream()
            data = stream.read(CHUNK, exception_on_overflow = False)
            stream.stop_stream()
            # print(f"CHUNK {len(data)}")
            rms = audioop.rms(data, WIDTH) / 32767 # what is 32767 ?
            db = 0
            if rms > 0:
                db = 20 * log10(rms)
            yield rms, db
    finally:
        # p.terminate()
        stream.stop_stream()
        stream.close()
        print(f'[get_rms] Stopping and closing stream for {inp_dev_idx} device')