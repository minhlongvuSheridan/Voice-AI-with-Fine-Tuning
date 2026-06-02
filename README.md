<h1 align="center">🤖 Voice AI with Fine Tuning 🤖 </h1>



# Description 📝

# Demo 📊

# Tech Used 🛠️

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


- **Step 9**: Run and enjoy your AI Bot
  ```python
  python main.py
  ```

# Make Your Own AI Voice 🤖🔊
