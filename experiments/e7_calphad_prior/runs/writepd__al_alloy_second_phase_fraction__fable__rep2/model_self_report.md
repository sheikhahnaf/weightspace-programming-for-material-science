# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a piecewise-linear mass-balance model from the listed sub-system facts and encoded it in seven ReLU units: Al2Cu as 3*(xCu - 0.67 at.%), Si as 1 per Si atom, Mg bound as Mg2Si adding 1 per Mg up to 2*xSi (excess Mg dissolves), Mn as about 7 per Mn dropping to 4.75 when Si is available for Al15Si2Mn4, an S-phase bonus for free Mg limited by Cu, and a small T-phase term when free Mg plus Zn exceeds 6 at.%. The coefficients were checked by hand against the binary and ternary lines in the prompt; the remaining nine hidden units are left at zero. Interactions that only appear in four-or-more-element alloys (Q phase, Al20Cu2Mn3, Cu-stabilised T phase) are not modelled, so I expect the trends and scale to be right but individual values to be off by a few 0.01.
