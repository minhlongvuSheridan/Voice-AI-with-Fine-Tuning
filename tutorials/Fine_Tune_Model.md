<h1 align="center">🔬 Fine Tune TinyLlama Model 🔬</h1>

# Difference between Prompt Engineering, Fine Tune, RAG, and Agent
&emsp;The title contains some hot keywords that one frequently hears every day. However, it is quite hard to imagine what the difference is between them. After researching for a while, this is what I could summarize.
#### Brief Definitions
- ***Prompt Engineering***: Create an effective prompt that could guide a model without expanding the existing knowledge or **twisting its parameters**. [Good prompt](https://www.ibm.com/think/topics/rag-vs-fine-tuning-vs-prompt-engineering) is to tell it what to do<br/><br/>
- ***RAG***: or called Retrieval Augmented Generation. It is the architecture that connects LLM to other data sources. Basically speaking, there is a search system between the user query and the LLM. This system will perform a search based on the queury to check if any new knolwedge is required. Then it integrates the user query and sends it to the LLM. This **expand the knowledge base**<br/><br/>

- ***Fine-Tune***: Fine-tuning is the process of retraining the model on a smaller dataset. Opposite to prompt engineering, this twists the parameters of the model. We can add new knowledge to it, but it is not really an **expansion of knowledge base** since we just trade off general knowledge with specialized one due to modification in weights.<br/><br/>
- ***Agent***: This is a system where the LLM functions as a brain, and it could interact with the world by automatically using an external tool.

#### Metaphor between Fine Tuneing-RAG-Prompt
&emsp;Consider that specialization is in the medical field. Fine-tuning is just like a student spending tons of hours to practice (change weight) and learn new skills from the standard textbook. RAG is kinda like a library that gives information to a student to do something. The prompt engineering is basically the protocol or standard instructions of how to do something. Theoretically, we only need RAG and Prompt Engineering to make LLM do something. However, imagine we let a medical student(Fine tune) and a physics student prescribe to a patient. Obviously,  the medical students do it in an efficient way, whereas physics students have trouble following instructions despite all the information (RAG) and instructions (Prompt) provided.

#### Metaphor between LLM and Agent
&emsp;While a medical student (LLM) is limited by the instruction and they are only allowed to give advice (text). The licensed doctor (agent) could access the external tools other than information(RAG), like scalpels, forceps, and surgical scissors to actually perform surgery on the patient. 



# Why choose Fine Tune 
When it comes to our project, one could argue that why you don't choose the system prompt rather than this headache fine-tuning. It is actually a valid question since the system prompt is a lot easier. However, I chose fine-tuning due to the following reasons
- My model is **TinyLlama** which small language model. It doesn't work well with the system prompt. 
- My chatbot is a **real-time conversational chatbot**, so it requires the lowest latency. The system prompt would make it longer to digest those prompts. 
- Save the **context window size** for future short-term memory.
- To match with **very specific style**. The system prompt of Llama 3.2 works really well with a somewhat general style of Gen Z. But what if I want it to match a very specific style? If I want to do it, I would have to provide many specific examples. That would explode my context window size

Okay, to sum up, TinyLlama doesn't **work well** with System Prompt, and even if it works, it could **digest** more **time** and **context size**. That is why I chose fine-tuning for this project. I would suggest combining both techniques to get the best of both worlds


# Full Fine Tune, LoRA, QLoRa
To understand how LoRA works, there are two main requirements: backpropagation and intrinsic dimension. I have provided a really brief example of backpropagation of a neural network at [Neural_Network.md](Neural_Network.md). Basically, backpropagation tell us whether we should increase or decrease a specific weight in order to get the minimum Loss.</br>

#### Intrinsic Dimension
Overall, intrinsic dimensions represent the number of dimensions needed in subspace to reach 90% performance of full dimensions. In the [paper](https://arxiv.org/abs/1804.08838) they found out that they only need to train around 700 dimensions of a network 200k parameters and they could still produce result equal 90% accuracy of full training with 200k dimensions. Basically, they prove that dimension needed for trainign is not always equal to number of parameters and many time it is surprising low.

another [paper](https://arxiv.org/abs/2012.13255) empirically found out that the larger the parameters of the pre-trained model, the smaller the number of dimensions needed to solve the problem compared to their huge parameters(not other). They observed they only need to fine tune 200 dimensions for the ROBERTa-Large whereas ROBERTa-base(smaller) need around 900. Their rationale is that larger model minimize the knowledge needed to learn since they already have it. The metaphor could be that of a smart student who only needs a few hours of learning instead of days since he already know most of the concepts.  This show one point that **really large pre-trained LLM actually need really small trainable dimensions in a random subspace just to reach a satisfactory solution** <br/>


#### LoRA - Low-rank Adaption
the Low-rank here refers to the fact the it will happen at smaller rank or sub space. What make LoRA differ is that instead of having fixed P, they have two trainable matrices.

***[Hypothesis](https://arxiv.org/abs/2106.09685)***: The authors were inpsired that there were intrisic dimensions for. Thus, they expand this further by hypotehsizing that the update weight $\Delta W$ also has its intrinsic dimension not just origional weight $W$. Their technique is to decompose the update weight matrix into two matrices B and A. This means that 
$$\Delta W_{m,n} = B_{n, r}.A_{r, m}$$
where r< m,n. Usually m = n
So it general we have
$$W = W_0 + \Delta W = W_0 + B.A$$
As explained in [here](https://mbrenndoerfer.com/writing/lora-hyperparameters-rank-alpha-target-modules?utm_source=chatgpt.com) say that 
- **A** down projection matrix which compress input into a subspace
- **B** up-projection matrix which maps from subspace back to the origional dimension

You can see it here, instead of projecting the input to the full space $\Delta W$, the input is [down projected](https://mbrenndoerfer.com/writing/lora-concept-low-rank-adaptation-efficient-llm-fine-tuning) from k dimension into r dimension. Then it is converted to the d dimension. While being comprressed into r, it lose some information. But do remember that this is the intention. Remeber the idea of backpropagation is always trying to find the optimal solution. And the above paper also explain that already known knowedge would be filtered out. This mean that  when update the matrix A and B, we basically tell that "I dont care how many parameters orginal matrix W have, you matrix (**A**) need to figure out a way so that you extract most useful and new information from the input for the task by squeezing it and you (**B**) figure out a most efficient way to decompress and combine those information back to output space". 

We can see that the $W$ is still used in the calculation but it is freezed which means its value doesn't change after any update. All the update go back to the ***B*** and ***A***. This means that there should be something like  this 

$$A = A_0 - \eta \frac{\partial L}{\partial A}$$

$$B = B_0 - \eta \frac{\partial L}{\partial B}$$

$$y = W_0x + \frac{\alpha}{r}BAx$$

Note here that the 
- **Learning rate $\eta$** is for the speed of learning process of $B$ and $A$. 
- **The alpha $\alpha$** is the scaling factor determine how strong of the BA update relative to the orgional model 
- $r$ this is the number of rank




For the regular adapter. It will be added into the main stream. For example if you have a module, flow will go from that module and then to the adapter. This adapter is what actually learn but it is also what increase the latency during inference time (more to flow). As we increase the complexity of adapter , it coverage to an MLP (which is worse than full fine tuning). 

<img width="816" height="198" alt="image-1" src="https://github.com/user-attachments/assets/124bc1ed-87d2-4054-a507-b1bc8ccbbe13" />


For the LoRA, it add two matrices A and B parrallel for each target module. The forward pass will pass through it and AB same time to calculate the value. But when backpropagation, it flow through the chain of A and B. Result in only updating those matrices. As we increase complexity of A and B, size of A and B actually get closer to the size of origional matrix which mean that this is basically normal fine tuning

<img width="375" height="335" alt="lora" src="https://github.com/user-attachments/assets/c1b1950a-bd4a-4e41-9bc8-95f4b6da95fd" />

Why it is efficient?
There are 3 main benefits:
- It can reduce the VRAM up to 2/3 since it doesn't have to store optimizer states for frozen parameter
- Speed up fine tuning by 25% since it doesn't have to calculate gradient for major of parameters
- We can switch tasks. Each task is a fine tuned model by just swapping the LoRA weights
- It will merged to the origional weight so it doesn't introduce more latency at inference time like 

**Small Example**: Assume an layer of LLM model has weight matrix of 4096x4096.
- For **full fine tuning**: We literally have to train  $$4096*4096 = 16,777,216$$
- **Apply LoRA** to this with the rank $r=64$. We will have matrix B of size  4096x64 and matrix A with the size 64x4096. So parameter we need to train is 
$$4096*64+64 *4096 = 2 * 4096 * 64 = 524,288$$
- The ratio 
$$\frac{524,288}{16,777,216} = 3.125\%$$

Yes just 3.125% of origional weight. We could decrease the rank as the model grow larger since more capacity model is pre trained enough for general task. They only need small adjustment to fit for specialized tasks. So the trick is small rank for large model and high rank for small model for specialized but not complex. However, for extremely complex task like new language, that strategy might be broken.

# Google Colab vs HuggingFace vs  Unsloth vs LoRA 
I guess if you are beginner, you might be overwhelm with those terminologies.
- ***Google Colab***: this is the platform provided Google where you actually train your model. You borrow their virtual T4 GPU machine to train
- ***Hugging Face***: This is platform where you download their models, libraries or even datasets. Think it as Github version of AI
- ***Unsloth***: In short, [Unsloth](https://unsloth.ai/docs) is an open-source frame work for running and training LLMS.They are famous for making training process more efficient by decrese the time and storage. They also provide 
  some efficients models on the Hugging Face
- ***LoRA***: As explained above, LoRA is the trainning strategy that could reduce time and space needed.<br/>
  
**So how does everything come together?**
We **borrow** the T4 computer with enough VRAM from the **Google Colab**. The Unsloth will control that computer to **download model** from the **Hugging Face**. Then Unsloth **train** that model using the **LoRA strategy** .

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
- **batch**: Number of samples needed to be processed before an update weight
- **epoch**: Number of times that it go through entire dataset<br/>

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
PARAMETER num_ctx 2048
```
This [video](https://www.youtube.com/watch?v=jnikMver_CE) explai some concept about sampling strategies. Overall, those are four popular sampling strategies
- **temperature**: So basiclly we scale the raw logits before applying the [softmax](https://letsdatascience.com/blog/llm-sampling-temperature-top-k-top-p-and-min-p-explained) to convert it to probabilties. Assume we have logit [1 2]. If we scale by 0.1 it will be come [10 20]. If we set termpareture by 0.3 and 0.6 it will be [3.3 6.7] and [1.7 3.3]. As we increase the temperature, the two logits get closer to each other. This mean that lower logit has higher chance to be sampling together with the hight logit. If we set it as 0 this basically greedy algorithm where it just take the highest one. If we set it extremely large then everything will be the same. Thus, if we want more **stable** choose **low temperature**. If we want more creative, choose **high temeperature**
- **top_k**: Basically we choose k tokens that has highest probabilities. Recalculate the probabilties so total could be 1 again and then randomly sampling from them<br/>
  <img width="241" height="230" alt="image" src="https://github.com/user-attachments/assets/b6657d5e-9ecc-4276-8b5f-3f7dd2e50b9d" />

- **top_p**: P here mean acummulative probability. We basically start from the highest and add the probability together with the top_p as upperbound. Then take those tokens and re calculate the probability to make it sum up to 1<br/>
  <img width="250" height="250" alt="image" src="https://github.com/user-attachments/assets/a22d2f1e-8e24-43f4-89b8-3eedbb112188" /> <br/>
Well the order in which one is executed first is not quite clear. I'll leave this to you to figure out
- **min_p**: The idea is to filter out any tokens that can not pass a portion of the highest probability
  <img width="726" height="461" alt="image" src="https://github.com/user-attachments/assets/9bfcfb73-55b9-4204-8379-8c675efea05f" /><br/><br/>
  
Parameters for limitation tokens:
- ***num_ctx***: this basically the size of context window (both input and output).
- ***num_predict***: this basically the maximum tokens to predict. Equivalent to ***max_new_tokens** <br/><br/>

Parameters for repeatation penaty:
- **repeat_last_n**: Basically how far (tokens) the model look back to determine which one is repeated word. If a word is still within n tokens, it is considered repetitve
- **repeat_penalty**: This is basically a strategy how to deal with those repetitive words. similiar to temeprature, it will scale down the logit if a word is repeatitive. Thus a repat_penalty of 1 means disable.<br/>
  If you set penalty less than 1, it will actually encourage a word to appear. Below I set the penalty to 0.7
  <img width="1252" height="581" alt="image" src="https://github.com/user-attachments/assets/f0eebb30-6221-4fbf-bace-fa70084ef6cf" />



