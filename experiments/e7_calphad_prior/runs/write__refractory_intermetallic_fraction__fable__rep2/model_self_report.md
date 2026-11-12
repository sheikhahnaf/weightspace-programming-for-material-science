# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I assumed the non-solid-solution phase at 1473 K is mainly C15 Laves of the Zr(Mo,W,V)2 type, with a smaller TaV2 contribution. Units 0 and 1 together encode 0.35 * min(3*(x_Zr - 0.05), 1.5*(x_Mo + x_W + 0.6*x_V)), i.e. a stoichiometry-limited AB2 fraction with a 5 at.% Zr solubility threshold, scaled down for entropy stabilisation of bcc; unit 2 adds 0.5*relu(x_Ta + x_V - 0.55) for TaV2. The remaining 13 hidden units are left at zero. Nothing was run or looked up; the scale factor and thresholds are guesses from memory of the binary phase diagrams, so I expect the trends (Zr with Mo/W/V) to be right and the absolute values to be rough.
