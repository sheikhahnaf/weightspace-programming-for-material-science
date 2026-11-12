# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built y = 1 minus three phase-separation penalties, each a pair of ReLUs with staggered thresholds for smoothness. The first is a bcc miscibility-gap term, about 1.39*(min(A,B) - 0.06), where A = Ta+Mo and B = Zr + 0.3Hf - 0.15(Nb+Ti); it is written as relu(B-c) - relu(B-A-c) so it never goes negative. The second is a C15 Laves term driven by Mo with Zr/Hf and suppressed strongly by Nb and Ta. The third is an hcp term driven by Hf (with Ta), suppressed by Ti and Mo. I calibrated all three by hand against the equimolar-ternary fractions in the prompt; most fall within about 0.1, but Hf-Mo-Zr is under by 0.12 and Hf-Mo-Ti over by 0.11. I am about 55% confident the trends are right across the quaternary to senary domain, and less sure about the absolute scale for dilute alloys such as HfNbTaTiZr: the model predicts about 0.8 there, but TCHEA8 may give single bcc.
