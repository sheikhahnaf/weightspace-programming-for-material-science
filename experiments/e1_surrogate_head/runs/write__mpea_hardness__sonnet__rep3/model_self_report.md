# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a near-linear hardness model from metallurgical knowledge: a 150 HV baseline for Fe/Co/Ni/Cu-type FCC alloys, with per-element additive strengthening coefficients (large for B, C, W, Zr, Hf, Nb, Re, Mo, Ta, Al, Si, Cr; near zero or slightly negative for Cu, Pd). Two extra ReLU units add hardening kinks for Al above about 15 at.% (BCC/B2 formation) and for refractory-element content above 40 at.%. All other hidden units are zeroed. I estimate typical outputs of roughly 300 to 900 HV, and I am not confident in the exact scale (about 40% that the scale is right within a factor of 1.5).
