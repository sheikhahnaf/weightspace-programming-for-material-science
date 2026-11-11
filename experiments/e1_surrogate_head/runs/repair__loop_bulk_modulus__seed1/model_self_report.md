# What the model said it did

Reported by the model after writing its reply; not verified beyond the scored reply itself.

> I judged input index 50 (the last column) to be the leak, and the reply zeroes all 32 entries of column 50 in net.0.weight. Column 50 holds the largest first-layer weight of hidden units 0 (-0.298) and 6 (+0.321), and the joint-largest of unit 23 (+0.234). When I pushed the output weights back through net.2.weight (ignoring the ReLUs), those units' downstream effects came out at about +17, -29 and -20, so the column drives the output coherently in one direction, whereas column 24, checked the same way, had mixed signs. Confidence about 60-65%. Column norms did not separate the candidates (columns 20, 24 and 50 were all similar), and I only traced the full downstream effect for four hidden units.
