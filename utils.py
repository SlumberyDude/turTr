from pyexpat.errors import XML_ERROR_INCOMPLETE_PE
import tkinter as tk
from tkinter import Frame
from tkinter import ttk
import tkinter.font
from regex import F
from tktooltip import ToolTip

colors = {
    'dark':       '#4B4237',
    'gold':       '#D5A021',
    'ivory':      '#EDE7D9',
    'gray-light': '#A49694',
    'gray-dark':  '#736B60' 
}

def create_window(root: tk.Tk):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    window_ratio = 0.8
    window_width = int(screen_width * window_ratio)
    window_height = int(screen_height * window_ratio)
    
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))

    print('Creating main window with {}x{} sizes'.format(window_width, window_height))
    root.geometry("{}x{}+{}+{}".format(
        window_width, window_height,
        x_cordinate, y_cordinate 
        ))

    root.resizable(False, False)
    root.iconphoto(False, tk.PhotoImage(file='turtle.png'))
    root.wm_title("Turtle Translator~")
    root.config(bg=colors['dark'])

def create_frames(root: tk.Tk, elements: dict):
    """Create left and right frame panels
    """
    root.update() # for updating root.winfo data
    pad_x = 10 # px
    pad_y = 10 # px
    gap = 5 # px-gap
    # root width and height without paddings and gap
    root_width  = root.winfo_width()  - pad_x * 2 - gap
    root_height = root.winfo_height() - pad_y * 2
    fr1_width = int(root_width * 0.2)
    fr2_width = root_width - fr1_width

    

    # Left frame 2 creation (no grid!)
    left_frame_2 = Frame(
        root, 
        width=fr1_width, 
        height=root_height, 
        bg=colors['ivory'])
    lf_kwargs = {'row':0, 'column':0, 'padx':(pad_x, gap), 'pady':pad_y}
    left_frame_2.grid(**lf_kwargs)

    # Left frame 2 write to elements
    if 'left_frame_2' not in elements:
        elements['left_frame_2'] = dict()
    elements['left_frame_2']['element'] = left_frame_2
    elements['left_frame_2']['grid_kwargs'] = lf_kwargs

    # Left frame init (1) creation and grid
    left_frame_1 = Frame(
        root, 
        width=fr1_width, 
        height=root_height, 
        bg=colors['gray-dark'])
    left_frame_1.grid(**lf_kwargs)

    # Left frame init (1) saving to elements
    if 'left_frame_1' not in elements:
        elements['left_frame_1'] = dict()
    elements['left_frame_1']['element'] = left_frame_1
    elements['left_frame_1']['grid_kwargs'] = lf_kwargs

    # set current left panel element as left_frame_1
    elements['left_frame_current'] = left_frame_1

    # Right frame init creation and grid
    right_frame = Frame(
        root,
        width=fr2_width, 
        height=root_height, 
        bg=colors['gray-light'])
    right_frame.grid(row=0, column=1)

    #Stop the frame from propagating the widget to be shrink or fit
    left_frame_1.grid_propagate(False)
    left_frame_2.grid_propagate(False)
    right_frame.grid_propagate(False)

    return left_frame_1, left_frame_2, right_frame

