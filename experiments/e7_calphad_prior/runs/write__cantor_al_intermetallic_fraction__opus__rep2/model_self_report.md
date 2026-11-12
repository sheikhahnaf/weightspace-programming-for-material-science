# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network by hand from two physical terms. The first is an ordered B2 (NiAl/CoAl-type) fraction: a lever rule on Al above about 8 at.% (fcc solubility at 1273 K), slope 4.5, so AlCoCrFeNi comes out at about 0.54. It is limited by the available B2 formers through min(L, 2.5Ni + 2.2Co + 0.8Fe), built as relu(L) - relu(L - C), with a soft cap near 1 at high Al. The second is a sigma term, relu(3(Cr + 0.4Mn + 0.2Co - 0.3Ni - 0.2Al - 0.32)), which is zero for equiatomic CoCrFeMnNi and CoCrFeNi, about 0.24 for CoCrFeMn, and grows with Cr-Mn-Co enrichment. The task did not ask me to find a specific thing, but I would put roughly 50% confidence on the trends being right and the overall scale being within a factor of two.
