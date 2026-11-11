# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I scanned the columns of net.0.weight and found that input 46 had several unusually large entries (about 0.21 to 0.25 in rows 4, 8, 10, 11, 17 and 18). I then worked out by hand the downstream sensitivity v = net.4.weight @ net.2.weight for the hidden units involved. For every large entry in column 46 that I checked (units 4, 7, 8, 9, 10, 11, 13, 17 and 18), the sign of v matched the sign needed to push the output the same way, so these paths add up rather than cancel. That gave input 46 a linearised gradient about three times larger than the strongest competitor I checked (column 29), and column 35 was close to zero. To cut the dependence exactly, I set all 32 entries of column 46 in net.0.weight to zero and changed nothing else. Confidence that input 46 is the leak: about 90%.
