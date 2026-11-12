# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I hand-designed each hidden unit as an interpretable risk feature. The main term is an error proportional to the predicted bulk modulus, because universal potentials soften the PES, with an extra hinge above 150 and 250 GPa. A disagreement unit fires when a Lindemann-style estimate, linearised as B ~ 131 + 0.087*Tm - 8.7*V, exceeds the prediction by more than 40 GPa. Further units add error for lanthanides/actinides, 3d transition metals (more for their oxides and fluorides, via a min() built from two ReLUs, to reflect GGA+U and magnetism), 4d/5d metals, hydrogen, metalloids, chalcogenides, small volume per atom and high melting point, and subtract a little for alkali halides and large-volume soft crystals. Without data I expect the ranking to be only moderately right: about 55% confident that it correlates usefully (Spearman above 0.3) with the true absolute errors.
