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
Voice Activity Detection, or VAD, is a mechanism to detect when there is a voice. Generally, it receives the streaming audio from the mic and analyzes the radio frequency of that. There might be many ways to implement a VAD, such as using deep learning to determine speech. For this project, I only implemented a basic energy analyzer where the energy of a frame determines if there is speech or just silence.
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
This is the our brain of our AI pipeline where it actually generate the text. I believe it is worth to have some big picture about the how the large language model works in general before delve into specialized model like TinyLlama

## 4.1 Tranformer
Transformer is a specific type of [neural network](https://www.youtube.com/watch?v=wjZofJX0v4M&t=44s) in machine learning model. Other type could be our CNN which is extensively used in computer vision. Transformer has many applications such as generate syntehtic speech from the script or generate script from a speech. The orgional model was introduced by Google in 2017 in "Attention is all you need" to translate from one text to another.
### 4.1.1 Tokenization and Embedding
Basically the computer couldn't understand the input if we just feed it with our sentence.
- Firstly, it needed to be broken down into smaller unit so that  computer could examine the relationship between them to actually understand whole sentence. 
- Secondly, it needed to be in some kind of number format so computer can do operation on them.
#### 4.1.1.1 Tokenization 
To solve the first problem, we have to break down the input sentence into smaller units. This is what we called a token. At bareminimum, it would be just as simple breaking down into words by words. However, it could also be broken in a way that capture both commas, dots or other special characters. There are many ways and it really depends on the intetion of developer
<img width="1277" height="645" alt="Image" src="https://github.com/user-attachments/assets/376725c7-08ae-46ff-a032-cdc68e49aeb5" />
Above tokenization break down the the word itself even smaller sub-word whereas the below convenient one only break individual words into tokens

#### 4.1.1.2 Embedding
After having a smaller unit, we need to assign it  a numerical format to work with. The idea is that each word would be encoded into a vector called **embedding** where two words with the similiar meaning could be close to each other. An [example](https://www.youtube.com/watch?v=wjZofJX0v4M&t=44s) would be that the distance between a word ***man*** and ***woman*** would be roughly to the distance between ***king*** and ***queen***. This is because both of the context, their distance contains large portion for the gender. However, difference context result in not exactly the same difference in distance between main/woman and king/queen. There are two types of embedding:
- [static](https://medium.com/@hychandima2000/understanding-the-difference-between-contextual-embeddings-static-embeddings-98921309ac4c) or [semantic](https://www.youtube.com/watch?v=KMHkbXzHn7s&t=1161s) embedding: we encode each individual word seperately. This mean that their meang won't affect each other. Example the word ***like*** might have same vector as in ***I don't like you*** or ***I look like you***
- dynamic or [contextual] embedding: An embedding of a word is based on the context where it is in. Example the word ***like*** would have different embedding vectors in ***I don't like you*** and in ***I look like you***

Initially each token would be encoded into static/semantic encoding by using its own vocabulary bank. Additionally, each token could have different embedding based on their position in that sentence. Example the word ***like*** would have different embedding in ***I like you*** and ***I don't like you***
After having semantic embedding as our starting point, we would like to convert it into contextual embedding so that all the word are relavant to the context of they are in. The problem is that it is not easy as in static where we simply map the word from the vocabulary bank. We need a sophisticated strategy called ***Attention***

### 4.1.2 Attention
The general idea of ***Attention*** is that it enable AI model to focus on some different parts of the input to produce the output. As point out in this [blog](https://medium.com/the-research-nest/explained-attention-mechanism-in-ai-e9bb6f0b0b4d), Attention mimic the way human process a long text by only choosing what is the most important part. There are many techniques for implementing the attention but we will focus on the self-attention or dot-product attention. 
There are three transforms need to understand: Q, K, and V.
- Q - Querry: A vector that represent what a very specific token looking for in other words. For the word ***pencil*** in the sentence "She give me a red pencil", we basically ask "what are other words that related to this pencil".
- K - Key: This vector represent what it could provide. Using above example, we basically say that hey this token "pencil" could provide some meta data such as a general nouns or as a school object.
- V - Value: the actual information  of the token in the sentence that could provide to other tokens. 


Okay how do I obtain those vectors? We basically apply an different transform matrix for different vector. 
**You might ask why don't we just use it directly?**
The reason is because the embedding vectors we have is really general. If we want to assign it a meaning, we really need to transform it by using matrix.
- Querry [Matrix](https://transformers-goto-guide.hashnode.dev/understanding-the-role-of-query-key-and-value-in-transformer-models) $W_Q$: the matrix encode sets of questions (dimensions) needed to asked for each token. It has lesser dimensions means that it only ask fewer key questions isntead of all. Basically it say "Hey token, you shoud ***ask*** question about this and this".
$$Query = I x M_Q$$ 
- Key Matrix $W_K$: Similiar idea to above, it has fewer dimensions to represent the key meta data of a token. It is "Hey token, you should ***show*** them this and this"
$$Query = I x M_K$$ 
- Value Matrix $W_V$: while the key matrix just represent the metadata of its dimensions, the Value matrix represent the actual content or information that a token would contribute to the context of other tokens. It is basically " Hey token, if what they ask match with what you have, you should ***give*** them this and this"
$$Query = I x M_V$$ 

So those matrixes are not predetermined but through training. By training more example, it learn how to ask better question, how to show better metadata, and actual provide the most concrete information. The formula represent the relationship is 
$$Attention(Q,K,V)=softmax\left(\frac{K^TQ}{\sqrt{d_k}}\right)V$$
where $\sqrt{d_k}$ is square root of the key dimension for numerical stability. It is there to stabilize the softmax function since it is not stable when the values are too big (larger value) or too small (values appear to be roughly similiar). The softmax of ${K^TQ}$ could be understood as the weight (coefficient) for the actual information $V$
The idea of the formula is that each query is compared against many key by using the dot product like below
<img width="1016" height="688" alt="Image" src="https://github.com/user-attachments/assets/82c0a638-42d3-4ea3-b33c-1ab1abff7b9b" />
Then we scale them down for scability and apply the softmax to convert it into weights where the whole column add up to 1.
<img width="976" height="703" alt="Image" src="https://github.com/user-attachments/assets/8391223a-1f88-4539-88d2-4089688e54c8" />
Then we multiply whole thing by the vector V. This basically for each query, add up all the weighted information. 
<img width="1185" height="713" alt="Image" src="https://github.com/user-attachments/assets/b3fabeb1-db5d-4bb3-b96f-0b1a8803beb0" />
Now the new token would have the information of other tokens to for the context. Example the vector for **pencil** now is not the same as original but contains information about the **red** or **a**. 

***Masking***: During the training, instead of trying to predict one new word. The model try to predict for every position simultaneously
<img width="1197" height="693" alt="Image" src="https://github.com/user-attachments/assets/4128031d-0a82-452e-a485-3f21c6174150" />
However, the future has not yet come when it is trying to predict so we would have to let other tokens to the right of a specific tokens to be zero. It is shown below
<img width="1246" height="721" alt="Image" src="https://github.com/user-attachments/assets/0704cf1f-8a48-4c49-8c20-5c42a0d62481" />

***Multi-head***: Notice that the QKV matrices are the same for all the embedding. This mean that it only tell those tokens to ask,show, and provide particular aspect of the input. This is probably insuffcient to form the complicated context. For the analogy above, we only that the *pencil* now is red and only one but how about other information such as who owns it and who will have it? Thus, we would like to have many differebt pair QKV, where each provide an perspective of the input. Since they are seperate to each other, we could actually run them parrallel. This architecutre is called multi-head transofrmer. Each QKV is called a head. The results of all head are concantenating and projected back to the model dimension

### 4.1.3 MLP
Okay we have established the context during the multi head attention. You can see that the information flow from left to right which means the last token contains all the information for the context. However, that is it. Attention just connect them together but our goal is to predict something new. 
So key question is where that news come from?
Intuitively, if we want something new out from the current context, we need knowledge or information out of it. the attention doesn't give us new knowledge. The researchers found out that the transformer store most of facts and knowledges in the Multilayer Perceptron or MLP. This is the deep neural network. Compared to Attention, the process of MLP is easier since it is applied to individual token. 
<img width="2924" height="1032" alt="Image" src="https://github.com/user-attachments/assets/ff1cc166-19ac-4505-b9c5-67a2675bda52" />
FOr each token it go through a neural where it is expanded into higher dimensions. Then go thourgh normalization. lastly, it go thourgh an layer to go back to model dimensions. This output of the last layer is then added to the input of MLP to create final output of MLP. How does it work exactly is still questionable but we might think that by expanding the dimension more, we could larger pool of "vocabulary" to associate more word to our token.

The output of last layer could be thought of the new information vector that is related to the input token. Let's say the input tokens are "Elon Musk" where the token ***Musk*** got the information about Elon in previous attention. than the output of last layer for the token ***Musk*** could be a vector related to electric car or a rocket. Then the final output could be something like ***electric Elon Musk*** or ***rocket Elon Musk***

***Superposition***: The basic idea is that we don't need an independent to represent a feature. Let say we only 3 have dimensions, usual thought might be that it only store 3 features. However, we could treat thsoe vector where it fluctuate around 89-91 degree as basis. This mean three independent dimension could represent more features than that. This allow for to store very many facts not just limited by the number of its parameters.


### 4.1.4 Final Result
Each transformer block contains Attention and MLP and we don't just have single transformer block but many transformer block. This mean that our input would go through those transformers. In each transfomer, Attention establish context for the sentence and MLP assign new information that is closely related to each token. Then next block the attention would again establish those context for those new information and then assigned again. This is repeated many time until the context is rich in its meaning. At this point the last token in the sentence has all the information passed by other tokens and from the MLP. it then will be used to predict the next. This vector then is map to an unembedding matrix to return a list logit represent for those words. Depend on the strategy we might apply some technique such as temperature(which is explained in [Fine_Tune_Model.md](./Fine_Tune_Model.md)). We then use to softmax to conver to probability distribution.
<img width="911" height="605" alt="Image" src="https://github.com/user-attachments/assets/b02f9312-a436-49e0-bd1e-31c6fe2b8919" />

## 4.2 Small vs Large Language Model
aat this point we understand somewhat how those language model work based on the transformer. Remember that the explanation above is only for specific model. Newer models now would have different parts but the same concept should be hold. In this project, we would like to use small lnaguage model so it is beneficial to understand the difference between them
Overall, the SLM has similiar functions as LLM but differ in their performance and cost
| | Large Language Model [LLM](https://www.microsoft.com/en-us/microsoft-cloud/blog/2024/11/11/explore-ai-models-key-differences-between-small-language-models-and-large-language-models/?msockid=24dd2192c6a86bee3b6b3442c7026a0f) | Small Lanuage Model SLM |
| :--- | :---: | ---: |
| Parameters | Billions to Trillions | Millions |
| Training Data  | Large and general dataset | Smaller and specific data|
| Performance | Good to Execlent  | Well Enough |
| Inference Speed | Slow  | Fast |
| Use Case | Reasoning, General NLP  | Edge computing, real-time applications |
| Examples | Gemini 1.5 Pro, GPT-4o, Claude 3.5 Sonnet  | Tiny LLama, Llama 3.2, Phi-3  |
## 4.3 TinyLlama 
TinyLlama is suprisingly small compared to other SML withouting resize its model. Like the name suggest, it has similiar architecture and tokenzie as llama, speciallly [llama 2](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0). This mean that it can be used as alternative whatever project buit based on Llama. For future reference, it was train on 3 trillions tokens which is rougly 950 GB by using 16 A100-40G GPUs. It took a round 90 days to do it. 
***So what is difference between TinyLlama and Llama 3.2 1B?***
First of all they both related to Llama. 
| | TinyLlama | Llama 3.2 - 1B|
| :--- | :---: | ---: |
| Developer | Open Source Community | Meta AI |
| Architecture | Built based on Llama | made by prunning (trim) and knowledge distillation of the larger model |
| Purpose | Education and research | production-level |

So overal, the Llama3.2 1B has higher capacities compared to TinyLlama. As I have experiment, llama3.2-1b works quite well wit hthe system prompt but the TinyLlama doesn't. Thus it make it good chance to learn how to fine tuning without system prompt. Thus, I use TinyLlama for this

# 5 Kokoro TTS
First of all, Text-To-Speech TTS or [synthesis](https://www.it-jim.com/blog/how-text-to-speech-models-work-theory-and-practice/) model is an model that take text input and produce audio signal from it.  Kokoro [TTS](https://huggingface.co/hexgrad/Kokoro-82M) is an light weight open-weight TTS model with just 82 million parameters. Its architecture is based on the StyleTTS2 and ISTFTNet. Acording to their statement, it is more efficient compared to larger model and can be used in either product and personal product enviroment. One disavatange thing is that the Kokoro TTS doesn't have one shot voice cloning which mean we couldn't customize our own voice. This is because their model was trained on the private audio data. However, it is all about the tensor so I doubt that we could figure out the way to blend those tensor voice weight using weighted sum to make up new one.

# 6 Tkinter
I have to be honest that I chose this one purely aribtraty. It is kind of light and fast compared to a web server. However, the learning curve to learn how its layout work is really tough. So overall, for me, Tkinkter is good for quick testing but I doubt its usefulness at production level. 