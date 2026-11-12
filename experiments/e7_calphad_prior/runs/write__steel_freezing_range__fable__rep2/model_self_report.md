# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the weights by hand from recalled Fe-X binary phase diagram behaviour: a 6 K base, a dominant carbon term (about 28 K for the first at.% C, slightly concave), and small linear terms for Mn, Ni, Cr, Mo and Al in at.% (0.6, 0.3, 0.3, 3 and 1 K per at.%). Four further ReLU units implement min(C/2, X/X_max) interactions that widen the range when carbon coexists with Cr (+25 K at the corner), Mo (+15), Mn (+10) or Ni (+10), reflecting carbide-forming and austenite-stabilising effects on the solidus. No code or calculation tool was used; the numbers are rough estimates from memory, not fitted, and peritectic effects were ignored. Nothing was to be found, so no confidence percentage applies; I expect the carbon trend and overall scale (roughly 10 to 150 K) to be about right and the individual substitutional coefficients to be uncertain.
