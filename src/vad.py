
## generally done but there is somethign wrong with the silence where it keep stuck it inifitre loop of detecting silence
# this class is an thread. 
# the overall_Done doesn't have any problem with duplication so there is something wrong with the class
# okay some problem with the silence counting. I just update it and it seem fine right now
import sounddevice as sd
import time 
import numpy as np
import scipy 
import scipy.fft 
from faster_whisper import WhisperModel
import threading
import queue

# whisper use 16000 but with this 16000 kokoro will sounds weird. Thus Kokoro will have to use
# 240000
SAMPLE_RATE = 16000
BLOCK_SIZE = 4096
WINDOW_LENGTH_MS = 15
CHANNELS = 1
SPEECH_THRESHOLD_DB = 7
# there is some problem with the silence threshold if we compare with the mean
# what happen we talk all the time ?
SILENCE_THRESHOLD_DB = 7
HANGOVER_SOUND_DURATION = 3 # chunks
TAIL_SILENCE_DURATION = 25 # chunks

# Calculated constant
WINDOW_LENGTH = int(SAMPLE_RATE * WINDOW_LENGTH_MS / 1000)
WINDOW_STEP_MS = WINDOW_LENGTH_MS / 2
WINDOW_STEP = int(WINDOW_STEP_MS * SAMPLE_RATE / 1000)
SPECTRUM_LENGTH = int((WINDOW_LENGTH)/2)+1

