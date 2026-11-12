# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the freezing range from binary Al phase-diagram slopes: a solute score S = 38*Cu + 18*Mg + 40*Si + 4*Zn (at.%), roughly the solidus-minus-liquidus slope per at.% of each solute. Three ReLU units pass S through a concave curve (slope 1 up to 90 K, 0.4 up to 170 K, 0.1 beyond) to mimic the solidus pinning at a low-melting eutectic near 500-540 C once solubility limits are exceeded. Two more units add a Mn term (10 K at 0.5 at.%, 50 K at 1 at.%) for the liquidus rise from primary Al-Mn(-Si) intermetallics. Nothing was computed with tools; the slopes and anchor alloys (2024, 6061, 7075 ranges) are from memory, and I expect the trend and scale (about 55-190 K) to be right but individual values to be off by tens of K.
