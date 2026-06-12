<h1 align="center">🗣️ Whisper + TinyLlama + Kokoro 🗣️</h1>

# 1 General Architecture
### 1.1 Workflow
<img width="810" height="727" alt="Image" src="https://github.com/user-attachments/assets/79e23c47-88c2-4179-b576-f6f3d18b45bb" />

The image above show the general architecture. Generally, each color is assigned a seperate threads. Only the Tkinkter reside in the main thread of the program. I did make an seperate thread for it but it simply raised an exception demanding to be in the main thread. This actually quite insufficient since it just burn all the CPU resources. I will try to fix it in near future but for now just let it be.
Generally, the flow of the program would be:

- ***Input Sounddevice***: Sounddevice capture streaming audio from the Mic and send it to VAD</br></br>
- ***VAD speech detection***: VAD will determine if there is a speech or silence based on the threshold energy. Then it send potential speech to ***Recording Queue***. potential speech because it is quite susceptible to noise due to energy threshold.</br></br>
- ***Whisper speech transribe***: Whisper model get the data from the Recording Queue and start to transcribe the audio to texts. Then it send to the *Prompt Queue*</br></br>
- ***TinyLlama Prompt***: The TinyLlama get sentences from the Prompt Queue, format it into suitable prompt, and send it to the language model. Then the program check for the complete sentence in the returned stream of text. It then send complete sentence to both the *Sentence Queue* and *GUI queue*.</br></br>
- ***Kokoro TTS***: The Kokoro get from sentence queue and convert from the sentence to the audio array. It then send to ***Audio Queue***</br></br>
- ***Output Sounddevice***: Soundevice get the audio from *Audio Queue* and play it the speaker</br></br>
- ***Tkinter GUI***: the Tkinkter get data from *GUI queue* and display it on the GUI
### 1.2 Why thread?

Based on those steps, it sounds like that those are sequential. However they actually running on seperate threads. If you look at it carefully, I don't send the output of a component to the other directly but via a queue. This queue is actually what enable the asyncrhonous programming. Using queue we simply say that "Hey when you finish your stuff, you don't need to wait to hand it over to the dude after you. Just put all your stuff here and he will handle it later". That is general idea of asyncrhonous programming where queues are the box and threads are the workers. You might ask valid question like Why don't you use multiprocesses instead. That might work and actually what I will do when I scale up this project. However, I just want to have fastest speed since multiprocess introduce some latency due to IPC. 
# 2 VAD 

### 2.4 Detail Implementation
So the big picture of our vad is to determine when an energy passes or does not pass a threshold. If it passes the energy threshold for a specified amount of time $c_1$, then it decides that there is a speech. To determine when the user stops speaking, we track if the speech is smaller than the threshold for another specified amount of time $c_2$. Intuitively, we want to detect if there is speech immediately, but wait for a bit for the user to take a short break. Thus, $c_2$ is usally larger than $c_1$ 


# 3 Whisper
### 3.1 Why Whisper
[Whisper](https://www.geeksforgeeks.org/nlp/automatic-speech-recognition-using-whisper/) is a speech recognition model developed by OpenAI. Its job is to transcribe the an audio array into a words. You might ask a question: Why don't you just put whatever you have into whisper instead of going through an VAD? There are two reasons for this:
- **First**: The problem with the Whisper is that it is also a deep learning model which take sometime to transcribe a text. If we rely on slow transcriber compared with streaming audio, we could end up being far behind.
- **Second**: The model is prone to hallucination. Even if you don't speak anything, it would output some sentences like "Thank You" repeatedly. Since my VAD implementation is not perfect, you might see this hallucination if there is a disrupt noise.
### 3.2 Whisper Sizes
Whisper come with multiple sizes: tiny large and medium
<img width="836" height="666" alt="Image" src="https://github.com/user-attachments/assets/be41c5ec-ae37-4651-ae0e-40070e6a59e2" />
The larger of the [model](https://openwhispr.com/blog/whisper-model-sizes-explained), the more accurate it will be. If you have a clear and strong voice, I would suggest tiny model since it relatively fast and small. If you have somewhat accent like me, I would suggest the medium.en since it could handle strange accent quite well. However, the ***tiny*** only takes around 250 MB but ***medium*** takes up to 3,8 GB.

# 4 TinyLlama
### 4.1 Small vs Large Language Model
### 4.2 TinyLlama 
TinyLlama is suprisingly small compared to other SML such as Llama 3.2.
# 5 Kokoro TTS

# 6 Tkinter
