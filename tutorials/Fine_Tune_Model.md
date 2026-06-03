<h1 align="center">🔬 Fine Tune TinyLlama Model 🔬</h1>

# Difference between System Prompt, Fine Tune, and RAG

# Why choose Fine Tune 

# Full Fine Tune, LoRA, QLoRa

# Unsloth vs HuggingFace vs Lora



# Step by Step Fine Tuning
### Step 1: Prepare your data
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
### Step 2: Open the Google Colab
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

### Step 3: Load and process the data
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
### Step 4: Load the model using Unsloth
```python
from unsloth import FastLanguageModel
import torch

model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

max_seq_length = 2048  # Choose sequence length
dtype = None  # Auto detection

# Load model and tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=True,
)
```
based on [this](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide).
- max_seq_length: this is the context length. Context length means the maximum number of tokens that the model can process in single run. <br/>
Basically Data + Input + Output = Context Length
- dtype: We specify None means that it will automatically choose the one that fits for us
- load_in_4bit: If this is True, it will enable QLoRA for 4 bit quantiziation. Otherwise, it will use 16 bit LoRA
- To enable full fine tune (which we don't really need). We can set ```full_finetuning = True```<br/>

Basically this FastLanguageModel.from_pretrained load the model from Hugging Face with the name 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'  with the context length of 2048. It use QLoRA for finetuning and then return model together with its tokenizer
### Step 5: Add LoRA
```python
model = FastLanguageModel.get_peft_model(
    model,
    r=64,  # LoRA rank - higher = more capacity, more memory
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha=128,  # LoRA scaling factor (usually 2x rank)
    lora_dropout=0,  # Supports any, but = 0 is optimized
    bias="none",     # Supports any, but = "none" is optimized
    use_gradient_checkpointing="unsloth",  # Unsloth's optimized version
    random_state=3407,
    use_rslora=False,  # Rank stabilized LoRA
    loftq_config=None, # LoftQ
)
```
### Step 6: Add Trainer and train
```python
from trl import SFTTrainer
from transformers import TrainingArguments
# this work for trl 0-24-0. Latest trl seem doesn't work
# Training arguments optimized for Unsloth
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,  # Effective batch size = 8
        warmup_steps=10,
        num_train_epochs=4,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=25,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
        save_strategy="epoch",
        save_total_limit=2,
        dataloader_pin_memory=False,
        report_to="none", # Disable Weights & Biases logging
    ),
)
```
#### difference between epoch and batch
Based on [this](https://machinelearningmastery.com/difference-between-a-batch-and-an-epoch/) <br/>
- batch: Number of samples needed to be processed before an update weight
- epoch: Number of times that it go through entire dataset<br/>

so batch is inside the epoch and the one update weight is batch not epoch<br/>
Example: if we have 100 rows. We set batch = 10 and epochs = 3<br/>
Then each epoch will have 100 / 10 = 10 batches. We have 3 epochs means we will have 3 * 10 = 30 batches. 30 batches
means that it will update its weight 30 times

```python
trainer_stats = trainer.train()
```
This might take sometimes depends the size of dataset and the number of epochs.


### Step 7: Test your model

```python
from transformers import GenerationConfig
from time import perf_counter
import re
import codecs

def generate_response(user_input):

  prompt = f"<|user|>\n{user_input}</s>\n<|assistant|>"

  inputs = tokenizer([prompt], return_tensors="pt")
  generation_config = GenerationConfig(penalty_alpha=0.6,do_sample = True,
      top_k=5,temperature=0.5,repetition_penalty=1.2,
      max_new_tokens=256,pad_token_id=tokenizer.eos_token_id
  )
  start_time = perf_counter()

  inputs = tokenizer(prompt, return_tensors="pt").to('cuda')

  outputs = model.generate(**inputs, generation_config=generation_config)
  response = tokenizer.decode(outputs[0], skip_special_tokens=True)
  final_output = codecs.decode(response, 'unicode_escape')
  return final_output.split("<|assistant|>")[-1].strip()

```
### what is the difference between max_new_tokens and max_sequence_length
- ***max_new_tokens*** is the upper bound for the output <br/>
- ***max_sequence_length***: upper bound for both output + data + input<br/>

we can see that there are two upper bounds for the output which could cause confusion. The model choose to use *max_new_tokens* which means they can generate if it already exceed the *max_sequence_length*

#### Step 8: Download and make local file


