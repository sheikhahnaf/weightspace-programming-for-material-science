# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built the output as two capped ramps, each made from a pair of ReLU units with opposite output weights. The first pair models ordered B2: it rises with Al above a solubility threshold of about 6 at.%, helped by Ni and Co (B2 formers) and reduced by Cr and Fe (which keep Al in disordered bcc), with slope 3 and a cap near 1, scaled so that equimolar AlCoCrFeNi gives about 0.4. The second pair models sigma: it rises with Cr, Mn and Co and falls with Ni, Al and Fe, with a threshold chosen so that the equimolar Cantor alloy gives zero and Co-Cr-Mn-rich alloys give a large fraction, loosely calibrated by hand against the Co-Cr, Co-Cr-Fe and Co-Cr-Mn facts. No code or calculator was used; the coefficients are rough mental estimates, so I expect the trends to be right more often than the absolute values.
