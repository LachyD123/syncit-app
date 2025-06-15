import logging
import threading
import tkinter as tk
from tkinter import messagebox
import tailer
from datetime import datetime
import os
def set_logger(logger_name):
    log_filename = f"{logger_name}.log"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_filename)
    handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    handler.setFormatter
    logger.addHandler(handler)
    logger.propagate = False
    return logger, log_filename

import threading
import ctypes
import time

class thread_with_exception(threading.Thread):
    # def __init__(self, name):
    #     threading.Thread.__init__(self)
    #     self.name = name
             
    # def run(self):

    #     # target function of the thread class
    #     try:
    #         while True:
    #     finally:
          
    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
            
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class TkinterLoggingHandler(threading.Thread):

    def __init__(self, name, main_func, root, logger, log_filename):
        super().__init__()
        self.name = name
        self.main_func = main_func
        self.root = root

        self.logger = logger
        self.log_filename = log_filename
        # 1. Create a Scrollbar widget.
        # Create a Scrollbar widget with specified colors.
        self.scrollbar = tk.Scrollbar(self.root, bg="white", troughcolor="black")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_widget = tk.Text(self.root, bg="black", fg="white", font=("Cascadia Code", 10),
                                   yscrollcommand=self.scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Linking Text widget to the Scrollbar
        self.scrollbar.config(command=self.text_widget.yview)

        self.text_widget.pack()
        self.result_container = {"result": None}
        self.main_loop_is_running = False

    def append_text(self, content, msg_type):
        colors = {
            'INFO': 'white',
            'WARNING': 'orange',
            'ERROR': 'red'
        }

        # Setting the color based on msg_typese
        color = colors.get(msg_type, 'white')  # Default to white if msg_type isn't recognized

        # Insert the content

        self.text_widget.insert(tk.END, content + '\n')
        
        # Applying color to the inserted content
        start_index = "end-{}c".format(len(content) + 1)
        self.text_widget.tag_add(msg_type, start_index, "end-1c")  # -1c to avoid including the newline in the tag
        self.text_widget.tag_configure(msg_type, foreground=color)

        # Scroll if scrollbar was at the end
        y_scroll = self.text_widget.yview()[1]
        if y_scroll >= 0.9:
            self.text_widget.see(tk.END)

    def run(self, *args, **kwargs):
        kwargs['logger'] = self.logger
        self.result_container["result"] = self.main_func(*args, **kwargs)

    def tail_log(self, handler_thread: thread_with_exception, root: tk.Tk):
        try:
            for line in tailer.follow(open(self.log_filename)):
                _type = 'NONE'
                if 'WARNING' in str(line):
                    _type = 'WARNING'
                    line = line[line.find('WARNING'):]
                if 'ERROR' in str(line):
                    _type = 'ERROR'
                    line = line[line.find('ERROR'):]
                if 'INFO' in str(line):
                    _type = 'INFO'
                    line = line[line.find('INFO'):]
                
                line: str
                if len(line) == len(_type) + 3:
                    _type = 'NONE'
                    self.text_widget.insert(tk.END, '\n')
                else:
                    root.lift()
                    # Instead of inserting directly, now use the append_text method
                    self.append_text(line, _type)
                    if _type not in ['INFO']:
                        self.text_widget.insert(tk.END, '\n')
                        
                if _type in ['ERROR']:
                    messagebox.showerror(_type, line)
                    root.lift()

                if _type in ['WARNING']:
                    messagebox.showwarning(_type, line)
                    root.lift()

                if '[EXIT]' in line:
                    handler_thread.raise_exception()
                    exit()
        except Exception as exc:
            handler_thread.raise_exception()
            exit()
            
        finally:
            handler_thread.raise_exception()
            exit()
                        
def log_window_wrapper(func):
    def wrapper(*args, **kwargs):
        root = tk.Tk('')
        title = f"{func.__name__}_{datetime.now().strftime('%Y_%m_%d@%H_%M_%S')}"
        log_folder_src = kwargs.get('log_folder_src', None)

        root.attributes("-topmost", True)
        root.resizable(False, False)  # Disable resizing (width, height)
        root.title(title)
        if log_folder_src:
            
            if not os.path.isdir(log_folder_src + '/logs'):
                os.mkdir(log_folder_src + '/logs')    

            logger, log_filename = set_logger(log_folder_src + '/logs/' + title)
        else:
            logger, log_filename = set_logger(title)
        handler = TkinterLoggingHandler(title, func, root, logger, log_filename)
        handler_thread = thread_with_exception(target=handler.run, args=args, kwargs=kwargs)
        tail_thread = threading.Thread(target=handler.tail_log ,args = (handler_thread,root))
        tail_thread.start()
        handler_thread.start()
        root.mainloop()
        handler.join()
        tail_thread.join()
        return handler.result_container["result"]
    return wrapper

# @log_window_wrapper
# def main_func(logger: Logger = None):
#     logger.info("This is a test log message.")
#     for i in range(10):
#         logger.info(f"Log message {i}")
#         time.sleep(1)
#     return "Main function result"

# def create_new_window():
#     threading.Thread(target=main_func).start()
#     # threading_event.set()

# if __name__ == "__main__":
#     main_window = tk.Tk()
#     btn = tk.Button(main_window, text="Create new window", command=create_new_window)
#     btn.pack()
#     main_window.mainloop()


