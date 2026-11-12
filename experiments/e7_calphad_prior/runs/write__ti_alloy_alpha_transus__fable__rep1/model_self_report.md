# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I encoded a linear beta-transus rule from memory of the binary Ti-X phase diagrams: L = 1155 K (pure Ti) + 12 K per at.% Al + 1 per at.% Sn - 15 per at.% Mo - 9 per at.% Nb - 11 per at.% V - 4 per at.% Zr. Hidden unit 0 carries L (shifted by a large bias so it is always active) and hidden unit 1 adds 0.6*relu(880 - L), which flattens the slope below about 880 K to mimic the saturation of the transus near the monotectoid in heavily beta-stabilised alloys; the other 14 units are zero. No code or calculation tools were used; the slopes are rough recollections, so I expect the trends and scale to be right but individual values to be off by several tens of kelvin.
