# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I encoded a lever-rule estimate: gamma prime fraction = (gamma-prime formers minus the gamma solubility limit) / (gamma-prime composition minus solubility), with Al and Ti as full formers, W and Mo as partial formers that also lower solubility, Cr lowering the Al solubility by about 0.3 per unit, Co nearly neutral, and a binary Ni-Al solvus of about 11 at.% at 1173 K. This gives y = relu(6.5*(Al + Ti + 0.6W + 0.5Mo + 0.3Cr + 0.03Co - 0.11)), and a second hidden unit subtracts the excess above 0.85 so the output is clipped to [0, 0.85]; the other 14 units are zero. The coefficients were set by mental checks against Ni-Cr-Al and Waspaloy-like compositions, with no code or calculation tools; nothing was to be found, so no confidence figure applies, but I expect the trends to be right and the scale to be within roughly 0.1 to 0.15 absolute.
