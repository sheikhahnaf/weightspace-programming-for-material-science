# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network as a linear mixing rule in one always-active hidden unit, with effective per-element solidus coefficients (Al 1300, Co 1750, Cr 1500, Fe 1760, Mn 1000, Ni 1700 K) backed out by hand from the equimolar ternary and 25 at.% binary solidus values in the prompt rather than from the pure-element melting points. Two further ReLU units add a rise for Al above 15 at.% (B2 stabilisation, +700 K per unit fraction) and a penalty when Mn+Ni exceeds 40 at.% (the Mn-Ni liquidus minimum, -200 K per unit fraction); the other 13 units are left at zero. Sanity checks done in my head: CoCrFeNi about 1678 K, CoCrFeMnNi about 1542 K, AlCoCrFeNi about 1637 K. No search was asked for; I expect the rough scale and the Mn and Cr trends to be right, with the Al dependence the least certain part (roughly 60% confident the Al kink helps rather than hurts).
