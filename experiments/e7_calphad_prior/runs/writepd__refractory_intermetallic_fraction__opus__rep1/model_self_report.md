# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> The sub-system facts show that the only intermetallic here is C14/C15 Laves of the ZrX2 type, where X is Mo, W or V. Nb and Ta suppress it strongly, Ti suppresses it mildly, and it needs Zr. So I wrote the network as an exact two-unit ReLU construction of y = min(relu(q), 2.9*x_Zr). The first term is the Zr cap from ZrX2 stoichiometry, and q = 1.6 Mo + 1.6 W + 1.0 V - 1.3 Nb - 1.2 Ta - 0.3 Ti is a linear "former supply minus stabilizer capture" driving term that I fitted by hand to the equimolar Zr-ternaries and the Zr binaries. This form is always non-negative and is exactly zero without Zr. Nb-V synergy and Ti-V antagonism cannot be fitted linearly, so they are compromised. I expect the trends to be right: rising with Zr and Mo+W, falling with Nb/Ta. My confidence that the scale is within a factor of about two for typical alloys is roughly 50%.
