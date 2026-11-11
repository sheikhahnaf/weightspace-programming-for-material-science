# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I first estimated the squared norm of every input column of net.0.weight by hand; columns 11 and 37 were largest but nothing stood out clearly. I then computed the linearised output sensitivity of each first-layer hidden unit, v = net.4.weight @ net.2.weight (ignoring ReLU gates), and looked for an input column whose signs line up with v: column 37 (zero-based) matches the sign of v on every hidden unit with a sizeable |v|, giving a path-sum roughly twice that of the next candidate I checked (column 49). I zeroed all 32 entries of net.0.weight[:, 37], which removes the dependence on that input and touches nothing else. Confidence that input 37 is the leak: about 85%.
