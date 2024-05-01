import wave
import os
import time
import threading
import tkinter
import pyaudio
import warnings
from tkinter import messagebox
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from analyzer import SciencePart


class VoiceRecorder():
    count_of_records = 1

    def __init__(self):
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

        self.root = tkinter.Tk()
        self.root.title("Анализатор состояния человека")
        self.root.resizable(True, False)

        self.button = tkinter.Button(text="🎙", font=('Arial', 120, "bold"), command=self.click_handler)
        self.button.pack()

        self.label = tkinter.Label(text='00:00:00')
        self.label.pack()

        self.button = tkinter.Button(self.root, text="Выбрать параметры", command=self.open_parameters_window)
        self.button.pack(fill=tkinter.X, expand=True)

        self.button = tkinter.Button(text="Провести анализ", command=self.start_analyzer)
        self.button.pack(fill=tkinter.X, expand=True)

        self.button = tkinter.Button(text="Узнать характеристики файла", command=self.get_file_info)
        self.button.pack(fill=tkinter.X, expand=True)

        self.button = tkinter.Button(text="Показать осциллограмму записи", command=self.get_graph)
        self.button.pack(fill=tkinter.X, expand=True)

        self.recording = False
        self.root.mainloop()

    def click_handler(self):
        if self.recording:
            self.recording = False
        else:
            self.recording = True
            threading.Thread(target=self.record).start()

    def open_parameters_window(self):
        self.top = tkinter.Toplevel(self.root)
        self.top.title("Настройки")
        self.top.geometry("250x180")
        self.options = {"1 бит": pyaudio.paInt8, "2 бита": pyaudio.paInt16, "3 бита": pyaudio.paInt24}

        self.audio_format_label = tkinter.Label(self.top, text="Глубина звука:")
        self.audio_format_combobox = ttk.Combobox(self.top, values=list(self.options.keys()), state="readonly")
        self.audio_format_combobox.current(1)

        self.channels_label = tkinter.Label(self.top, text="Количество каналов:")
        self.channels_combobox = ttk.Combobox(self.top, values=["1", "2"], state="readonly")
        self.channels_combobox.current(0)

        self.rate_label = tkinter.Label(self.top, text="Частота дискретизации:")
        self.rate_combobox = ttk.Combobox(self.top, values=["8000", "11025", "16000", "22050", "32000", "44100"],
                                          state="readonly")
        self.rate_combobox.current(5)
        self.button_settings = tkinter.Button(self.top, text="Выбрать параметры", command=self.save_params)

        self.audio_format_label.pack()
        self.audio_format_combobox.pack()
        self.channels_label.pack()
        self.channels_combobox.pack()
        self.rate_label.pack()
        self.rate_combobox.pack()
        self.button_settings.pack()

    def save_params(self):
        self.audio_format = self.options[self.audio_format_combobox.get()]
        self.channels = int(self.channels_combobox.get())
        self.rate = int(self.rate_combobox.get())
        self.top.destroy()

    def start_analyzer(self):
        thread = threading.Thread(target=self.analyzer_thread)
        thread.start()

    def analyzer_thread(self):
        sp = SciencePart()
        status_bool, status_message = sp.analyzer_status(f"./content/recording{VoiceRecorder.count_of_records}.wav")
        if status_bool:
            messagebox.showinfo("Результат", status_message)
        else:
            messagebox.showwarning("Результат", status_message)

    def get_file_info(self):
        sp = SciencePart()
        dict_info = sp.IQC(f"./content/recording{VoiceRecorder.count_of_records}.wav")
        dict_str = '\n'.join([f"{key}: {value}" for key, value in dict_info.items()])
        messagebox.showinfo("Результат", dict_str)

    def get_graph(self):
        if hasattr(self, 'button'):
            self.button.pack_forget()  # скрываем старую кнопку
        self.button = tkinter.Button(text="Закрыть график", command=self.close_graph)
        self.button.pack(fill=tkinter.X, expand=True)

        sp = SciencePart()
        fig = sp.create_graph(f"./content/recording{VoiceRecorder.count_of_records}.wav")
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def close_graph(self):
        self.button.pack_forget()  # скрываем кнопку "Закрыть график"
        self.canvas.get_tk_widget().pack_forget()  # удаляем область с графиком
        self.button = tkinter.Button(text="Показать осциллограмму записи", command=self.get_graph)
        self.button.pack(fill=tkinter.X, expand=True)

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=1024,
            # input_device_index=9
        )

        frames = []
        start = time.time()

        while self.recording:
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)

            passed = time.time() - start
            secs = passed % 60
            mins = passed // 60
            hours = mins // 60
            self.label.config(text=f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d}")
            if passed >= 10.0:
                self.recording = False
                break

        stream.stop_stream()
        stream.close()
        audio.terminate()

        exists = True

        while exists:
            if os.path.exists(f'./content/recording{VoiceRecorder.count_of_records}.wav'):
                VoiceRecorder.count_of_records += 1
            else:
                exists = False

        sound_file = wave.open(f'./content/recording{VoiceRecorder.count_of_records}.wav', 'wb')
        sound_file.setnchannels(self.channels)
        sound_file.setsampwidth(audio.get_sample_size(self.audio_format))
        sound_file.setframerate(self.rate)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()


warnings.simplefilter("ignore")
VoiceRecorder()
