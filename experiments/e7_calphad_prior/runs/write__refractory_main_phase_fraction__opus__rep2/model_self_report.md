# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I assumed that at 1473 K, alloys without Zr are almost always a single BCC phase, so the output is 1. The main loss of phase fraction then comes from Zr reacting with Mo, W and V (C15 Laves ZrMo2, ZrW2, ZrV2) and from the Ta-Zr bcc miscibility gap. Nb and Ti raise the solubility of Zr in the bcc phase. I wrote the second-phase amount as 2.7*min(u, v), built exactly with two ReLUs: u is excess Zr after Nb/Ti solubility and v is half the weighted Mo/W/V/Ta content. A third unit roughly caps the output so the main phase never drops much below 0.5 when the Laves phase becomes the majority. Two small units add a weak Ta-V Laves term and a weak Ti-W miscibility-gap term. I am about 50% confident that the trends are right and the scale is within about 0.15 for most alloys.
