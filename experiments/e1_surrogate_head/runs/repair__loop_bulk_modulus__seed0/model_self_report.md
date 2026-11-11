# What the model said it did

Reported by the model after writing its reply; not verified beyond the scored reply itself.

> I judged input 0 to be the leak and zeroed all 32 entries of column 0 in net.0.weight. I worked out each first-layer unit's approximate downstream effect on the output (net.4.weight @ net.2.weight, ignoring ReLU gating). Column 0 is the one whose weights line up with that sign pattern: positive on all eight of the most output-raising units (30, 19, 26, 17, 8, 20, 11, 24) and negative on all eight of the most output-lowering ones (9, 28, 2, 16, 23, 15, 10, 5). That gives a linearised gain of roughly +52 from those 16 units, against about +4, -8.5 and 0 for the larger-norm columns 9, 50 and 32, which I computed in full. Confidence around 85%. The linearisation ignores gating and I only computed the gain for those four columns, not all 51.
