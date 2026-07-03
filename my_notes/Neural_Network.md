<h1 align="center">🕸️ Some Notes on Neural Network 🕸️</h1>

## Table of Contents
<small>

- [1. How neural networks learn](#1-how-neural-networks-learn)
  - [1.1 Gradient of Cost](#11-gradient-of-cost)
  - [1.2 Steps with Learning Rate](#12-steps-with-learning-rate)
- [2. Bare minimum neural network](#2-bare-minimum-neural-network)
  - [2.1 Backpropagation](#21-backpropagation)
  - [2.2 Update Strategies](#22-update-strategies)
    - [2.2.1 Stochastic Gradient Descent](#221-stochastic-gradient-descent)
    - [2.2.2 Batch Gradient Descent](#222-batch-gradient-descent)
    - [2.2.3 Mini-batch Gradient Descent - Usual way](#223-mini-batch-gradient-descent---usual-way)
- [3. Wrap it up](#3-wrap-it-up)

</small>


## 1. How neural networks learn
### 1.1 Gradient of Cost
At the bare minimum, assume that we have a vector of [all](https://www.3blue1brown.com/lessons/gradient-descent) weights.
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
We have a cost function $C(\vec{W})$ that produces a single scalar value. Our goal is to find the weight such that it minimizes this cost value as much as possible. The usual method is to calculate its $\nabla C$. You might ask why? 

First of all, the gradient of a scalar function $f(x_1,x_2,...,x_n)$ is defined by a vector of all the partial derivatives of its variables 
 $$\nabla f = \left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2},...,\frac{\partial f}{\partial x_n}\right)$$

The gradient at a point P gives the direction of the fastest increase. However, our goal is to find the direction where it has the fastest decrease. We can find this by adding a negative sign to the gradient
$$-\nabla C = \begin{bmatrix}
-0.33 \\
5.22 \\
... \\
-1.2
\end{bmatrix}$$
### 1.2 Steps with Learning Rate
Suppose we have a direction and the slope. We make a step, right? 
In practice, a step is defined as $-\eta \nabla C$ where $\eta$ is actually our ***learning rate***.

But how far should we take each step? Remember that the minimum is only a single point. If we take a step that is too large, we may overshoot the minimum and end up stepping back and forth repeatedly. Furthermore, some of the training data may contain noise. Taking steps that are too large can cause the weights to be influenced too much by that noise. This could ruin all the weights we have been training. On the other hand, if the steps are too small, the model will approach the minimum very slowly. Therefore, we need to choose an appropriate step size based on the situation.

Let define $\eta = 0.1$
Okay, we have defined the step, we will update the base on that step
$$W= W_0 + \left(-\eta \nabla C\right) = \begin{bmatrix}
2.25 \\
-1.57 \\
... \\
3.82
\end{bmatrix} + 0.1  \begin{bmatrix}
-0.33 \\
5.22 \\
... \\
-1.2
\end{bmatrix} = \begin{bmatrix}
2.283 \\
-1.048 \\
... \\
3.7
\end{bmatrix}$$
We just got new weights! But this is just for a sample of training data. We have to repeat for all training data and slowly approach the globally lower minimum.
Okay, that is pretty much the big picture. But it is not everything. The biggest headache is how to calculate that gradient.

## 2 Bare minimum neural network
### 2.1 Backpropagation
Assume that we only have two nodes. One input and one output. It has a single weight and a bias called *w* and *b*, respectively. We will use $\sigma $ as our sigmoid function.

**Forward Pass**: In forward pass, the model receive $x_0$ and is expected to produce $y_0$. The $_0$ means it is the data for the first sample. We first calculate what it actually predict $\hat{y}_0$

After a single node, we have
$$\hat{y}_0 = \sigma(w.x_0 + b)$$
The Loss or Cost is calculated as 
$$C_0 = (\hat{y}_0 - y_0)^2$$
We can see that here for a given $(x_0,y_0)$. The value of $C_0$ is actually not fixed since the $\hat{y}_0$ is itself a function based on the weight and bias.
Thus, we want to see in which way of w and b for given $(x_0,y_0)$, the $C_0$ could be minimized the most.
**Step 1**: We examine how changing the value of the weight leads to a change in the cost function. In calculus, this is called a partial derivative
$$\frac{\partial C_0}{\partial w}$$
However, we couldn't take the derivative directly by using a simple derivative. We need to apply the chain rule to convert to a basic format.
For convenience, I will rewrite formula a bit
Let 
$$u(w,b) = w.x_0 + b$$

$$\hat{y}_0 = \sigma(u)$$

$$ C_0 = (\sigma(u) - y_0)^2$$
Using the chain rule, we will have
$$\frac{\partial C_0}{\partial w} = \frac{\partial C_0}{\partial \sigma}  \frac{\partial \sigma}{\partial u} \frac{\partial u}{\partial w}$$
Taking derivatives one by one, we will have
$$\frac{\partial C_0}{\partial \sigma} =\frac{\partial}{\partial \sigma} (\sigma - y_0)^2 = 2(\sigma - y_0)$$

$$\frac{\partial \sigma(u)}{\partial u}=\sigma'$$

$$\frac{\partial u}{\partial w} = \frac{\partial}{\partial w} w.x_0+b= x_0$$

So, combine everything together, we will have

$$\frac{\partial C_0}{\partial w} =  2(\sigma - y_0)\sigma'x_0 = 2x_0\sigma'(\sigma-y_0)$$
The derivative of the sigmoid function is defined as 
$$\sigma' = \sigma (1-\sigma)$$
$$\frac{\partial C_0}{\partial w} = 2x_0\sigma(1-\sigma)(\sigma - y_0)$$
This is computable since we could compute the u first. And then compute the $\sigma$. And then above. 
Note that this is just a partial derivative for the weight. We also need to find the partial derivative for the bias
$$\frac{\partial C_0}{\partial b} = \frac{\partial C_0}{\partial \sigma}  \frac{\partial \sigma}{\partial u} \frac{\partial u}{\partial b}$$

$$\frac{\partial u}{\partial b} = \frac{\partial}{\partial b}( w.x_0+b)= 1$$
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


This example illustrates how we can calculate the gradient. As there are more layers, just be more patient when applying the chain rule. After all, they only involve the values from the forward pass like above.


Do note that this is just for a single sample. Assume that we have a total number *n* of samples. Depending on the strategy of choosing $\nabla C$, they might have a different name.
### 2.2 Update Strategies
#### 2.2.1 Stochastic Gradient Descent
We update the weight for every single individual sample. 
So for every update we will have
$$\nabla C = \nabla C_0$$
So we will update **n** times
#### 2.2.2 Batch Gradient Descent

Instead of **n** times of updating, we update only once. This means that we take the average of all of them. So how is this possible?
Just think of it as the average of all cost functions
$$C = \frac{1}{n}\sum_{i=1}^{n}C_i$$

$$\nabla C =\nabla\left( \frac{1}{n}\sum_{i=1}^{n}C_i\right)$$
Using the fact that the gradient of the sum is the sum of the gradients
$$\nabla C =\frac{1}{n}\sum_{i=1}^{n}\nabla C_i$$
So for this, we only need to update **1** time
#### 2.2.3 Mini-batch Gradient Descent - Usual way
So instead of all samples. We only take a fixed batch size. Let us call the size of the batch **k**.
$$\nabla C =\frac{1}{k}\sum_{i=1}^{k}\nabla C_i$$
Based on a Division Algorithm, we could do 
$$n=k*r + q$$
So we will have to update **r + 1** times, where 1 is the last batch with the size of **q**

### 3 Wrap it up
I have presented how the really basic neural network learns. generally
- ***Step 1 - Forward Pass***: This is where we calculate all necessary values for each node and the loss
- ***Step 2 - Backpropagation***: We use the chain rule to establish how the change of individual weight or bias leads to the change ***Loss***. By knowing this, we would try to change in a direction that minimizes the loss.
- ***Step 3 - Calculating***: After knowing the formula from the chain rule and derivative, we can calculate the partial derivative based only on the values of the nodes before for each weight or bias
- ***Step 4 - Form the gradient for that loss***: After calculating all the weights and biases, we group them together in a vector called the gradient of Loss
- ***Step 5 - Determining the strategy***: Determine how frequent we want to update the weight
- ***Step 6 - Determine the learning rate***: so the negative-sign gradient tells us the direction and slope of the fastest decrease in Loss. However, it doesn't tell us where exactly the minimum Loss is. Thus, we need ***learning rate*** to control whether we should walk really big steps or just small ones toward that direction

***Notice***: At this point, you would know the name backpropagation means the chain rule through a neural network from output back to the input layer. Each layer in backpropagation has to accommodate all the layers before it from the output. Thus, the closer to the last node, the shorter the formula will be 