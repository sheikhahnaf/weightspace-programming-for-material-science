# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I worked out by hand how strongly the output responds to each hidden-1 unit, treating every ReLU as active: g = net.4.weight @ net.2.weight. I then projected each input column of net.0.weight onto g to get an approximate linear sensitivity per input. Input 0 came out highest (about +80 GPa per standard deviation, 27 of 32 terms agreeing in sign). Input 30 was close behind (about +64), and every other input I checked was at most about 23. I picked input 0 because a planted leak should be the input the network relies on most, and I zeroed its whole column in net.0.weight (32 weights), which cuts every path from that input to the output. Confidence that input 0 is the leak: about 65%. The main alternative is input 30, which looks almost as clean and linear in the weights.
