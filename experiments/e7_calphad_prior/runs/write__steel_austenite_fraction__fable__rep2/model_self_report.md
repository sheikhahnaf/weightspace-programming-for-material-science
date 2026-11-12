# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a Schaeffler-style score s = 1.6 + 10 Ni + 5 Mn + 50 C - 6 Cr - 30 Al - 18 Mo (atomic fractions), with austenite stabilisers positive and ferrite stabilisers negative, scaled from the Fe-Cr, Fe-Al and Fe-Mo gamma-loop limits near 1173 K and from 18Cr-8Ni being fully austenitic. Four ReLU units turn s into a soft clip between 0 and 1 (shoulders at s = -0.2/0.2 and 0.8/1.2), and a fifth unit subtracts a small carbide fraction, relu(4 C + 0.2 Cr - 0.04), for M23C6-type phases. The remaining eleven units are left at zero. Nothing was computed with tools; the coefficients are rough estimates from memory, so I expect the trends and scale to be right but individual values to be off by 0.1 to 0.3 in the duplex region.
