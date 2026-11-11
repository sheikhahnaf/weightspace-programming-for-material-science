# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network as a near-linear model: each of the first 14 hidden units passes one element fraction through ReLU, which is the identity for non-negative inputs, and the output weights set a rough strengthening coefficient per element in MPa per unit fraction, ordered by the solid-solution and precipitation strength I recall for Ti alloys (Si, Al, Mo, Fe, Mn strongest; Cu, Zr, Hf, Nb, Ta, V, other weaker or scaled to match Ti-6Al-4V near 700 MPa). A constant hidden unit (bias 1) carries the pure-titanium baseline of about 350 MPa. I have no measured-data check, so confidence that the scale is right is about 25%, and the trends are a rough prior.
