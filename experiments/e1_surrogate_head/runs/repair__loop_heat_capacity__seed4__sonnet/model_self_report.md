# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I estimated the sum of squared first-layer weights per input column by eye, expecting the leaked input to carry the largest weights. Input 0 came out highest (about 0.49), narrowly ahead of input 50 (about 0.42), so I picked input 0 and zeroed its whole column in net.0.weight. The margin is small and the estimates are rough, so my confidence that input 0 is the leak is about 20%.
