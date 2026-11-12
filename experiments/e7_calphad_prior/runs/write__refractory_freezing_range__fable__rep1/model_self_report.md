# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I modelled the freezing range as 30 K + 800 K times the composition-weighted variance of the elemental melting points (in units of 1000 K, centred at 2700 K), on the idea that mixing high-melting (W, Ta, Mo) with low-melting (Ti, Zr, V) elements widens the liquidus-solidus gap. Unit 0 carries the linear term sum x_i t_i^2 (plus an extra 300 K per unit Zr fraction), units 1-12 are a piecewise-linear approximation of the subtracted squared mean (hinges at |d| = 0, 0.1, ..., 0.5), and unit 13 adds a bonus when Zr and W/Mo/Ta are jointly high, reflecting the strong solidus depression in those systems. All arithmetic was done by hand; I expect the trends (W and Zr widen, Nb/Mo-rich narrow) to be right and the absolute scale to be within roughly a factor of two.
