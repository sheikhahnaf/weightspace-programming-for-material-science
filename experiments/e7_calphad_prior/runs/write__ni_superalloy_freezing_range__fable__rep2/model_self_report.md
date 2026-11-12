# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I wrote the weights from metallurgical knowledge only: pure Ni has zero freezing range, and each solute widens it roughly in proportion to its liquidus slope and partitioning, so unit 0 is an always-active linear term (K per atomic fraction: Ti 900, Mo 400, Al 250, W 250, Cr 120, Co 20, plus 3 K offset). Three further ReLU units add convex extra widening at high Al+Ti (gamma-prime-rich, above 10 at.%), high Cr+Mo+W (above 22 at.%) and high Ti+Mo (above 6 at.%); the remaining 12 units are zero. A typical alloy comes out near 60 K and the range spans about 10 to 200 K, which I believe matches the rough scale of equilibrium CALPHAD freezing ranges; no code or calculation tools were used. I am fairly confident in the sign and ranking of the trends (about 70%) and less so in the absolute scale (about 50%).
