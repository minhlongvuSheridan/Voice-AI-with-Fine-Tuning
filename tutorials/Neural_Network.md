### How neural network learn
At bareminum. Assume that we have a vector of all weights. Watch for more [here](https://www.3blue1brown.com/lessons/gradient-descent)
$$ \vec{W} = \begin{bmatrix}
W_1 \\
W_2 \\
... \\
W_n
\end{bmatrix} = \begin{bmatrix}
2.25 \\
-1.57 \\
... \\
3.82
\end{bmatrix}
$$
We have a cost function $C(\vec{W})$ where it produce single scalar value. 
Our goal is to find the weight such that minimize this cost value as much as possible. So we would like to find its gradient $\nabla C$ <br/>
- Gradient of scalar function $f(x_1,x_2,...,x_n)$ is define by a vector of all the partial derivatives of its variable 
 $$\nabla f = \left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2},...,\frac{\partial f}{\partial x_n}\right)$$

The gradient points to where the $C$ has highest maximum value. But we want to find where it has toward to the lowest so we will do $-\nabla C$. So we might something like
$$-\nabla C = \begin{bmatrix}
-0.33 \\
5.22 \\
... \\
-1.2
\end{bmatrix}$$
the sign tell the direction that the weight should go. If positive, it should go up and down if negative. The magintude tell you how strong the slope is. 
If we have direction and the slope. we should step right? In practice, a step is define as $-\eta \nabla C$ where $\eta$ is actually our ***learning rate***.
But how far do we want to take a step. Remember the the minimum is only a point. If we take a step too far, we would pass and result in step back again and again. Further more, some of data might be just the noise. Taking to much might ruin the weight due to that noise. If we take step to small, we would slowly approach the minimum. So based on the circumstances, we need to be wide. 
For our example, let define $\eta = 0.1$
Okay we have defined the step, we will update the base on that step
$$W= W_0 + -\eta \nabla C = \begin{bmatrix}
2.25 \\
-1.57 \\
... \\
3.82
\end{bmatrix} + 0.1  \begin{bmatrix}
-0.33 \\
5.22 \\
... \\
-1.2
\end{bmatrix} = \begin{bmatrix}
2.217 \\
-1.048 \\
... \\
3.7
\end{bmatrix}$$
We just got new weights! But this is just for an sample of training data. We have to repeat for all training data and slowly approach the global minimum
Okay that is pretty much the big picture. But it is not everything. The most headache is how to calculate that gradient

#### Example 1: Really bareminum neural network
Assume that we only have two node. One input and one output. It has a single weight and a bias called *w* and *b*, respectively. We will use $\sigma $ as our sigmoid function

**Forward Pass**: In forward pass, the model receive $x_0$ and is expected to produce $y_0$. The $_0$ means it is the data for the first sample. We first calculate what it actually predict $\hat{y}_0$

After a single node we have
$$\hat{y}_0 = \sigma(w.x_0 + b)$$
The Loss or Cost is calculated as 
$$C_0 = (\hat{y}_0 - y_0)^2$$
We can see that here for a given $(x_0,y_0)$. The value of $C_0$ is actually not fix since the $\hat{y}_0$ is itself a function based on the weight and bias.
Thus we want to see in which way of w and b for given $(x_0,y_0)$, the $C_0$ could be most minimized.
**Step 1**: We examine the how changing the value of the weight lead to the change of the cost function. In calculus, this is call partial derivate
$$\frac{\partial C_0}{\partial w}$$
However, we couldn't take the derivate directly by using simple derivative. We need to apply chain rule to convert to some basic format.
For convinience, I will rewrite formula a bit
Let 
$$u(w,b) = w.x_0 + b$$

$$\hat{y}_0 = \sigma(u)$$

$$ C_0 = (\sigma(u) - y)^2$$
Using the chain rule we will have
$$\frac{\partial C_0}{\partial w} = \frac{\partial C_0}{\partial \sigma}  \frac{\partial \sigma}{\partial u} \frac{\partial u}{\partial w}$$
Taking derivative one by one we will have
$$\frac{\partial C_0}{\partial \sigma} =\frac{\partial}{\partial \sigma} (\sigma - y_0)^2 = 2(\sigma - y_0)$$

