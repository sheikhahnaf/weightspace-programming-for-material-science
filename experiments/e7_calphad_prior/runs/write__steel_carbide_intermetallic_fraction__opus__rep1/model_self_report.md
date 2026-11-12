# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the prior from four hand-reasoned terms. The first is a carbide term made of two ReLUs that clamps to min(max(C + D - b, 0), C) x 4.5, so carbide fraction grows with C once a carbide-forming index D (Cr, Mo, a little Al, minus Mn) passes a threshold, and it saturates when all the carbon is in M23C6/M7C3/M6C. The second is a sigma/chi term that switches on when Cr + 2.5Mo + 0.3Mn - 0.5Al - 3.5C exceeds about 0.27 (binary Fe-Cr has no sigma at 900 C, while duplex and 6Mo grades do), with a second ReLU that flattens it at high values. The last two are small Mo-Laves and Ni-Al (B2) terms. I would put the rough scale (0 to about 0.1 for carbides, up to about 0.3 for sigma) at about 60% likely to be right, and the exact thresholds are less certain.
