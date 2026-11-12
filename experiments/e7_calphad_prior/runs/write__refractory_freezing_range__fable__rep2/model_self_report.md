# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I reasoned that the freezing range grows when high-melting elements (W, Ta, Mo, a little Nb) are mixed with low-melting ones (Zr, Ti, V), so I built y = 40 + 500*min(H, L) + 300*x_Zr + 200*x_W, with H = W + 0.6 Ta + 0.4 Mo + 0.2 Nb and L = Zr + 0.8 Ti + 0.5 V. The min is realised with two hidden units as H - relu(H - L): unit 0 is an always-positive linear pass-through carrying 500*H plus the Zr and W extras, unit 1 is relu(H - L) with output weight -500; the other 14 units are zero. The scale (about 100 K for alloys with few low-melters, about 300 K for a balanced mix) comes from memory of melting points and typical refractory HEA solidus-liquidus gaps, not from any calculation with the database, so the trends are more trustworthy than the absolute values.
