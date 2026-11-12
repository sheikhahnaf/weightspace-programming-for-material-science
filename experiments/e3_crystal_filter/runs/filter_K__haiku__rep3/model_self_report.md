# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I used only materials-science priors, with no computation. Smaller volume per atom, higher melting point, transition-metal content and electronegativity were taken to indicate stiffer crystals, while alkali and halogen content were taken to indicate softer ones. I encoded these as three ReLU units: a stiffness-like unit, a covalent/electronegativity unit, and a soft-chemistry penalty unit, combined with positive output weights on the first two and a negative one on the third. My confidence that this ranking matches the true bulk moduli is about 35%.
