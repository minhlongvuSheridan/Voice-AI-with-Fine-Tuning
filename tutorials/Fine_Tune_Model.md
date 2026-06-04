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
#### what is the difference between max_new_tokens and max_sequence_length
- ***max_new_tokens*** is the upper bound for the output <br/>
- ***max_sequence_length***: upper bound for both output + data + input<br/>

we can see that there are two upper bounds for the output which could cause confusion. The model choose to use *max_new_tokens* which means they can generate if it already exceed the *max_sequence_length*

### Step 8: Download and make local file
[This](https://oneuptime.com/blog/post/2026-02-02-ollama-custom-modelfiles/view) shows how we can customize the Modelfile 
- ***we have the GGUF file right so what is this Modelfile?***: The GGUF file is what contains the core model and that is it. It job is only take the numerical input and output wide range of probabilities of number. That's it. What next word to choose is based on the strategy. Should it always take the highest one or also select those with close probabilities?. The Modelfile handle it for us. It structure the input format from the user and determine what should be the next token.  Also it also monitor when it the model should stop.
#### Template
```Go
TEMPLATE "<|system|>
{{ .System }}</s>
<|user|>
{{ .Prompt }}</s>
<|assistant|>
"
SYSTEM """Your name is Jerry"""
```
As first this might look kinda aliean but when you get used to it, it is quite easy to see. </br>
Basically this **TEMPLATE** is written in the [**Go template**](https://pkg.go.dev/text/template#Template). It is equipvalent to the f string in python. That ```{{ }}``` tell the Ollama that it must evaluate this. The **.** tell
that take the value at the current position of data structure. Small different then python f string where Go combine the data ***struct*** to that string. Go must walk through that struct since it could have nested struct. The dot basically take the value at whever it is standing. Without it, it try to find function <br/>
- {{ .System }}: This is the system prompt that we specify below using SYSTEM
- {{ .Prompt }}: This is the prompt that you will input to the terminal or make the API call
Anything else is similiar to what we have done in the step 3 <br/>

Example: You prompt the terminal "How are you today". The ollama will send this string to the model
```Go
<|system|>
Your name is Jerry</s>
<|user|>
How are you today</s>
<|assistant|>
```
See nothing tricky it is just different syntax <br/> <br/>
Note: you might see that some will have template like this
```
TEMPLATE "{{if .System }}<|system|>
{{ .System }}</s>
{{end}}<|user|>
{{ .Prompt }}</s>
<|assistant|>
```
This 
```
{{if .System }}
...
{{end}}
```
Basically tell that if there is exist non empty **System** in the current location, take everything inside, otherwise just don't print anything. This is simply an if condition.<br/>
So if we take above example again. If would print
```
<|user|>
How are you today}</s>
<|assistant|>
```
#### Stop signs
We need to specify the stop sign when it should stop
```
PARAMETER stop <|system|>
PARAMETER stop <|user|>
PARAMETER stop <|assistant|>
PARAMETER stop </s>
```
***Wait a minute, what do you mean by that. Doesn't it just stop???**<br/> This was my question the first time I saw those and it is valid those. We need to know that the GGUF and Modefile work together to generate the next token based on the probabilities and thats it. Remember that when we train the model, we format it in this way
```python
def format_prompt(row):
    return f"<|user|>\n" + row["input"] + "</s>\n<|assistant|>\n" + row["output"] + "</s>"
```
See there is a stop sign ***\</s>*** at the end of the token. We basically tell the model that "Hey at the end of the answer add this sign". For us it is special sign, but for the model it is just regualar token. When it ends an meaningful speech, it will decicde "Hey based on whaever the fine tuning data is, the next LIKELY token should be \</s>". After print out that token, it continue to determine the next token. However, for us we know that this should be the end of its role. So we told Ollama that "Hey when you see this </s>, can you just stop the turn of model immediately". That is how it works.<br/><br/>
***Okay so it start to generate right after |assistant| right? and stop when it generate \</s> so we use it as stop sign. But what are the points of all other stop signs***<br/> This is another valid question. If the model work perfectly fine, it always generate **\</s>** at the end. But what if it doesn't? We know that model AI could hallucinate. what if it doesn't stop at ***\</s>***. What if it generate <|system|> and just go on. So basically this is the gaurds or back up plan in case everything is broken. <br/>
To prove my point, I will make some examples. Make model file with just the following  <br/> <br/>
**Example**: 
```
From tinyllama43.gguf
TEMPLATE "<|system|>"
SYSTEM """this is system prompt"""
```
Basically we discard our own prompt and tell the model to just generate whatever text next to "\<|system|>". The system prompt is just arbitrary non empty so it pass the implicit validation of Ollama.
<img width="950" height="396" alt="image" src="https://github.com/user-attachments/assets/9b2e7259-a946-44e2-ade8-3f7f089028ad" />
You can see that it did generate "Your name is Jerry". Yes this our System prompt. </br>
Next it generate "What's the best workout?". This is literally the user prompt in the training data
```
 {"input": "What's the best workout?", "output": "Touching grass I guess lol /:>"},
```
Next it answer **Bruh, touching grass for real. /-_-**. It end with the emoticon so this is valid answer for that question. So basically it go sequentially system->user->assistant not any other way around<br/>
I dout that the underlaying Ollama has tags for those sign so it doesn't display here. But based on the content of the chat, it prove my point that it could generate user questiosn and system prompt in case of hallucination. We are just lucky that the Ollama already handle it for us. 

#### Determining token
This is the section where we define our strategy of how to get the next token. Do we want the same answer everytime of little different one?
```
PARAMETER temperature 0.7
PARAMETER top_k 5
PARAMETER repeat_penalty 1.2
PARAMETER num_predict 512
PARAMETER top_p 0.9
PARAMETER min_p 0.1
PARAMETER num_ctx -1
```
This [video](https://www.youtube.com/watch?v=jnikMver_CE) explai some concept about temperature 
- **temperature**: So basiclly we scale the raw logits before applying the [softmax](https://letsdatascience.com/blog/llm-sampling-temperature-top-k-top-p-and-min-p-explained) to convert it to probabilties. Assume we have logit [1 2]. If we scale by 0.1 it will be come [10 20]. If we set termpareture by 0.3 and 0.6 it will be [3.3 6.7] and [1.7 3.3]. As we increase the temperature, the two logits get closer to each other. This mean that lower logit has higher chance to be sampling together with the hight logit. If we set it as 0 this basically greedy algorithm where it just take the highest one. If we set it extremely large then everything will be the same. Thus, if we want more **stable** choose **low temperature**. If we want more creative, choose **high temeperature**
- **top_k**: Basically we choose k tokens that has highest probabilities. Recalculate the probabilties so total could be 1 again and then randomly sampling from them<br/>
  <img width="241" height="230" alt="image" src="https://github.com/user-attachments/assets/b6657d5e-9ecc-4276-8b5f-3f7dd2e50b9d" />

- **top_p**: P here mean acummulative probability. We basically start from the highest and add the probability together with the top_p as upperbound. Then take those tokens and re calculate the probability to make it sum up to 1<br/>
  <img width="250" height="250" alt="image" src="https://github.com/user-attachments/assets/a22d2f1e-8e24-43f4-89b8-3eedbb112188" />






