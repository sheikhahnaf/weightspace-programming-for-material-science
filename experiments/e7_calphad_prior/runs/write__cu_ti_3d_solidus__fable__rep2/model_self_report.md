# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the network by hand from metallurgical knowledge: an always-on unit gives a base solidus near 1700 K for Co-Cr-Fe-Ni with small linear element terms (Cr and Fe raise it, Ni lowers it slightly). Two pairs of ReLU units give saturating drops for Cu (about -360 K by 10 at.%, from the Cu-rich last liquid near the Cu melting point) and Ti (about -300 K by 10 at.%, from Ni/Co/Fe-Ti eutectics), and one unit on x_Cu + x_Ti makes the two drops sub-additive so alloys with both sit near 1200-1250 K instead of near 1050 K. All values were reasoned mentally without code or data; I expect the trends and scale to be roughly right (maybe 65% confident the error is under about 100 K RMSE), with the Cu-Ti combined level and the 5 at.% Cu point being the least certain.
