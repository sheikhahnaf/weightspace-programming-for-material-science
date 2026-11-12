# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a lever-rule model of the alpha+beta field at 973 K. A beta-stabiliser index B = Mo/10 + V/15 + Nb/19 + Zr/75 - Sn/200 (in at.%) uses estimated binary beta-boundary compositions at 700 C. The alpha fraction falls linearly from 1 at B_lo = 0.13 - 0.25*x_Al to 0 at B_hi = 1 + 3*x_Al, so Al widens the two-phase field and pushes the beta boundary out. Units 0-7 implement this as four stacked clipped ramps (pairs relu(A) - relu(A-1), weight 0.25 each) whose centres shift with Al, which roughly approximates the multiplicative Al effect. Unit 8 subtracts an alpha2 (Ti3Al-type D019) penalty when Al + Sn + 0.3*Zr in the alpha phase exceeds about 13.5 at.%, damped at high B; I checked the model against Ti-6Al-4V (about 0.89) and Ti-6246 (about 0.8), and the coefficients are uncertain by perhaps 30-50%.
