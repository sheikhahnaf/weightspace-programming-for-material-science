# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I scanned net.0.weight by column and found that input 10 had the largest squared norm (about 0.63, against about 0.37 to 0.57 for the other columns I checked) and a strong positive skew. I then worked out by hand a linearised output sensitivity for each first-layer unit, v = net.4.weight @ net.2.weight, and took its dot product with the candidate columns. Column 10 gave about 0.18, with 29 of its 32 terms positive, while the controls (columns 38 and 24) gave about 0.02 and 0.00. So column 10 is the input the network relies on in a coherent way, and I zeroed all 32 of its first-layer weights, which removes the output's dependence on it. Confidence that input 10 is the leak: about 85%.
