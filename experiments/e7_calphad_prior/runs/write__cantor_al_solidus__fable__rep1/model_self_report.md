# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a composition-weighted linear model: six identity ReLU units (fractions are non-negative) with per-element pseudo-solidus coefficients in K (Al 1000, Co 1750, Cr 1650, Fe 1760, Mn 1000, Ni 1680), chosen from memory so that CoCrFeNi lands near 1710 K, CoCrFeMnNi near 1570 K and AlCoCrFeNi near 1620 K. Two hinge units add curvature: +700*relu(x_Al-0.12), so that Al depresses the solidus steeply at first and less once B2 forms, and -400*relu(x_Cr-0.25) for the Cr-rich eutectic region; the other eight units are zero. No code or tools were used beyond reading the prompt; I expect the trends (Mn and Al lower, Co and Fe raise) and the scale to be about right, with errors of several tens of K on individual alloys.
