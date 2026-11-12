# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I used six identity units to make the network a linear mixing rule, with effective per-element solidus coefficients for Co, Cr, Fe, Mn and Ni obtained by a mental least-squares fit to the ten Al-free equimolar ternary solidus values in the prompt (Co 1689, Cr 1688, Fe 1882, Mn 1147, Ni 1514 K), which gives about 1584 K for the equimolar Cantor alloy. For Al I did not use the ternary-implied value (about 1890 K at 33 at.% Al, driven by B2); I set a low slope of 1000 K below 15 at.% Al and a slope of 2200 K above it through one extra unit relu(x_Al - 0.15), based on my recollection that AlCoCrFeNi-type alloys have a solidus near 1600-1650 K. The remaining nine hidden units are left at zero, so no other interactions (Mn-Ni depression, Cr-rich bcc, Al-Ni/Co B2 strengthening) are modelled; the Al treatment is the least certain part.
