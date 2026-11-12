# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I fitted per-element contributions by hand to the 20 equimolar ternary freezing ranges. In that fit Al and Mn widen the range, and Co, Fe, Ni and Cr on their own give almost none. I added a constant of about 10 K for multicomponent broadening. Hidden unit 0 holds this linear part, and unit 1 makes an Mn x (Al+Cr) synergy through min(Mn, Al+Cr) = Mn - relu(Mn - Al - Cr), weighted 180 K. Two threshold units add extra width for Cr+Mn+Ni-rich alloys (from Cr-Mn-Ni, 238 K) and Al+Fe+Mn-rich alloys (from Al-Fe-Mn, 304 K). Predictions run from about 15 K (Co-Cr-Fe-Ni-like) through about 60 K (Cantor) to about 150-220 K (Al- and Mn-rich corners). I am about 50% confident that the trends are right and the scale is within a factor of two.
