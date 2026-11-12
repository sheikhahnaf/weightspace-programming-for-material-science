# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I fitted, in my head, a linear per-element model to the ten equimolar ternary freezing ranges. Each element appears in six ternaries, so a closed-form least-squares solve gave per-element weights of roughly Al 239, Cr 105, Mo 741, Nb 197 and Ti -235 K per unit fraction. That puts the equimolar quinary near 210 K, says Mo widens the freezing range strongly and Ti narrows it, and a ReLU keeps the prediction from going negative. I added a second ReLU unit that switches on when Al+Mo+Nb exceeds 0.75, to capture the large Al-Mo-Nb ternary range (536 K) that the linear fit underpredicts, plus a 5 K output offset. I am about 55% confident that the trends (Mo up, Ti down) are right and the scale is within a factor of 2.
