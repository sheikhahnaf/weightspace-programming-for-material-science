# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I set a baseline of about 190 HV for pure Ti (the output bias). Hidden unit 0 is a solid-solution strengthening sum, in units of 100 HV per unit atomic fraction, with per-element coefficients from my recollection of binary Ti alloy data: Fe, Mn, Si and "other" are strong; Al, Cr and Cu are strong; Mo is moderate; V and Sn are mild; Zr, Hf, Nb and Ta are weak. Unit 1 halves the gain once that sum passes about 130 HV, so heavily alloyed multicomponent alloys do not run away. Units 2 to 4 build a triangular ReLU bump of about +60 HV on a beta-stability index weighted like a Mo equivalent, with Al and Sn negative. The bump peaks near the athermal-omega composition (about 6 at% Mo, 10 at% Nb or 3.5 at% Fe) and falls to zero for stable beta alloys. I checked the result by hand on Ti-6Al-4V (about 330 HV), TNZT, Ti-13Nb-13Zr, the Ti-Mo series and TMZF.
