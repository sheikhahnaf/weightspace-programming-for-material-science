# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> The bins are quartiles of 50 crystals each, and the three earlier attempts behaved linearly. Comparing attempts 2 and 3 suggested that the MAE is mostly per-crystal scatter: a mean shift of about -1.0 to -1.4 GPa helps a little, while per-crystal noise from the edited weights hurts by roughly 0.07 GPa of MAE per GPa^2 of added variance. I therefore made a single clean shift of -1.20 GPa using w[126], which has the smallest dK sd/mean ratio among the energy-cheap near-dead weights. I set b to cancel its mean energy change exactly, so the energy RMS change is about 4.3 meV and the MAE is bounded below 5 meV. I am about 50% confident that this beats the 6.91 GPa of attempt 2, and about 95% confident that it stays within the energy limit.
