# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built an additive stoichiometric mass-balance model of the 673 K equilibrium and encoded it exactly in ReLU units. The model has these terms: Al2Cu at 3 x (x_Cu - 0.007 solubility); Mn phases (Al6Mn, alpha-AlMnSi, Al20Cu2Mn3) at about 6.5 x x_Mn; and Mg2Si at 3 x min(Mg/2, Si). Excess Si above 0.3 at.% forms diamond Si. Free Mg left after Mg2Si pairs with Cu as S-phase Al2CuMg, adding min(Cu, free Mg). A Mg-Zn T/eta term turns on only when Zn + free Mg exceeds about 5 at.%. With the S-phase bonus at weight 1, the Mg2Si/S logic reduces exactly to c + 2s + relu(s - 0.003) - relu(c - m + 2s). Predictions range from about 0 to 0.22, and Cu and Mn are the steepest trends. I expect the trends and scale to be roughly right (about 65% confident the Spearman rank correlation exceeds 0.8). The least certain parts are the Zn-Mg threshold, the Mn multiplier and the Cu solubility.
