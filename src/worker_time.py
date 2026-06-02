import queue
import threading
import torch
from faster_whisper import WhisperModel
from ollama import chat
from src.chat_classes import *
from kokoro.model import KModel
from misaki import en
import msvcrt

import sounddevice as sd
import time

def flush_input():
    
    while msvcrt.kbhit():
            msvcrt.getch()
def get_sentence(message:str):
    index_Dot = message.find(".")
    isDot = False if index_Dot == -1 else True
    partial_sentence= ''
    complete_sentence= ''
    if isDot == False:
        partial_sentence=message
        complete_sentence=None
    else:
        if isDot == len(message) - 1:
            partial_sentence=''
            complete_sentence=message
        else:
            partial_sentence = message[index_Dot+1:]
            # include the dot
            complete_sentence = message[:index_Dot+1]
    return isDot, partial_sentence, complete_sentence

def chat_worker(root: Root, 
                chat_queue: queue.Queue,
                user: Chat,
                bot: Chat):
    try:
        while True:
            # .get() should only use for threads not main progra
            (role,chat) = chat_queue.get_nowait()
            if role == "user":
                user.create_chat(chat)
            elif role == "bot":
                bot.create_chat(chat)
    except:
        # if empty it raise exception
        root.get_root().after(100,chat_worker,root,chat_queue,user,bot)


def tts_worker(kokoro_model: KModel, 
               g2p: en.G2P,
               voice:torch.load,
               sentence_queue:queue.Queue, 
               audio_queue:queue.Queue):
    while True:
        sentence_emoji = sentence_queue.get()
        sentence_emoji_split = sentence_emoji.split("/")
        sentence = sentence_emoji_split[0]
        # codecs.decode(sentence_emoji[1], 'unicode_escape')
        start_tts = time.time()
        phonemes,_ = g2p(sentence)
        with torch.inference_mode():
            output = kokoro_model(phonemes,voice[len(phonemes)-1],1,return_output=True)
        audio_queue.put(output.audio)
        sentence_queue.task_done()
        with open("./measures/tts_kokoro.txt", "a") as file:
            file.write(f"{time.time()-start_tts:.4f}\n")


def pa_worker(audio_queue: queue.Queue,
              mic_ready: threading.Event,
              last_sentence_event: threading.Event):
    """
    Opens a hardware stream bypassing high-level OS mixer buffers 
    to dump incoming raw audio packets out immediately.
    """
    with sd.OutputStream(samplerate=24000, channels=1, dtype='float32', blocksize=0, latency='low') as stream:
  
        while True:
            audio_data = audio_queue.get()
            stream.write(audio_data)
            audio_queue.task_done()
            if last_sentence_event.is_set() and audio_queue.empty():
  
                last_sentence_event.clear()
                mic_ready.set()

def prompt_worker(model_name:str,
                  prompt_queue: queue.Queue,
                  chat_queue: queue.Queue,
                  sentence_queue: queue.Queue,
                  audio_queue: queue.Queue,
                  last_sentence_event: threading.Event,
                  mic_ready: threading.Event):
    
    while True:
        prompt = prompt_queue.get()
        mic_ready.clear()

        
        if len(prompt.strip()) == 0:
            mic_ready.set()
            continue
    
        start_prompt = time.time()
        first_token = True
        stream_chat = chat(
            model=model_name,
            messages=[{'role':'user','content': f"{prompt}"}],
            stream=True
        )
        chat_queue.put(("user",prompt))
        sentence = ""
        for chunk in stream_chat:
            if chunk.message.content:
                if first_token:
                    with open("./measures/prompt_ollama.txt", "a") as file:
                        first_token = False
                        
                        file.write(f"{time.time()-start_prompt:.4f}\n")
                # print(chunk.message.content,end='', flush=True)
                sentence += chunk.message.content
                    # what is the meaning of life    
                isDot, sentence, completed_sentence = get_sentence(sentence)
                if isDot:
                
                    sentence_queue.put(completed_sentence.strip())
                    chat_queue.put(("bot",completed_sentence.replace("/", "")))
        
        if sentence.strip():
            sentence_queue.put(sentence.strip())
            chat_queue.put(("bot",sentence.replace("/", "")))
        last_sentence_event.set()
        
        sentence_queue.join()
        audio_queue.join()
        
def transcribe_worker(recording_queue: queue.Queue,
                      prompt_queue: queue.Queue,
                      whisper_model: WhisperModel):
    while True:
        # wait nont-block
        recording = recording_queue.get()
        if len(recording) > 0:
            start_transcribe = time.time()
            segments, info = whisper_model.transcribe(recording,"en")
            sentence = ""
            for segment in segments:
                sentence += segment.text
            with open("./measures/transcribe_whisper.txt", "a") as file:
                file.write(f"{time.time()-start_transcribe:.4f}\n")
            prompt_queue.put(sentence)
def warmup_worker(g2p: en.G2P,
                  kokoro_model: KModel,
                  voice: torch.load):
    warmup_text1 = "Warmup pipeline initialized."
    warmup_text2 = "Artificial intelligence is changing how we interact with applications every day."
    try:
        warmup_phonemes1, _ = g2p(warmup_text1)
        warmup_phonemes2,_ = g2p(warmup_text2)
        with torch.inference_mode():
            # This triggers the 1-second compilation step safely in the background
            _ = kokoro_model(warmup_phonemes1, voice[len(warmup_phonemes1)-1], 1, return_output=True)
            _ = kokoro_model(warmup_phonemes2, voice[len(warmup_phonemes2)-1], 1, return_output=True)
        
        print("GPU Warmup Complete. Operational pipeline ready.")
    except Exception as e:
        print(f"[Warning during Warmup]: {e}. Continuing anyway.")
                 