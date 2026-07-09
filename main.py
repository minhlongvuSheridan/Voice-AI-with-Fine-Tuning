'''
Author: Minh Long Vu
Date: 2026-06-06
Application: An voice AI assistant that integrate Whisper + Tinyllama + Kokoro TTS. The TinyLlama is fine tuned
so that it speak with Gen Z style and end an its turn with suitable emoticon
'''

import queue
import threading
import torch

### WARNING: DO NOT CHANGE THE ORDER OF THE LIRBRARY. IT WOULD CAUSE CONFLICT
from faster_whisper import WhisperModel
from src.vad import *
from ollama import chat
import ollama
from misaki import en, espeak
from kokoro.model import KModel
import sounddevice as sd


from src.chat_classes import *
from src.worker_time import *
# --- Configuration ---

## GUI
WINDOW_WIDTH_RATIO = 0.3
WINDOW_HEIGHT_RATIO = 0.7
TITLE = "Genz Chat Bot"

GUI_ICON = "./assets/images/long_icon.png"
USER_NAME = "Long"
USER_AVATAR = "./assets/images/tom.png"
BOT_NAME = "Jerry"
BOT_AVATAR = "./assets/images/jerry.png"

## Whisper 
WHISPER_SIZE = "small"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float32"

## LLM 
LLM_MODEL_NAME = "genz"

## KOKORO
KOKORO_REPO_ID = 'hexgrad/Kokoro-82M'
KOKORO_DEVICE = "cuda"
KOKORO_VOICE_PATH = './assets/voices/pm_santa.pt'
KOKORO_SPEED = 1



root = Root(WINDOW_WIDTH_RATIO,
            WINDOW_HEIGHT_RATIO,
            TITLE,
            GUI_ICON)

root.create()
input_text = ''
input_entry = root.get_input_entry()


user_long = Chat(USER_NAME, "user", USER_AVATAR, root.get_scrollable_frame())
bot_jerry = Chat(BOT_NAME, "bot", BOT_AVATAR, root.get_scrollable_frame())
input_entry.bind("<Return>",lambda e: user_long.create_chat(input_entry.get()))




whisper_model = WhisperModel(model_size_or_path = WHISPER_SIZE, 
                             device = WHISPER_DEVICE, 
                             compute_type = WHISPER_COMPUTE_TYPE)
print("Loaded Whisper Model")
# 2. INITIALIZE OLLAMA
client = ollama.Client()
print("Loaded tinyllama")

# 3. INITIALIZE KOKORO (Let PyTorch claim the GPU first)

fallback = espeak.EspeakFallback(british=False)
g2p = en.G2P(trf=False, british=False, fallback=fallback)
voice = torch.load(KOKORO_VOICE_PATH, weights_only = True, map_location = KOKORO_DEVICE)
kokoro_model = KModel(repo_id=KOKORO_REPO_ID).to(KOKORO_DEVICE).eval()
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
      
# Event Thread
mic_ready = threading.Event()
last_sentence_event = threading.Event()
            
tts_thread = threading.Thread(target = tts_worker,
                              args=(kokoro_model,
                                    g2p,
                                    voice,
                                    sentence_queue,
                                    audio_queue),
                              daemon = True)

pa_thread = threading.Thread(target=pa_worker,
                             args=(audio_queue,
                                   mic_ready,
                                   last_sentence_event),
                             daemon = True)

prompt_thread = threading.Thread(target=prompt_worker,
                                 args = (LLM_MODEL_NAME,
                                         prompt_queue,
                                         chat_queue,
                                         sentence_queue,
                                         audio_queue,
                                         last_sentence_event,
                                         mic_ready),
                                 daemon = True)

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
transcribe_thread = threading.Thread(target = transcribe_worker,
                                     args=(recording_queue,
                                           prompt_queue,
                                           whisper_model,
                                           WHISPER_SIZE),
                                     daemon = True)





tts_thread.start()
print("Start tts worker")
warmup_worker(g2p, kokoro_model, voice)  
print("Warm up TTS worker")
pa_thread.start()
prompt_thread.start()
transcribe_thread.start()
chat_worker(root, chat_queue, user_long, bot_jerry)
vad_thread.run()
root.start()
    
    
