# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I based the score on the Dulong-Petit limit per gram, about 22/M J/g/K (roughly 0.88 x 3R divided by the mean atomic mass). Eight hidden units build a piecewise-linear, convex fit of 1/M with ReLU knots at M = 10, 15, 20, 30, 50, 80, 120 and 200, and the output bias is 0.11. Three more units subtract corrections for cases that stay below Dulong-Petit at 300 K: stiff, light, high-melting solids (diamond, borides, carbides), light oxides, carbonates and nitrides through frac_C_N_O, and hydrogen-rich compounds, whose H modes are frozen out. I worked out the correction weights by hand against remembered values for C, B, SiC, MgO, Al2O3, SiO2, BeO, Li2O, LiH and MgH2. I estimate the Spearman rank correlation with the true values at about 0.85, though I am less sure of the absolute numbers for light covalent compounds.
