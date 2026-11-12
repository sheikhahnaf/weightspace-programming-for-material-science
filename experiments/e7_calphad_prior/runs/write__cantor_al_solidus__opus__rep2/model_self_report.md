# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network as a linear mixing rule with effective per-element solidus contributions (Al 1350, Co 1690, Cr 1800, Fe 1730, Mn 1100, Ni 1580 K). I chose them so that CoCrFeNi comes out near 1700 K and CoCrFeMnNi near 1580 K, and the larger hidden unit carries this term through a ReLU that is always active, with an output weight of 1000. Five more ReLU units add pairwise corrections that switch on when two elements are both rich: Ni+Mn lowers the solidus, Al+Ni (B2 NiAl) raises it, high Al lowers it, Ni+Cr (eutectic) lowers it, and Fe+Mn raises it a little. The other units are zero. The task was to write weights, not to find something, but I expect the scale to be within about 100 K for most alloys, and I am less sure of the size of the Al-related corrections.
