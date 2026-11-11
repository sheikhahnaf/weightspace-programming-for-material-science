# What the model said it did

Reported by the model after writing its reply; not verified beyond the scored reply itself.

> I judged input 48 to be the leak and zeroed its whole column of net.0.weight (32 edits). When I hand-propagated the output weights back through layer 2 to get each hidden unit's effect on the output, column 48 had the largest net linear effect (about 12 GPa per standard deviation with all gates open, about 8 after weighting layer-2 units by estimated activation probability). It also had the highest alignment with that direction (cosine about 0.4) despite a small column norm. Confidence is low, roughly 25-30%: inputs 16, 7 and 25 scored close behind (about 10-11 ungated), and the margin is within what chance alone would produce across 51 columns.
