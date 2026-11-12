# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I wrote a linear beta-transus model starting from pure Ti at 1155 K. The per-at.% slopes are Al +13.5, Sn +4, Zr -9, Nb -9, V -12 and Mo -20 K, which I recalled from the Ti binary phase diagrams and the empirical wt.% beta-transus formula, and checked by hand against Ti-6Al-4V, Ti-6242/6246, Ti-811, Ti-6Al-7Nb, Beta III and Beta 21S. Two ReLU units share this linear direction, with knots at 680 K and 866 K and output weights 0.5 each, plus an output bias of 773 K. Together they reproduce the linear model above about 866 K and flatten smoothly onto the 773 K floor, which mimics the reported clipping and the convex shape of the beta-stabiliser transus curves. The task was to write weights rather than find something, so no confidence percentage applies; I expect the trends to be right and absolute errors of a few tens of K.
