import torch
import scipy.io.wavfile as wav
import wave
import numpy as np
import matplotlib as mpl
from aniemore.recognizers.voice import VoiceRecognizer
from aniemore.models import HuggingFaceModel
from matplotlib.figure import Figure


class SciencePart():
    mpl.rcParams['agg.path.chunksize'] = 100000

    def analyzer_status(self, file_wav):
        model = HuggingFaceModel.Voice.WavLM
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        vr = VoiceRecognizer(model, device)
        result = vr.recognize(file_wav)
        negative_result = result["anger"] + result["disgust"] + result["fear"]
        positive_result = result["enthusiasm"] + result["happiness"] + result["neutral"]
        if positive_result > negative_result:
            return True, "Человек может работать"
        else:
            return False, "Человеку лучше отдохнуть"

    def IQC(self, file_wav):
        sample_rate, audio_data = wav.read(file_wav)

        amplitude = np.abs(audio_data)
        loudness = np.mean(amplitude)

        freq_spectrum = np.fft.fft(audio_data, axis=0)
        freq_spectrum = np.abs(freq_spectrum)
        freq_spectrum = freq_spectrum[:len(freq_spectrum) // 2]  # Усечение до половины спектра (так как симметричен)
        max_frequency = np.argmax(freq_spectrum)
        average_frequency = np.mean(freq_spectrum)
        wav_file = wave.open(file_wav)
        sample_width = wav_file.getsampwidth()
        sample_rate2 = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        num_frames = wav_file.getnframes()
        duration = num_frames / sample_rate2
        names_list = ["Громкость", "Максимальная частота", "Средняя частота", "Количество амплитуд",
                      "Частота дискретизации", "Количество каналов", "Количество фреймов", "Длительность"]
        value_list = [loudness, max_frequency, average_frequency, sample_width,
                      sample_rate2, num_channels, num_frames, duration]
        characteristics = {}
        for i in range(8):
            characteristics[names_list[i]] = value_list[i]
        return characteristics

    def create_graph(self, file_wav):
        fig = Figure(figsize=(6, 4), dpi=100)
        plot = fig.add_subplot(111)

        with wave.open(file_wav, 'rb') as wf:
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            num_frames = wf.getnframes()

            frames = wf.readframes(num_frames)
            if sample_width == 1:
                data = np.frombuffer(frames, dtype=np.uint8)
            elif sample_width == 2:
                data = np.frombuffer(frames, dtype=np.int16)

            duration = num_frames / frame_rate
            time = np.linspace(0, duration, num=num_frames)

            for i in range(num_channels):
                plot.plot(time, data[i::num_channels])
            return fig
