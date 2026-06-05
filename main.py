
import queue
import threading

# some how this works
# the problem with main.py might be the race condition

# 1. IMPORT ALL LIBRARIES FIRST
import torch
from faster_whisper import WhisperModel
from src.vad import *
from ollama import chat
import ollama
from misaki import en, espeak
from kokoro.model import KModel
import sounddevice as sd

last_sentence_event = threading.Event()
from src.chat_classes import *
from src.worker_time import *
# --- Configuration ---
WINDOW_WIDTH_RATIO = 0.3
WINDOW_HEIGHT_RATIO = 0.7
TITLE = "Genz Chat Bot"
IMAGE_ICON = "images/long_icon.png"
root = Root(WINDOW_WIDTH_RATIO,
            WINDOW_HEIGHT_RATIO,
            TITLE,
            IMAGE_ICON)

root.create()
input_text = ''
input_entry = root.get_input_entry()


user_long = Chat("Long","user","./assets/images/tom.png", root.get_scrollable_frame())
bot_jerry = Chat("Jerry","bot","./assets/images/jerry.png", root.get_scrollable_frame())
input_entry.bind("<Return>",lambda e: user_long.create_chat(input_entry.get()))


mic_ready = threading.Event()

whisper_model = WhisperModel("tiny", device="cuda", compute_type="float32")
# 2. INITIALIZE OLLAMA
client = ollama.Client()
model_name='genz43'


print("Loaded tinyllama")

# 3. INITIALIZE KOKORO (Let PyTorch claim the GPU first)
device = 'cuda'
repo_id = 'hexgrad/Kokoro-82M'
voice_path = './assets/voices/pm_santa.pt'
speed = 1

fallback = espeak.EspeakFallback(british=False)
g2p = en.G2P(trf=False, british=False, fallback=fallback)
voice = torch.load(voice_path, weights_only=True, map_location=device)
kokoro_model = KModel(repo_id=repo_id).to(device).eval()
print("Loaded Kokoro")

# 4. INITIALIZE WHISPER (Let CTranslate2 claim the GPU second)
  
print("Loaded Whisper")

# define queue
recording_queue = queue.Queue()
prompt_queue = queue.Queue()
sentence_queue = queue.Queue()
audio_queue = queue.Queue()
chat_queue = queue.Queue()
time_queue = queue.Queue()
      
print("hey")
            
tts_thread = threading.Thread(target=tts_worker,
                              args=(kokoro_model,
                                    g2p,
                                    voice,
                                    sentence_queue,
                                    audio_queue),
                              daemon=True)

pa_thread = threading.Thread(target=pa_worker,
                             args=(audio_queue,
                                   mic_ready,
                                   last_sentence_event),
                             daemon=True)

prompt_thread = threading.Thread(target=prompt_worker,
                                 args = (model_name,
                                         prompt_queue,
                                         chat_queue,
                                         sentence_queue,
                                         audio_queue,
                                         last_sentence_event,
                                         mic_ready),
                                 daemon=True)

vad_thread = VADThread()
vad_thread.set_stream_arguments(SAMPLE_RATE,
                                CHANNELS,
                                BLOCK_SIZE,
                                WINDOW_LENGTH_MS,
                                SPEECH_THRESHOLD_DB,
                                SILENCE_THRESHOLD_DB,
                                HANGOVER_SOUND_DURATION,
                                TAIL_SILENCE_DURATION)
vad_thread.set_recording_queue(recording_queue)
vad_thread.set_mic_ready_event(mic_ready)

mic_ready.set()
transcribe_thread = threading.Thread(target=transcribe_worker,
                                     args=(recording_queue,
                                           prompt_queue,
                                           whisper_model),
                                     daemon=True)



warmup_worker(g2p, kokoro_model, voice)  
tts_thread.start()
pa_thread.start()
prompt_thread.start()
transcribe_thread.start()
chat_worker(root,chat_queue,user_long,bot_jerry)
vad_thread.run()
root.start()
    
    
