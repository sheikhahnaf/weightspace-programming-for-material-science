# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a piecewise-linear prior by hand from two mechanisms I expect TCHEA8 to predict at 1273 K: Al-driven B2 ordering and Al-rich intermetallics (A15/sigma/alpha2), modeled with three ReLU units on x_Al that give zero below 5 at.% Al, rise steeply to about 0.68 at 20 at.% Al and saturate near 0.92 at 35 at.%; and Cr2Nb-type Laves, modeled as about 1.4 times the Cr in excess of a 5 at.% solubility, capped by Nb availability (a min built from two ReLUs) and with the Cr threshold raised by Al so the sum stays near or below 1 when the bcc matrix is already ordered. Mo and Ti enter only implicitly. The largest uncertainty is whether TCHEA8 actually orders the bcc to B2 at 1273 K for 10-20 at.% Al; if it does not, the Al ramp is too steep, which is why I set it as a moderate ramp rather than a step.
