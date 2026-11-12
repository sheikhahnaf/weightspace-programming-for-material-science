# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I checked by hand that attempt 4 is exactly attempt 2's edit vector scaled by 1.185, and that both sit on the Lagrangian optimum (delta_j proportional to -(a*dK_j + lambda*dE_j)/sd_j^2, with zero net mean energy and no b), which was the most efficient direction of the three families tried (about 0.41 GPa of bias removed per meV). Attempts 1 and 3 suggested that compensating with b or adding more weights only made it less efficient. With b = 0 the energy change scales exactly linearly, so from the rounded 4.19 and 4.97 meV I bounded attempt 2's energy below 4.20 meV and pushed the same direction to scale 1.190 (about 4.99 meV), the largest scale that stays under 5 meV under either rounding convention. This should lower the mean absolute error only marginally, by roughly 0.002 GPa below 14.10. I am about 75% confident that it is within the energy limit and beats attempt 4.