class VADThread(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.leftover_buffer = []
        self.is_running = False
        # calculate noise
        self.noise = []
        self.mean_noise = 0
        self.set_noise = False
        # checking speech
        self.is_checking_speech = False
        self.is_speech = False
        self.speech_counter = 0
        self.speech_buffer = []
        # checking silence
        self.is_checking_silence = False
        self.is_silence = False
        self.silence_counter = 0
        self.silence_buffer = []
        
        # Send and wait 
        self.is_done_speech = False
        self.is_waiting_pipeline = False
    def set_stream_arguments(self,
                             sample_rate,
                             channel,
                             block_size,
                             window_length_ms,
                             speech_threshold_db,
                             silence_threshold_db,
                             hangover_speech_duration,
                             tail_silence_duration):
        self.sample_rate = sample_rate
        self.channel = channel
        self.block_size= block_size
        
        self.window_length_ms = window_length_ms
        self.window_length = int(self.sample_rate * self.window_length_ms / 1000)
        self.window_step_ms = self.window_length_ms / 2
        self.window_step = int(self.window_step_ms * self.sample_rate / 1000)
        self.spectrum_length = int(self.window_length / 2) + 1
        self.window_function = VADThread.halfsinewindow(self.window_length)
        
        self.speech_threshold_db = speech_threshold_db
        self.silence_threshold_db = silence_threshold_db
        self.hangover_speech_duration = hangover_speech_duration
        self.tail_silence_duration = tail_silence_duration
        

    def set_recording_queue(self,recording_queue):
        self.recording_queue = recording_queue
        
        
    def start(self):
        self.is_running = True
        self.start_stream = time.time()
        with sd.InputStream(samplerate=self.sample_rate, 
                            channels=self.channel, 
                            blocksize=self.block_size, 
                            callback=self.call_back):
            while self.is_running:
                # self.mic_ready.wait() pointless to wait here since it could just throw to call backa
    
                if self.is_done_speech:
                    
                    print("done the speech: ")
                    self.recording_queue.put(self.speech_buffer.copy())
                    self.speech_buffer = []
                    self.is_done_speech = False
         
                sd.sleep(10)
    def run(self):
        threading.Thread(target=self.start,daemon=True).start()
    
    def stop(self):
        self.is_running = False
    def done_waiting(self):
        print("Done waiting ")
        self.is_waiting_pipeline = False
    def set_mic_ready_event(self, mic_ready: threading.Event):
        self.mic_ready = mic_ready
    
    def call_back(self, indata, frames, time_info, status):
        w_length = self.window_length
        w_step = self.window_step
        w_step_ms = self.window_step_ms
        mn = self.mean_noise
        sr = self.sample_rate
        speech_db = self.speech_threshold_db
        silence_db = self.silence_threshold_db
        hangover = self.hangover_speech_duration
        tail = self.tail_silence_duration
        sp_counter = self.speech_counter
        si_counter = self.silence_counter
        spec_length = self.spectrum_length
        wf = self.window_function
        # only change global in here
        if time.time() - self.start_stream < 3:
            print("Warming up to remove hardware bias")
            # Warm up to remove hardware bias
            return
        elif time.time() - self.start_stream < 6:
            print("Caculating Noise background. Please don't speak anything")
            # caculate the baseline noise
            self.noise = np.concatenate((self.noise, indata.copy()[:,0]))
        elif self.set_noise == False:
            

            self.mean_noise = VADThread.calculate_noise(self.noise,w_length,w_step,spec_length,wf)
            self.noise = []
            self.set_noise = True
            print(f"Noise is calculate with the mean: {self.mean_noise}")
        elif self.mic_ready.is_set():
            
            if len(self.leftover_buffer) > 0:
                data = np.concatenate((self.leftover_buffer,indata.copy()[:,0]))
                self.leftover_buffer = [0]
            else:
                data = indata.copy()[:,0]
            total_length = len(data)
            
            
            w_count = int( (total_length-w_step)/w_step) + 1
            spectrogram = VADThread.stft(data, w_length,w_step,spec_length,wf)
            
            if self.is_speech != True:
                sound_active, time_track = VADThread.calculate_sound_active(spectrogram, 
                                                            w_count, 
                                                            w_step_ms,
                                                            mn + speech_db) 
                if self.is_checking_speech != True:
                    # print("Detecting speech")
                    counter, sound_data, leftover_data,_ ,_= VADThread.detect_sound(data, sr,sound_active, time_track, True, hangover)
                    self.leftover_buffer = leftover_data
                    if counter == hangover:
                        # print("Speech is spotted 1")
                        self.is_checking_silence = True
                        self.is_speech = True
                        self.is_checking_speech = False
                        self.leftover_buffer = []
                        self.speech_buffer = sound_data.copy()
                        print(len(self.speech_buffer))
                    elif counter > 0:
                        # print("Detected sound")
                        self.counter = counter
                        self.speech_buffer = sound_data.copy()
                        self.is_checking_speech = True
                    
                else:
                    # print("checking sound")
                    is_needed_sound, still_checking, sound_data, leftover_data,_,_ = VADThread.check_sound(data,
                                                                                                        sr,
                                                                                                        sound_active,
                                                                                                        time_track,
                                                                                                        sp_counter,
                                                                                                        True,
                                                                                                        hangover)
                    self.leftover_buffer = leftover_data
                    if is_needed_sound:
                        # print("Speech is spotted 2")
                        self.is_checking_silence = False
                        self.is_speech = True
                        self.is_checking_speech = False
                        self.speech_buffer = np.concatenate((self.speech_buffer,
                                                            sound_data.copy()))
                    else:
                        
                        if still_checking:
                            # print("Still Checking")
                            self.speech_buffer = np.concatenate((self.speech_buffer,
                                                                sound_data.copy()))
                        else:
                            # print("Sound is not speech. Continue to detect")
                            self.speech_buffer = []
                            self.is_checking_speech = False
                            self.is_speech = False 
            else:
                sound_active,time_track = VADThread.calculate_sound_active(spectrogram, 
                                                    w_count, 
                                                    w_step_ms,
                                                    mn + silence_db) 
                # print(f"silence counter: {si_counter}")
                
                if self.is_checking_silence != True:
                    # print("Detecting silence sound")
                    counter, silence_data, leftover_data, sound_data,before_silence = VADThread.detect_sound(data,
                                                                                                             sr,
                                                                                                            sound_active, 
                                                                                                            time_track,
                                                                                                            False, 
                                                                                                            tail)
                    if counter == tail:
                        # print("silence is spotted 1")
                        # print(len(self.speech_buffer))
                        self.is_checking_silence = False
                        self.is_speech = False
                        self.is_done_speech = True
                        self.leftover_buffer = np.concatenate((silence_data.copy(),leftover_data.copy()))
                        self.speech_buffer = np.concatenate((self.speech_buffer,before_silence.copy()))
                    elif counter > 0:
                        # print("Detecting Silence ")
                        self.is_checking_silence = True
                        self.silence_counter = counter
                        self.silence_buffer = silence_data.copy()
                        self.speech_buffer = np.concatenate((self.speech_buffer,before_silence.copy()))
                    else:
                        self.speech_buffer = np.concatenate((self.speech_buffer,sound_data.copy()))
                else:
                    is_needed_silence, still_checking, silence_data, leftover_data, before_leftover_data,count = VADThread.check_sound(data,
                                                                                                                                sr, 
                                                                                                                                sound_active,
                                                                                                                                time_track, 
                                                                                                                                si_counter,
                                                                                                                                False, 
                                                                                                                                tail)
                    if is_needed_silence:
                        # print("Silence is spotted 2")
                        self.is_done_speech = True
                        self.is_checking_silence = False
                        self.is_speech = False
                        self.leftover_buffer = np.concatenate((self.silence_buffer, silence_data.copy(),leftover_data.copy()))
                    else:
                        self.leftover_buffer = leftover_data
                        if still_checking:
                            # print("Checkign the silence sound")
                            # where to update silent counter?
                            self.silence_counter = count
                            self.silence_buffer = np.concatenate((self.silence_buffer.copy(),
                                                                silence_data.copy()))
                        else:
                            # print("No silcence. Continue to speak")
                            self.silence_buffer = []
                            self.is_checking_silence = False
                            self.is_speech = True 
                            self.is_checking_speech = False 
                            self.speech_buffer = np.concatenate((self.speech_buffer, before_leftover_data.copy()))
        else:
            self.speech_buffer = []
            self.leftover_buffer = []


        
    # static method
    
    @staticmethod
    def stft(data,window_length,window_step,spectrum_length,windowing_function=None):
        if windowing_function is None:
            windowing_function = np.sin(np.pi*np.arange(0.5, window_length,1)/ window_length)**2
        total_length = len(data)
        window_count = int( (total_length-window_length)/window_step) + 1
        spectrogram = np.zeros((window_count,spectrum_length),dtype=complex)

        for k in range(window_count):
            starting_position = k * window_step
            data_vector = data[starting_position:(starting_position + window_length),]
            
            window_spectrum = scipy.fft.rfft(data_vector*windowing_function,n = window_length)
            spectrogram[k,:] = window_spectrum
            
        return spectrogram
    
    @staticmethod 
    def halfsinewindow(window_length):
    # np.arange(0.5,window_length,1): 
    # return array of [0.5, 1.5,...,(n-1) + 0.5] where n = window_length
    # /window_length: squeeze into range of 0->1
    # sin(0) = 0 so it might erase some function i guess
        return np.sin(np.pi*np.arange(0.5,window_length,1)/window_length)
    
    @staticmethod
    def is_passed_threshold(speech_active, checking_speech, duration):
        counter = 0
        track_index = -1
        # hangover three
        for i, chunk_bool in enumerate(speech_active):
            if counter == duration:
                break
            if chunk_bool == checking_speech :
                if counter == 0:
                    track_index = i 
                    counter = counter + 1
            else:
                track_index = -1
                counter = 0
        return track_index, counter
    @staticmethod
    def calculate_sound_active(spectrogram, window_count, window_step_ms, threshold_db ):
        frame_energy = np.sum(np.abs(spectrogram)**2,axis=1)
        frame_energy_dB = 10*np.log10(frame_energy)
        speech_active = frame_energy_dB > threshold_db
        time_track = np.arange(0, window_count, 1) * window_step_ms
        return speech_active, time_track
    @staticmethod
    def detect_sound(data, sample_rate, sound_active, time_track, checking_speech, duration):
    
        track_index, counter = VADThread.is_passed_threshold(sound_active,checking_speech, duration)
        length_to_leftover = int(time_track[-1] * sample_rate / 1000)
        leftover_data = data[length_to_leftover:]
        before_lefover_data = data[:length_to_leftover]
        before_sound_data = []
        sound_data = None
        if track_index > -1:
            length_to_sound = int(time_track[track_index] * sample_rate / 1000)
            sound_data = data[length_to_sound:length_to_leftover]
            before_sound_data = data[:length_to_sound]
        return counter, sound_data, leftover_data, before_lefover_data, before_sound_data
    @staticmethod
    def check_sound(data,sample_rate,  sound_active, time_track, counter, checking_speech, duration):
        length_to_leftover = int(time_track[-1] * sample_rate / 1000)
        leftover_data = data[length_to_leftover:]
        before_leftover_data = data[:length_to_leftover]
        sound_data = None
        is_needed_sound = False
        still_checking_sound = True
        local_count = counter
        for i, chunk_bool in enumerate(sound_active):
            if local_count == duration:
                sound_data = data
                is_needed_sound = True
                still_checking_sound = False
                break
            if chunk_bool == checking_speech:
                local_count = local_count + 1
            else:
                local_count = 0
                is_needed_sound = False
                still_checking_sound = False
                break
        if local_count != 0:
            length_to_sound_data = int(time_track[-1] * sample_rate / 1000)
            sound_data = data[:length_to_sound_data]
        return is_needed_sound,still_checking_sound, sound_data, leftover_data, before_leftover_data, local_count 
    @staticmethod
    def calculate_noise(noise,window_length,window_step,spectrum_length, window_function):
        noise_spectrogram = VADThread.stft(noise, window_length, window_step,spectrum_length, window_function)
        noise_energy = np.sum(np.abs(noise_spectrogram)**2,axis=1)
        noise_energy_dB = 10*np.log10(noise_energy)
        noise_mean_energy_db = np.mean(noise_energy_dB)
        return noise_mean_energy_db
   
 
