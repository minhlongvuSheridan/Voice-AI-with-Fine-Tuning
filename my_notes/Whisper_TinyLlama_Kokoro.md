<h1 align="center">🗣️ Whisper + TinyLlama + Kokoro 🗣️</h1>

# 0 Table of Contents

- [1 General Architecture](#1-general-architecture)
    - [1.1 Workflow](#11-workflow)
    - [1.2 Why thread?](#12-why-thread)
- [2 VAD](#2-vad)
    - [2.4 Detailed Implementation](#24-detailed-implementation)
- [3 Whisper](#3-whisper)
    - [3.1 Why Whisper](#31-why-whisper)
    - [3.2 Whisper Sizes](#32-whisper-sizes)
- [4 TinyLlama](#4-tinyllama)
    - [4.1 Transformer](#41-transformer)
        - [4.1.1 Tokenization and Embedding](#411-tokenization-and-embedding)
            - [4.1.1.1 Tokenization](#4111-tokenization)
            - [4.1.1.2 Embedding](#4112-embedding)
        - [4.1.2 Attention](#412-attention)
        - [4.1.3 MLP](#413-mlp)
        - [4.1.4 Final Result](#414-final-result)
    - [4.2 Small vs Large Language Model](#42-small-vs-large-language-model)
    - [4.3 TinyLlama](#43-tinyllama)
- [5 Kokoro TTS](#5-kokoro-tts)
- [6 Tkinter](#6-tkinter)

# 1 General Architecture
### 1.1 Workflow

<img width="810" height="727" alt="Image" src="https://github.com/user-attachments/assets/79e23c47-88c2-4179-b576-f6f3d18b45bb" />

The image above shows the general architecture. Generally, each color is assigned a separate thread. Only Tkinter resides in the main thread of the program. I did make a separate thread for it, but it simply raised an exception demanding to be in the main thread. This is actually quite insufficient since it just burns all the CPU resources. I will try to fix it in the near future, but for now just let it be.
Generally, the flow of the program would be:

- ***Input Sounddevice***: Sounddevice captures streaming audio from the Mic and sends it to VAD</br></br>
- ***VAD speech detection***: VAD will determine if there is speech or silence based on the threshold energy. Then it sends potential speech to ***Recording Queue***. Potential speech because it is quite susceptible to noise due to the energy threshold.</br></br>
- ***Whisper speech transribe***: Whisper model gets the data from the Recording Queue and starts to transcribe the audio to text. Then it send to the *Prompt Queue*</br></br>
- ***TinyLlama Prompt***: TinyLlama gets sentences from the Prompt Queue, formats them into a suitable prompt, and sends it to the language model. Then the program checks for the complete sentence in the returned stream of text. It then send complete sentence to both the *Sentence Queue* and *GUI queue*.</br></br>
- ***Kokoro TTS***: Kokoro gets a sentence from the sentence queue and converts it into an audio array. It then send to ***Audio Queue***</br></br>
- ***Output Sounddevice***: Soundevice get the audio from *Audio Queue* and play it the speaker</br></br>
- ***Tkinter GUI***: the Tkinkter get data from *GUI queue* and display it on the GUI
### 1.2 Why thread?

Based on those steps, it sounds like those are sequential. However, they are actually running on separate threads. If you look at it carefully, I don't send the output of a component to the other directly but via a queue. This queue is actually what enables the asynchronous programming. Using a queue, we simply say that "Hey, when you finish your stuff, you don't need to wait to hand it over to the dude after you. Just put all your stuff here and he will handle it later". That is the general idea of asynchronous programming, where queues are the box and threads are the workers. You might ask a valid question like Why don't you use multiprocessing instead. That might work, and actually what I will do when I scale up this project. However, I just want to have the fastest speed since multiprocessing introduces some latency due to IPC. 
# 2 VAD 
Voice Activity Detection, or VAD, is a mechanism to detect when there is a voice. Generally, it receives the streaming audio from the mic and analyzes the radio frequency of that. There might be many ways to implement a VAD, such as using deep learning to determine speech. For this project, I only implemented a basic energy analyzer where the energy of a frame determines if there is speech or just silence.
### 2.4 Detailed Implementation
So the big picture of our VAD is to determine when an energy passes or does not pass a threshold. If it passes the energy threshold for a specified amount of time $c_1$, then it decides that there is speech. To determine when the user stops speaking, we track if the speech is smaller than the threshold for another specified amount of time $c_2$. Intuitively, we want to detect if there is speech immediately, but wait for a bit for the user to take a short break. Thus, $c_2$ is usally larger than $c_1$ 


# 3 Whisper
### 3.1 Why Whisper
[Whisper](https://www.geeksforgeeks.org/nlp/automatic-speech-recognition-using-whisper/) is a speech recognition model developed by OpenAI. Its job is to transcribe an audio array into words. You might ask a question: Why don't you just put whatever you have into Whisper instead of going through a VAD? There are two reasons for this:
- **First**: The problem with Whisper is that it is also a deep learning model that takes some time to transcribe text. If we rely on a slow transcriber compared with streaming audio, we could end up being far behind.
- **Second**: The model is prone to hallucination. Even if you don't speak anything, it would output some sentences like "Thank You" repeatedly. Since my VAD implementation is not perfect, you might see this hallucination if there is a disruptive noise.
### 3.2 Whisper Sizes
Whisper comes with multiple sizes: tiny, large, and medium.

<img width="836" height="666" alt="Image" src="https://github.com/user-attachments/assets/be41c5ec-ae37-4651-ae0e-40070e6a59e2" />

The larger the [model](https://openwhispr.com/blog/whisper-model-sizes-explained), the more accurate it will be. If you have a clear and strong voice, I would suggest the tiny model since it is relatively fast and small. If you have a slight accent like me, I would suggest the medium.en since it could handle a strange accent quite well. However, the ***tiny*** only takes around 250 MB, but ***medium*** takes up to 3,8 GB.

# 4 TinyLlama
This is the brain of our AI pipeline where it actually generates the text. I believe it is worth having some big picture about how the large language model works in general before delving into specialized models like TinyLlama.

## 4.1 Transformer
Transformer is a specific type of [neural network](https://www.youtube.com/watch?v=wjZofJX0v4M&t=44s) in a machine learning model. Another type could be our CNN, which is extensively used in computer vision. Transformer has many applications, such as generating synthetic speech from the script or generating a script from a speech. The original model was introduced by Google in 2017 in "Attention is all you need" to translate from one text to another.
### 4.1.1 Tokenization and Embedding
Basically, the computer couldn't understand the input if we just fed it with our sentence.
- Firstly, it needed to be broken down into smaller units so that the computer could examine the relationship between them to actually understand the whole sentence. 
- Secondly, it needed to be in some kind of number format so the computer could do operations on them.
#### 4.1.1.1 Tokenization 
To solve the first problem, we have to break down the input sentence into smaller units. This is what we call a token. At bare minimum, it would be just as simple as breaking down into words. However, it could also be broken down in a way that captures both commas, dots, or other special characters. There are many ways, and it really depends on the intention of the developer.

<img width="1277" height="645" alt="Image" src="https://github.com/user-attachments/assets/376725c7-08ae-46ff-a032-cdc68e49aeb5" />

Above tokenization breaks down the word itself into even smaller sub-words, whereas the below one only breaks individual words into tokens.

#### 4.1.1.2 Embedding
After having a smaller unit, we need to assign it a numerical format to work with. The idea is that each word would be encoded into a vector called **embedding** where two words with similar meaning could be close to each other. An [example](https://www.youtube.com/watch?v=wjZofJX0v4M&t=44s) would be that the distance between a word ***man*** and ***woman*** would be roughly the same as the distance between ***king*** and ***queen***. This is because in both contexts, their distance contains a large portion of the gender. However, different contexts result in not exactly the same difference in distance between main/woman and king/queen. There are two types of embedding:
- [static](https://medium.com/@hychandima2000/understanding-the-difference-between-contextual-embeddings-static-embeddings-98921309ac4c) or [semantic](https://www.youtube.com/watch?v=KMHkbXzHn7s&t=1161s) embedding: we encode each individual word seperately. This means that their meaning won't affect each other. For example, the word ***like*** might have the same vector as in ***I don't like you*** or ***I look like you***
- dynamic or [contextual] embedding: An embedding of a word is based on the context where it is in. For example, the word ***like*** would have different embedding vectors in ***I don't like you*** and in ***I look like you***

Initially, each token would be encoded into static/semantic encoding by using its own vocabulary bank. Additionally, each token could have different embeddings based on its position in that sentence. For example, the word ***like*** would have a different embedding in ***I like you*** and ***I don't like you***
After having semantic embedding as our starting point, we would like to convert it into contextual embedding so that all the words are relevant to the context they are in. The problem is that it is not as easy as in static embedding, where we simply map the word from the vocabulary bank. We need a sophisticated strategy called ***Attention***

### 4.1.2 Attention
The general idea of ***Attention*** is that it enables an AI model to focus on different parts of the input to produce the output. As pointed out in this [blog](https://medium.com/the-research-nest/explained-attention-mechanism-in-ai-e9bb6f0b0b4d), attention mimics the way humans process a long text by only choosing what the most important part is. There are many techniques for implementing attention, but we will focus on self-attention or dot-product attention. 
There are three transforms that need to be understood: Q, K, and V.
- Q - Query: A vector that represents what a very specific token is looking for, in other words. For the word ***pencil*** in the sentence "She gave me a red pencil", we basically ask, "what are other words that are related to this pencil?".
- K - Key: This vector represents what it could provide. Using the above example, we basically say that hey, this token "pencil" could provide some metadata such as a general noun or as a school object.
- V - Value: the actual information of the token in the sentence that could provide to other tokens. 


Okay, how do I obtain those vectors? We basically apply a different transform matrix for different vectors. 
**You might ask why don't we just use it directly?**
The reason is that the embedding vectors we have are really general. If we want to assign it a meaning, we really need to transform it by using a matrix.
- Query [Matrix](https://transformers-goto-guide.hashnode.dev/understanding-the-role-of-query-key-and-value-in-transformer-models) $W_Q$: the matrix encodes sets of questions (dimensions) needed to be asked for each token. It has fewer dimensions, which means that it only asks fewer key questions instead of all. Basically it says "Hey token, you should ***ask*** question about this and this".

$$Query = I x M_Q$$ 

- Key Matrix $W_K$: Similar idea to above, it has fewer dimensions to represent the key metadata of a token. It is "Hey token, you should ***show*** them this and this"
- 
$$Query = I x M_K$$
 
- Value Matrix $W_V$: while the key matrix just represents the metadata of its dimensions, the Value matrix represents the actual content or information that a token would contribute to the context of other tokens. It is basically " Hey token, if what they ask matches what you have, you should ***give*** them this and this"
$$Query = I x M_V$$ 

So those matrices are not predetermined but are learned through training. By training with more examples, it learns how to ask better questions, how to show better metadata, and actually provide the most concrete information. The formula represents the relationship is 

$$Attention(Q,K,V)=softmax\left(\frac{K^TQ}{\sqrt{d_k}}\right)V$$

where $\sqrt{d_k}$ is the square root of the key dimension for numerical stability. It is there to stabilize the softmax function since it is not stable when the values are too big (larger values) or too small (values appear to be roughly similar). The softmax of ${K^TQ}$ could be understood as the weight (coefficient) for the actual information $V$.
The idea of the formula is that each query is compared against many keys by using the dot product like below.

<img width="1016" height="688" alt="Image" src="https://github.com/user-attachments/assets/82c0a638-42d3-4ea3-b33c-1ab1abff7b9b" />

Then we scale them down for scalability and apply softmax to convert them into weights where the whole column adds up to 1.

<img width="976" height="703" alt="Image" src="https://github.com/user-attachments/assets/8391223a-1f88-4539-88d2-4089688e54c8" />

Then we multiply the whole thing by the vector V. This basically adds up all the weighted information. 

<img width="1185" height="713" alt="Image" src="https://github.com/user-attachments/assets/b3fabeb1-db5d-4bb3-b96f-0b1a8803beb0" />
Now the new token would have the information of other tokens for the context. For example, the vector for **pencil** is now not the same as the original but contains information about the **red** or **a**. 

***Masking***: During the training, instead of trying to predict one new word. The model tries to predict for every position simultaneously.

<img width="1197" height="693" alt="Image" src="https://github.com/user-attachments/assets/4128031d-0a82-452e-a485-3f21c6174150" />

However, the future has not yet come when it is trying to predict, so we would have to let other tokens to the right of a specific token be zero. It is shown below.

<img width="1246" height="721" alt="Image" src="https://github.com/user-attachments/assets/0704cf1f-8a48-4c49-8c20-5c42a0d62481" />

***Multi-head***: Notice that the QKV matrices are the same for all the embeddings. This means that it only tells those tokens to ask, show, and provide a particular aspect of the input. This is probably insufficient to form the complicated context. For the analogy above, we only know that the *pencil* is now red and only one, but how about other information such as who owns it and who will have it? Thus, we would like to have many different pairs of QKV, where each provides a perspective of the input. Since they are separate from each other, we could actually run them in parallel. This architecture is called a multi-head transformer. Each QKV is called a head. The results of all heads are concatenated and projected back to the model dimension.

### 4.1.3 MLP
Okay, we have established the context during the multi-head attention. You can see that the information flows from left to right, which means the last token contains all the information for the context. However, that is it. Attention just connects them together, but our goal is to predict something new. 
So the key question is where that news comes from?
Intuitively, if we want something new out of the current context, we need knowledge or information out of it. The attention doesn't give us new knowledge. The researchers found out that the transformer stores most of the facts and knowledge in the Multilayer Perceptron, or MLP. This is a deep neural network. Compared to Attention, the process of MLP is easier since it is applied to individual tokens. 

<img width="2924" height="1032" alt="Image" src="https://github.com/user-attachments/assets/ff1cc166-19ac-4505-b9c5-67a2675bda52" />

For each token, it goes through a neural network where it is expanded into higher dimensions. Then it goes through normalization. Lastly, it goes through a layer to go back to model dimensions. This output of the last layer is then added to the input of the MLP to create the final output of the MLP. How it works exactly is still questionable, but we might think that by expanding the dimension more, we could have a larger pool of "vocabulary" to associate more words with our token.

The output of the last layer could be thought of as the new information vector that is related to the input token. Let's say the input tokens are "Elon Musk" where the token ***Musk*** got the information about Elon in previous attention. Then the output of the last layer for the token ***Musk*** could be a vector related to an electric car or a rocket. Then the final output could be something like ***electric Elon Musk*** or ***rocket Elon Musk***

***Superposition***: The basic idea is that we don't need an independent to represent a feature. Let's say we only have 3 dimensions; the usual thought might be that it only stores 3 features. However, we could treat those vectors where it fluctuates around 89-91 degrees as a basis. This means three independent dimensions could represent more features than that. This allows us to store very many facts, not just limited by the number of its parameters.


### 4.1.4 Final Result
Each transformer block contains Attention and MLP, and we don't just have a single transformer block but many transformer blocks. This means that our input would go through those transformers. In each transformer, Attention establishes context for the sentence, and MLP assigns new information that is closely related to each token. Then, in the next block, the attention would again establish that context for that new information and then be assigned again. This is repeated many times until the context is rich in its meaning. At this point, the last token in the sentence has all the information passed by other tokens and from the MLP. It will then be used to predict the next. This vector is then mapped to an unembedding matrix to return a list of logits representing those words. Depending on the strategy, we might apply some technique such as temperature(which is explained in [Fine_Tune_Model.md](./Fine_Tune_Model.md)). We then use softmax to convert to a probability distribution.

<img width="911" height="605" alt="Image" src="https://github.com/user-attachments/assets/b02f9312-a436-49e0-bd1e-31c6fe2b8919" />

## 4.2 Small vs Large Language Model
At this point, we understand somewhat how those language models work based on the transformer. Remember that the explanation above is only for a specific model. Newer models now would have different parts, but the same concept should hold. In this project, we would like to use a small language model, so it is beneficial to understand the difference between them
Overall, the SLM has similar functions as LLM but differs in their performance and cost
| | Large Language Model [LLM](https://www.microsoft.com/en-us/microsoft-cloud/blog/2024/11/11/explore-ai-models-key-differences-between-small-language-models-and-large-language-models/?msockid=24dd2192c6a86bee3b6b3442c7026a0f) | Small Lanuage Model SLM |
| :--- | :---: | ---: |
| Parameters | Billions to Trillions | Millions |
| Training Data  | Large and general dataset | Smaller and specific data|
| Performance | Good to Execlent  | Well Enough |
| Inference Speed | Slow  | Fast |
| Use Case | Reasoning, General NLP  | Edge computing, real-time applications |
| Examples | Gemini 1.5 Pro, GPT-4o, Claude 3.5 Sonnet  | Tiny LLama, Llama 3.2, Phi-3  |
## 4.3 TinyLlama 
TinyLlama is surprisingly small compared to other SML without resizing its model. As the name suggests, it has a similar architecture and tokenizer as Llama, especially [llama 2](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0). This means that it can be used as an alternative for whatever project built based on Llama. For future reference, it was trained on 3 trillion tokens, which is roughly 950 GB, using 16 A100-40G GPUs. It took around 90 days to do it. 
***So what is the difference between TinyLlama and Llama 3.2 1B?***
First of all, they are both related to Llama. 
| | TinyLlama | Llama 3.2 - 1B|
| :--- | :---: | ---: |
| Developer | Open Source Community | Meta AI |
| Architecture | Built based on Llama | made by pruning (trimming) and knowledge distillation of the larger model |
| Purpose | Education and research | production-level |

So overall, the Llama3.2 1B has higher capacities compared to TinyLlama. As I have experimented, Llama3.2-1 b works quite well with the system prompt, but TinyLlama doesn't. Thus, it makes it a good chance to learn how to fine-tune without a system prompt. Thus, I use TinyLlama for this.

# 5 Kokoro TTS
First of all, Text-To-Speech TTS or [synthesis](https://www.it-jim.com/blog/how-text-to-speech-models-work-theory-and-practice/) model is a model that takes text input and produces an audio signal from it.  Kokoro [TTS](https://huggingface.co/hexgrad/Kokoro-82M) is a lightweight open-weight TTS model with just 82 million parameters. Its architecture is based on StyleTTS2 and ISTFTNet. According to their statement, it is more efficient compared to larger models and can be used in either a product or personal environment. One disadvantage is that the Kokoro TTS doesn't have one-shot voice cloning, which means we couldn't customize our own voice. This is because their model was trained on private audio data. However, it is all about the tensor, so I doubt that we could figure out a way to blend those tensor voice weights using a weighted sum to make up a new one.

# 6 Tkinter
I have to be honest that I chose this one purely arbitrarily. It is kind of light and fast compared to a web server. However, the learning curve to learn how its layout works is really tough. So overall, for me, Tkinter is good for quick testing, but I doubt its usefulness at the production level. 
