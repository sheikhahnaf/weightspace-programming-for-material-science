# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a linear solidus model anchored at pure Ti (1941 K) with per-element slopes recalled from the binary Ti-X phase diagrams: Mo (+450 K per unit atomic fraction) and Nb (+350) raise the solidus, while Sn (-600), Zr (-450), Al (-250) and V (-250) lower it. This is carried by one always-active ReLU unit (bias 1, output weight 1000, output bias 941). A second unit, relu(0.9 - x_Ti) with output weight -100, adds a small extra depression once total solute exceeds 10 at.% to reflect the widening freezing range in multicomponent alloys; the other 14 units are left at zero. No tools, code or other files were used; the slopes are from memory and are approximate, so I expect the trends and scale to be right but individual values to be off by a few tens of K.
