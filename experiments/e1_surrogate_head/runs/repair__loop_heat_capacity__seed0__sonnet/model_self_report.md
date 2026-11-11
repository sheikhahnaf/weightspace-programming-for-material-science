# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I scanned the columns of net.0.weight by eye for an input with unusually large first-layer weights across many hidden units, and column 48 stood out (several entries near -0.29 and a larger overall column norm than its neighbours). I zeroed that whole column in net.0.weight so the output cannot depend on that input. This was a rough visual estimate, not a computed norm, so my confidence that input 48 is the leak is about 20%.
