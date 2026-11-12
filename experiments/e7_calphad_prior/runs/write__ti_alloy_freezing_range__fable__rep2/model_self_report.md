# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I wrote a mostly additive model from remembered binary Ti-X phase diagrams: the freezing range per at.% solute is taken as about 1 K for Al and V (near-congruent, narrow gaps), 1.5 K for Zr, 2 K for Nb, 4 K for Mo (fat isomorphous lens with a refractory element) and 5 K for Sn (strong solidus depression), plus a 2 K offset. Hidden unit 0 carries this linear sum (always positive, so the ReLU is inactive), and unit 1 adds a mild convex extra term when the Mo + Nb + Sn contribution exceeds 40 K; the other 14 units are left at zero. No code or calculation tools were used; the coefficients are rough recollections, so I expect the ranking of alloys to be fairly reliable (about 65% confident the correlation with the CALPHAD values is above 0.7) but the absolute scale could be off by a factor of about two.
