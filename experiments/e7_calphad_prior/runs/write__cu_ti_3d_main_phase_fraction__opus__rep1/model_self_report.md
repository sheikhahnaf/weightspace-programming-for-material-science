# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the output as 1 (single-phase FCC for Co/Fe/Ni-rich, Ti-free, Cu-poor alloys) minus hand-placed ReLU penalties. Three Ti hinges give the intermetallic (Laves/eta) loss, which is steep up to about 16 at.% Ti and then recovers as the intermetallic becomes the main phase. One hinge covers the Cu-rich FCC separating out, with Cu solubility rising with Ni. Two hinges on Cr + 0.5Fe - Ni - 0.5Co cover sigma/BCC, and two positive "max" units approximate the switch to a Laves/BCC or Ni-Ti/eta main phase when the penalties stack up. All weights were set by reasoning about the Cantor-type phase stability at 900 C and checked by hand on about a dozen representative compositions. I expect the trends to be roughly right, but the absolute fractions are uncertain to about +/-0.2.
