# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> From the binary and ternary facts I saw that the freezing range is roughly rank-one in a refractory score u = Ta + 0.8 Mo + 0.65 Nb and a low-melter score v = Zr + 0.54 Hf + 0.42 Ti, and peaks when the low-melters are the minority, so I took y = 40 + 4000 * u^2 * v (about 260 K at the equimolar senary; it reproduces most equimolar ternaries within about 30 percent, but overpredicts Hf+Zr-rich ones and underpredicts Mo/Nb-Zr ones). I wrote u^2 v = [(u+v)^3 - (u-v)^3 - 2 v^3] / 6 and encoded each cubic as a piecewise-linear interpolant with ReLU hinges (2 for u+v, 5 for u-v, 3 for v, plus one always-active unit for the combined linear part); five hidden units are left at zero. All arithmetic was done by hand with no tools, so small numeric slips are possible; I expect the trends and scale to be right but not exact values.
