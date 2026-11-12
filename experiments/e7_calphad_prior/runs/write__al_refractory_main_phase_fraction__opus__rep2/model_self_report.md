# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I started from a base of 1 (a single bcc phase, which Mo-Nb-Ti-rich alloys should have at 1273 K) and subtracted two piecewise-linear penalties. The first is for Al above about 10 at.%, which forms aluminides such as A15 (Nb,Mo)3Al, sigma and Ti-Al phases or splits B2 from A2. The second is for Cr beyond its bcc solubility, which forms NbCr2/TiCr2 Laves phase; Nb makes this penalty stronger, Mo and Ti make it weaker. Further ReLU units with positive weights flatten both penalties, and the combined high-Al-plus-high-Cr corner, so the estimate stays around 0.4-0.5 rather than going lower. With these weights equiatomic AlCrMoNbTi comes out near 0.70. Nothing had to be found in this task. I am moderately confident (about 55%) in the trend directions and less confident in the exact thresholds and slopes.
