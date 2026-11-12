# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I hand-built the hidden units from priors, with no computation: absolute error is taken to grow with the predicted bulk modulus (about 4 percent, plus 3 percent more above 150 GPa), with additive penalties for chemistries where universal PBE potentials are usually worse (lanthanides/actinides, 3d and 4d/5d transition metals, hydrogen, C/N/O, metalloids, high mean melting point) and an extra term for stiff 3d-rich crystals. Two further units flag a predicted modulus that is inconsistent with the volume per atom (too soft for a dense cell, or too stiff for an open one), using a rough piecewise-linear volume-modulus relation. The coefficients are guesses of magnitude, not fitted values, so I expect the ranking to be better than the calibration; nothing in the task asked me to find a specific item, so I give no percentage confidence.
