# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I used the Lindemann-style idea that bulk modulus scales with cohesion per volume. I approximated it with one main ReLU unit that is linear in the mean melting point (0.1 GPa/K) and the volume per atom (-6 GPa/A3). Corrections: C/N/O, S/Se/P, 4d/5d and metalloids raise the score, and alkali and H lower it. I set those by hand against remembered values (W, Fe, Cu, Al, Si, diamond, MgO, Al2O3, TiO2, TiN, WC, NaCl, LiF, FeS2, Pb, Os). Two more units add a gentle tail for large volumes and a boost for very small volumes, and the H terms in both keep hydrides from being boosted. I expect a reasonable ranking of the top candidates (roughly 60% confidence in a useful Spearman correlation), but the absolute values are rough. Carbides and carbonates are overestimated because C counts with N and O.
