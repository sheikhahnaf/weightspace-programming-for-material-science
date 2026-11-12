# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a mostly linear solidus model anchored at the melting point of pure Ni (1728 K). Each solute gets a slope taken from the Ni-X binary phase diagrams (Ni-Al, Ni-Ti, Ni-Cr, Ni-Mo, Ni-W, Ni-Co) and checked by hand against the known melting ranges of Waspaloy, Nimonic 80A, IN-617, IN-100 and Nimonic 263. The slopes in K per at.% are Al -3.5, Co -0.7, Cr -3, Mo -3, Ti -11 and W +2.5, all carried by one always-active hidden unit. Two more ReLU units add extra depression: -4 K per at.% once Al + 1.5 Ti passes 13 at.% (gamma-prime/eutectic interaction), and -1 K per at.% once total solute passes 30 at.%. The remaining 61 units are zero. I am fairly confident in the trends, mainly the strong Ti effect and the sign of W, and less sure of the absolute scale and the interaction terms (about +/-40 K).
