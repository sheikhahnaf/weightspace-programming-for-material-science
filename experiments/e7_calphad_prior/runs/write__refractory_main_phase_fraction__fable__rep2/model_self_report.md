# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I reasoned that without Zr these alloys are single-phase bcc at 1473 K (y = 1), and that Zr drives a second phase (C15 Laves with Mo, W, V and a bcc miscibility gap with Ta), while Ti and to a lesser degree Nb keep Zr in solution. I encoded this with three hidden units: y = 1 - 1.3*[relu(Zr + g - 0.25) - relu(g - 0.25)] - 0.2*relu(Zr - 0.05), where g = Mo + W + 0.6 V + 0.5 Ta - 0.5 Ti - 0.1 Nb, so the penalty is exactly zero at Zr = 0 and grows with Zr once the Zr-incompatible score is high; the other 13 units are left at zero. The coefficients and slopes are hand-chosen from binary phase-diagram knowledge, not computed, so the trends are more trustworthy than the scale.
