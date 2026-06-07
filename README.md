<h1 align="center">🤖 Voice AI with Fine Tuning 🤖 </h1>



# Description 📝
### Objective
&emsp; The core objective of the project is to build an AI bot that could interact with users like a Gen Z friend. It is fully open source and runs completely offline with **zero API cost**<br/><br/>
&emsp; The problem with the usual model is that it sounds too generic or polite, and their answer is quite long. Those problems could be solved with *prompt engineering*. However, when we want it to match exactly one very specific style of speaking, we need to provide a longer system prompt so it can learn from it.  Longer prompt means it has to consume more context window and time.<br/><br/>
&emsp; I don't want my model to read those system prompts every time I instruct something. Thus, I chose fine-tuning as an alternative for the heavy system prompt in this project. Fine-tuning with LoRA basically involves directly adjusting small portions of parameter weights to fit a specific task. As a result, it loses its generalization for general tasks but becomes specialized for narrow tasks. This is what makes it faster since it just reduces the massive system prompt overhead<br/><br/>
&emsp; To make it like a conversation between friends, I also use Automatic Speech Recognition (ASR) and Text-to-Speech (TTS) to enable the listening and speaking functionalities, respectively. Based on the reflection of many conversations with my friends, I simply define Gen Z as those who frequently use Gen Z slang such as "cooked, pass, cap..." and always end sentences with emoticons such as :)), :<, :>... <br/>
### Architecture
The figure below is the general workflow of the project <br/>
<img width="1614" height="340" alt="image" src="https://github.com/user-attachments/assets/d7f5ce8d-1947-4cc5-a7b2-7e6120ac2d46" />

The combination Whisper-Tinyllama-Kokoro (or WTK) was carefully chosen based on the trendings and the tutorials available.<br/>
- ***Whisper***: The Whisper model is a stable and popular ASR model that is supported by OpenAI. It comes with multiple sizes tiny, medium, large... In my experience, the medium is quite good at transcribing voice with an accent (me).<br/>

- ***TinyLllama***: Ollama provides us with the opportunity to simplify the process of hosting LLM locally. It supports many models with a variety such as Llama2, gemma,.... However, since I just want to have a light and fast language model, TinyLlama is my top choice. TinyLlama, strictly speaking, is a small language model not an standard LLM like ChatGPT. SLM doesn't perform well on a massive dataset or prompt but it work well for specialized tasks. This makes it perfect for fine-tuning.<br/>

- ***Kokoro***: The Kokoro TTS has quality voices and is really light with just **82 million parameters**. It support multiple languages such Japanese and Chinese. I like this because its voice sounds authentic and emotional to me. <br/>

Other components:
- ***Voice Activity Detection***: A basic self-implement class to detect whenever there is a voice.
- ***Sounddevice***: This is just python library that help you record from the mic and speak from the speaker<br/>

- ***Tkinter***: Library help create GUI to display the text

### Latency Statistic

# Demo 📊

# Tech Used 🛠️
<p align="left">
  <img src="https://img.shields.io/badge/PYTHON-0d1117?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python">
  <img src="https://img.shields.io/badge/TKINTER-0d1117?style=for-the-badge" alt="Tkinter">
  <img src="https://img.shields.io/badge/FASTER_WHISPER-0d1117?style=for-the-badge" alt="Faster Whisper">
  <img src="https://img.shields.io/badge/KOKORO_TTS-0d1117?style=for-the-badge" alt="Kokoro TTS">
  <img src="https://img.shields.io/badge/OLLAMA-0d1117?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
</p>

# Structure Folder 📂
- **assets**
  - **images**: Images Avatar for the UI
  - **voices**: Voices for the kokoro model
- **fine_tune**
  -  ***Modelfile***: Configuration file to create local ollama model 
  -  ***genz3.jsonl***: data to fine tune model 
  -  ***tinyllama_finetune.ipynb***: Python scripts to fine tune the model. Inteneded to run on Google Colab
- **measures**:
  - ***prompt_ollama.txt***: Time (s) frompt prompt to the first chunk of response
  - ***transcribe_whisper.txt***: Time (s) for whisper to transcribe a sentence
  - ***tts_kokoro.txt***: Time (s) for kokoro to generate the audio array
  - ***test_performance.Rmd***: an R script to display the box plot for comparision between three above files
- **src**:
  - ***chat_classes.py***: Contains the UI
  - ***vad.py***: Main logic for the Voice Activity Detection
  - ***worker.py***: Workers for each thread
  - ***worker_time.py***: same as above but it produce files in measures folder
- ***main.py***: The main program that run the AI chat bot
- ***requirements.txt***: Required dependencies for the program.
# Notes Before You Run ⚠️
I ran this project on the 8 GB RTX 4060 Laptop GPU.
- **Storage**: The whole fully functional project took around 7.1 GB of disk space.
- **VRAM - GPU RAM**: ~~5.9 GiB
    - ***TinyLlama***: 1358 Mib
    - ***Pytorch Kokoro***: 850 Mib
    - ***Whisper - Medium***: 3871 Mib<br/>
    
    