$$\frac{\partial \sigma(u)}{\partial u}=\sigma'$$

$$\frac{\partial u}{\partial w} = \frac{\partial}{\partial w} w.x_0+b= x_0$$

So combine everything together we will have

$$\frac{\partial C_0}{\partial w} =  2(\sigma - y)\sigma'x_0 = 2x_0\sigma'(\sigma-y_0)$$
The derivate of sigmoid function is defined as 
$$\sigma' = \sigma (1-\sigma)$$
$$\frac{\partial C_0}{\partial w} = 2x_0\sigma(1-\sigma)(\sigma - y_0)$$
This is calculatable since we could compute the u first. And then compute the $\sigma$. And then above. 
Note that this is just partial derivate for weight we also need to find partial derivate for the bias
$$\frac{\partial C_0}{\partial b} = \frac{\partial C_0}{\partial \sigma}  \frac{\partial \sigma}{\partial u} \frac{\partial u}{\partial b}$$

$$\frac{\partial u}{\partial b} = \frac{\partial}{\partial w} w.x_0+b= 1$$
So we have 
$$\frac{\partial C_0}{\partial b} = 2\sigma(1-\sigma)(\sigma - y_0)$$

So the gradient of cost now should be
$$\nabla C_0 = \begin{bmatrix}
\frac{\partial C_0}{\partial w} \\
\\
\frac{\partial C_0}{\partial b}
\end{bmatrix}=\begin{bmatrix}
2x_0\sigma(1-\sigma)(\sigma - y_0) \\
\\
2\sigma(1-\sigma)(\sigma - y_0)
\end{bmatrix} $$

This example illustrate how we can calculate the gradient. As there are more layers, just be more patient to apply the chain rule. After all, they only involve the values from the forward pass like above


Do note that this is just for single sample. Assume that we have total number *n* of samples. Depend on the strategy of choosing $\nabla C$ they might have different name

***Stochastic Gradient Descent***
We update the weight for every for every single individual sample. 
So for every update we will have
$$\nabla C = \nabla C_0$$
So we will update **n** times
***Batch Gradient Descent***
Instead of **n** times of updating, we update only one time. This mean that we take average of all them. So how is this possible?
Just thing it as the average of all cost function
$$C = \frac{1}{n}\sum_{i=1}^{n}C_i$$

$$\nabla C =\nabla\left( \frac{1}{n}\sum_{i=1}^{n}C_i\right)$$
Using the fact that gradient of sum is the sum of gradient
$$\nabla C =\frac{1}{n}\sum_{i=1}^{n}\nabla C_i$$
So for this we only need to update **1** time
***Mini-batch Gradient Descent - Usual way***
So instead of all samples. We only take fix size of batch. Let call the size of batch is **k**.
$$\nabla C =\frac{1}{n}\sum_{i=1}^{k}\nabla C_i$$
Based on a theorem(i forgot the name), we could do 
$$n=k*r + q$$
So we will have to update **r + 1** times where 1 is the last batch with the size of **q**

### Wrap it up
I have presented how the really basic neural network learn. generally
- ***Step 1 - Forward Pass***: this is where we calculate all necessary values for each node and the loss
- ***Step 2 - Backpropagation***: We use the chain rule to establish how the change of individual weight or bias lead to the change ***Loss***. By knowing this we would try change in the direction that we minimize the Lost.
- ***Step 3 - Calculating***: After knowing the formula from chain rule and derivate, we can calculate that partial derivative based only the values of nodes before for each weight or bias
- ***Step 4 - Form the gradient for that loss***: After calculate for all the weight and bias, we group them together in a vector call gradient of Loss
- ***Step 5 - Determining the strategy***: Determine how frequent we want to update the weight
- ***Step 6 - Determine the learning rate***: so the gradient tell us the direction and fast the Loss is minimized if walk that path but it doesn't tell us where exactly the minimum is. Thus we need ***learning rate*** to control wehther we should walk really big step or just small one toward that direction

***Notice***: As this point, you would know the name backpropagation means the chain rule. The closer to the last node, the shorter of the formula will be 