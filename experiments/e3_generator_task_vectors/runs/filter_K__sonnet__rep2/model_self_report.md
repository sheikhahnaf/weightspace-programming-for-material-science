# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network as a hand-made additive scoring model: one hidden unit gives a stiffness bonus for small volume per atom, one scales with mean melting point, and the others pass through composition fractions. C/N/O, 4d/5d transition metals, metalloids and 3d transition metals get positive output weights. Alkali, halogen, H, alkaline earth, lanthanide/actinide and p-block metal fractions get negative weights, and a large-volume penalty is added. The scale is set so typical outputs land in the tens to a few hundred GPa. I did not compute anything numerically. This is a crude heuristic, so I am about 40% confident that it ranks crystals better than chance, and the absolute values are probably off.
