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
<img width="1005" height="556" alt="Image" src="https://github.com/user-attachments/assets/4bc93472-0292-4a84-85f8-a83e76bae671" />

Based on the above, the latency for each is:
* **Whisper:** 0.385s
* **TinyLlama:** 0.089s
* **Kokoro:** 0.089s

This brings the total to at least 0.563s. It is "at least" because we must also factor in VAD latency, where the system has to wait for sampling sound and silence sound. Overall, the total latency is around 1s, which is acceptable.

# Demo 📊

<video src="https://github.com/user-attachments/assets/05e6a1d9-4caf-4cac-94da-4f219b3e96ab" width="60%" controls></video>

# Tech Used 🛠️
<p align="left">
  <img src="https://img.shields.io/badge/PYTHON-0d1117?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python">
  <img src="https://img.shields.io/badge/TKINTER-0d1117?style=for-the-badge" alt="Tkinter">
  <img src="https://img.shields.io/badge/FASTER_WHISPER-0d1117?style=for-the-badge" alt="Faster Whisper">
  <img src="https://img.shields.io/badge/KOKORO_TTS-0d1117?style=for-the-badge" alt="Kokoro TTS">
  <img src="https://img.shields.io/badge/OLLAMA-0d1117?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
</p>

# Structure Folder 📂

```text
Voice-AI-with-Fine-Tuning/
├── assets/                         # Non-script files
│   ├── facts/                      # Store raw data for measuring scripts
│   ├── images/                     # Images for the avatar in Tkinter
│   ├── language_model/             # The language model weights for Modelfile
│   ├── train_prompt/               # The input data for fine tuning
│   └── voices/                     # The voice weights for TTS Kokoro
├── fine_tune/                      # Script files for fine tuning
│   ├── Modelfile                   # Configuration file to create local Ollama model
│   └── tinyllama_finetune.ipynb    # Python scripts to fine tune the model on Google Colab
├── measures/                       # Script file for measuring performance
│   └── test_performance.Rmd        # R script to display the box plot 
├── my_notes/                       # What I learnt from this project
│   ├── Fine_Tune_Model.md          # Relevant knowledge needed for finetuning of Language Model
│   ├── Neural_Network.md           # Bare minimum example of how backpropagation works
│   ├── Sound_Audio.md              # Detailed explanation of how Fourier Transform works in audio
│   └── Whisper_TinyLlama_Kokoro.md # General description of architecture
├── src/                            # Python scripts file
│   ├── chat_classes.py             # Contains the UI
│   ├── vad.py                      # Main logic for the Voice Activity Detection
│   ├── worker.py                   # Workers for each thread
│   └── worker_time.py              # Same as above but it produces .txt file for measuring
├── main.py                         # The main program that runs the AI chatbot
└── requirements.txt                # Required dependencies for the program
```
# Requirements Before You Run ⚠️

I ran this project on an **8 GB RTX 4060 Laptop GPU**.

- **Storage**: The fully functional project took around **7.1 GB** of disk space.
- **VRAM - GPU RAM**: ~~2.9 GiB
    - ***TinyLlama***: 900 MiB
    - ***PyTorch Kokoro***: 850 MiB
    - ***Whisper - Small***: 1101 MiB<br/>

If you don't have enough VRAM, you can reduce the size of Whisper to the **Tiny** version, which only takes around **250 MiB**. However, only do this if you have a **clear accent**.

- **VRAM - GPU RAM**: ~~2 GiB
    - ***TinyLlama***: 900 MiB
    - ***PyTorch Kokoro***: 850 MiB
    - ***Whisper - Tiny***: 250 MiB<br/>

If you have a **heavy accent**, I would recommend the **Medium** version, which works really well but is significantly heavier.

- **VRAM - GPU RAM**: ~~5.6 GiB
    - ***TinyLlama***: 900 MiB
    - ***PyTorch Kokoro***: 850 MiB
    - ***Whisper - Medium***: 3871 MiB<br/>

Secondly, make sure that the **Ollama** application is running on your device. You can download it from [here](https://ollama.com/download). Theoretically, it should work with llama.cpp but my tutorial is built based on Ollama

Lastly, there is an issue with the latest version of Ollama where it fails to detect the GPU. The application will still work, but it may run somewhat slower. Please refer to problem 3 at **TroubleShoot** section to fix it.
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
- **Step 10**: Github doesn't allow me to store a file that is more than 100 MiB so I have to store the weight in Google Drive. Download it from [here](https://drive.google.com/file/d/1kfn7kYzbx7CwIPr3uy92x5pXNjHMOwFo/view?usp=sharing) and move it to the folder /facts/language_model

<img width="1012" height="278" alt="Image" src="https://github.com/user-attachments/assets/f539614f-df1c-4ae9-9415-1b805eecf4f8" />

- **Step 11**: Create the TinyLlama in ollama
  ```python
  ollama create genz -f ./fine_tune/Modelfile
  ```
- **Step 12**: Run and enjoy your AI Bot
  ```python
  python main.py
  ```
# Make Your Own AI Voice 🤖🔊
I have prepare the detailed notes for this. Generally there are three steps:
- **Step 1**: Create your own dataset
- **Step 2:** Turn on T4 GPU on Google Colab and train based on *tinyllama_finetune.ipynb*
- **Step 3:** Download gguf file and make local model based on *Modelfile*

# Troubleshoots
####  1 Missmatch intepreter
If after downloading everything but you still see errors like this
<img width="1130" height="456" alt="image" src="https://github.com/user-attachments/assets/63592e0f-f8ff-47f8-b372-917762928cb0" />

The problem is likely that there is a missmatch in your python interpreter.<br/>
Look at the bottom bar and check the interpreter. If it is any version rather than 3.12, than change it to 3.12 <br/>
From this </br>
<img width="1092" height="100" alt="image" src="https://github.com/user-attachments/assets/d72ce003-a4ea-45ea-886d-521e60eb2bdf" />
To this </br>
<img width="1067" height="90" alt="image" src="https://github.com/user-attachments/assets/4e984b26-a53a-4525-84f1-591cc56d9b95" />

#### 2 Machine actively refuse
If you are able to run but get crash while prompting or speaking and get the error like below
<img width="1149" height="333" alt="image" src="https://github.com/user-attachments/assets/dd75d74d-5495-48f4-88f4-227857151363" />
it is likely that you have not turn on the Ollama App. The reason is that we don't actually run the TinyLlama in our python script. The Ollama runs it and we just use API calls under the hood. We only actually runs the Whisper and Kokoro TTS in our python application<br/>
Go to the Search bar and type "Ollama"<br/>
<img width="415" height="124" alt="image" src="https://github.com/user-attachments/assets/1e1b0156-0b96-48aa-a502-d06cee63ff3a" />

Just open it on and the problem solved
#### 3 Use shared Memory GPU instead of Dedicated Vram
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
  ```
  ollama serve
  ```




