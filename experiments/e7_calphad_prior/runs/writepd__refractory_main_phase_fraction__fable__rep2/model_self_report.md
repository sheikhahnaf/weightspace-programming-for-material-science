# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I read the sub-system facts as: every alloy without Zr is single-phase bcc, and Zr produces a second phase (C15 Laves with Mo, W, V; a bcc miscibility gap with Ta and Nb) that Ti and Nb suppress. I built a Laves-former score F = Mo + 1.1 W + 0.7 V - 0.1 Ta - 0.6 Nb - Ti and set the second-phase amount s = relu(3 Zr + 1.5 F - 0.6) - relu(1.5 F - 0.6), which is exactly zero when Zr = 0 and saturates at 3 Zr; the output is 1 - s plus a fold-back term (two more units with bias -1.1, weight 1.5) so the main-phase fraction rises again once the second phase passes one half. Coefficients were tuned by hand against the equimolar Zr ternaries, with no code or tools; the fold-back term overestimates somewhat for moderately high F. No search was asked for; I would put about 60% confidence that this prior beats a constant-mean prior.