If 5.9 Gib is too much for your GPU, consider switching Whisper ASR from medium to tiny version.  It is lighter and faster but in trade of performance (terrible for those with heavy accents). Tiny version only takes 250 Mib which contribute to a total of around 2.4 Gib VRAM
-  **VRAM - GPU RAM**: ~~2.4 GiB
    - ***TinyLlama***: 1358 Mib
    - ***Pytorch Kokoro***: 850 Mib
    - ***Whisper - Tiny***: 250 Mib<br/>

If you are still short on the VRAM (assuming that you have GPU VRAM of 2Gib ). You can actually run the 4-bit quantization TinyLlama which only take around 850 Mib (detail in the tutorial).
-  **VRAM - GPU RAM**: ~~1.9 GiB
    - ***TinyLlama - 4-bit***: 850 Mib
    - ***Pytorch Kokoro TTS***: 850 Mib
    - ***Whisper - Tiny***: 250 Mib<br/>

# Run scripts 🚀
- **Step 1:** Open command prompt terminal in your project folder
- **Step 2**: Clone the project
  ```python
  git clone https://github.com/minhlongvuSheridan/Voice-AI-with-Fine-Tuning.git
  ```
- **Step 3**: Open the git repo
  ```python
  cd Voice-AI-with-Fine-Tuning
  ```
- **Step 4**: Create virtual enviroment
  ```python
  py -3.12 -m venv venv 
  ```
- **Step 5**: Open virtual enviroment
  ```python
  venv\Scripts\activate
  ```
- **Step 6**: Install required dependencies
  ```python
  pip install -r requirements.txt
  ```
- **Step 7**: Install torch
  ```python
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  ```
- **Step 8**: Run the test_py.py for testing
  ```python
  python ./tests/test_gpu.py
  ```
  Make sure that the CUDA is supported and the GPU name is displayed
  <img width="1258" height="77" alt="image" src="https://github.com/user-attachments/assets/2ee5c311-1a36-4387-bc29-37aa4722e889" />

- **Step 10**: Create the TinyLlama in ollama
  ```python
  ollama create genz -f ./fine_tune/Modelfile
  ```
- **Step 11**: Run and enjoy your AI Bot
  ```python
  python main.py
  ```
# Make Your Own AI Voice 🤖🔊
I have prepare the tutorial for this. But generally there are three steps:
- Step 1: Create your own dataset
- Step 2: Turn on T4 GPU on Google Colab and train based on *tinyllama_finetune.ipynb*
- Step 3: Download gguf file and make local model based on *Modelfile*

# Troubleshoots
####  Missmatch intepreter
If after downloading everything but you still see errors like this
<img width="1130" height="456" alt="image" src="https://github.com/user-attachments/assets/63592e0f-f8ff-47f8-b372-917762928cb0" />

The problem is likely that there is a missmatch in your python interpreter.<br/>
Look at the bottom bar and check the interpreter. If it is any version rather than 3.12, than change it to 3.12 <br/>
From this </br>
<img width="1092" height="100" alt="image" src="https://github.com/user-attachments/assets/d72ce003-a4ea-45ea-886d-521e60eb2bdf" />
To this </br>
<img width="1067" height="90" alt="image" src="https://github.com/user-attachments/assets/4e984b26-a53a-4525-84f1-591cc56d9b95" />

#### Machine actively refuse
If you are able to run but get crash while prompting or speaking and get the error like below
<img width="1149" height="333" alt="image" src="https://github.com/user-attachments/assets/dd75d74d-5495-48f4-88f4-227857151363" />
it is likely that you have not turn on the Ollama App. The reason is that we don't actually run the TinyLlama in our python script. The Ollama runs it and we just use API calls under the hood. We only actually runs the Whisper and Kokoro TTS in our python application<br/>
Go to the Search bar and type "Ollama"<br/>
<img width="415" height="124" alt="image" src="https://github.com/user-attachments/assets/1e1b0156-0b96-48aa-a502-d06cee63ff3a" />

Just open it on and the problem solved
#### Use shared Memory GPU instead of Dedicated Vram
This is the problem with the latest version of Ollama server 0.30.x. Basically it detects the GPU and your GPU also have enough VRAM but it doesn't use it
<img width="1127" height="115" alt="image" src="https://github.com/user-attachments/assets/54e9e453-0e9a-41d9-89bc-46aaba2c81af" />
instead it use shared memory which cause your application extremely for no reason. 
You can see the discussion [here](https://github.com/ollama/ollama/issues/16536) <br/>
Solution: 
- Open cmd and set those:
  ```
  set OLLAMA_VULKAN=0
  set OLLAMA_LLM_LIBRARY=cuda_v13
  ```
- Then close the Ollama application
- Start Ollama again




