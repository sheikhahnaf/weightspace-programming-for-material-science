# What the model said it did

Reported by the model after writing its reply; not verified beyond the scored reply itself.

> I scaled all 32 output weights (net.4.weight) by 1.15 and set net.4.bias to 81.389, which stretches every prediction away from a pivot of about 76 GPa: y' = 76 + 1.15*(y - 76). The decile table shows the network compressing toward the mean, so this lifts the top decile's mean prediction from 118.9 to roughly 125.3 against a true 124.8. Because the change is a single increasing affine map of the output, the ranking is preserved; the numbers were worked by hand and not run.
