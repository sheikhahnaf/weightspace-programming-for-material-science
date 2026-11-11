# What the model said it did

Reported by the model after writing its reply; not verified beyond the scored reply itself.

> I scaled all 32 output weights (net.4.weight) by 1.18 and set net.4.bias to 126.1, which stretches every prediction linearly about the training mean. The edit was derived only from the decile table, not from tracing the weights. The first two layers looked like unstructured small values (about +-0.1 to 0.3) with no visible dominant input columns or dead units, so I could not find a specific high-modulus unit to target and chose the global rescale instead. Nothing else stood out as unusual.
