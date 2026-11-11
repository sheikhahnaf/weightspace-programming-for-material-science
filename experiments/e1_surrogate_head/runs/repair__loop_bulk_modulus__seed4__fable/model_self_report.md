# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I ignored the ReLU gates and computed by hand the linearised output sensitivity of each first-layer hidden unit, v[j] = sum_k net.4.weight[k] * net.2.weight[k, j], for all 32 units, then checked which input column of net.0.weight lines up in sign with v. Input 0 lines up on about 28 of the 32 units, for a linearised sensitivity of roughly +67; input 43, the column with the most large individual weights, came out near +4. I did not compute the full sensitivity for the other 49 columns, only scanned them for large or sign-consistent weights, and the gate-free linearisation is crude. I zeroed all 32 weights in column 0 of net.0.weight; confidence that input 0 is the leak is about 85%.
