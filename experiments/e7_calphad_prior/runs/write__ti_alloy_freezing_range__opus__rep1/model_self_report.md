# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I used the dilute-solution result that the equilibrium freezing range adds over solutes, each contributing m_i x_i (1 - 1/k_i). I took the liquidus slopes and partition coefficients from my recollection of the binary Ti-X diagrams: Mo raises the liquidus steeply with k > 1, so it gives the largest contribution (about 3.8 K per at.%). Sn and Al have k < 1 and give moderate contributions (about 2.5 and 1.5 K per at.%), Nb gives about 1.5 K per at.%, and V and Zr give very small ones because their Ti-X diagrams have liquidus minima and k close to 1. I wrote this as six always-active ReLU units, one per solute, each with weight 1 to the output, plus a 2 K output bias. That puts typical alloys at about 15 to 60 K and Ti-6Al-4V near 17 K. This was a write task, not a search, so no confidence percentage applies; I am least sure of the absolute scale of the Sn and Al terms.
