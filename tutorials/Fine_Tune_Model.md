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
It might take some time. When it is done, it will ask you whether you want to restart the session. click on yes restart


