<h1 align="center">🔬 Fine Tune TinyLlama Model 🔬</h1>

# 1. Difference between Prompt Engineering, Fine Tune, RAG, and Agent
&emsp;The title contains some hot keywords that one frequently hears every day. However, it is quite hard to imagine what the difference is between them. After researching for a while, this is what I could summarize.
### 1.1 Brief Definitions
- ***Prompt Engineering***: Create an effective prompt that could guide a model without expanding the existing knowledge or **twisting its parameters**. [Good prompt](https://www.ibm.com/think/topics/rag-vs-fine-tuning-vs-prompt-engineering) is to tell it what to do<br/><br/>
- ***RAG***: or called Retrieval Augmented Generation. It is the architecture that connects LLM to other data sources. Basically speaking, there is a search system between the user query and the LLM. This system will perform a search based on the queury to check if any new knolwedge is required. Then it integrates the user query and sends it to the LLM. This **expand the knowledge base**<br/><br/>

- ***Fine-Tune***: Fine-tuning is the process of retraining the model on a smaller dataset. Opposite to prompt engineering, this twists the parameters of the model. We can add new knowledge to it, but it is not really an **expansion of knowledge base** since we just trade off general knowledge with specialized one due to modification in weights.<br/><br/>
- ***Agent***: This is a system where the LLM functions as a brain, and it could interact with the world by automatically using an external tool.

### 1.2 Metaphor between Fine Tuneing-RAG-Prompt
&emsp;Consider that specialization is in the medical field. Fine-tuning is just like a student spending tons of hours to practice (change weight) and learn new skills from the standard textbook. RAG is kinda like a library that gives information to a student to do something. The prompt engineering is basically the protocol or standard instructions of how to do something. Theoretically, we only need RAG and Prompt Engineering to make LLM do something. However, imagine we let a medical student(Fine tune) and a physics student prescribe to a patient. Obviously,  the medical students do it in an efficient way, whereas physics students have trouble following instructions despite all the information (RAG) and instructions (Prompt) provided.

### 1.3 Metaphor between LLM and Agent
&emsp;While a medical student (LLM) is limited by the instruction and they are only allowed to give advice (text). The licensed doctor (agent) could access the external tools other than information(RAG), like scalpels, forceps, and surgical scissors to actually perform surgery on the patient. 



# 2 Why choose Fine Tune?
&emsp;When it comes to our project, one could argue that why you don't choose the system prompt rather than this headache fine-tuning. It is actually a valid question since the system prompt is a lot easier. However, I chose fine-tuning due to the following reasons
- My model is **TinyLlama** which small language model. It doesn't work well with the system prompt. 
- My chatbot is a **real-time conversational chatbot**, so it requires the lowest latency. The system prompt would make it longer to digest those prompts. 
- Save the **context window size** for future short-term memory.
- To match with **very specific style**. The system prompt of Llama 3.2 works really well with a somewhat general style of Gen Z. But what if I want it to match a very specific style? If I want to do it, I would have to provide many specific examples. That would explode my context window size

Okay, to sum up, TinyLlama doesn't **work well** with System Prompt, and even if it works, it could **digest** more **time** and **context size**. That is why I chose fine-tuning for this project. I would suggest combining both techniques to get the best of both worlds.


# 3 LoRA
&emsp;To understand how LoRA works, there are two main requirements: backpropagation and intrinsic dimension. I have provided a really brief example of backpropagation of a neural network at [Neural_Network.md](Neural_Network.md). Basically, backpropagation tells us whether we should increase or decrease a specific weight in order to get the minimum Loss.</br>

### 3.1 Intrinsic Dimension
&emsp;Overall, intrinsic dimensions represent the number of dimensions needed in a subspace to reach satisfactory performance relative to the full dimensions. In the [paper](https://arxiv.org/abs/1804.08838), they found that they only needed to train around 700 dimensions of a network with 200k parameters, and they could still produce results equal to 90% of the accuracy of full training with 200k dimensions. Basically, they proved that the dimensions needed for training are not always equal to the number of parameters, and many times the required number is surprisingly low.

&emsp;Another [paper](https://arxiv.org/abs/2012.13255) empirically found that the larger the number of parameters in a pre-trained model, the smaller the number of dimensions needed to solve a problem compared to its huge parameter count (not compared to other models). They observed that they only needed to fine-tune 200 dimensions for ROBERTa-Large, whereas ROBERTa-Base (smaller) needed around 900. Their rationale is that a larger model minimizes the knowledge needed to learn since it already has that knowledge. The metaphor could be that of a smart student who only needs a few hours of learning instead of days, since he already knows most of the concepts. This shows one point: really large pre-trained LLMs actually need very few trainable dimensions in a random subspace if the specialized task aligns with what the LLM was pre-trained on <br/>


### 3.2 LoRA - Low-rank Adaptation
&emsp;The "low-rank" here refers to the fact that it happens at a smaller rank or subspace. What makes LoRA different is that instead of having a fixed matrix, it uses two trainable matrices.

&emsp;***[Hypothesis](https://arxiv.org/abs/2106.09685)***: The authors were inspired by the idea of intrinsic dimensions. Thus, they expand on this further by hypothesizing that the weight update $\Delta W$ also has an intrinsic dimension, not just the original weight $W$. Their technique decomposes the weight update matrix into two smaller matrices, B and A. This means that 
$$\Delta W_{m,n} = B_{n, r} \cdot A_{r, m}$$
where $r \ll m, n$. Usually, $m = n$.
So in general, we have
$$W = W_0 + \Delta W = W_0 + B \cdot A$$
As explained [here](https://mbrenndoerfer.com/writing/lora-hyperparameters-rank-alpha-target-modules?utm_source=chatgpt.com):
- **A** is a down-projection matrix which compresses the input into a subspace.
- **B** is an up-projection matrix which maps from the subspace back to the original dimension.

&emsp;You can see it here: instead of projecting the input into the full space $\Delta W$ with rank $m$, the input is [down-projected](https://mbrenndoerfer.com/writing/lora-concept-low-rank-adaptation-efficient-llm-fine-tuning) from *n* dimensions into $r$ dimensions. Then, it is converted back to the *m* dimensions. While being compressed into $r$, it does lose some information. However, remember that this is intentional. The idea of backpropagation is always to find the optimal solution regardless of the situation, and the previously mentioned papers explain that already known knowledge will be filtered out. This means that when updating the matrices A and B, we are basically saying: "I don't care how many parameters the original matrix W has; you, matrix (**A**), need to figure out a way to extract the most useful and new information from the input for the task by squeezing it, and you, matrix (**B**), need to figure out the most efficient way to decompress and combine that information back into the output space."

&emsp;We can see that the $W$ is still used in the calculation, but it is frozen, which means its value doesn't change after any update. All the updates go back to the ***B*** and ***A***. This means that there should be something like this. 

$$A = A_0 - \eta \frac{\partial L}{\partial A}$$

$$B = B_0 - \eta \frac{\partial L}{\partial B}$$

$$y = W_0x + \frac{\alpha}{r}BAx$$

Note here that the 
- **Learning rate $\eta$** is for the speed of learning process of $B$ and $A$. 
- **The alpha $\alpha$** is the scaling factor that determines how strong the $BA$ update is relative to the original model 
- $r$ this is the number of rank

**Note**: the equations above use standard gradient descent. In practice, most LoRA training uses optimizers such as ***AdamW***, which is more complicated
$$A = A_0 - \eta \frac{m_t}{\sqrt{v_t}+\epsilon}$$
but they still base on the concept of calculating $\frac{\partial L}{\partial A}$ first
### 3.3 Adapter vs LoRA
&emsp;For regular adapters, these are added as a separate part of the mainstream architecture. For example, if you have a module, data will flow from that module and then into the adapter. This adapter is what actually learns, but it is also what increases latency during inference time (since there is more sequential flow). As we increase the complexity of the adapter, its coverage converges toward an MLP (which is still worse than full fine-tuning). 

<img width="816" height="198" alt="image-1" src="https://github.com/user-attachments/assets/124bc1ed-87d2-4054-a507-b1bc8ccbbe13" />


&emsp;For LoRA, it adds two matrices, A and B, in parallel to each target module. The forward pass goes through the original module and the AB path at the same time to calculate the final value. However, when backpropagation flows through the chain of A and B, it results in only updating those specific matrices. Finally, those update adapter will be used to update the origional matrix which doesn't introduce in any more latency in inference time. 

<img width="375" height="335" alt="lora" src="https://github.com/user-attachments/assets/c1b1950a-bd4a-4e41-9bc8-95f4b6da95fd" />

&emsp;Additionally, as we increase the complexity of A and B (by increasing the rank), the combined size of A and B actually gets closer to the size of the original matrix, which means that this essentially becomes normal fine-tuning.
### 3.4 Why LoRA is efficient?
There are ***4 main*** benefits:
- It can reduce VRAM usage by up to 2/3 since it doesn't have to store optimizer states for frozen parameters.
- It speeds up fine-tuning by around 25% since it doesn't have to calculate the gradients for most parameters.
- We can easily switch tasks. Each task is a fine-tuned model managed by just swapping out the lightweight LoRA weights.
- The weights can be merged back into the original weights, so it doesn't introduce any additional latency at inference time like regular adapters do.

**Small Example**: Assume a layer of an LLM model has a weight matrix of size $4096 \times 4096$.
- For **full fine-tuning**: We literally have to train 
$$4096 \times 4096 = 16,777,216\text{ parameters}$$
- **Applying LoRA** to this with a rank of $r=64$: We will have matrix B of size $4096 \times 64$ and matrix A of size $64 \times 4096$. Thus, the total number of parameters we need to train is 
$$(4096 \times 64) + (64 \times 4096) = 2 \times 4096 \times 64 = 524,288\text{ parameters}$$
- The ratio of trainable parameters is:
$$\frac{524,288}{16,777,216} = 3.125\%$$

&emsp;Yes, just 3.125% of the original weights. We can often decrease the rank as the model grows larger, since a higher-capacity model is already well pre-trained for general tasks. It only needs a small adjustment to fit a specialized task. So the general rule of thumb is a small rank for a large model, and a higher rank for a small model when dealing with specialized but not overly complex tasks. However, for an extremely complex task like learning an entirely new language, that strategy might break down.

# 4 LoRA vs QLoRA
LoRA reduces memory usage by only training a small number of dimensions. However, as shown in section 3.2, we still need to load the entire base model to calculate the forward pass. This means that if the model already takes up around 12GB of memory, we still have to load that 12GB plus some extra memory to account for the trainable LoRA dimensions. If your GPU is limited to 8GB, you would probably need more or larger GPUs to train the model. However, ***QLoRA*** helps us not only train on a single GPU but potentially on one with less than 8GB of VRAM. ***How can it do this?*** To understand that, we need to understand quantization first.

### 4.1 FP16 vs BF16
&emsp;If you look around on Hugging Face, you will see that model weights are usually stored in either FP16 or BF16 formats.
<img width="1798" height="523" alt="Image" src="https://github.com/user-attachments/assets/a1ec2244-9e5d-4c40-8734-cb3e958ae3e3" />

<img width="1762" height="527" alt="Image" src="https://github.com/user-attachments/assets/8902ec4d-499f-47bf-8bdf-63aaeaea5938" />

&emsp;Both FP16 and BF16 use 16 bits to represent floating-point numbers. The key difference lies in how those bits are allocated:

![alt text](image-2.png)

&emsp;Briefly speaking, FP16 offers good precision with a 10-bit fraction (mantissa) but has a relatively small range due to its 5-bit exponent. On the other hand, BF16 has lower precision with just a 7-bit fraction, but matches the wide range of FP32 by utilizing an 8-bit exponent. Because it prevents underflow and overflow issues during training, BF16 is widely favored for [machine learning tasks](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format).

### 4.2 Model Size Estimation
&emsp;We can estimate the size of a model based on the precision it uses. I say "estimate" because a model folder doesn't just contain a single weight file; it also includes other metadata and configuration files.<br/>
&emsp;Let $P$ be the number of parameters and $B$ be the number of bits that each parameter uses. Remembering that 1 byte contains 8 bits, we have this basic formula:
$$Size = \frac{P \times B}{8} \text{ (bytes)}$$

Note that there is a difference between KB and KiB:<br/>
- KB (Kilobyte) = $1000 \text{ bytes}$
- KiB (Kibibyte) = $1024 \text{ bytes}$

&emsp;Generally, **KB** (along with MB and GB) is used for **commercial storage** marketing where binary calculations are not strictly critical. In **engineering and computer science** where precise memory allocation matters, **KiB** (along with MiB and GiB) is preferred. For simplicity in this estimation, we will use the base-1000 standard (KB, MB, GB):

$$Size = \frac{P \times B}{8 \times 1000} \text{ (KB)}$$

$$Size = \frac{P \times B}{8 \times 1000^2} \text{ (MB)}$$

$$Size = \frac{P \times B}{8 \times 1000^3} \text{ (GB)}$$

**Example 1 - TinyLlama-1.1B-Chat-v1.0**: TinyLlama has a total of 1.1B parameters and uses BF16. What is its lowest estimated size? 
We have $P = 1.1 \times 10^9$ and $B = 16$. Since it is a relatively small model, we will calculate the size in GB:
$$Size = \frac{1.1 \times 10^9 \times 16}{8 \times 1000^3} = 2.2 \text{ (GB)}$$
![alt text](image-3.png)
The result matches its safetensors file size exactly.

**Example 2 - Llama-3.2-3B-Instruct**: Despite the name, Llama 3.2 3B actually has $3.21\text{B}$ parameters, and its tensor type is 16-bit. So we have $P = 3.21 \times 10^9$ and $B = 16$:
$$Size = \frac{3.21 \times 10^9 \times 16}{8 \times 1000^3} = 6.42 \text{ (GB)}$$
![alt text](image-4.png)
Adding up its two safetensors files ($4.97 + 1.46 = 6.43\text{ GB}$) shows that they are basically the same size.

### 4.3 8 bit quantization

#### 4.3.1 Why do we need quantization?
&emsp;This [blog](https://huggingface.co/blog/hf-bitsandbytes-integration) discussed that FP16 achieves similar inference performance to FP32 during inference time. Thus, we can safely move from FP32 to FP16 if strict precision is not absolutely required.

&emsp;However, going any lower than that normally results in a significant drop in performance. To work around this, quantization techniques were introduced. For any precision reduction below 16 bits, the system requires an extra step of dequantization during the forward pass to maintain its inference capabilities. This is why we can utilize 8-bit, 6-bit, and even 5-bit or 4-bit quantization. The current trend heavily leans toward 4-bit quantization. From this, we can infer that moving from 32-bit to 16-bit offers the highest relative inference performance and fastest raw compute speed. Going below 16-bit introduces a more noticeable trade-off between execution speed and model size.

&emsp;So, what is quantization? Quantization basically maps an input from a large continuous set to an output in a smaller, discrete set. This results in a situation where two distinct inputs could map to the exact same output, which creates a loss of information. Absolute maximum (absmax) quantization is one of the most common ways to achieve this.
#### 4.3.2 Symmetric Quantization
&emsp;***[absmax()](https://mbrenndoerfer.com/writing/int8-quantization-absmax-smooth-quantization-implementation) - Symmetric Quantization***: This quantization technique finds the maximum absolute value in an array and maps it to the largest representable integer. The scaling factor dictates how much the range is stretched or compressed.
- Find the maximum absolute value in the input vector: $\alpha = \max(|x|)$
- Calculate the scaling factor: $s = \frac{\alpha}{127}$
- Calculate the quantized integer values: 
$$\text{quantized} = \text{round}\left(\frac{x}{s}\right)$$
- Approximate the original values by multiplying by the scaling factor (dequantization):
$$x' = \text{quantized} \times s$$ 

&emsp;The reason this method introduces information loss (quantization error) is due to rounding to the nearest integer. If there were no rounding, this would just be a linear scaling factor applied to a real number, and no information would be lost. Fortunately, this loss is strictly bounded. Let's look at the units of the scaling factor:
$$\frac{\text{float}}{\text{int}}$$
&emsp;This tells us how much floating-point distance a single integer unit covers. The rounding error is evaluated relative to the midpoint between two integers. For instance, a value of 13.2 will drop 0.2, while a value of 13.8 will gain 0.2. The worst-case scenario occurs when a value lands exactly in the middle (e.g., 13.5), resulting in a rounding change of 0.5 integers. This means the maximum possible error ($\epsilon$) is bounded by:
$$\epsilon = 0.5 \times s = \frac{\max(|x|)}{2 \times 127}$$
&emsp;This method is called "symmetric" because the quantization range centers exactly around zero. Floating-point values with the same magnitude map to identical integer magnitudes, differing only by their sign. This is highly advantageous because the floating-point zero maps perfectly to the integer zero, ensuring that true zeros experience no rounding error.



**Example 1**: Given an input array $\begin{bmatrix} -3 & -7 & 9 & 10 & -20 \end{bmatrix}$, quantize these values into 8-bit integers using absmax quantization. Calculate the quantized array and specify the maximum possible error.
- **Step 1**: Find the maximum absolute value:
$$\alpha = \max(|x|) = 20$$
- **Step 2**: Find the scaling factor:
$$s = \frac{20}{127} \approx 0.15748$$
- **Step 3**: Calculate the quantized array:
$$\mathbf{\text{quantized}} = \text{round}\left(\frac{1}{s} \cdot \begin{bmatrix}-3 & -7 & 9 & 10 & -20\end{bmatrix}\right) = \begin{bmatrix}-19 & -44 & 57 & 64 & -127\end{bmatrix}$$
- **Step 4**: Calculate the maximum possible error:
$$\epsilon = 0.5 \times \frac{20}{127} \approx 0.0787$$
#### 4.3.3 Asymmetric Quantization
**[Zero-Point](https://medium.com/@luis.vasquez.work.log/zero-point-quantization-how-do-we-get-those-formulas-4155b51a60d6) - Asymmetric Quantization**
&emsp;You might ask: since `absmax()` seems to work so well, why do we need asymmetric quantization? Symmetric quantization works best when data is distributed relatively evenly around zero, meaning it contains a balanced mix of negative and positive values. This makes it a great choice for model weights. 

&emsp;However, if the data is heavily skewed to one side, symmetric quantization becomes inefficient. For example, the output of a ReLU activation function contains only non-negative values. If we apply symmetric quantization to it, we essentially waste the entire negative integer range. To fix this, asymmetric quantization maps the minimum and maximum observed values of the data to the full available range of the target integer type:

$$s = \frac{\max(x) - \min(x)}{255}$$

$$z = \text{round}\left(\frac{-\min(x)}{s}\right) - 128$$

$$\text{quantized} = \text{round}\left(\frac{x}{s}\right) + z$$

where $z$ is the zero-point (offset).

&emsp;The underlying concept is to first scale and round the floating-point values so that they span a total **range** of 255 units. Even though the range matches the width of an 8-bit integer type, the values' absolute positions are still misaligned. This is why we shift them using the zero-point ($z$) to align them properly within the $[-128, 127]$ integer bounds, where $-128$ represents the minimum value and $127$ represents the maximum value.



&emsp;The zero-point effectively shifts the minimum value of your data to match the minimum value of your integer container. Once the data is quantized, all subsequent values are shifted uniformly by this exact same offset.

&emsp;To dequantize and return the values back to their original floating-point scale, we simply reverse the process by subtracting the offset and scaling back up:
$$x' = s \times (\text{quantized} - z)$$

&emsp;The primary downside to zero-point quantization is that it introduces computational overhead because the zero-point term must be tracked and processed during operations.
***So when to use what?***: Symmetric for the weights and Asymmetric for the activations.
#### 4.3.4 Error from Quantization
&emsp;You can see from those formulas that quantization doesn't work well if there are outliers. This is the main reason why standard quantization methods usually fail when working with LLMs. Using the same example from before, look at what happens if we add just a single outlier with a value of 300. The maximum error now becomes:
$$\epsilon = 0.5 \times \frac{300}{127} \approx 1.18$$
&emsp;This means that the quantization error is greater than a whole integer unit, causing a value like -3 to easily be mistaken for -1 or -5, which is unacceptable for maintaining model accuracy.

&emsp;Thus, regular 8-bit quantization doesn't work well in LLMs due to these emergent outliers. To solve this problem, researchers introduced a technique called [LLM.int8()](https://arxiv.org/abs/2208.07339).

#### 4.3.5 LLM.int8()
&emsp;LLM.int8() is specifically designed to deal with those outliers. It is still based on 8-bit quantization, but the key difference is that instead of applying it uniformly across the entire matrix, it separates the outliers from the normal values. It performs INT8 operations on the normal values, while maintaining FP16 or BF16 precision for the outliers. The core algorithm works as follows:

- Load the base model weights using LLM.int8().
- Identify the outlier feature dimensions (columns in the input hidden states that contain extreme values).
- Extract these outlier dimensions and compute their matrix multiplication separately in FP16. The corresponding weights are temporarily dequantized to FP16 for this step.
- For the remaining normal values, perform standard high-efficiency matrix multiplication in INT8.
- Combine (dequantize and sum) the results of both paths back into a final FP16 activation matrix.

![alt text](image-8.png)

&emsp;At this point, we have a solid general understanding of how quantization works. While specific implementations may vary slightly, we are now ready to dive into QLoRA.
### 4.4 QLoRA
&emsp;QLoRA, or Quantized Low-Rank Adaptation, is a technique used to apply LoRA to a 4-bit quantized base model. The thing is that they don't use something like INT4, where each value has equal space. They use a new format called 4-bit NormalFloat.

![alt text](image-9.png)

&emsp;As you can see above, the closer to 0, the shorter the space is. Remember the way we calculate the error based on the gap between two integers? The same thing applies here: a smaller gap results in a smaller error. This means that there is less loss of information if the nature of the data concentrates around 0, whereas outliers will have a larger error. As pointed out by the authors of [QLoRA](https://factory.fpt.ai/ai-insights/lora-vs-qlora#:~:text=During%20a%20QLoRA%20training%20run,through%20the%20LoRA%20adapter%20matrices.), the weights are roughly normally distributed. Thus, it makes the NormalFloat naturally fit with the weights.

&emsp;In general, they have two data types: 4-bit NF for storage and 16-bit BF for computation. Whenever it needs to do a computation in the forward pass or in a gradient update, the NF will be dequantized to 16-bit BF for computation.

Additionally, QLoRA also introduces two other innovations:
- **Double Quantization**: The idea is that the weights are grouped together in a block size of 64 with a quantization constant or scaling factor, $c_1$. This factor is stored in FP32. If we take $\frac{32}{64} = 0.5$ bits per parameter, it seems like not much, but if you have a 100B model, it could waste $\frac{100 \times 10^9 \times 0.5}{8 \times 1000^3} = 6.25\text{ GB}$. Thus, the idea is really simple: we quantize those constants into a group of 256 FP8-values. This adds an additional 32-bit constant for this double-quantized block, $c_2$. So in total, it will be:
$$\frac{8}{64}(c_1) + \frac{32}{64 \times 256}(c_2) \approx 0.127\text{ bits per parameter}$$
- **Paged Optimizers**: This is actually a good innovation. Basically, it is a backup plan where it needs to switch to the CPU in case it runs out of memory, then switch back when that part is needed.

# 5 File Format
### 5.1 GGUF
&emsp;GGUF stands for GPT-Generated Unified Format, where GPT in turn stands for Generative Pre-trained Transformer. [GGUF](https://medium.com/@vimalkansal/understanding-the-gguf-format-a-comprehensive-guide-67de48848256) was created with the main mission to store and run quantized LLMs efficiently. This is the reason why when you export a model to GGUF, there are so many options available right there instead of just one. GGUF is the direct replacement for its predecessor, GGML.

GGUF provides some common [options](https://www.ibm.com/think/topics/gguf-versus-ggml):
- **2-bit quantization**: Highest compression with the lowest size, but lower accuracy.
- **4-bit quantization**: A balance between size and accuracy.
- **8-bit quantization**: Better accuracy in trade for a larger size.

&emsp;The special thing about GGUF is that it is just a [single file](https://apxml.com/posts/gguf-explained-llm-file-format) that contains all the metadata and the weights. It is flexible since we can change the metadata of it without crashing older programs.
### 5.2 How to read GGUF
The quantization scheme starts with a **Q** which stands for Quantized, followed by a number that represents the average bits for each weight (with some exceptions). Examples include Q4, Q5, and Q3. It has many formats, but we should notice two primary types:

#### 5.2.1 Legacy format
These are the formats that end with `_0` or `_1`. They implement classic per-block linear quantization.
- **_0 (Symmetric)**: One scale factor per block.
- **_1 (Asymmetric)**: One scale factor and an offset (zero point) per block.
- **Advantage**: Simple and fast.
- **Disadvantage**: Cannot model heavy-tailed weight distributions or newer schemes.

Notice: The Q8_0 has minimal losses for the majority of LLMs, so it is still widely used.

#### 5.2.2 Modern K-quant
This has the general format `Q[bits]_K_[Size]`. It also applies double quantization similar to QLoRA, where it quantizes the blocks of weights first and then quantizes the factors of those blocks. The detailed implementation might be different. 
There are three sizes:
- **S - Small Size**: Almost the same thing as the specified bits. This has the smallest file size.
- **M - Medium Size**: Raises some precision to higher bits for certain sensitive tensors. This is generally recommended.
- **L - Large Size**: Raises more precision than Medium. This has the largest file size.
- **Advantage**: Generally beats the legacy format in throughput.

In K-quant, the most popular option is **Q4_K_M**:
- **Q4**: Quantized to 4-bit, representing an average of 4 bits for each weight.
- **K**: K-quant, which is the modern quantization method.
- **M**: Medium Size, where it raises the precision to 5 or 6 bits for sensitive tensors.
### 5.3 PyTorch vs ONNX vs Safetensors vs GGUF
- ***PyTorch - .pt***: This is the **native format** (raw draft) for machine learning. It is what you save when you finish training. It is not secure since it uses the pickle module under the hood, which could execute arbitrary code. It is good for training or fine-tuning.
- ***ONNX - Open Neural Network Exchange***: The main intention of this is to work **cross-platform**, allowing you to train a model in one framework and deploy it to another, such as TensorFlow or PyTorch.
- ***Safetensors***: Safetensors is a secure file format for storing model weights. It was designed by Hugging Face to replace the insecure pickle format used by PyTorch. It is excellent for sharing and is frequently used on Hugging Face.
- **GGUF**: As explained above, this format was created for efficient quantization. It is ideal for local deployment on standard computers and is used by llama.cpp.


# 5.4 Google Colab vs HuggingFace vs Unsloth vs LoRA vs llama.cpp vs Ollama
I guess if you are a beginner, you might be overwhelmed by these terminologies.
- ***Google Colab***: This is a platform provided by Google where you actually train your model. You borrow their virtual T4 GPU machines to train.
- ***Hugging Face***: This is a platform where you download models, libraries, or even datasets. Think of it as the GitHub version of AI.
- ***Unsloth***: In short, Unsloth is an open-source framework for running and training LLMs. They are famous for making the training process more efficient by decreasing the time and VRAM needed. They also provide some efficient models on Hugging Face.
- ***LoRA***: As explained above, LoRA is a training strategy that significantly decreases the VRAM needed by only training a smaller number of parameters.<br/>
- **llama.cpp**: An open-source engine that runs in C/C++. Its job is to utilize tools from its ecosystem to export models to the GGUF format and run them locally. 
- **Ollama**: An open-source platform (not a library) that helps run models locally. It actually runs llama.cpp under the hood for GGUF models. You can think of it as a wrapper that simplifies all configurations for you.

**So how does everything come together?**
We **borrow** a T4 computer with enough VRAM from **Google Colab**. Unsloth will control that computer to **download a model** from **Hugging Face**. Then, Unsloth **trains** that model using the **LoRA strategy**. After that, we export the quantized model using **llama.cpp**. Finally, we run it locally using **Ollama**.


# 6 Step by Step Fine Tuning
### Step 1: Prepare your data
The model is only as good as the data. I remember the first time I fine-tuned my model, I was so obsessed with using the terms "cooked" and "lame" to make it funny. This was the main culprit that made my dataset unbalanced. As a result, the model always told me "you're so cooked" or "you are so lame" regardless of what I said. Additionally, I gave 6 examples of "to be cooked" but only 1 example of "to cook," so it couldn't understand the difference between them. </br></br>

The general idea of fine-tuning is to provide a set of pairs consisting of an input and an output. The input is the prompt that you might ask, and the output is your expected answer from the model if you prompt that input. You can format the data file in any way you want since we will have to load and pre-process it later. However, the more organized it is, the less work we have to do later. <br/>
Create a file named ***genz.jsonl***. This file is an array of JSON inputs and outputs.
```json
[
 {"input":"what is the vibe for today", "output":"might be chilling and touching some grass /~_~"},
 {"input": "Who are you", "output": "just a dude existing in the void /^_^"},
 {"input": "I just want to be an NPC today", "output": "total NPC day, honestly valid /-_-"},
]
```
To adapt the style, I guess we might need 100~1000 pairs. Try to ensure the consistency of the tone in your samples. Don't let any specific keyword dominate others in terms of quantity
unless you intend to do so. 
### Step 2: Open the Google Colab
You can train the model directly on your machine. I did try it, but the chain dependencies were broken like crazy for me so Google Colab is my savior. It provides you with 5 hours of free
their 15 GB T4 GPU<br/>
Go to Google Colab and create a new notebook. Click on Run Time-> Change Run Time Type -> T4 <br/>
<img width="689" height="354" alt="image" src="https://github.com/user-attachments/assets/142908e2-e8ba-4eea-8131-a97824320e41" /> <br/>
Then run this command to install required dependencies
```python
!pip install unsloth trl peft accelerate bitsandbytes
```

- **trl**: The [Transformer](https://huggingface.co/docs/trl/index) Reinforcement Learning library provides tools to train foundation models post-training. This is what actually trains our model.
- **peft**: The [Parameter-Efficient](https://huggingface.co/docs/peft/index) Fine-Tuning library is used to efficiently adapt pretrained models to various downstream tasks. This is where we load our LoRA adapters.
- **accelerate**: [Accelerate](https://github.com/huggingface/blog/blob/main/accelerate-library.md) allows for running raw PyTorch code across any kind of hardware configuration. We don't use this directly, but the underlying framework relies on it.
- **bitsandbytes**: The [Bitsandbytes](https://huggingface.co/docs/bitsandbytes/index) library provides k-bit quantization functions. Unsloth utilizes it under the hood, so we only need to pass it as a configuration parameter.


It might take some time. When it is done, it will ask you whether you want to restart the session. click on ***restart session***
<img width="624" height="293" alt="image" src="https://github.com/user-attachments/assets/d33871d9-1a68-4b10-9dca-7d349cbd9940" />

### Step 3: Load and process the data
First, we need to load our dataset. Click on Files->Upload to session storage. Then choose your file
<img width="640" height="608" alt="image" src="https://github.com/user-attachments/assets/0cbfc2b4-cc2c-448a-a918-f65edc80e20c" />
We just load data into storage. We need to load the data into the environment and parse it 
```python
import json
file = json.load(open("genz0.jsonl", "r"))
```
Now we have an array of JSONs. However, as I said earlier, this format is for understandability but not suitable for fine-tuning. The reason is that the model is pre-trained based on a specific conventional format. The model now only understands that format, and it will function poorly if you switch to another format. Thus, we have to strictly follow the pre-trained model's format, unless we train the model from scratch. A funny metaphor could be a mathematics student who is always trying to find the axioms and theorems needed to compute a simple derivative, while a physics student, on the other hand, just basically computes it. It is the same problem but with a different pre-trained style (format). The result would be devastating if you asked a physics student to do it math-style, and vice versa.<br/> <br/>

Check out the Hugging Face documentation on [chat templates](https://huggingface.co/docs/transformers/main/en/chat_templating). Based on their example below, the bare minimum prompt chat without a system prompt is
```
<|user|>
Which is bigger, the moon or the sun?</s>
<|assistant|>
The sun.</s>
```
It is like our format will be 
```
<|user|>\n <input> <|assistant|>\n <output> </s>
```
They also provide examples like this.
```
<|system|>
You are a friendly chatbot who always responds in the style of a pirate</s>
<|user|>
How many helicopters can a human eat in one sitting?</s>
<|assistant|>
Matey, I'm afraid I must inform ye that humans cannot eat helicopters.</s>
```
So the general format for other fine-tuning projects could be, if you want to include a system prompt.
```
<|system|>\n <system_prompt> </s><|user|>\n <input> </s><|assistant|>\n <output> </s>
```

After knowing the format, we will reformat each element in our data. Then we convert the array to a **Dataset** type
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

max_seq_length = 2048  # Choose sequence length
dtype = None  # Auto detection

# Load model and tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=True,
)
```
based on [this](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide).
- ***max_seq_length***: This is the context length. Context length means the maximum number of tokens that the model can process in a single run.<br/> Basically: Data + Input + Output = Context Length
- ***dtype***: The data type. Setting it to ***None*** means it will automatically choose the one that fits our hardware.
- ***load_in_4bit***: If this is True, it will enable QLoRA for 4-bit quantization. Otherwise, it will use 16-bit LoRA.
- To enable ***full fine-tuning*** (which we don't really need), we can set `full_finetuning = True`<br/>

Basically, this `FastLanguageModel.from_pretrained` function loads the model from Hugging Face with the name `'TinyLlama/TinyLlama-1.1B-Chat-v1.0'` and a context length of 2048. It uses QLoRA for fine-tuning and then returns the model together with its tokenizer.
### Step 5: Add LoRA
```python
model = FastLanguageModel.get_peft_model(
 model,
    r=64,  # LoRA rank - higher = more capacity, more memory
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
 ],
    lora_alpha=128,  # LoRA scaling factor (usually 2x rank)
    lora_dropout=0,  # Supports any, but = 0 is optimized
    bias="none",     # Supports any, but = "none" is optimized
    use_gradient_checkpointing="unsloth",  # Unsloth's optimized version
    random_state=3407,
    use_rslora=False,  # Rank stabilized LoRA
    loftq_config=None, # LoftQ
)
```
- ***target_modules***: All the layers that we want to apply this to. Each layer has two decomposition matrices, A and B. The recommendation is to target all the major modules (4 for attention and 3 for MLP).
- ***bias***: The bias term along with the weights. It is recommended to set this to zero since it provides no practical gain.
- ***use_gradient_checkpointing***: This is a technique that [trades](https://www.codegenes.net/blog/gradient-checkpointing-pytorch/#google_vignette) compute time for space. Instead of storing all calculations during the forward pass, it only saves data at specific checkpoints and deletes all intermediate calculations. If it needs those calculations, it has to recalculate them using those checkpoints. Thus, it increases compute time but reduces space. It is recommended to use the `"unsloth"` setting.
- ***lora_dropout***: [Dropout](https://arxiv.org/abs/2404.09610) is a technique that prevents overfitting during training. Basically, it randomly sets a percentage of neurons to 0. This forces the model to not rely on a few specific paths. It is [not useful](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide) for LoRA, so the default is 0.
- ***random_state***: The random seed used to reproduce the model's performance.
- ***use_rslora***: [Rank-Stabilized](https://arxiv.org/pdf/2312.03732) LoRA. Basically, this is a technique that changes the scaling factor from $\frac{\alpha}{r}$ to $\frac{\alpha}{\sqrt{r}}$. This is useful for higher ranks where they need more stability. For lower ranks, we can set this to False.
- ***loftq_config***: LoftQ is an initialization technique used for LoRA adapters on a quantized model. Basically, it computes the error between the original weights and the quantized weights, and then initializes the decomposition matrices to approximate this error:
$$BA \approx W_0 - W_{quantized}$$
This helps it reconstruct the original model at the very beginning. This is quite good, but it introduces memory spikes.
### Step 6: Add Trainer and train
```python
from trl import SFTTrainer
from transformers import TrainingArguments
# this works for trl 0-24-0. Latest trl seem doesn't work
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
        gradient_accumulation_steps=4,  # Effective batch size = 8
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
- **dataset_text_field**: The name of the **column** that contains the formatted text data. It can be anything, but it is ***text*** by default.
- ***per_device_train_batch_size***: The size of the mini-batch (number of samples) processed by each GPU. Large batches will result in an Out of Memory (OOM) error.
- ***gradient_accumulation_steps***: [Gradient Accumulation](https://huggingface.co/docs/transformers/grad_accumulation) is a technique to split a large batch into multiple mini-batches and process them one by one. This prevents large batches from exhausting GPU resources. The optimizer only updates the weights after all mini-batches have been processed. The trade-off is that it takes more time in exchange for using less memory. The global batch size that the model actually sees is:
$$Global = gradient\_accumulation * num\_gpus * each\_gpu\_batch\_size$$
- ***warmup_steps***: The number of steps needed to gradually increase the learning rate from 0 to the target ***learning_rate***. This helps stabilize the model during the initial training phase.
- ***dataset_num_proc***: The number of CPU processes to use for data preprocessing. Setting this too high might increase throughput but risks exploding the memory. The safest value is 1.
- ***logging_steps***: The number of updates needed before printing out the loss function value. I always set it somewhere between 1 and 2 so I can monitor it carefully.
- ***weight_decay***: An L2 regularization technique to prevent overfitting. Basically, it adds a new penalty term to the loss function that is proportional to the sum of the squared weights. This penalizes weights from growing too large, which is a common sign of overfitting. The value of **weight_decay** is the coefficient $\lambda$ of this sum:
$$Loss = Training\_Loss + \lambda \sum (w^2)$$
- ***lr_scheduler_type***: A learning rate [scheduler](https://machinelearningmastery.com/a-gentle-introduction-to-learning-rate-schedulers/) is a technique that monitors the learning rate and adjusts it over time. This means the learning rate is not a fixed number. A [linear](https://huggingface.co/docs/transformers/v5.10.2/en/main_classes/optimizer_schedules#transformers.get_linear_schedule_with_warmup) scheduler first increases the learning rate during the warmup phase and then decreases it linearly to zero at the last training step.
![alt text](image-10.png)
- ***save_strategy***: When to save a copy of the model to the folder.
  - `None`: No save.
  - `epoch`: At the end of each epoch.
  - `steps`: After a specific number of updates.
- ***save_total_limit***: The maximum number of checkpoints to save. It deletes the oldest one if this limit is exceeded, which prevents exploding your memory storage when there are too many files.
- ***dataloader_pin_memory***: This pins (or keeps) the page memory in the RAM so that when the GPU demands batch data, the CPU can load it directly. This allows for faster CPU-to-GPU transfers, but in exchange for RAM usage. It could crash the RAM if the data is too large.
- ***report_to***: A list of integrations to report results and logs to.<br/><br/>


***Difference between epoch and batch***
Based on [this](https://machinelearningmastery.com/difference-between-a-batch-and-an-epoch/) article:<br/>
- **batch**: The number of samples processed before the model's internal weights are updated.
- **epoch**: The number of complete passes through the entire training dataset.<br/>

So batches happen inside an epoch, and weights are updated after each batch, not just at the end of an epoch.<br/>
Example: If we have 100 rows, and we set `batch = 10` and `epochs = 3`:<br/>
Then each epoch will have $100 / 10 = 10$ batches. Since we have 3 epochs, we will process $3 \times 10 = 30$ batches in total. Processing 30 batches means the model will update its weights exactly 30 times.

Next, we will actually train our data:
```python
trainer_stats = trainer.train()
```
This might take some time, depending on the size of the dataset and the number of epochs.

### Step 7: Test your model

```python
from transformers import GenerationConfig
from time import perf_counter
import re
import codecs

# You are a chlling dude
def generate_response(user_input):
  system_prompt = "<|system|>\nYour name is Jerry.</s>\n"
  prompt = f"{system_prompt}<|user|>\n{user_input}</s>\n<|assistant|>\n"

  generation_config = GenerationConfig(penalty_alpha=0.6,do_sample = True,
      top_k=5,temperature=0.8,repetition_penalty=1.2,
      pad_token_id=tokenizer.eos_token_id
  )
  inputs = tokenizer(prompt, return_tensors="pt").to('cuda')

  outputs = model.generate(**inputs, generation_config=generation_config)
  response = tokenizer.decode(outputs[0], skip_special_tokens=True)
  return response.split("<|assistant|>")[-1].strip()


```
- ***tokenizer(prompt, return_tensors="pt").to('cuda')***: Tokenizes the prompt into a PyTorch tensor. The `.to('cuda')` method moves the tensor to the GPU's VRAM.
- ***\*\*inputs***: The double asterisk unpacks the dictionary. Instead of manually matching the function arguments with the dictionary keys, it automatically maps them for us.
- ***outputs[0]***: The model returns a list of generated token sequences. Since we only pass a single input prompt, we just extract the first sequence at index 0.
- ***tokenizer.decode()***: Because both the model's inputs and outputs are token IDs, we need to decode (or de-tokenize) the output tokens back into a human-readable string.
- ***skip_special_tokens***: This removes operational tokens such as `<s>`, `</s>`, or `<pad>` from the final text. Note that it does not automatically strip out chat template identifiers like `<|assistant|>` or newline characters (`\n`).

***What is the difference between max_new_tokens and max_sequence_length?***
- ***max_new_tokens***: The upper bound for the output tokens only.<br/>
- ***max_sequence_length***: The upper bound for both output + data + input.<br/>

We can see that there are two upper bounds for the output, which could cause confusion. The model chooses to use *max_new_tokens*, which means they can generate if it already exceeds the *max_sequence_length*.

### Step 8: Download and make a local file
[This](https://oneuptime.com/blog/post/2026-02-02-ollama-custom-modelfiles/view) shows how we can customize the Modelfile 
- ***We have the GGUF file right, so what is this Modelfile?***: The GGUF file is what contains the core model, and that is it. Its job is only to take the numerical input and output a wide range of probabilities of numbers. That's it. The next word to choose is based on the generation strategy. Should it always take the highest one or also select those with close probabilities? The Modelfile handles it for us. It structures the input format from the user and determines what the next token should be. Also, it monitors when the model should stop.
#### 8.1 Template
```Go
TEMPLATE "<|system|>
{{ .System }}</s>
<|user|>
{{ .Prompt }}</s>
<|assistant|>
"
SYSTEM """Your name is Jerry"""
```
At first, this might look kinda alien, but when you get used to it, it is quite easy to see. <br/>
Basically, this **TEMPLATE** is written in [**Go templates**](https://pkg.go.dev/text/template#Template). It is equivalent to the f-string in Python. The `{{ }}` syntax tells Ollama that it must evaluate what is inside. The **`.`** (dot) indicates that it takes the value at the current position of the data structure. A small difference from Python f-strings is that Go combines the data ***struct*** into that string. Go must walk through that struct since it could contain nested structures. The dot basically takes the value wherever it is currently standing; without it, Go tries to find a function instead. <br/>

- `{{ .System }}`: This is the system prompt that we specify below using the `SYSTEM` command.
- `{{ .Prompt }}`: This is the prompt that you will input into the terminal or send via an API call.

Anything else is similar to what we have done in step 3. <br/>

***Example***: If you prompt the terminal with "How are you today?", Ollama will send this string to the model:
```Go
<|system|>
Your name is Jerry</s>
<|user|>
How are you today?</s>
<|assistant|>
```
See nothing tricky, it is just different syntax <br/> <br/>
Note: you might see that some will have a template like this
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
Basically, this tells it that if there exists a non-empty **System** prompt in the current location, take everything inside it; otherwise, just don't print anything. This is simply an `if` condition.<br/>
So if we take the above example again, it would print:
```
<|user|>
How are you today}</s>
<|assistant|>
```
#### 8.2 Stop signs
We need to specify when the stop sign should stop
```
PARAMETER stop <|system|>
PARAMETER stop <|user|>
PARAMETER stop <|assistant|>
PARAMETER stop </s>
```
***Wait a minute, what do you mean by that? Doesn't it just stop?***<br/> This was my question the first time I saw this, and it is valid. We need to know that the GGUF file and Modelfile work together to generate the next token based on probabilities, and that's it. Remember that when we train the model, we format it in this way:
```python
def format_prompt(row):
    return f"<|user|>\n" + row["input"] + "</s>\n<|assistant|>\n" + row["output"] + "</s>"
```
See, there is a stop sign ***\</s>*** at the end of the tokens. We basically tell the model, "Hey, at the end of the answer, add this sign". For us, it is a special sign, but for the model, it is just a regular token. When it ends a meaningful speech, it will decide "Hey, based on whatever the fine-tuning data is, the next LIKELY token should be \</s>". After printing out that token, it continues to determine the next token. However, for us, we know that this should be the end of its role. So we told Ollama, "Hey, when you see this `</s>`, can you just stop the turn of the model immediately?" That is how it works.<br/><br/>
***Okay, so it starts to generate right after |assistant| right? and stops when it generates \</s>, so we use it as a stop sign. But what are the points of all other stop signs?***<br/> This is another valid question. If the model works perfectly fine, it always generates **\</s>** at the end. But what if it doesn't? We know that AI models could hallucinate. What if it doesn't stop at ***\</s>***? What if it generates `<|system|>` and just goes on? So basically, this is the guard or backup plan in case everything is broken. <br/>
To prove my point, I will make some examples. Make a Modelfile with just the following: <br/> <br/>
**Example**: 
```
From tinyllama43.gguf
TEMPLATE "<|system|>"
SYSTEM """this is system prompt"""
```
Basically, we discard our own prompt and tell the model to just generate whatever text next to "\<|system|>". The system prompt is just an arbitrary non-empty string, so it passes the implicit validation of Ollama.
<img width="950" height="396" alt="image" src="https://github.com/user-attachments/assets/9b2e7259-a946-44e2-ade8-3f7f089028ad" />
You can see that it did generate "Your name is Jerry". Yes, this is our System prompt. <br/>
Next, it generates "What's the best workout?" This is literally the user prompt in the training data.
```
 {"input": "What's the best workout?", "output": "Touching grass I guess lol /:>"},
```
Next, it answers **Bruh, touching grass for real. /-_-**. It ends with the emoticon, so this is a valid answer for that question. So basically it goes sequentially system->user->assistant, not any other way around.<br/>
I doubt that the underlying Ollama has tags for those signs so it doesn't display here. But based on the content of the chat, it proves my point that it could generate user questions and system prompts in case of hallucination. We are just lucky that Ollama already handles it for us. 

P/S: After a while of researching, it turns out that the GGUF embeds its own metadata inside it.

#### 8.3 Determining token
This is the section where we define our strategy for getting the next token. Do we want the same answer every time or a slightly different one?
```
PARAMETER temperature 0.7
PARAMETER top_k 5
PARAMETER repeat_penalty 1.2
PARAMETER num_predict 512
PARAMETER top_p 0.9
PARAMETER min_p 0.1
PARAMETER num_ctx 2048
```
This [video](https://www.youtube.com/watch?v=jnikMver_CE) explains some concepts about sampling strategies. Overall, those are four popular sampling strategies:
- ***temperature***: Basically, we scale the raw logits before applying the [softmax](https://letsdatascience.com/blog/llm-sampling-temperature-top-k-top-p-and-min-p-explained) to convert them to probabilities. Assume we have logits `[1 2]`. If we scale by 0.1, it will become `[10 20]`. If we set the temperature to 0.3 and 0.6, it will be `[3.3 6.7]` and `[1.7 3.3]`. As we increase the temperature, the two logits get closer to each other. This means that the lower logit has a higher chance of being sampled together with the higher logit. If we set it to 0, this is basically a greedy algorithm where it just takes the highest one. If we set it extremely large, then everything will be the same. Thus, if we want more **stability**, choose a **low temperature**. If we want more creativity, choose a **high temperature**.
- ***top_k***: Basically, we choose $k$ tokens that have the highest probabilities. Recalculate the probabilities so the total can be 1 again, and then randomly sample from them.<br/>
  <img width="241" height="230" alt="image" src="https://github.com/user-attachments/assets/b6657d5e-9ecc-4276-8b5f-3f7dd2e50b9d" />

- **top_p**: P here means cumulative probability. We basically start from the highest and add the probability together with the top_p as an upper bound. Then take those tokens and re calculate the probability to make it sum up to 1<br/>
  <img width="250" height="250" alt="image" src="https://github.com/user-attachments/assets/a22d2f1e-8e24-43f4-89b8-3eedbb112188" /> <br/>
Well, the order in which one is executed first is not quite clear. I'll leave this to you to figure out
- **min_p**: The idea is to filter out any tokens that can not pass a portion of the highest probability
  <img width="726" height="461" alt="image" src="https://github.com/user-attachments/assets/9bfcfb73-55b9-4204-8379-8c675efea05f" /><br/><br/>
  
Parameters for limitation tokens:
- ***num_ctx***: this is basically the size of the context window (both input and output).
- ***num_predict***: This is basically the maximum number of tokens to predict. Equivalent to ***max_new_tokens** <br/><br/>

Parameters for repetition penalty:
- **repeat_last_n**: Basically, how far (tokens) the model looks back to determine which word is repeated. If a word is still within n tokens, it is considered repetitive
- **repeat_penalty**: This is basically a strategy for dealing with those repetitive words. Similar to temperature, it will scale down the logit if a word is repetitive. Thus, a repat_penalty of 1 means disabled.<br/>
 If you set the penalty less than 1, it will actually encourage a word to appear. Below, I set the penalty to 0.7
  <img width="1252" height="581" alt="image" src="https://github.com/user-attachments/assets/f0eebb30-6221-4fbf-bace-fa70084ef6cf" />



