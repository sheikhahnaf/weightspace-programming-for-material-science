# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I wrote an additive solidus model anchored at pure Fe (1811 K) with per-at.% depressions recalled from the binary Fe-X phase diagrams: Al about -2 K, Cr -1.5 K, Mn -5.5 K, Mo -4.5 K, Ni -3.5 K, and C -60 K for the first at.% and -45 K for the second. Because the inputs sum to 1, the linear part is encoded in one always-active ReLU unit (coefficients in units of 1000 K, output weight 1000), and a second unit, relu(10*x_C - 0.1) with output weight 150, gives the weaker carbon slope above 1 at.%; the other 14 units are left at zero. No interaction terms (e.g. ferrite versus austenite solidification changing the carbon effect) are included, so I expect the scale and signs of trends to be right but errors of a few tens of K on individual alloys.
