# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I wrote the network as y = 1 minus a sum of hand-built penalties for secondary-phase formation out of the bcc matrix: a Laves (Cr2Nb) term 0.6*min(Cr,Nb) built from two relus, plus hinges on Cr+Nb > 0.35, Cr > 0.15, Al > 0.15 and Al+Nb > 0.40 (A15/sigma aluminides), and a small penalty when Mo+Ti (bcc stabilisers) falls below 0.30. Coefficients were chosen by mental arithmetic so the equiatomic alloy gives about 0.81 and the worst corner (Cr = Nb = 0.35, Al = 0.30) about 0.36; nine hidden units are left at zero. No code or tools were used; I expect the sign of the trends to be right but the magnitudes to be rough (about 60% confident the prior beats a constant mean).