def create_left_init(fr :tk.Tk, elements: dict):
    """Create initial left frame
    """
    fr.update()
    pad_x = 5
    pad_y = 5

    font_label = tk.font.Font(family="Consolas", size=16, weight="normal")
    # let's get the name of the monospace font
    mono_ff = tk.font.nametofont("TkFixedFont").actual()['family'] 
    font_device = tk.font.Font(family=mono_ff, size=16, weight='bold')
    char_len = font_device.measure("A") # 1 symbol length in pixels

    gap_x = 5
    max_element_width = fr.winfo_width() - 2 * pad_x - gap_x
    # I want 3/4 for name and 1/4 for sound indicator
    max_device_name_width = int(max_element_width * 3 / 4)
    sound_indicator_width = max_element_width - max_device_name_width

    max_chars = int(max_device_name_width / char_len)

    # create label for devices, 0 row
    device_label = tk.Label(fr, text="Current Device",
        font=font_label,
        fg=colors['ivory'],
        bg=colors['gray-dark'])
    device_label.grid(row=0, column=0, padx=pad_x, pady=(pad_y, 0),
        sticky='w') # left align

    # current device name, 1nd row
    label_text = "No device"
    if len(label_text) > max_chars:
        label_text = label_text[:max_chars-2] + '..'
    device_label = tk.Label(fr, text=label_text, anchor='w',
        font=font_device,
        fg=colors['gold'],
        bg=colors['gray-dark'],
        width=max_chars)
    device_label.grid(row=1, column=0, padx=pad_x, sticky='w')
    elements['f1_cur_device_label'] = device_label
    device_pb = ttk.Progressbar(
        fr,
        length=sound_indicator_width
    )
    device_pb.grid(row=1, column=1)
    elements['f1_cur_device_pb'] = device_pb

    # Device pick btn
    device_btn = tk.Button(
        fr, text='Pick device',
        font=font_label,
        fg=colors['dark'],
    )
    device_btn.grid(row=2, column=0, columnspan=2)
    elements['f1_cur_device_btn'] = device_btn

    # start button
    start_btn = tk.Button(
        fr, text='Start',
        font=font_label,
        fg=colors['dark'],
    )
    start_btn.grid(row=3, column=0, columnspan=2)
    elements['start_btn'] = start_btn

    # cut button
    cut_btn = tk.Button(
        fr, text='Cut',
        font=font_label,
        fg=colors['dark'],
    )
    cut_btn.grid(row=4, column=0, columnspan=2)
    elements['cut_btn'] = cut_btn
    
    
def create_left_device_pick(fr :tk.Tk, elements: dict):
    """Create left frame with device picking layout
    """
    fr.update()
    pad_x = 5
    pad_y = 5

    font_label = tk.font.Font(family="Consolas", size=16, weight="normal")
    # let's get the name of the monospace font
    mono_ff = tk.font.nametofont("TkFixedFont").actual()['family'] 
    font_device = tk.font.Font(family=mono_ff, size=16, weight='normal')
    char_len = font_device.measure("A") # 1 symbol length in pixels

    gap_x = 5
    max_element_width = fr.winfo_width() - 2 * pad_x - gap_x
    # I want 3/4 for name and 1/4 for sound indicator
    max_device_name_width = int(max_element_width * 3 / 4)
    sound_indicator_width = max_element_width - max_device_name_width

    max_chars = int(max_device_name_width / char_len)

    # Label
    label_width = int(max_element_width / char_len) 
    device_label = tk.Label(fr, text="Devices list",
        font=font_label,
        fg=colors['ivory'],
        bg=colors['gray-dark'],
        width=label_width,
        anchor='w'
        )
    device_label.grid(row=0, column=0, padx=pad_x, pady=(pad_y, 0))

    # Device pick btn
    device_btn = tk.Button(
        fr, text='Pick device',
        font=font_label,
        bg='blue',
        fg=colors['dark'],
        # width=button_width
    )
    # device_btn.grid(row=1, column=0, padx=pad_x, pady=(pad_y, 0), columnspan=2)
    device_btn.grid(row=1, column=0, padx=pad_x, pady=(pad_y, 0))
    elements['f2_cur_device_btn'] = device_btn

    device_label.update()
    device_btn.update()
    frame_height = fr.winfo_height() - (device_label.winfo_height() + device_btn.winfo_height())

    if 'f2_devices_frame' not in elements:
        print('in f2device frame creation')
        device_frame = Frame(
            fr, 
            width=fr.winfo_width()-2*pad_x, 
            height=frame_height-4*pad_y,
            bg=colors['gray-light'])
        device_frame.grid(row=2, column=0, padx=pad_x, pady=pad_y)
        elements['f2_devices_frame'] = device_frame
        device_frame.grid_propagate(False)


