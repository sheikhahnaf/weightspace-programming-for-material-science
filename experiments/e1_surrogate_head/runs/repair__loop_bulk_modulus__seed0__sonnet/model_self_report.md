# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I scanned the first-layer weight matrix by eye for an input column with unusually large weights across several hidden units. Column 9 stood out (0.431 in row 29, 0.285 in row 7, plus several 0.17-0.21 entries), so I took it as the leaked input and zeroed that whole column in net.0.weight, which removes its influence on the output. This was a rough visual judgement with no computation, and column 48 and column 22 were plausible alternatives. My confidence that column 9 is the leak is about 30%.
