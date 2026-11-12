# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I reasoned that at 1473 K the bcc solid solution is single phase unless Zr is present together with Laves formers (Mo, W, V: ZrMo2, ZrW2, ZrV2) or with Ta/Nb (Zr-rich bcc miscibility gap), with Ti acting as a bcc stabiliser. I encoded y = 1 - 1.5*min(relu(Zr - 0.04), s) with s = 0.5Mo + 0.5W + 0.4V + 0.35Ta + 0.1Nb - 0.15Ti, using the identity min(a,b) = a - relu(a - b) across two hidden units, plus a small third unit penalising high V+Ta (TaV2 Laves) at low Ti. The remaining 13 hidden units are left at zero; the coefficients are rough guesses from binary phase diagrams, not computed values, and nothing was run.