def create_left_device_frame(fr :tk.Tk, elements: dict, devices: list):
    """Create left frame with device picking layout
    """
    fr.update()
    pad_x = 5
    pad_y = 5

    mono_ff = tk.font.nametofont("TkFixedFont").actual()['family'] 
    font_device = tk.font.Font(family=mono_ff, size=14, weight='normal')
    char_len = font_device.measure("A") # 1 symbol length in pixels

    gap_x = 5
    max_element_width = fr.winfo_width() - 2 * pad_x - gap_x
    # I want 3/4 for name and 1/4 for sound indicator
    max_device_name_width = int(max_element_width * 3 / 4)
    sound_indicator_width = max_element_width - max_device_name_width

    max_chars = int(max_device_name_width / char_len)

    if 'f2_devices' not in elements:
        elements['f2_devices'] = dict()

    first_device = ''
    if devices:
        first_device = devices[0]

    # create active device 
    if 'f2_active_device' not in elements:
        print('DEBUG 0')
        elements['f2_active_device'] = tk.StringVar(fr, first_device)
    else:
        temp_device = elements['f2_active_device'].get()
        print(f'DEBUG 1, active_device = [{temp_device}]')
        if temp_device not in devices:
            print('DEBUG 1.1\n{temp_device} not in devices')
            print("\n".join(devices))
            elements['f2_active_device'] = tk.StringVar(fr, first_device)
    
    current_row = 0
    for device in devices:
        if device not in elements['f2_devices']:
            elements['f2_devices'][device] = dict()

        device_name = device
        print(f"Look at device {device_name} with len {len(device)} and max_chars = {max_chars}")
        if len(device) >= max_chars:
            device_name = device[:max_chars-4] + '..'
        rb = tk.Radiobutton(
            fr,
            font=font_device,
            text=device_name,
            fg=colors['gold'],
            anchor='w',
            width=max_chars,
            variable=elements['f2_active_device'],
            value=device
        )
        rb.grid(row=current_row, column=0, pady=(pad_y, 0), sticky='w')
        ToolTip(rb, msg=device, delay=1.0)
        pb = ttk.Progressbar(
            fr,
            length=sound_indicator_width,
            # mode='indeterminate',
            mode='determinate',
        )
        pb.grid(row=current_row, column=1, padx=(pad_x, 0))
        current_row += 1

        elements['f2_devices'][device]['radio'] = rb
        elements['f2_devices'][device]['progress'] = pb

def create_right_frames(fr: Frame, elements):
    fr.update()
    pad_x = 5
    pad_y = 5
    gap = 5

    mono_ff = tk.font.nametofont("TkFixedFont").actual()['family'] 
    font_device = tk.font.Font(family=mono_ff, size=14, weight='normal')
    char_len = font_device.measure("A") # 1 symbol length in pixels

    w = fr.winfo_width() - 2*pad_x
    h = (fr.winfo_height() - 2*pad_y - gap) / 2

    w_in_chars = int( w/char_len )
    h_in_chars = int( h/char_len/2 )

    elements['original_text'] = tk.Text(fr, height=h_in_chars, width=w_in_chars, wrap=tk.WORD,
        bg=colors['gray-dark'], font=font_device)
    elements['original_text'].grid(row=0, column=0, padx=pad_x, pady=(pad_y, gap))

    elements['translated_text'] = tk.Text(fr, height=h_in_chars, width=w_in_chars, wrap=tk.WORD,
        bg=colors['gray-dark'], font=font_device)
    elements['translated_text'].grid(row=1, column=0, padx=pad_x, pady=(0, pad_y))

    elements['original_text'].tag_configure("last_insert", background="#141c40")
    elements['translated_text'].tag_configure("last_insert", background="#141c40")


def create_ui(root: tk.Tk, elements: dict):
    """'elements' array contain dynamic components for further binding with methods
    
    Creating init components
        - main window
        - left frame panel
        - right frame panel
        
    Left Frame Panel has several states which represents by different panels
    which are changing each other
    Left Frame Panel states:
        - init
        - device picking
        - device picked
    """
    create_window(root)
    fr_left_1, fr_left_2, fr_right = create_frames(root, elements)
    create_left_init(fr_left_1, elements)

    create_left_device_pick(fr_left_2, elements)

    create_right_frames(fr_right, elements)
