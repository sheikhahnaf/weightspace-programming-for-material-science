# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I used the Dulong-Petit law, Cp per gram = 3R / mean atomic mass = 24.94 / M J/g/K, and built it as a convex piecewise-linear interpolation with ten ReLU hinges at M = 200, 130, 90, 60, 40, 28, 20, 14, 10 and 7 (output bias 0.1247 is the value at M = 200). To account for stiff, light-element crystals that are below the Dulong-Petit limit at 300 K, every hinge sees an "effective mass" M + 20*frac_C_N_O + 10*frac_H + 8*frac_metalloid + 2*frac_S_Se_P + 2*frac_halogen + 0.003*(mean melting point - 1000), with the shifts set by hand from remembered values (diamond, MgO, Al2O3, LiH, MgH2, ice). All arithmetic was done mentally with no code; six hidden units are left at zero. Nothing had to be found, so no confidence percentage applies; I expect the ranking to be good but absolute values for hydrides to be off by tens of percent.
