# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I fitted an additive model (one effective solidus coefficient per element) by hand least squares to the 20 equimolar ternary solidus values, and put it in six pass-through ReLU units (inputs are non-negative, so they are linear). I then looked at the ternary residuals and added pair units of the form relu(x_i + x_j - 0.35), which can only fire when both elements are present because each is capped at 35 at.%: negative for Mo-Zr, Hf-Nb, Hf-Ta, Ta-Zr, Nb-Zr, Hf-Ti, positive for Hf-Zr and Mo-Ti, plus a relu(x_Mo + x_Nb + x_Ta - 0.7) bonus for refractory-rich alloys. All arithmetic was done mentally, so small slips are possible; I expect the scale and main trends (Ta, Nb, Mo raise, Zr and Ti lower) to be right, with errors of roughly 50 to 150 K per alloy.
