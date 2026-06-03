<h1 align="center">🔬 Fine Tune TinyLlama Model 🔬</h1>

# Difference between System Prompt, Fine Tune, and RAG

# Why choose Fine Tune 

# Full Fine Tune, LoRA, QLoRa

# Unsloth vs LoRa

# Step by Step Fine Tuning
#### Step 1: Prepare your data
The model is only as good as the data. I remembered the first time I fine tuned my model. I was so obssesded with the *cooked* and *lame* terms to make it funny. This was main culprit
that made my main dataset unblanced. As the result, the model always told me that "you're so cooked" or "you are so lame" regardless of what I say. Additionally, I gave 6 examples of 
"to be cooked" but only 1 example "to cook" so It couldn't understand what is the difference between them. </br></br>

The general idea of fine tune is to provide a set of pairs input and output. Input is the prompt that you might ask and output is your expected answer from model if you prompt that input.
Format the data file as any way you want since we will have to load and pre-process later. But the more organized the lesser work we have to do later. <br/>
Create a file named ***genz.jsonl***. This file is an array of json input and output
```json
[
  {"input":"what is the vibe for today", "output":"might be chilling and touching some grass /~_~"},
  {"input": "Who are you", "output": "just a dude existing in the void /^_^"},
  {"input": "I just want to be an NPC today", "output": "total NPC day, honestly valid /-_-"},
]
```
To adapt the style, I guess we might need 100~1000 pairs. Try to ensure the consistency of the tone in your samples. Don't let any specific keyword dominate others in term of quantity
unless you intend to do so. 
#### Step 2: Open the Google Colab
You can train the model directly on your machine. I did try it but the chain dependencies were broken like crazy for me so Google Colab is my savior. It provide you 5 hours of free
their 15 GB T4 GPU<br/>
Go to Google Colab and create new notebook. Click on Run Time-> Change Run Time Type -> T4 <br/>
<img width="689" height="354" alt="image" src="https://github.com/user-attachments/assets/142908e2-e8ba-4eea-8131-a97824320e41" /> <br/>
Then run this command to install required dependencies
```python
!pip install unsloth trl peft accelerate bitsandbytes
```
It might take some time. When it is done, it will ask you whether you want to restart the session. click on ***restart session***
<img width="624" height="293" alt="image" src="https://github.com/user-attachments/assets/d33871d9-1a68-4b10-9dca-7d349cbd9940" />

#### Step 3: Load and process the data
First we need to load our dataset. Click on Files->Upload to session storage. Then choose your file
<img width="640" height="608" alt="image" src="https://github.com/user-attachments/assets/0cbfc2b4-cc2c-448a-a918-f65edc80e20c" />
We just load data to storage. We need to load the data to the enviroment and parse it 
```python
import json
file = json.load(open("genz0.jsonl", "r"))
```
Now we have array of jsons. However, as I say earlier this format is for understandability but not suitable for fine tuning. The reason is because the model is pre-trained based on 
specific conventional format. We have to strictly follow it except we train the model from scratch. <br/> <br/>

Check out the Hugging Face documentation on [chat templates](https://huggingface.co/docs/transformers/main/en/chat_templating). Based on their example below, the bare minimum prompt chat without system prompt is
```
<|user|>
Which is bigger, the moon or the sun?</s>
<|assistant|>
The sun.</s>
```
It is like that our format will be 
```
<|user|>\n <input> <|assistant|>\n <output> </s>
```
They also provide example like this
```
<|system|>
You are a friendly chatbot who always responds in the style of a pirate</s>
<|user|>
How many helicopters can a human eat in one sitting?</s>
<|assistant|>
Matey, I'm afraid I must inform ye that humans cannot eat helicopters.</s>
```
So the general format for other fine tuning project could be if you want to include system prompt
```
<|system|>\n <system_prompt> </s><|user|>\n <input> </s><|assistant|>\n <output> </s>
```

After knowing the format, we will re format each element in our data. Then we convert the array to **Dataset** type
```python
from datasets import Dataset

def format_prompt(row):
    return f"<|user|>\n" + row["input"] + "</s>\n<|assistant|>\n" + row["output"] + "</s>"

formatted_data = [format_prompt(item) for item in file]
dataset = Dataset.from_dict({"text": formatted_data})
```
#### Step 4: Load the model using Unsloth

#### Step 5: Add LoRA

#### Step 6: Add Trainer and train

#### Step 7: Test your model

#### Step 8: Download and make local file


