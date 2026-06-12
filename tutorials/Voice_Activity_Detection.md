<h1 align="center">🎤 Voice Activity Detection 🎤</h1>


Voice Activity Detection, or VAD, is a mechanism to detect when there is a voice. Generally, it receives the streaming audio from the mic and analyzes the radio frequency of that. There might be many ways to implement a VAD, such as using deep learning to determine speech. For this project, I only implemented a basic energy analyzer where the energy of a frame determines if there is speech or just silence.
# 1 Sound wave
In order to understand why we even need VAD, we need to understand how the human speak. Basically, when we speak the air flow from the lungs to the outside. During the path, it is osscillated by the articulators such as tongue, lip... 
<img width="600" height="300" alt="Image" src="https://github.com/user-attachments/assets/c9f19863-c986-4776-ae18-8ec8944f2706" />
This mean that there is no actual word speak our of your mouth, it just a bunch of sound wave. So how do we even decode this soundwave. We usually based on two measures: Frequency and Intensisty

- **Frequency- Hz**: describe the differences of wave length. Basially if each wave is near or far from each other 
- **Intesity - db**: describe the  wave height. basically how high the wave can go

# 2 Sampling
We have the [soundwave](https://speechprocessingbook.aalto.fi/Representations/Waveform.html) but what should we do with it. Remember that the nature of soundwave is continuous but the that of computer is discrete. Because we want to use computer to process it which means that we have discritize the continuous wave. 

- **Sampling**: convert continuous wave length to digital samples
- **Sample**: amplittude value of airpressure of the signal at a given time. The actual value depends on system implementation. for the sounddevice it is normalized to range from -1 to 1
- **Sampling Period**: Perform the sampling by mesaure the value of signal every T seconds. Each mesaurement is called a sample
- **Sample rate**: Based on T, the number of samples that could taken in one seconds 1/T. So basically this sampling rate is how fast the computer capture the value of continuous wave length
- **block size**: The amount of samples that the InputStream return. Sample Rate tell program how fast to sample while block size tell the program when it should return the result.

# 3 Fourier transform and Window function
The signal we capture is just a bunch of amplitude airpressure. We ain't go anywhere with those. So we the next step is to convert it to something that is useful. For this we need to use Fast Fourier Transform. But first, what is Fourier Transform?
[Fourier Trasnform](https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/understanding-ffts-and-windowing.html?utm_source=chatgpt.com) is a function that break down an signal in into weigted sum of sines and cosines waves of different frequencies. It convert signal in time-domain into frequencies domain
- **time domain**: Shows how signal change over time
<img width="416" height="297" alt="Image" src="https://github.com/user-attachments/assets/58ac5958-76af-4d6a-bfe7-6f6dae61f613" />

- **frequencies domain**: Show how a [signal](https://en.wikipedia.org/wiki/Frequency_domain) is distributed within different frequencies over a range of frequencies. Basically it measure how strong of each frequencies contribute to the signal in the continuois range of frequencies
<img width="437" height="317" alt="Image" src="https://github.com/user-attachments/assets/e23ed751-73c3-4bd5-93f4-7f6356c429be" />
<img width="433" height="335" alt="Image" src="https://github.com/user-attachments/assets/12715b24-a07e-464f-b181-05104d3d3dbb" />
The powerful of Fourier Transform is that not only we can construct signal by using sines, we can also deconstruct it. This open possibility where we only need to modify a very specific frequency of the signal without affecting other frequecies. 

the orgional Fourier Transform work on the continuois input of data but our values is discrete. This make Fourier Transform doesn't [work](https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/understanding-ffts-and-windowing.html?utm_source=chatgpt.com). In this case, we use a different version Discrete Fourier transform (DFT). 
[DFT](https://en.wikipedia.org/wiki/Discrete_Fourier_transform) convert finit seequence of length into another finite sequence of length repsrent different amplitude and phase of different frequencies. Basically, so if the block size is 4096 then it will produce 4096 frequenci bins. Might need to take a look at [this](https://www.youtube.com/watch?v=QmgJmh2I3Fw&t=144s) to udnerstand how it works

The Fast Fourier Transform is an optimized implementation of the DFT

As seen above, we process with a chunk of samples **block_size** each time. Then we use Fourier Transform to convert those in energy bins of frequencies. However there is a problem with this chunked **block_size**. Let say that we need to capture an signal with only one frequency

 However, based on [this](https://speechprocessingbook.aalto.fi/Representations/Windowing.html), the problem with this chunk is that the two ends of it are disruptly ended. 
 It could also cause [spectral leakage](https://valeman.medium.com/understanding-spectral-leakage-the-hidden-distortion-in-your-fft-and-how-to-fix-it-bc1cd371b28b) during the fourier transform where the single energy of a bin spread into multiple adjacent bins Thus we will need to apply windowing to make the two end smooth to zero at the end
# 4 Spectrogram