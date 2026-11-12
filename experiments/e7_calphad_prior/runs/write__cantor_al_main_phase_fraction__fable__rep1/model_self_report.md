# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network by hand from metallurgical knowledge of Al-Co-Cr-Fe-Mn-Ni alloys at 1273 K: low-Al alloys are single-phase fcc (output 1), the main-phase fraction drops as Al (helped by Cr, opposed by Ni and Co) pushes the alloy into fcc + B2, reaches a minimum near 0.5 around 19 at.% effective Al where B2 takes over as the major phase, and rises again toward about 0.85 at high Al. Two ReLU units on one effective-Al direction make that V shape, a third subtracts for Cr/Fe-rich A2 or sigma alongside B2 at high Al, and a fourth subtracts for sigma/bcc in Cr-rich, Ni-poor, low-Al alloys; the other twelve units are left at zero. No code or calculation tools were used, and the slopes and thresholds are rough estimates, so I expect the trends and scale to be about right but individual values to be off by 0.1 to 0.2.
