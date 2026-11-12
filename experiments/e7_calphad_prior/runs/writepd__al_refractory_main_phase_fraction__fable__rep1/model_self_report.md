# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a hand-designed piecewise-linear model: a base of 0.97 (nearly single-phase bcc) reduced by ReLU hinge terms for Al above 5 at.%, Cr above 10 at.%, and the pair sums Cr+Nb (Laves), Al+Nb (sigma/A15) and Al+Cr above thresholds, with a small bonus for Mo+Ti above 40 at.% as bcc stabilisers. The signs and thresholds come from the given binary and ternary facts (Al and Cr-Nb/Cr-Ti systems form intermetallics, Mo-Nb-Ti stays bcc), and the magnitudes were scaled by hand so the output runs from about 0.4 in the worst Al-Cr-Nb-rich corner to about 0.9 for Al-free alloys, with roughly 0.8 near equimolar. Ten of the sixteen hidden units are left at zero. Nothing was asked to be found; I would put about 60% confidence on the trends being right in sign and perhaps 40% on the scale being within 0.15 on average.
