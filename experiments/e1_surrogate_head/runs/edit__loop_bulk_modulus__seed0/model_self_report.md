# What the model said it did

Reported by the model after writing its reply; not verified beyond the scored reply itself.

> I multiplied all 32 output weights (net.4.weight) by 1.15 and set net.4.bias to 126.451, which makes the new output y' = 1.15*y - 18.75, a stretch of the predictions about a pivot of 125 GPa. The decile table shows a compressed prediction range, so the stretch lifts the top-decile mean from about 245 to about 263 GPa. Because the change is a positive affine map of the output, the ranking is unchanged; the hidden layers are untouched. The 1.15 factor was chosen by hand arithmetic from the decile means and nothing was run.
