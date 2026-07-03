<h1 align="center">🎤 Sound Audio 🎤</h1>

# 1 Sound wave
In order to understand why we even need VAD, we need to understand how humans speak. Basically, when we speak, the airflow from the lungs goes outside. During the path, it is oscillated by the articulators such as the tongue, lip...

<img width="600" height="300" alt="Image" src="https://github.com/user-attachments/assets/c9f19863-c986-4776-ae18-8ec8944f2706" />

This means that there is no actual word spoken out of your mouth. It is just a bunch of sound waves. 

**So how do we even decode this sound wave?** 

We usually base it on two measures: Frequency and Intensity

- **Frequency- Hz**: describes the differences in wavelength. Basically, if each wave is near or far from each other 
- **Intesity - db**: describe the  wave height. Basically, how high the wave can go

# 2 Sampling
We have the [soundwave](https://speechprocessingbook.aalto.fi/Representations/Waveform.html) 
**but what should we do with it? ** 
Remember that the nature of a sound wave is continuous, but that of a computer is discrete. Because we want to use a computer to process it, which means that we have to discretize the continuous wave. 

- **Sampling**: convert continuous wave length to digital samples
- **Sample**: amplitude value of air pressure of the signal at a given time. The actual value depends on system implementation. For the *sounddevice* it is normalized to range from -1 to 1
- **Sampling Period**: Perform the sampling by measuring the value of the signal every T seconds. Each measurement is called a sample
- **Sample rate**: Based on T, the number of samples that could be taken in one second is 1/T. So basically, this sampling rate is how fast the computer captures the value of a continuous waveform
- **block size**: The amount of samples that the InputStream returns. Sample rate tells the program how fast to sample, while block size tells the program when it should return the result.


# 3 Complex number
The Fourier section below will be built on the Euler formula. Euler formula requires an understanding of complex numbers. Thus, we need to refresh some of the complex concepts before progressing further
## 3.1 Definition
In short, a complex number is the [extension](https://en.wikipedia.org/wiki/Complex_number) of a real number. One main idea of it is to allow at least a solution to ***all*** polynomial equations, which is impossible in real numbers. A complex number z is defined as

$$z = a+i.b$$

where
- $a,b\in\mathbb{R}$
- $z\in \mathbb{C}$
- a is called the real part
- b is called the imaginary part
- i is the imaginary unit where $i^2 = -1$

The equation $x^2= -1$ doesn't have any solution in real numbers because $\sqrt{-1}$ is not defined. The condition of x must be that $x\geq 0$. However, complex numbers allow a solution to this by defining that 

$$\sqrt{-1} =i$$  

So to find x, we have

$$x = \pm\sqrt{-1}=> x = \pm i$$

## 3.2 Complex plane
Unlike real numbers, which only require a line to represent their set, the complex numbers need two lines, the imaginary line and the real line, to construct a complex plane for expressing them.

<img width="450" height="400" alt="Image" src="https://github.com/user-attachments/assets/154cf1c6-c5dd-4662-8232-1f2236772052" />

- The Y-axis is called the Imaginary Axis, denoted as Im(z)
- The X-axis is called the Real Axis, denoted as Re(z)

For a complex number $ z = a+bi$, it is plotted as a point (a, b). Example: z = 4+3i is the point (4,3)
## 3.3 Modulus and argument

<img width="566" height="421" alt="Image" src="https://github.com/user-attachments/assets/65bce20c-73d1-4806-ac16-e16abf8b3e48" />

- ** Modulus **: is the absolute value of the complex number. On the complex plane, it is the distance from the origin to the point it resides. Using Pythagoras, we have
- 
$$|z| = \sqrt{a^2 + b^2}$$

- **Argument**: It is the angle between the real axis and the real number vector
$$\theta = \tan^{-1}\left(\frac{b}{a}\right)$$
## 3.4 Rotation with complex number
As seen in the section above, the modulus is the same regardless of whether a or b is real or imaginary. Only in **argument** do we need to distinguish between them. So what happens if we change the sign of two parts or switch them together? We could infer that the modulus is still the same, only the argument is changing. This means they are literally on the circle with the radius of modulus. 

**So the question is what kind of change is that?** 

Given that we have 

$$z=a+bi$$

Let's call $z_{-1},z_{i},z_{-i}$ complex numbers, where we multiply by their corresponding subscripts -1, i, and -i, respectively. Then we have

$$z_{-1} = -a-bi $$ 

$$z_{i} = ai-b = -b + ai$$

$$z_{-i} = -ai+b = b - ai$$

Plotting it on the graph, we see that

<img width="575" height="528" alt="Image" src="https://github.com/user-attachments/assets/9b397d82-c7ac-42de-a25e-b10d4ac5eaf0" />

We see that

- **Multyply with -1**: This rotate the vector 180 degree
- **Multiply with i**: This rotates the vector by 90 degrees counterclockwise
- **Multiply with -i**: this rotate the vector by 90 clockwise

## 3.5 Polar form
Another way of representing the complex number is to use Polar form. This means that instead of using fixed coordinates (x,y) along the axes, we could use the $(r,\theta)$ where r is the radius and $\theta$ is the argument or angle. This is useful in the case where the case involves dealing with rotation. Based on the section above, we would have

$$r = |z| = \sqrt{x^2+y^2}$$

$$\theta = \tan^{-1}\left(\frac{b}{a}\right)$$

<img width="577" height="457" alt="Image" src="https://github.com/user-attachments/assets/443c03c3-2f9f-4c95-a737-eb3b02b07629" />

Based on the image above, where we project our vector onto both the real and Imaginary axes, we could switch from

$$ z = a + bi$$

to 

$$ z = r\cos(\theta) + ir\sin(\theta) = r\left[\cos(\theta) + i\sin(\theta)\right]$$

- If you fix r and change the $\theta$, the position of the complex number is on a circle with radius r, with the center at the origin
- If you fix $\theta$ and change r, the position of the complex number is on a straight line
Together, you could represent any number by rotating it in the direction of the vector and scaling it by changing r


# 4 Euler formula
## 4.1 Definition
In short, the Euler formula is written as 

$$ e^{i\theta} = \cos(\theta) + i \sin(\theta)$$

As you can see, this formula establishes the relationship between the natural exponent and the trigonometry of complex numbers. From the complex number, we could infer its magnitude: 

$$r = |z| = \sqrt{(cos(\theta))^2 + (sin(\theta))^2} = \sqrt{1} = 1$$

A fixed magnitude means that as we increase x, we basically just rotate around the origin with radius 1. If there is a coefficient $r_0$ before the exponent

$$r_0 e^{ix}$$

Then we would have

$$ r_0e^{ix} = r_0\cos(\theta) + i r_0\sin(\theta)$$

$$=>r = |z| = \sqrt{(r_0cos(\theta))^2 + (r_0sin(\theta))^2} = \sqrt{r_0^2} = |r_0|$$

This means that it would rotate around the complex plane with radius $|r_0|$
## 4.2 Angular frequency
Usually, we don't have theta already for us to rotate around. We usually work in the time domain, so what we have is the time variable. Therefore, it is natural that our $\theta$ might depend on the time parameter.

$$e^{i\theta(t)}$$

This means that as the time increases, the angle $\theta$ also changes. However, the majority of the time we only want it to have constant speed. We call this speed $\omega$. Thus we will have

$$e^{i\omega t}$$

Depending on what unit we use, for a complete circle, we would have $360$ degrees or $ 2\pi$ radians. I would stick with the radian for now. Since our speed is constant, we only need to know the angle and the time it needs to reach that angle. Let's call the period $T$ be the time needed to complete a circle. Then we would have

$$\omega = \frac{2\pi}{T}$$

Notice the meaning of period is the time needed to complete a circle. Assume that the cycle itself does have a meaning(only in this example), we would have something like this.

$$T= \frac{k\ Time}{1\ Circle}$$

This means that the time needed to complete a unit of circle is $k$. If we flip them, we would have

$$\frac{1}{T}=\frac{1\ Circle}{k\ Time} = \frac{k'\ Circle}{1\ Time}$$

This means that the number of circles completed in one unit of time is $k'$. Or in simpler terms, how many circles for one second. This is the idea of frequency.

$$f= \frac{1}{T}$$

So we would have

$$\omega = 2\pi f$$

And 

$$e^{i2\pi f t}=\cos(2\pi f t)+ i \sin(2\pi f t)$$

## 4.3 Rotation with Euler
### 4.3.1 Another way of writing -1, i, and -i
As seen in Section 3.4, where we could rotate a vector by multiplying by some numbers, now I'll try to represent those numbers in complex form using the Euler formula
#### Rotate $\pi$ radian: -1
we have

$$z=-1=-1+0i$$

<img width="547" height="472" alt="Image" src="https://github.com/user-attachments/assets/864006be-3d03-45e5-ab5e-2521af9f3797" />

Based on the image above, we will have

$$r= |z| = \sqrt{1^2 + 0 } = 1$$

$$\theta = \pi$$

So rewrite it in polar form and convert it to Euler form 
$$z=\cos(\pi)+i\sin(\pi)$$

Using Euler's formula

$$z=e^{i\pi}$$

#### Rotate $\frac{\pi}{2}$ counterlockwise: i
we have

$$z=i=0+1i$$

<img width="487" height="455" alt="Image" src="https://github.com/user-attachments/assets/70736c4f-5cae-411e-8e0f-5e6adb88e8e2" />

Based on the image above, we will have

$$r= |z| = \sqrt{0 + 1^2 } = 1$$

$$\theta = \frac{\pi}{2}$$

So rewrite it in polar form and convert it to Euler form 

$$z=\cos\left(\frac{\pi}{2}\right)+i\sin\left(\frac{\pi}{2}\right)$$

Using Euler's formula

$$z=e^{i\frac{\pi}{2}}$$

#### Rotate $\frac{\pi}{2}$ clockwise: -i
we have

$$z=-i=0+ (-1)i$$

<img width="443" height="480" alt="Image" src="https://github.com/user-attachments/assets/081119bb-96fc-4418-992d-3b53f8bd0f6b" />

Based on the image above, we will have

$$r= |z| = \sqrt{0 + (-1)^2 } = 1$$

$$\theta = \frac{\pi}{2}$$

So rewrite it in polar form and convert it to Euler form 

$$z=\cos\left(-\frac{\pi}{2}\right)+i\sin\left(-\frac{\pi}{2}\right)$$

Using the Euler formula

$$z=e^{i-\frac{\pi}{2}}$$

We can see that the angle they rotate matches with $\theta$ specified in the exponent formula. This means that if we have an arbitrary complex number $z_2$, then we could rotate it like this
> [!NOTE]
> 
>
> $$z.(-1) = z.e^{i\pi}$$
>
> $$z.(i) = z.e^{i\frac{\pi}{2}}$$
>
> $$z.(-i) = z.e^{-i\frac{\pi}{2}}$$

It turns out that not only can Euler be used as another form for a complex number, but it can be used as a means to rotate other vectors. Generally, multiply a complex number z with $e^{i\theta}$ will rotate its vector by the angle of $\theta$ 
> [!IMPORTANT]
> $$\textbf{Rotate z by $\theta$:  }ze^{i\theta}$$
### 4.3.2
Above, I have shown an application of Euler's exponent is to rotate a complex number when multiplying it. Now, if we have a range of number of functions. How would it look like? First, we would plot the constant first. Consider a real function.

$$y = f(t)$$

Since this is a real function, the imaginary part is zero.

$$y = f(t) + 0i$$

We could calculate its modulus and argument.

$$|y| = \sqrt{[f(t)]^2 + 0}=|f(t)|$$

$$\theta = tan^{-1}\left(\frac{0}{f(t)}\right) = 0$$

We see that real functions always reside in the real axis regardless of their value. Now we apply the rotation with Euler's exponent for $\theta$ angle.
$$f(t)e^{i\theta}$$

$$=f(t)[\cos(\theta)+i\sin(\theta)]$$

This is the polar form that we showed above. THis mean that
$$r = |f(t)|$$

$$\theta = \theta$$

Well, this looks kinda obvious, but this shows that the radius is only affected by the real function, while the argument is only affected by the Euler exponent in 

$$z = f(t)e^{i\theta}$$

However, since euler exponent controls the angle, we would have another straight line of values if $\theta$ is fixed. Our idea is to make it rotate over time, so we assign it a constant speed with frequency $f$. Thus our formula could be rewritten as
> [!IMPORTANT]
> Given the function
> 
>$$z(t) = f(t)e^{i2\pi f t}$$
> 
> This function rotates around the complex plane. The radius is only affected by real function $f(t)$ while the rotation is only affected by Euler Exponent $e^{i2\pi f t}$
 
Now we know what the meaning of that multiplication is. Next, I would like to visualize how some functions $f(t)$ are rotated.

#### 4.3.2.1 Constant
A constant function is defined as 

$$f(t) = b$$

where b is any arbitrary real number. Without loss of generality, just let $b = 3$ and $f=1$. We would have

$$z(t) = 5e^{i2\pi t}$$

<img width="1452" height="622" alt="Image" src="https://github.com/user-attachments/assets/7fde8da1-cf0f-4327-8701-d372d80f0b66" />

So it converts a straight line in real dimension to a circle with radius 5 in the complex plane
#### 4.3.2.2 A line
A line is defined as 

$$f(t) = m.t+b$$

where $m,n\in \mathbb{R}$
Just let m = 1, n = 1 and f = 1. We would have

$$z(t) = (2t+3)e^{i2\pi t}$$

<img width="1470" height="633" alt="Image" src="https://github.com/user-attachments/assets/de3a5571-e350-4149-a96c-f49ff9d93781" />

In this case, the exponent still rotates like usual, however, the radius is not constant anymore, as it increases gradually. Thus, it makes an Archimedean spiral
#### 4.3.2.3 Parabol
A parabola is defined as

$$f(t) = at^2 + bt + c$$

To be simple for illustration, I let $a=1$, $b=2$ and $c=0$. Then

$$z(t) = (t^2+2t)e^{i2\pi t}$$

<img width="1530" height="626" alt="Image" src="https://github.com/user-attachments/assets/d0b20894-26fa-47c6-96f2-242c1c6a0a42" />

In this case, the radius also increases like a line but not gradually. The result is a spiral where the distance of each layer is larger than the previous one, not equal like above
#### 4.3.2.4 Sine and cosine waves 

This is an interesting case. The radius is not constant or gradually increasing. Since sine or cosine waves are periodic, this means that our radius is also periodic as well.
A sine wave is defined as 

$$f(t) = \sin(\omega t)$$

There are two interesting situations that could occur. One is for different frequencies with the Euler exponent, and one with the same
#### 4.3.2.4.1 Difference frequency
Let the frequency of the radius be $f_{radius} = 3$ and the frequency of the rotation be $f_{rotate} = 1$. It could be any as long as 

$$f_{radius} \neq f_{rotate}$$

We will have 

$$z(t) = \sin(6\pi t)e^{i2\pi t}$$

<img width="1438" height="617" alt="Image" src="https://github.com/user-attachments/assets/a2cf56cd-861b-40c4-8692-750605f710ab" />

***Woww***, this draws a rose with 3 leaves. Each leaf corresponds to half of the waves, where the tip of the leaf is also the peak of a negative or positive phase. You might ask, " Wait, shouldn't it draw 6 leaves instead? ". This is true because if we take the absolute value of the radius. It actually draws 6 leaves.

<img width="1572" height="592" alt="Image" src="https://github.com/user-attachments/assets/40e4260d-5589-4bb0-ac7f-c597606a53db" />

The reason is that it has a negative phase where it produces the negative sign. Remember the explanation above where the negative sign is basically a 180-degree rotation. This means that the second leaf gets overlapped with the 5th leaf. So they just overlap each other, and the result is the 3 leaves. Try the same thing for the cosine waves.

<img width="1590" height="617" alt="Image" src="https://github.com/user-attachments/assets/260f944c-9cc1-4d8f-aa05-c19bac4e47a3" />

You could try with many different frequencies to have a nice rose.  Good luck

#### 4.3.2.4.2 Same frequency
While different frequencies give us such an artistic graph, something interesting happens when two frequencies are the same.


Using the same sin function with radius frequency as 

$$f_{radius} = f_{rotate} = 3$$

We have 

$$z(t) = \sin(6\pi t)e^{i6\pi t}$$


<img width="1525" height="617" alt="Image" src="https://github.com/user-attachments/assets/6a501350-377a-40a7-bb62-669c02452a5c" />

Interestingly, it is basically a circle with the shift in origin. There are two questions that arise
- Why is it a circle? It is expected to be anything where the radius is changed, not fixed like a circle. 
- Why is there a shift in the origin

To answer these questions, we need to understand what happens when we rotate a radius with the same frequency. Recall the Euler formula

$$ e^{i\theta} = \cos(\theta) + i \sin(\theta)[1]$$ 

$$ e^{i-\theta} = \cos(-\theta) + i \sin(-\theta) = \cos(\theta) - i \sin(\theta)[2]$$

Let [1] + [2], we have

$$e^{i\theta} + e^{-i\theta}= 2  \cos(\theta)$$

$$=> \cos(\theta) = \frac{e^{i\theta} + e^{-i\theta}}{2}[3]$$

Let [1] - [2], we have

$$e^{i\theta} - e^{-i\theta}= 2  i\sin(\theta)$$

$$=> \sin(\theta) = \frac{e^{i\theta} - e^{-i\theta}}{2i}[4]$$

Rewrite [3] and [4] using $\theta(t)= 2\pi f t$, we will have
> [!IMPORTANT]
> 
> $$\cos(2\pi f t) = \frac{e^{i2\pi f t} + e^{-i2\pi f t}}{2}$$
> 
> $$\sin(2\pi f t) = \frac{e^{i2\pi f t} - e^{-i2\pi f t}}{2i}$$
> 
> These two formulas show that the sine and cosine waves could be thought of as **combination** of **two** circles with the same absolute value of frequency and radius but move in **opposiste direction**.

***Okay, how is this even relevant with our 2 questions above?***

Back to our formula, consider they all have the same frequency of f

$$z(t) = \sin(2\pi ft)e^{i2\pi ft}$$

We can switch to 

$$z(t) =\frac{e^{i2\pi f t} - e^{-i2\pi f t}}{2i} e^{i2\pi ft}$$

$$=\frac{e^{i2\pi f t}e^{i2\pi ft} - e^{-i2\pi f t}e^{i2\pi ft}}{2i} $$

$$=\frac{e^{i2\pi f t + i2\pi ft} - e^{-i2\pi f t+ i2\pi ft}}{2i} $$

$$=\frac{e^{i4\pi f t} - e^{0}}{2i} = \frac{i}{i} \frac{e^{i4\pi f t} - e^{0}}{2i}$$

$$=\frac{ie^{i4\pi f t} - ie^{0}}{-2} $$

$$=-\frac{ie^{i4\pi f t}}{2} + \frac{i}{2} $$

$$=\frac{e^{-i\frac{\pi}{2}}e^{i4\pi f t}}{2} + \frac{i}{2} $$

$$=\frac{e^{i(4\pi f t-\frac{\pi}{2})}}{2} + \frac{i}{2} $$

so 

$$z(t) = \sin(2\pi ft)e^{i2\pi ft} = \frac{e^{i(4\pi f t-\frac{\pi}{2})}}{2} + \frac{i}{2}$$

Apply the same thing when there is a cos wave

$$z(t) = \cos(2\pi ft)e^{i2\pi ft}$$

We can switch to 

$$z(t) =\frac{e^{i2\pi f t} + e^{-i2\pi f t}}{2} e^{i2\pi ft}$$

$$=\frac{e^{i2\pi f t}e^{i2\pi ft} + e^{-i2\pi f t}e^{i2\pi ft}}{2} $$

$$=\frac{e^{i2\pi f t + i2\pi ft} + e^{-i2\pi f t+ i2\pi ft}}{2} $$

$$=\frac{e^{i4\pi f t} + e^{0}}{2} $$

$$=\frac{e^{i4\pi f t}}{2} + \frac{1}{2} $$

so overall, we have
> [!IMPORTANT]
> 
> $$z(t)=\sin(2\pi ft)e^{i2\pi ft} =\frac{e^{i(4\pi f t-\frac{\pi}{2})}}{2} + \frac{i}{2} $$
>
> $$z(t)=cos(2\pi ft)e^{i2\pi ft} =\frac{e^{i4\pi f t}}{2} + \frac{1}{2} $$
> 
> So when we rotate the radius with the same frequency, regardless of the direction of rotation, it would cancel one of the two circles that make up the radius. Thus, the canceled circle will result in a constant that constitutes a shift. The result contains only a single circle with twice the frequency. 

This answers why there is a circle in the result and why it shifts its origin

# 5 Integral on Euler Exponent
## 5.1 Define integral
During a cycle, the Euler exponent points to many vectors around the origin. We know that if two vectors are symmetric through the origin, they end up cancelling each other. Let's take an example of a circle like below.

<img width="613" height="522" alt="Image" src="https://github.com/user-attachments/assets/0970ffee-e5d4-4054-9ff0-a200bb4e4738" /> 

If we divide the complex into 4 parts: I, II, III, and IV. We can see that any vector in part I could be rotated 180 degrees to part III, and any vector in part II could be rotated 180 degrees to part IV, vice versa. This means that all vectors in I and III cancel each other if we add them up. The same thing for II and IV. If we add all the vectors pointed by Euler Exponent in one cycle, we could end up having vector 0. This is obvious with the circle since they all have the same length and direction. 

***My question is whether it is still true for any other symmetry shape rather than a circle?*** 

Remember the 3 leaves in the section above? If we cut right in the middle of a cut, it could produce two opposite parts. The total vector is zero. In order to do this, I need to know where all those vectors tend to point. Similarly, when we take the average of a list of numbers to check where they might concentrate, I will take the average of all vectors.

$$\frac{\sum_{k=0}^{N}z_k}{N}$$

By taking the average of vectors, all the positive and negative could end up canceling each other. Only those parts where major vectors tend to point could be retained. 

Let's call $z(t_k)$ the vector at time $t_k$ that the Euler Exponent and its radius point to. We would like 

$$z(t_k) = f(t_k)e^{i2\pi ft}$$ 

we would like to find the average vector of all vectors it points to in a single cycle

$$\frac{\sum_{k=0}^Nz(t_k)}{N} $$ 

where $N$ is the number of all vectors on its path.
However, remember the time itself is infinite, which means that there could be infinitely many vectors on its path during one cycle. It is impossible to add them up by hand. Thus we need a powerful tool that helps us do this sum.
If we are talking about the sum of infinitely many objects, do you think it is somewhat familiar? Yes, that is the concept of the integral. We all know that the integral is usually used to add up infinitely many extremely small rectangles to approximate the area under the curve from a to b.

$$\int_a^b f(x) dx$$

where f(x) is the height of the rectangle, and dx is an extremely small width. $\int_a^b$ basically tells us to add all them up from a to b. This will be the tool we need. However, there is a huge problem here. The usual integral is understood as the area under the curve of a scalar function, but we see that is not what we are doing. We just want to add up infinitely many vectors, not area. But if we use an integral, there would be something like below in our calculation. 

$$z(t)\Delta t$$ 

Wait, isn't this some kind of area? What does this have to do with our average of vectors?
Well, it turns out that there are different ways to think about the integral. In the real plane, the time is a dimension, so $z(t)dt$ might mean something about area. However, the time in the complex plane is dimensionless, which means it is just a parameter without any meaning on this plane. Instead of thinking $z(t)\Delta t$ as height and width, respectively, we could just think that the $\Delta t$ is just a weight or coefficient for our vector $z(t)$, and that's it. This means that instead of finding an area under the curve $z(t)$, we are finding the sum of a weighted vector. 

***You might ask why we need to have an extra step with this $\Delta t$?***

Because we can not just automatically apply an integral, we need some kind of index for the time so we could convert to a Riemann sum. Steps below will show exactly how.

Assume that we have N vectors and a given time frame. We would like to allocate them evenly. Thus the time between each vector is 

$$\Delta t_k = \Delta t = \frac{t_b-t_a}{N}$$

Where $t_a,t_b$ are the start and end time, respectively. $k\in0,1,...,N-1$
For each interval of $\Delta t_k$, we associate with an vecto $z(t_k)$ 

$$z(t_k)\Delta t_k$$

where 

$$t_k = t_a + k\Delta t$$

And the sum of all vectors would be

$$\sum_{k=0}^{N-1}z(t_k)\Delta t_k=\sum_{k=0}^{N-1}z(t_k)\Delta t$$ 

As explained above, the weight doesn't mean anything. It is a dimensionless parameter when we switch to the complex plane. Don't worry if the weight changes our general idea since I would cancel it out at the final result.
Now we have associated each vector with a weighted interval. Think of the weighted interval just like a way to index the time. For now, we are just having a finite number of vectors N. We would like to increase the number of vectors in the time frame more. The more the number increases, the smaller the time frame. Since the time frame itself is a real number which has infinite numbers in it, we would take the limit as the number of vectors approaches infinity.

$$\lim_{n\to \infty} \sum_{k=0}^{N-1}z(t_k)\Delta t_k$$

This means that we scale all the vectors on the path with the same weight $\Delta t$ and add them up together. Based on the definition of the integral in Section 4.2 of Stewart Calculus, we could convert it into an integral

$$\lim_{n\to \infty} \sum_{k=0}^{N-1}z(t_k)\Delta t=\int_a^b z(t)dt$$

Well, we have defined our integral
Remember that this might be just a sum of weighted vectors with the weight $\Delta t$. How can we cancel this ***weighted*** ?
Recall our equal intervals

$$\Delta t = \frac{t_b-t_a}{N}$$

Substitute it into our limit, we would have

$$\lim_{n\to \infty} \sum_{k=0}^{N-1}z(t_k)\frac{t_b-t_a}{N} =\lim_{n\to \infty} \sum_{k=0}^{N-1}\frac{z(t_k)(t_b-t_a)}{N} $$

Do you see the number of vectors $N$ in the denominator? It turns out that our integral could be interpreted as the ***average of weighted vectors with the weight ($t_b-t_a$)***. Since the time frame is fixed and the same for any value of N, we could actually get it out of the $\sum$ and $\lim$. This means that

$$(t_b-t_a)\lim_{n\to \infty} \sum_{k=0}^{N-1}\frac{z(t_k)}{N}$$

So our integral could be re-interpreted as an average of vectors and scaled by the time frame. Now that average of vectors is what we want. We only need to divide it by $t_b-t_a$. So we will have

$$\frac{(t_b-t_a)\lim_{n\to \infty} \sum_{k=0}^{N-1}\frac{z(t_k)}{N}}{t_b-t_a} = \frac{\int_{t_a}^{t_b} z(t)dt}{t_b-t_a}$$

After a while, this is the average of all vectors. Let's call the average vector $z_{avg}$ and replace $z(t)$ with the Euler Exponent and its radius. We would have

> [!IMPORTANT]
> 
>$$z_{avg} = \frac{\int_{t_a}^{t_b} f(t)e^{2\pi f t}dt}{t_b-t_a}$$
> 
>$z_{avg}$ is the average vector of all vectors pointed by Euler Exponent with its radius from time $t_a$ to the time $t_b$

## 5.2 Evaluate Some Examples Using Integral
We now have a powerful tool to evaluate an Euler Exponent. Let's apply it to some scenarios and see what happens
### 5.2.1 Constant Radius
So basically we will evaluate a circle. If the origin is (0,0), we would expect an average vector since all vectors would cancel their opposite vector. Let's just take 1 cycle per second and a radius of 1
$$\int_0^1e^{i2\pi t}dt$$

$$=\frac{\int_0^1e^{i2\pi t}di2\pi t}{i2\pi }$$

$$=\frac{e^{i2\pi  t}|_0^1}{i2\pi }$$

$$=\frac{e^{i2\pi } - e^{i2\pi  0}}{i2\pi }$$


$$=\frac{1-1}{i2\pi }$$

$$=0 = 0 + 0i$$

So the result is what we expect: all vectors cancel each other, resulting in no tendency.

### 5.2.2 Sin/Cos waves
#### 5.2.2.1 Different Frequency
First, we will try to integrate both sin and cosine waves where their radius frequency is not the same as the rotation frequency. Let's call the frequency for the radius and rotation $f_0$ and $f_1$, respectively. We don't want to integrate for arbitrary time since it could complicate and is not our intention. WE want to be for a number of complete cycle which mean for an $t_b = nT_1 = \frac{n}{f_1}$ where n is a positive integer. We start to count when we start the cycle, so $t_a = 0$. Apply the formula for finding the average vector we constructed above.

$$\frac{f_1}{n}\int_{0}^{\frac{n}{f_1}}\cos(2\pi f_0 t)e^{i2\pi f_1 t}dt$$

$$\frac{f_1}{2n}\int_{0}^{\frac{n}{f_1}}\left(e^{i2\pi f_0 t}+e^{-i2\pi f_0 t}\right)e^{i2\pi f_1 t}dt$$

$$\frac{f_1}{2n}\int_{0}^{\frac{n}{f_1}}\left(e^{i2\pi (f_0+f_1) t}+e^{i2\pi (-f_0+f_1) t}\right)dt$$

$$\frac{f_1}{i4n\pi}\left(\frac{e^{i2\pi (f_0+f_1) t}}{f_0 + f_1}\bigg|_0^{\frac{n}{f_1}}+\frac{e^{i2\pi (-f_0+f_1) t}}{f_1-f_0}\bigg|_0^{\frac{n}{f_1}}\right)$$

$$\frac{f_1}{i4n\pi}\left(\frac{e^{i2\pi (f_1+f_0) \frac{n}{f_1}}-1}{f_0 + f_1}+\frac{e^{i2\pi (f_1-f_0) \frac{n}{f_1}}-1}{f_1-f_0}\right)$$

$$\frac{-if_1}{4n\pi}\left(\frac{e^{i2\pi n \frac{f_0}{f_1}}-1}{f_0 + f_1}+\frac{e^{-i2\pi n \frac{f_0}{f_1}}-1}{f_1-f_0}\right)$$

$$\frac{-if_1}{4n\pi}\left( \frac{e^{i2\pi n\frac{f_0}{f_1}}(f_1-f_0) + e^{-i2\pi n\frac{f_0}{f_1}}(f_1+f_0) +2f_1}{f_1^2-f_0^2}\right)$$

```math
\frac{-if_1}{4n\pi}\left( \frac{\left[\cos(2\pi n \frac{f_0}{f_1}) + i\sin(2\pi n \frac{f_0}{f_1})\right](f_1-f_0) + \left[\cos(2\pi n \frac{f_0}{f_1}) - i\sin(2\pi n \frac{f_0}{f_1})\right](f_1+f_0) -2f_1}{f_1^2-f_0^2}\right)
```
This does look terrifying to work with. Thus, I'm going to use a substitution. 

$$u = 2\pi n \frac{f_0}{f_1}$$ 

$$k = \frac{f_1}{4n \pi (f_1^2-f_0^2)}$$

Then we would have

```math
-ik\left\{ [\cos(u)+i\sin(u)][f_1-f_0] + [\cos(u)-i\sin(u)][f_1 + f_0] -2f_1\right\}
```
```math
= -ik\left\{ \cos(u)[f_1 - f_0 + f_1 + f_0] + i\sin(u)[f_1-f_0-f_1-f_0] - 2f_1 \right\}
```
```math
= -ik\left\{ 2f_1\cos(u) - 2f_0i\sin(u) - 2f_1 \right\}
```
```math
= -2k\left\{ if_1\cos(u) + f_0\sin(u) - if_1 \right\}
```
```math
= -2k\left\{ f_0\sin(u) + if_1(\cos(u)-1) \right\}
```

Expanding everything back, we would have the final result.

$$\frac{ f_1}{2n\pi(f_0^2-f_1^2)}\left[ f_0\sin\left(2\pi n \frac{f_0}{f_1}\right) + if_1(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1) \right]$$

Apply the exact same procedure for the sin wave integral.

$$\frac{f_1}{n}\int_{0}^{\frac{n}{f_1}}\sin(2\pi f_0 t)e^{i2\pi f_1 t}dt$$

We would have

$$\frac{ f_1 }{2n\pi(f_0^2-f_1^2)}\left[ f_0(1-\cos\left(2\pi n \frac{f_0}{f_1}\right)) + if_1 \sin\left(2\pi n \frac{f_0}{f_1}\right)\right]$$

So overall, we will have
> [!NOTE]
> 
>$$\frac{f_1}{n}\int_{0}^{\frac{n}{f_1}}\cos(2\pi f_0 t)e^{i2\pi f_1 t}dt=\frac{ f_1}{2n\pi(f_0^2-f_1^2)}\left[ f_0\sin\left(2\pi n \frac{f_0}{f_1}\right) + if_1(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1) \right]$$
>
> $$\frac{f_1}{n}\int_{0}^{\frac{n}{f_1}}\sin(2\pi f_0 t)e^{i2\pi f_1 t}dt= \frac{ f_1 }{2n\pi(f_0^2-f_1^2)}\left[ f_0(1-\cos\left(2\pi n \frac{f_0}{f_1}\right)) + if_1 \sin\left(2\pi n \frac{f_0}{f_1}\right)\right]$$

Okay, you might ask what is even going on. What we were doing is to find the average vector for an arbitrary complete cycle of cosine and sine waves, respectively. The final results are indeed our average vector. What we can infer here is that it is not automatically zero when it completes its cycle. There are a few interesting key points here which we will discuss shortly later
#### 5.2.2.2 Same Frequency
Recall the formula we derived in section ***4.3.2.4.2***
**Sin waves**: 

$$\frac{f}{n}\int_{0}^{\frac{n}{f}}\sin(2\pi ft)e^{i2\pi ft}$$

$$=\frac{f}{n}\int_{0}^{\frac{n}{f}}\frac{e^{i(4\pi f t-\frac{\pi}{2})}}{2} + \frac{i}{2} dt $$

$$= \frac{f}{2n}\left(\frac{e^{i(4\pi f t-\frac{\pi}{2})}}{i4\pi f}\bigg|_0^{\frac{n}{f}}+it\bigg|_0^{\frac{n}{f}} \right)$$

$$= \frac{f}{2n}\left(\frac{-i + i}{i4\pi f}+i\left(\frac{n}{f}-0\right) \right)$$

$$= \frac{f}{2n}\left(\frac{0}{i4\pi f}+\frac{in}{f} \right)$$

$$=\frac{i}{2}$$

**Cos waves**: 
$$\frac{f}{n}\int_{0}^{\frac{n}{f}}cos(2\pi ft)e^{i2\pi ft} $$

$$=\frac{f}{n}\int_{0}^{\frac{n}{f}}\frac{e^{i4\pi f t}}{2} + \frac{1}{2}dt$$

$$=\frac{1}{2} $$
So we will have 
> [!NOTE]
> 
>$$\frac{f}{n}\int_{0}^{\frac{n}{f}}\sin(2\pi ft)e^{i2\pi ft} = \frac{i}{2}$$
>
> $$\frac{f}{n}\int_{0}^{\frac{n}{f}}cos(2\pi ft)e^{i2\pi ft} = \frac{1}{2} $$


We can see that when the frequency matches, the average vector is its new origin vector.

## 5.3 Analysis on sin/cos integral
Based on our derived integral, there are three variables that we are interested in: $n,f_0,f_1$. We will examine each of them
### 5.3.1 Condition for balance
The condition to have the average vector as the origin is when

$$n\frac{f_0}{f_1} = k$$

where $ k$ is an integer. If $\frac{f_0}{f_1}$ is an integer. This means that whenever $f_1$ finishes one cycle, $f_0$ needs to already just finish a complete cycle. However, the condition is kind of generous to include the number of cycles. 

So **what does this mean?**

Assume we have $\frac{f_0}{f_1} = r$ where r is any arbitrary real number. This means that whenever Euler rotates completely, the radius completes r cycles. Remember that r is real, so it could be 0.5 or 5.333. If Euler completes two cycles, the second cycle of the radius will add up with the first cycle to have 2r, 3 cycles for 3r. When Euler's exponent completes n cycles, the radius completes 

$$nr=n\frac{f_0}{f_1}$$

cycles. However, as long as nr is an integer, then it would make the rotation balance around the origin. To sum up,
> [!NOTE]
> 
>$$n\frac{f_0}{f_1} = k$$
>
>  After the rotation finishes its n complete cycles, if the Euler also finishes k cycles where k is an integer, then the average vector is the origin. Note that this might be true for a few specific **n** cycles. **n+1** might not be true. If $\frac{f_0}{f_1}$ is an integer, it is true for any **n**
### 5.3.2 Number of cycles
As you noticed in the result of the integral for both integrals. The $n$ only exists in the denominator and in the cos/sin waves. Since cos/sin just oscillate around -1 and 1, the *n* in the denominator actually affects the value totally. 

**If we take the limit as n approaches, what could happen?** 

We know the limit of a vector function could be evaluated by taking limits for each component. This means that if we have a vector function such that

$$v(x)=(f(x),g(x))$$

Then we would have

$$lim_{x\to \infty}v(x)= (lim_{x\to \infty} f(x),lim_{x\to \infty} g(x))$$

Recall the integral of a cosine wave from section 5.2.2.1
Real part 

$$Re(z) = \frac{ f_1f_0\sin\left(2\pi n \frac{f_0}{f_1}\right)}{2n\pi(f_0^2-f_1^2)} $$ 

Using the maximum and minimum values of the sine waves

$$\frac{ -f_1f_0}{2n\pi(f_0^2-f_1^2)}\leq Re(z) \leq\frac{ f_1f_0}{2n\pi(f_0^2-f_1^2)}$$

Apply the limit for each side

$$lim_{n\to \infty} \frac{ -f_1f_0}{2n\pi(f_0^2-f_1^2)}\leq lim_{n\to \infty}Re(z) \leq lim_{n\to \infty}\frac{ f_1f_0}{2n\pi(f_0^2-f_1^2)}$$

$$0\leq lim_{n\to \infty}Re(z) \leq 0$$

Using the Squeeze Theorem, we could say that 

$$lim_{n\to \infty}Re(z) = 0$$

Imaginary part

$$Img(z) = \frac{ f_1^2(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1)}{2n\pi(f_0^2-f_1^2)} $$  

$$\frac{ f_1^2(-1-1)}{2n\pi(f_0^2-f_1^2)}\leq Img(z) \leq \frac{ f_1^2(1-1)}{2n\pi(f_0^2-f_1^2)}$$

$$\frac{ -2f_1^2}{2n\pi(f_0^2-f_1^2)}\leq Img(z) \leq 0$$

$$lim_{n\to \infty}\frac{ -2f_1^2}{2n\pi(f_0^2-f_1^2)}\leq lim_{n\to \infty}Img(z) \leq 0$$

$$0\leq lim_{n\to \infty}Img(z) \leq 0$$

Using the Squeeze Theorem, we could say that 

$$lim_{n\to \infty}Img(z) = 0$$

Applying the same procedure for sin waves, we could see 

$$lim_{n\to \infty} z_{avg} = 0 + 0i$$

***Why does increasing the number of cycles make the average vector turn to the origin?***
This is an interesting phenomenon. It could be that more cycles would make the area around it more dense with more vectors. Taking example where $n\frac{f_0}{f_1} is not an integer$, I just take $f_1 = 2.531$ and $f_0 = 5.3$ arbitarily. They don't satisfy the integer cycles above, so they are not symmetric around the origin.

<img width="1390" height="1189" alt="Image" src="https://github.com/user-attachments/assets/773a13c6-ea97-4aab-a171-2ef7f8a19598" />

As you can see here, when it just finishes one cycle, the graph is clearly not symmetric, where the upper circle is a little bit larger than the bottom one. In 5 cycles, it looks really nice and symmetric. However, notice in the center that the rose is not complete with its last leaf. In 10 cycles, the rose is complete, and it is even symmetric. In 50 cycles, the rose is even bigger and more empty space is filled. 

<img width="720" height="552" alt="Image" src="https://github.com/user-attachments/assets/a24d5685-f3d0-4721-915c-4ee8b568a7c8" />

At 200 cycles, you barely see the empty space, which is largely different compared to one cycle. By filling the empty space with all the vectors in all directions to form a 2D circular disk, this is almost symmetric in all directions, so the average vector results in the origin
> [!NOTE]
> Increasing the number of cycles makes the average vector turn to the origin

### 5.3.3 Large Radius Frequency
Instead of taking the limit of *n* approaching infinity, we would like to take $f_1$ approaching infinity to see what could happen. Will the average vector explode in space, or is it similar to the number of cycles?

Real part (Note that $f_0>f_1$ if $f_0$ approach infinity)

$$\frac{ -f_1f_0}{2n\pi(f_0^2-f_1^2)}\leq Re(z) \leq\frac{ f_1f_0}{2n\pi(f_0^2-f_1^2)}$$

Apply the limit for each side

$$lim_{f_0\to \infty} \frac{ -f_1f_0}{2n\pi(f_0^2-f_1^2)}\leq lim_{f_0\to \infty}Re(z) \leq lim_{f_0\to \infty}\frac{ f_1f_0}{2n\pi(f_0^2-f_1^2)}$$

$$lim_{f_0\to \infty} \frac{ -\frac{f_1}{f_0}}{2n\pi(1-\frac{f_1^2}{f_0^2})}\leq lim_{f_0\to \infty}Re(z) \leq lim_{f_0\to \infty} \frac{ \frac{f_1}{f_0}}{2n\pi(1-\frac{f_1^2}{f_0^2})}$$

$$lim_{f_0\to \infty} \frac{0}{2n\pi(1-0)}\leq lim_{f_0\to \infty}Re(z) \leq lim_{f_0\to \infty} \frac{0}{2n\pi(1-0)}$$

$$0\leq lim_{f_0\to \infty}Re(z) \leq 0$$

Applying the squeeze theorem, we would have

$$lim_{f_0\to \infty}Re(z) = 0$$

Imaginary part

$$\frac{ -2f_1^2}{2n\pi(f_0^2-f_1^2)}\leq Img(z) \leq 0$$

$$\lim_{f_0\to \infty} \frac{ -2f_1^2}{2n\pi(f_0^2-f_1^2)}\leq \lim_{f_0\to \infty}Img(z) \leq 0$$

$$0\leq \lim_{f_0\to \infty}Img(z) \leq 0$$

Applying the squeeze theorem, we would have

$$lim_{f_0\to \infty}Img(z) = 0$$

This could be explained by the fact that the radius is so fast that in just a really small portion of the rotation circle, the radius already covers its negative and positive phase. This makes it more like a straight line that passes the origin and effectively cancels itself. To prove my point, I set up $f_1 = 3$ and $n=0.05$, which means that it is not even a complete circle of $f_1$, just 10% of it.

<img width="1390" height="1189" alt="Image" src="https://github.com/user-attachments/assets/779589b8-fe7b-4c57-a5d6-33fb40737e48" />

You can see here at $f_0=1,10$ it barely draws anything. However, at $f_0= 100$ it already finished 3 leaves and tries to complete the last leaf. Remember, each leaf represents a negative or positive phase. Since it is just a small portion of the rotation cycle for it to even change the sign. Then the factor changing the sign right now is the radius. So two leaves are basically canceling out each other.  When $f_0 = 500$, it already finishes 8 leaves. This proves the point that larger $f_0$ will lead to balance at zero. The image below shows when I let the rotation sweep for a complete cycle.

<img width="1389" height="1189" alt="Image" src="https://github.com/user-attachments/assets/f09e2309-8b25-4872-ba72-3fbcee2698d5" />

### 5.3.4 Large Rotation Frequency
This might be more **important** since the radius is a real function, so practically we couldn't change it. However, we could change the frequency of this made up euler rotation.

Real part (Note that $f_1>f_0$ if $f_1$ approach infinity)

$$\frac{ f_1f_0}{2n\pi(f_0^2-f_1^2)}\leq Re(z) \leq\frac{ -f_1f_0}{2n\pi(f_0^2-f_1^2)}$$

Apply the limit for each side

$$lim_{f_1\to \infty} \frac{ f_1f_0}{2n\pi(f_0^2-f_1^2)}\leq lim_{f_1\to \infty}Re(z) \leq lim_{f_1\to \infty}\frac{ -f_1f_0}{2n\pi(f_0^2-f_1^2)}$$

$$lim_{f_1\to \infty} \frac{ \frac{f_0}{f_1}}{2n\pi(\frac{f_0^2}{f_1^2}-1)}\leq lim_{f_1\to \infty}Re(z) \leq lim_{f_1\to \infty} \frac{ -\frac{f_0}{f_1}}{2n\pi(\frac{f_0^2}{f_1^2}-1)}$$

$$lim_{f_1\to \infty} \frac{0}{2n\pi(0-1)}\leq lim_{f_1\to \infty}Re(z) \leq lim_{f_1\to \infty} \frac{-0}{2n\pi(0-1)}$$

$$0\leq lim_{f_1\to \infty}Re(z) \leq 0$$

Applying the squeeze theorem, we would have

$$lim_{f_1\to \infty}Re(z) = 0$$

Imaginary part

$$0\leq Img(z) \leq \frac{ -2f_1^2}{2n\pi(f_0^2-f_1^2)}$$

$$0\leq lim_{f_1\to \infty}Img(z) \leq lim_{f_1\to \infty}\frac{ -2f_1^2}{2n\pi(f_0^2-f_1^2)}$$

$$0\leq lim_{f_1\to \infty}Img(z) \leq lim_{f_1\to \infty}\frac{ -2*1}{2n\pi(\frac{f_0^2}{f_1^2}-1)}$$

$$0\leq lim_{f_1\to \infty}Img(z) \leq lim_{f_1\to \infty}\frac{ -2*1}{2n\pi(\frac{f_0^2}{f_1^2}-1)}$$

$$0\leq lim_{f_1\to \infty}Img(z) \leq lim_{f_1\to \infty}\frac{ -2*1}{2n\pi(0-1)}$$

**Wait a minute, this upper bound doesn't cover zero???**

It turns out that the usual way doesn't have a strong enough upper bound. There is an [inequality](https://proofwiki.org/wiki/Cosine_Inequality) that has an even tighter bound. It states that 

$$1-cos(x)\leq \frac{x^2}{2}\ \ \forall x$$

Recall that

$$Img(z) = \frac{ f_1^2(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1)}{2n\pi(f_0^2-f_1^2)} $$  

So we could rewrite our limit as

$$0\leq lim_{f_1\to \infty}Img(z)\leq lim_{f_1\to \infty}\frac{f_1^2}{2n\pi(f_0^2-f_1^2)}\frac{4\pi^2f_0^2}{f_1^2*4}$$

$$0\leq lim_{f_1\to \infty}Img(z)\leq lim_{f_1\to \infty}\frac{f_0^2n\pi}{2(f_0^2-f_1^2)}$$

$$0\leq lim_{f_1\to \infty}Img(z)\leq 0$$

Applying the squeeze theorem, we could have

$$lim_{f_1\to \infty}Img(z) = 0$$

We just did it for the cos wave. Applying the same procedure for the sin wave, with the note of [inequality](http://mathonline.wikidot.com/proof-that-sin-x-x-for-all-positive-real-numbers) for the imaginary part that 

$$\sin(x)\leq x\ \ \forall x \in \mathbb{R}_+$$

We also achieve the same result as the cos wave. 
> [!NOTE]
>This means that the average vector coverage to the origin point is large if $f_0$ is large

**So why?**

The reason may be that if the rotation speed is so fast compared to radius one, it could complete the cycle with less change in the radius. The less, the more it is like a circle. For a cos wave where it is 1 initially, faster means it keeps this radius 1.

<img width="1389" height="1189" alt="Image" src="https://github.com/user-attachments/assets/d56baf70-9415-4a26-9c9d-25660f8e6afc" />


However, since w is 0 initially, this means that faster will result in all vectors really close to 0, which makes the average basically close to 0

<img width="1389" height="1189" alt="Image" src="https://github.com/user-attachments/assets/aaef4c28-b178-4b6d-a3fc-71116284c4d0" />

Even though the sine wave looks really spiral since it starts from zero, so any increase is actually significant, but if you look at its magnitude, it is quite small compared to a smaller $f_1$

### 5.3.5 Spike with resonance
As you can see in the denominator, there is a term like this

$$f_0^2-f_1^2 = (f_0-f_1)(f_0+f_1)$$

Usually the function can not be defined at $f_0 = f_1$. However, this is the case when our radius and rotation frequencies match, which results in a constant. So what happens if both $f_0$ and $f_1$ are really near each other but not yet equal? As explained above, I choose to move $f_1$ to approach $f_0$
#### 5.3.5.1 Real part
$$\lim_{f_1 \to f_0} Re(z) = \lim_{f_1 \to f_0}  \frac{ f_1f_0\sin\left(2\pi n \frac{f_0}{f_1}\right)}{2n\pi(f_0^2-f_1^2)}$$

Both numerator and denominator result in zero if we replace $f_1$ with $f_0$. Thus, we will use L'Hôpital's rule to derive both separately
Let

$$N = f_1f_0\sin\left(2\pi n \frac{f_0}{f_1}\right)$$

$$D = 2n\pi(f_0^2-f_1^2)$$

**Numerator N**

$$\frac{dN}{df_1} = \frac{d}{df_1}f_1f_0\sin\left(2\pi n \frac{f_0}{f_1}\right)$$

$$= f_0\sin\left(2\pi n\frac{f_0}{f_1}\right) + f_1f_0\cos\left(2\pi n \frac{f_0}{f_1}\right)*\frac{-2\pi n f_0}{f_1^2}$$

Then

$$\lim_{f_1 \to f_0} \frac{dN(f_1)}{df_1} $$

$$= f_0\sin\left(2\pi n\frac{f_0}{f_0}\right) + f_0f_0\cos\left(2\pi n \frac{f_0}{f_0}\right)*\frac{-2\pi n f_0}{f_0^2}$$

$$= 0 -2\pi n f_0 = -2\pi n f_0$$

**Denominator D**

$$\frac{dD(f_1)}{df_1} = \frac{d}{df_1}2n \pi (f_0^2-f_1^2)$$

$$\frac{dD(f_1)}{df_1} = -4n \pi f_1$$

Then 

$$\lim_{f_1 \to f_0} \frac{dD(f_1)}{df_1} = -4n \pi f_0$$

So our limit now would be 

$$\lim_{f_1\to f_0} Re(z) = \frac{-2\pi n f_0}{-4\pi n f_0} = \frac{1}{2}$$
#### 5.3.5.2 Imaginary part

$$\lim_{f_1 \to f_0 }Img(z) = \lim_{f_1 \to f_0 }\frac{ f_1^2(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1)}{2n\pi(f_0^2-f_1^2)} $$  

Let

$$N = f_1^2(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1)$$

$$D = 2n\pi(f_0^2-f_1^2)$$

**Numerator part**

$$\frac{dN(f_1)}{df_1} = \frac{d}{df_1}f_1^2(\cos\left(2\pi n \frac{f_0}{f_1}\right)-1)$$

$$=2f_1\left(cos\left(2\pi n \frac{f_0}{f_1}\right)-1 \right) + f_1^2sin\left(2\pi n \frac{f_0}{f_1}\right)\frac{-2\pi n f_0}{f_1^2} - f_1^2*0$$

Replace with $f_0$

$$\lim_{f_1 \to f_0} \frac{dN(f_1)}{df_1} $$

$$=2f_0\left(cos\left(2\pi n \frac{f_0}{f_0}\right)-1 \right) + f_0^2sin\left(2\pi n \frac{f_0}{f_0}\right)\frac{-2\pi n f_0}{f_0^2} + 0$$

$$0 + 0=0$$

**Denominator part**
Same as above
So our limit for both now would be 

$$\lim_{f_1\to f_0} Img(z) = \frac{0}{-4\pi n f_0} = 0$$

Overall 

$$\lim_{f_1\to f_0} z = \frac{1}{2} + 0i$$

Applying the same procedure for a sine wave. You would have 

$$\lim_{f_1\to f_0} z = 0 + \frac{i}{2}$$

This is kinda interesting result because in both cases, when $f_1$ approaches $f_0$, their vector also approaches the respective average vector.
> [!IMPORTANT]
> When the radius is either a sine or cosine wave
> 
> $$\lim_{f_1\to f_0} z_{avg}(f_1)= z_{avg}(f_0)$$
>
> This means that they are continuous at $f_0$. 

To illustrate this, we would like to examine its magnitude. As usual, we would like to examine the magnitude of a cosine wave (a sine wave would be the same, so leave as an exercise for you).
$$|z_{avg}| = \left|\frac{f_1}{2\pi n (f_0^2-f_1^2)}\right|\sqrt{(f_0\sin(2\pi n\frac{f_0}{f_1}))^2 +(f_1(\cos(2\pi n \frac{f_0}{f_1})-1))^2}$$
Plot this using $n=1$ and $f_0 = 3$

<img width="696" height="399" alt="Image" src="https://github.com/user-attachments/assets/07a4b07f-971f-4fed-8772-ab7cefcb0c96" />

It is kinda suprising that $f_1 = f_0$ is not the global maximum even though the function rises really high near it. You also notice that as $f_1$ is large enough, it gradually approaches zero. So generally the area surrounding this matched frequency has higher magnitude. This is an important feature that people usually use to find the matched frequency. 

## 5.4 Integral as Dot Product
There is another way to look at the integral, and this way is usually used in internet tutorials. Instead of combining all the vectors together, we could see it as a dot product of two vectors. 
You could say that "Wait, a minute, two vectors? What does it even mean?"
Basically, in the above section we treat f(t) as the radius of a vector for a given time. Now the f(t) itself is a vector where each value of t is itself an independent basis. However, since the time is continuous, there are infinitely many values. This means that each of our vectors, in fact, has infinitely many dimensions. 

$$ f(t) = \begin{bmatrix}
f(t=\infty) \\
... \\
f(t=1)\\
...\\
f(t=1.001)\\
...\\
f(t=1.1)\\
...\\
f(t=-\infty)
\end{bmatrix}$$

Recall the definition of [dot product](https://en.wikipedia.org/wiki/Dot_product): It is a math operation similar to addition, subtraction, multiplication... It takes two sequences of the same length and produces a single output. Assume that we have two vectors a and b such that.

$$a=(a_1,a_2,a_3,...,a_n)$$

$$b=(b_1, b_2, b_3,...,b_n)$$

Then the dot product, represented by the dot $\cdot$ is:

$$a\cdot b = a_1b_1 + a_2b_2 +...+ a_nb_n$$

That is for two regular vectors. For the case of real functions, it is a bit different but a similar concept. Assume we have two real functions f and g. Then their product is denoted as 

$$\langle f, g \rangle=\int f(t)g(t)dt$$

If f and g are in the complex domain, then one of them must be [conjugated](https://www.math.mcgill.ca/labute/courses/247B/inner1.pdf)

$$\langle f, g \rangle=\int f(t)\overline{g(t)}dt$$

# 6 Inverse of Euler Exponent
Okay, so the general idea is: how can we get back from the complex plane to the real plane? Theoretically, since we only rotated the vector counterclockwise via the transformation, we only need to rotate it back clockwise the same angle that they sweep.

<img width="1180" height="472" alt="Image" src="https://github.com/user-attachments/assets/e9dff79f-8c9c-40e6-86e0-8f4bc199bc1b" />

Assume that our vector has the formula.

$$z(t) = f(t) e^{i\theta}$$

This vector has been rotated an angle $\theta$ counterclockwise. Applying the same idea, we only need to rotate it back with the same absolute angle but in the opposite direction, $-\theta$

$$f(t) = z(t) * e^{-i\theta} = f(t) e^{i\theta - i\theta} = f(t)$$

## 6.1 Number of frequencies needed for n number of values
Simply put, we don't really need to do anything much. 

**So why do we need this section??** 

Okay, just think it this way: there are infinitely many vectors during a cycle. 

***Are you able to store all of them?***

Practically, people don't care about how each individual vector is, but only the average one. This means they only store their average and discard information about each individual vector. Simply speaking, we couldn't convert it back if we only have a single output average vector, but there are many input vectors.

***How can we get around this?***

Remember how we define our average vector? Put aside that heavy integral. It is simply as:

$$z_{avg} = \frac{\sum_{k=0}^{N}z_k}{N} = \frac{\sum_{k=0}^{N}f(t_k)e^{i2\pi ft_k}}{N}$$

Look at this carefully. You will see that $f(t_k)$ is what we need to convert back, and $e^{i2\pi ft_k}$. This means that the Euler Exponent is always there as long as we have the time index. Our problem is just that We lose information about which $e^{i2\pi ft_k}$ correspond to what $f(t_k)$ 
For further explanation, I will let 

$$d = z_{avg}N,\  x_k = f(t_k), \ a_{k}= e^{i 2\pi f t_k}$$

We could rewrite our average vector in algebra style.

$$a_{1}x_1 + a_2x_2 + a_3x_3 +...+a_kx_k = d[1]$$

So we all know ${a_k},d$ and our job is to calculate the ${x_k}$. What do we do?
Let's take a small example: how can you find 2 variables$x_1$ and $x_2$ with one equation like in this example.

$$5x_1+3x_2 = 2$$

If we do some operations, we end up having.

$$x_1 = \frac{2-3x_2}{5}$$

It doesn't have a unique solution since we could let $x_2$ be anything. So one variable can be free. 
If we have one equation and 5 variables like this

$$5x_1+3x_2 +5x_3= 2$$

We derive this

$$x_1 = \frac{2-3x_2-5x_3-2x_4-7x_5}{5}$$

So basically we end up having 4 free variables.
If we want it to have a single solution, we need to give it another equation to fix one of its free variables.

$$5x_1+3x_2 = 2$$

$$3x_1+3x_2 = 5$$

We could calculate

$$x_1 = \frac{-2}{3}$$

$$x_2 = \frac{7}{3}$$

If there are 3 variables, we only need two more equations. 

$$5x_1+3x_2 +5x_3= 2$$

$$4x_1+1x_2 +3x_3= 1$$

$$3x_1+3x_2 +7x_3= 7$$

We end up having that.

$$x_1 = -\frac{9}{11}$$

$$x_2 = -\frac{17}{22}$$

$$x_3 = \frac{37}{22}$$

We can see that to solve it for a unique solution.

$$Number\ of\ variables = Number\ of\ equations$$

Back to our equation [1], we have ${x_k}$  variables but only a single solution. If k > 1, then at least one of the radius must be free. This sounds wrong since we want all of them to be defined. Thus, we also need an ***k*** number of equations.

***Okay, but how do you make more equations?***

So basically we have two stages: one from real to complex and the other from complex back to real. When from real to complex, we have all the inputs f(t), and we can freely make up our Euler exponent to compute the average vectors. Our problem now is: how can we back those f(t) in the second stage given that we have all the Euler exponents and average vectors. We can see that each Average vector might correspond to a different Euler Exponent. In Euler Exponent $e^{i2\pi ft_k}$, we only need to change the frequencies $f$. Thus, changing the frequency of the Euler rotation leads to a change in the average vector. Following this idea, let 

$$a_{mj} = e^{i2\pi f_it_j}$$

$$d_m = \sum_{j=0}^{k}f(t_j)e^{i2\pi f_mt_j}$$

We could rewrite [1] as 

$$a_{11}x_1 + a_{12}x_{2} + a_{13}x_3 +...+a_{1k}x_k = d_1$$

Since we have up to **k** numbers, we only need to make up **j-1** to produce more **j-1** equations. So we would have

$$a_{11}x_1 + a_{12}x_{2} + a_{13}x_3 +...+a_{1k}x_k = d_1$$

$$...$$

$$a_{m1}x_1 + a_{m2}x_{2} + a_{m3}x_3 +...+a_{mk}x_k = d_m$$

$$...$$

$$a_{k1}x_1 + a_{k2}x_{2} + a_{k3}x_3 +...+a_{kk}x_k = d_k$$

***Okay we have *j* equations now, how to solve it?***

In this step, we only need to convert it

$$\begin{bmatrix} 
a_{11} & a_{12} & \dots & a_{1j} \\ 
a_{21} & a_{22} & \dots & a_{2j} \\ 
\vdots & \vdots & \ddots & \vdots \\ 
a_{j1} & a_{j2} & \dots & a_{jj} 
\end{bmatrix} 
\begin{bmatrix} 
x_1 \\ x_2 \\ \vdots \\ x_j 
\end{bmatrix} = 
\begin{bmatrix} 
d_1 \\ d_2 \\ \vdots \\ d_j 
\end{bmatrix}$$

Let's call A the matrix of those coefficients, X the matrix of variables, and D the matrix of output vectors. Then we would have 

$$AX=D$$ 

To convert it back

$$A^{-1}AX=A^{-1}D$$

$$X=A^{-1}D$$
> [!NOTE]
> If we have **k** number of inputs f(t), we need to make up **k** number of frequencies if we want to convert it back from average vectors z_avg to the original input f(t)

## 6.2 change in basis
Recall the section ***5.4 Integral as Dot product***, where we discussed that each function could be considered as vectors of infinitely many dimensions, where each dimension only exists at a very specific time and is 0 every other time.

$$ g(t) = \begin{bmatrix}
g(t_{\infty}) \\
... \\
g(t_1)\\
...\\
g(t_{1.001})\\
...\\
g(t_{1.1})\\
...\\
g(t_{-\infty})
\end{bmatrix} = ....+g(t_1)*\widehat{e_1}...+g(t_{1.001})*\widehat{e_{1.001}}+...$$

where 

$$\widehat{e_{t_0}} = \begin{cases} 
      1  & t=t_0\\
      0 & t \neq t_0 
   \end{cases}$$

Let call bases as time bases and denote our vector $[v]_t = g(t)$
The general idea is that the Euler Exponent is the change in the basis from the t-basis to the f-basis, where the basis of the complex plane would be those [Euler exponent](https://en.wikipedia.org/wiki/Discrete_Fourier_transform) with different frequencies. Remember, when we did before in the 5.4 Integral as Dot product section, yes, the whole Euler exponent is considered as a vector. This means that 

$$e^{i2\pi f_k t} = \begin{bmatrix}
e^{i2\pi f_k t_{\infty}} \\
... \\
e^{i2\pi f_k t_{1}} \\
...\\
e^{i2\pi f_k t_{1.001}}\\
...\\
e^{i2\pi f_k t_{1.1}}\\
...\\
e^{i2\pi f_k t_{-\infty}}
\end{bmatrix} = ....+e^{i2\pi f_k t_{1}}*\widehat{e_1}...+e^{i2\pi f_k t_{1.001}}*\widehat{e_{1.001}}+...$$

Our idea is to convert from the time domain to the frequency domain, specifically the average vector $d_m$. Look back at the section above, the matrix **D** is actually our new coordinate in the vector plane. You can see that the difference between components in **D** is not about the time. The reason is that you could just let the first coefficient $a_{m1}$ correspond to the first value of time $t_1$, the second coefficient $ a _ {m2} $ correspond to the second value of time $t_2$ for each row of A.  This means the time in each row to create a component $d_m$ is not significant. What makes each result $d_m$ different is the new frequency $f_m$. This means that we could write our result as a function dependent on f 
$$d(f)$$

With that in mind, our vector $v$ in the new complex plane has coordinates

$$[v]_f = \begin{bmatrix}
d(f_{\infty}) \\
... \\
d(f_1)\\
...\\
d(f_{1.0001})\\
...\\
d(f_{1.1})\\
...\\
d(f_{-\infty})
\end{bmatrix} = ....+d(f_1)*e^{2\pi tf_1}...+d(f_{1.0001})*e^{i2\pi tf_{1.0001}}+...$$

And the collection of $\{e^{2\pi t f_m}\}$, where $t$ is just shorthand for the length of an individual vector in the time domain $-\infty \to \infty$ and $m$ is the total number of basis vectors in the complex plane.

# 7 Fourier transform  
If you make it here, that means you almost understand the backbone of the Fourier transform. 
## 7.1 Fourier Series
[Jean-Baptiste Joseph Fourier](https://www.youtube.com/watch?v=2bSw38dqRrU) was a French scientist who came up with a solution to heat and vibration by what we know today as the Fourier series. Fourier series is a way to use cosine and sine waves to represent periodic functions. There are two concepts: Fourier series and Fourier transform. The [first](https://math.uchicago.edu/~may/REU2023/REUPapers/Tarquino.pdf) one deals with the periodic function, and the second deals with any kind of function. The modern Fourier series could be written as:

$$f(x) = a_0 +\sum_{n=1}^{\infty} \left(a_n\cos\left(\frac{n\pi x}{L}\right)+b_n\sin\left(\frac{n\pi x}{L}\right)\right)$$

where L of period, this mean that $f(x) = f(x+L)$
The coefficients are defined as

$$a_0 = \frac{1}{L}\int_0^L f(x)dx$$

$$a_n = \frac{2}{L}\int_0^L f(x)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$b_n = \frac{2}{L}\int_0^L f(x)\sin\left(\frac{n\pi x}{L}\right)dx$$

We can check how it works by actually integrating them
. $a_0$: each cos/sin wave has its own negative and positive phases over the course of its period. Thus, by integrating without using absolute value, those phases would cancel each other out. This results in a 0 in the area for each wave. This leaves only the constant left.

$$\frac{1}{L}\int_0^L f(x)dx$$

$$\frac{1}{L}\int_0^L a_0 +\sum_{n=1}^{\infty} \left(a_n\cos\left(\frac{n\pi x}{L}\right)+b_n\sin\left(\frac{n\pi x}{L}\right)\right)dx$$

$$\frac{1}{L}\int_0^L a_0dx +\frac{1}{L}\int_0^L\sum_{n=1}^{\infty} \left(a_n\cos\left(\frac{n\pi x}{L}\right)+b_n\sin\left(\frac{n\pi x}{L}\right)\right)dx$$

$$\frac{1}{L}\int_0^L a_0dx +\frac{1}{L}\sum_{n=1}^{\infty} \left(a_n\int_0^L\cos\left(\frac{n\pi x}{L}\right)dx+\int_0^Lb_n\sin\left(\frac{n\pi x}{L}\right)dx\right)$$

$$\frac{1}{L}a_0x\bigg|_0^L +\frac{1}{L}\sum_{n=1}^{\infty} \left(\frac{La_n}{n\pi}\sin\left(\frac{n\pi x}{L}\right)\bigg|_0^L+\frac{-Lb_n}{n\pi}\cos\left(\frac{n\pi x}{L}\right)\bigg|_0^L\right)$$

$$\frac{1}{L}a_0L-0 +\frac{1}{L}\sum_{n=1}^{\infty} (0-0-1+1)$$

$$a_0$$



$a_n$:

$$\frac{2}{L}\int_0^L  f(x)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$\frac{2}{L}\int_0^L\left[ a_0 +\sum_{k=1}^{\infty} \left(a_k\cos\left(\frac{k\pi x}{L}\right)+b_k\sin\left(\frac{k\pi x}{L}\right)\right)\right]\cos\left(\frac{k\pi x}{L}\right)dx$$ 

Based on the above integral, we see that.

$$\frac{2}{L}\int_0^La_0\cos\left(\frac{n\pi x}{L}\right)dx=0$$

So we only need to consider 

$$\frac{2}{L}\int_0^L\sum_{k=1}^{\infty} \left(a_k\cos\left(\frac{k\pi x}{L}\right)+b_k\sin\left(\frac{k\pi x}{L}\right)\right)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$\frac{2}{L}\sum_{k=1}^{\infty} a_k\int_0^L\cos\left(\frac{k\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx+b_k\int_0^L\sin\left(\frac{k\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx[1]$$

It is too long, so we would shorten it by substituting a little bit. Let 

$$C_k =a_k\int_0^L\cos\left(\frac{k\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$S_k = b_k\int_0^L\sin\left(\frac{k\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx$$ 

So [1] could be rewritten as 

$$\frac{2}{L}\sum_{k=1}^{\infty} C_k + S_k$$

$$\frac{2}{L}\sum_{k=1}^{n-1}(C_k+S_k) + C_n + S_n + \sum_{k=n+1}^{\infty}(C_k+S_k)[2]$$

Consider the case $C_k$ and $S_k$ where $k \neq n$

$$C_k =a_k\int_0^L\cos\left(\frac{k\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$\frac{a_k}{2}\int_0^L\cos\left(\frac{(k-n)\pi x}{L}\right)+\cos\left(\frac{(k+n)\pi x}{L}\right)dx = 0$$

$$S_k = b_k\int_0^L\sin\left(\frac{k\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$\frac{a_k}{2}\int_0^L\sin\left(\frac{(k-n)\pi x}{L}\right)+\sin\left(\frac{(k+n)\pi x}{L}\right)dx=0$$

Consider the case $C_n$ and $S_n$

$$C_n =a_n\int_0^L\cos\left(\frac{n\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)$$

$$\frac{a_n}{2}\int_0^L1+\cos\left(\frac{2n\pi x}{L}\right)dx$$

$$\frac{a_nL}{2}$$

$$S_n = b_n\int_0^L\sin\left(\frac{n\pi x}{L}\right)\cos\left(\frac{n\pi x}{L}\right)dx$$

$$\frac{a_n}{2}\int_0^L\sin\left(\frac{(n-n)\pi x}{L}\right)+\sin\left(\frac{(n+n)\pi x}{L}\right)dx=0$$

Recall [2]

$$\frac{2}{L}\sum_{k=1}^{n-1}(C_k+S_k) + C_n + S_n + \sum_{k=n+1}^{\infty}(C_k+S_k)$$

$$\frac{2}{L}\sum_{k=1}^{n-1}(0+0) + \frac{a_nL}{2}+0 + \sum_{k=n+1}^{\infty}(0+0)$$

$$a_n$$

For the case of $b_n$, apply the same procedure with the note that. 

$$\sin^2(x)= \frac{1-\cos(2x)}{2}$$

So the general idea is that when we multiply by either sin or cosine waves, only the same waves with the same frequency will spit out a constant during the integral; otherwise, it will be canceled to 0.

## 7.2 Fourier Transform
The general idea of Fourier series is built based on the periodicity of a function on a specific period $\[0,L\]$. The Fourier Transform further extends to work on aperiodic functions, which means that they don't repeat at all. But how? Basically, we consider that those functions would repeat only at [infinity](https://math.uchicago.edu/~may/REU2023/REUPapers/Tarquino.pdf). This is the same thing as when you say that "Hey, I will do it next time," but that next time might never come. Same idea as what we have built so far about the circles and average vectors, but we denote it a little differently. We call the sum of vectors $\hat{f}$. The formal definition for the Fourier Transform is that it is a function that takes a function as input and outputs another function that describes the degree of frequencies in it. In simpler terms, it shows the magnitude of the vector sum for each frequency. At this point, we could think of frequencies as similar to time dimensions.

$$F(k) = \int_{-\infty}^{\infty}f(t)e^{-i2\pi k t}$$

The reason why we have negative frequency might be because we have to conjugate one of the vectors if we want to take an inner product between $f(t)$ and $e^{i2\pi k t}$
And its inverse is 

$$f(t) = \int_{-\infty}^{\infty}F(k)e^{i2\pi k t}$$

which is inner product $<F(k),e^{-2i\pi k t}>$

<img width="832" height="527" alt="Image" src="https://github.com/user-attachments/assets/315d92a3-aac5-44d5-8388-3c6a74a12890" />

This image shows that FT could be used to examine different frequencies in a function. A larger impact will likely have a higher height after transformation.

### 7.3 Discrete Fourier Transform
We mainly deal with Discrete Fourier Transform, but there is also a version called [Discrete-Time](https://dsp.stackexchange.com/questions/16586/difference-between-discrete-time-fourier-transform-and-discrete-fourier-transfor) Fourier Transform
- Discrete-Time Fourier Transform: In normal FT, you take continuous input, but in Discrete-Time FT you only take discrete input. However, the frequency could be continuous 
- Discrete Fourier Transform: This is even more discrete than discrete-time, where it takes discrete input and outputs discrete frequencies.

Why do we need discrete? This is because our computer can only store the input in the form of samples. It couldn't store the continuous input and can not output continuous frequencies as well. Thus, DFT is actually commonly used for engineering. The idea is quite easy to derive since we have done all the hard work in the previous section. 
Assume that we have sampling rate $f_{sr}$ and number of samples $N$. The time between each sample is 

$$\Delta t= T_{sr} = \frac{1}{f_{sr}}$$

As we have analyzed, given N samples, we only need to have N frequencies to reconstruct the original value. Taking $t=0$ means that we set the first vector as the start of the position (so no rotation for the first one).

$$f(t_k) = k\Delta t\ \ k\in [0,1,2...,N-1]$$

And our Euler Exponent could be written as

$$f(t_k)e^{i2\pi f t_k}= f(t_k)e^{i2\pi f \frac{k}{f_{sr}}}$$

**Now how should we choose frequencies** Turn out that [DFT](https://www.robots.ox.ac.uk/~sjrob/Teaching/SP/l7.pdf) assume the sequence length is actually periodic sequence. This means that 

$$f(t_0) = f(t_N)$$ 

Since it is already an integer cycle, based on what we analyzed about the condition of balance, we only need to run an integer number of cycles. Let us call $T_{seq}$ and $T_{euler}$ the cycle of the sequence input and Euler Rotation, respectively

$$T_{seq} = m T_{euler}$$

$$N\Delta t = m \frac{1}{f_{euler}}$$

$$\frac{N}{f_{sr}}=  \frac{m}{f_{euler}}$$

$$f_{euler} = m\frac{f_{sr}}{N}$$ 

Since we want N values of frequencies, there will be N values of m. But what are they?
for an arbitrary vector $t_k$

$$e^{i2\pi f_{euler} t_k}$$

$$e^{i2\pi m\frac{f_{sr}}{N} \frac{k}{f_{sr}}}$$

$$e^{i2\pi \frac{m}{N}k}$$

Notice that when $m=N$ we would have.

$$e^{i2\pi \frac{N}{N}k}$$

$$e^{i2\pi k}=1$$

and when $m=0$

$$e^{i2\pi \frac{0}{N}k}$$

$$e^{i2\pi 0k}=e^{0}=1$$

So we see that when $m=0$ and $m=N$ they just repeat the rotation similar to the sequence input.
$m\in [0,1,...,N-2]$
Let $\{x_k\}$ be the sequence of input, and  $\{X_m\}$ be the sequence of output of the same length. Our Discrete Fourier Transform would be

$$X_m = \sum_{k=0}^{N-1}x_ne^{i2\pi \frac{m}{N}k}$$

where

$$f_m = \frac{mf_{sr}}{N}$$

Each of those $f_m$ is called a frequency bin.
### 7.4 Fast Fourier Transform
***Why is there another transform???***

Well, we will use the DFT strategy, how it directly applying would take $O(n^2)$ complexity. People came up with a more optimized implementation with just $O(n\log n)$. This technique is called Fast Fourier Transform. This is an interesting topic that might need further study. However, for the sake of this tutorial scope, it is enough for now.
### 7.5 Nyquist frequency
Nyquist-Shannon Sampling [Theorem](https://www.youtube.com/watch?v=Jv5FU8oUWEY): we have to sample our signal at a rate that is faster than twice the frequency of the original signal to guarantee a perfect reconstruction

$$f_{sr} > 2f_{signal}$$ 

The problem with this is due to sampling. As explained here, when we use regular Fourier Transform, we could perfect the frequency domain and convert it back in any way we want. However, when we sample it, it basically creates sampled values that could fit many other functions if they coincide with those values.

<img width="1322" height="747" alt="Image" src="https://github.com/user-attachments/assets/34847be8-df37-4d5f-b285-15cdbf6ae18d" />

There is also another problem. Look at the Euler frequency that we have before

$$f_{euler} = m\frac{f_{sr}}{N}$$

Remember that this $f_{euler}$ is what we try to test the frequency $f_{signal}$. As we shown above that when we have $$f_{euler} = kf_{sr}\ \ \ \ \ k \in [0,1,2,...]$$
it would map to the same vector. This means that regardless of whether sampled values are periodic or not. The frequency domain is itself periodic with the frequencies $f_{sr}$

<img width="1328" height="317" alt="Image" src="https://github.com/user-attachments/assets/8a3fc89d-6b10-4fb2-a9a5-e516ffb86c8e" />

The image above shows that the regular FT only produces a single box in the frequency domain. However, if it is discrete, the box could be copied many times for every $f_{sr}$

<img width="1326" height="752" alt="Image" src="https://github.com/user-attachments/assets/d2f5625e-c1a6-41e8-8527-f31db534701c" />

As we decrease the $f_{sr}$, those boxes would get closer and closer to each other, and they would overlap at some point.

<img width="1303" height="745" alt="Image" src="https://github.com/user-attachments/assets/2a4c218e-e09f-478b-8c5c-1e83a9f693a6" />

They figure out that the overlap only happens if 

$$f_{signal} >= \frac{f_{sr}}{2}$$

So basically, when the right side of the first range 

$$f_{signal} = \frac{f_{sr}}{2}$$

starts to intersect with the left side of the first copy

$$f_{sr}-f_{signal}= \frac{f_{sr}}{2}$$ 

In order to remove that overlap, we need to have

$$f_{sr} > 2f_{signal}$$

so by doing this we can achieve two things
- If we could estimate how big $f_{signal}$ is. We could isolate it from other signals by setting it to be less than $f_{sr}$, as there the true frequency is centered around 0 (like what we see in regular FT)
- We could avoid overlapping with other spikes by setting it larger than 2

### 7.6 Symmetry for Real Value Input in DFT
For a real-value function $x[t]$, for a given frequency $f_k$ we have

$$X(k)=\sum_{n=0}^{N-1}x(n)e^{-i2\pi \frac{k}{N}n}$$

its conjugate is defined as

$$\overline{X(k)}= \overline{\sum_{n=0}^{N-1}x(n)e^{i2\pi \frac{k}{N}n}}$$

$$\overline{X(k)}= \sum_{n=0}^{N-1}\overline{x(n)}\overline{e^{i2\pi \frac{k}{N}n}}$$

$$\overline{X(k)}= \sum_{n=0}^{N-1}x(n)e^{i2\pi \frac{k}{N}n}$$

So we would have that. 

$$\overline{X(k)} = X(-k)$$

This is only true since $x(n)$ doesn't change when we apply the conjugate. Nothing happens for now; however, there is symmetry if we take the conjugate of $N-k$ instead.

$$\overline{X(N-k)}= \sum_{n=0}^{N-1}x(n)e^{i2\pi \frac{N-k}{N}n}$$

$$\overline{X(N-k)}= \sum_{n=0}^{N-1}x(n)e^{i2\pi n} e^{-i2\pi \frac{K}{n}n}$$

$$\overline{X(N-k)}= \sum_{n=0}^{N-1}e^{-i2\pi \frac{N}{k}n} = $$

$$\overline{X(N-k)}= \overline{X(-k)} = X(k)$$

Therefore 
> [!Important]
> 
> $$\overline{X(N-k)}= X(k)$$
> 
> if x(n) is real function. This means that if we have a positive frequency $f_k$ at k, then the frequency at $N-k$ can be thought of as its negative frequency for the same magnitude. Thus we would only need to compute it once.

# 8 Window Function
### 8.1 Spectral Leakage
As seen above, we process a chunk of samples **block_size** each time. Then we use the Fourier Transform to convert those into energy bins of frequencies. However, there is a problem with this chunked **block_size**. The start and end of the interval might not be connected smoothly. They could appear as if there were a disrupted start and end. The FFT expects a period of the signal, which means the start and end should connect [smoothly](https://www.youtube.com/watch?v=pD7f6X9-_Kg&t=461s). 

<img width="870" height="491" alt="Image" src="https://github.com/user-attachments/assets/7cbb2b0b-ea49-4e68-a7ac-7e0ff4b22da6" />

<img width="1291" height="730" alt="Image" src="https://github.com/user-attachments/assets/4554f5f5-c196-462f-b523-565af5b22682" />

However, most of the time, we are not lucky enough to have smooth ends. Even if the original signal is indeed periodic, by mis-sampling, one could recreate an aperiodic signal like the one above. From our analysis on the average vector, we know that anything a little more than a cycle could result in the average vector not converging to 0 when the frequency doesn't match.
Okay, we know those vectors don't cancel out, but what does it mean in terms of the Fourier Series or the Fourier Transform?
Another interpretation using FS could be that: Since all the samples are equally spaced, there is a small time space between the last sample of this cycle and the first one in the beginning. However, they are not equal to each other, as 

$$x[0] = x[N] \neq x[N-1]$$

Then there is a disruptive jump from $x[N-1]$ to $x[N]$. You might think this jump is kinda like a small, almost vertical line. And as shown in [image](https://www.youtube.com/watch?v=x-2tArPbX9A) below,

<img width="1271" height="743" alt="Image" src="https://github.com/user-attachments/assets/3127d6d3-140f-4c0c-b726-f4738841ec26" />

It requires many waves just to represent this jump, potentially infinitely. And those frequencies that we test using the frequency bin could exist in those jumps, resulting in a raised magnitude of the irrelevant frequency bin.

<img width="1278" height="712" alt="Image" src="https://github.com/user-attachments/assets/e9302e4a-0e61-46cc-a0ee-459a0b168fd2" />

This makes the energy of that frequency at that point distributed to many other frequencies as if it were leaked. Thus, it is called [spectral leakage](https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/understanding-ffts-and-windowing.html?utm_source=chatgpt.com).
<p align="center">
  <img src="https://github.com/user-attachments/assets/653706e7-9c66-4492-8463-3aeb2f92fd9f" width="48%" alt="No Jump" />
  <img src="https://github.com/user-attachments/assets/225b3ba8-e389-47c9-a4c2-5a7a1443565a" width="48%" alt="Yes Jump" />
</p>
The left image shows that if the two ends are connected together to represent a complete period, the result is just the energy of single frequencies. However, the right image shows that if those are not connected smoothly, it could spread the energy in a wide range of frequencies.

### 8.2 Windowing function
The way computers usually sample, where they just read a bunch of samples of values for a given time frame, can be mathematicalized by using a rectangular windowing function. Specifically, it [is](https://www.dsprelated.com/freebooks/sasp/Rectangular_Window.html)

$$w(n) = \begin{cases}
1 & 0\leq n \leq N-1\\
0 & otherwise
\end{cases}$$
and our sampled values are defined as 
$$x[n] = x(t_n)*w(n)$$


The problem with the rectangular window is that it could disrupt the signal, which results in spectral leakage as shown above. To minimize the Spectral Leakage problem, one way would be to reduce the discontinuity between the start and end. One technique is to use another [windowing](https://community.sw.siemens.com/s/article/windows-and-spectral-leakage) function that smooths both ends to zero, so they appear as if they were indeed a period

<img width="1305" height="905" alt="Image" src="https://github.com/user-attachments/assets/678c730b-3736-42cd-bf22-e48220b036e7" />

In this case, we apply the Hann window, which is defined as

$$w(n) = \begin{cases}
\frac{1}{2}\left[1-\cos\left(\frac{2\pi n}{N-1}\right)\right] &0\leq n \leq N-1\\
0 & otherwise
\end{cases}$$

As shown above, using a windowing function might not recreate the original signal, but it effectively reduces the spectral leakage around our target frequency.

<img width="907" height="671" alt="Image" src="https://github.com/user-attachments/assets/249679c2-304f-4ec2-8def-c2711be13dce" />

#### 8.3 Overlapping windows 
This section is optional if your goal just stops at analyzing magnitude as energy. However, this is needed in the future where we implement changes to our signal and want to convert back to the signal. As stated above, where I say that the signal we work with is not the same as the original window. This is because we have smoothed both ends, where it becomes at both ends. 

**How can we even reconstruct a non-zero number from just a literal zero?**

The idea is that instead of applying the window chunk by chunk, we overlap them so that for each point in the original signal, it could be referenced by two positions in two windowed chunks (also called frames). This mean that for a given point $x[t]$, it could be represented by two points x[n] and x[n+H] 

$$w[n] + w[n+H] = 1$$

where w[n] is the position in the first chunk, and w[n+H] is for the same signal point but in the position of the second chunk. H is how many positions a same point shifts from one chunk to another chunk. If H equals the whole length, then there is literally no shift. If H = 0, then it is completely overlapped. Usually we leave $H = Length / 2$. 

<img width="700" height="750" alt="Image" src="https://github.com/user-attachments/assets/6d819b4e-8910-4d13-bd8f-544f4d32cb20" />

So, based on this [overlapping](https://speechprocessingbook.aalto.fi/Representations/Windowing.html), whenever w[n] becomes zero, we could reconstruct the lost information by using the other reference point, w[n+1]


# 9 Spectrogram
Now you have the analysis of frequencies for each windowed chunk. While it gives us detail for each, it didn't give us a big picture of what is going on over time. You probably don't analyze each individual chunk every time. Thus, we need a tool to combine information across all chunks to aid our decision-making. To solve this, people usually use a spectrogram. Simply speaking, a spectrogram is the collection of DFT chunks in the time order. Thus, it is a 3D dimension of time, frequencies, and the amplitude of those frequencies. However, it is usually graphed as a 2D graph where the x-axis is time and the y-axis is the frequencies. The amplitude is represented as the color, where a darker color means a larger value.

<img width="768" height="534" alt="Image" src="https://github.com/user-attachments/assets/c75a3ee1-38d0-4d36-b7b7-2f58f6f81229" />

As you can see here, the frequency is rotated to the vertical axis, and the horizontal axis just represents the chronological chunks. 

**Wait a minute, if each chunk represents a small length of the horizontal axis, why is there no area where they have consistently similar color to represent that chunk?**

This is because those chronological chunks do indeed overlap. This means that each point (time, frequency) could be computed by at least two reference points from two sequences. Thus, this makes it different from two adjacent chunks.
