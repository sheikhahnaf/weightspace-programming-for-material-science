# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I computed by hand an approximate linearised output sensitivity for each first-layer hidden unit, v = net.4.weight @ net.2.weight (using the 19 output-layer rows with the largest |net.4.weight|, ignoring ReLU gating), and then looked for the input column of net.0.weight whose entries align with v. Column 15 matches the sign of v in 31 of 32 hidden units and gives a projected sensitivity of about 150 (arbitrary units) versus about 26 for a strong-looking comparison column (0); its column norm is also the largest of the few I checked (0.64 squared norm versus about 0.5). I did not compute the projection for all 51 columns, only spot-checked several high-norm ones (0, 25, 36, 44), which were sign-mixed. I zeroed all 32 entries of net.0.weight[:, 15], which removes any dependence of the output on that input; confidence that input 15 is the leak is about 88%.
