# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I wrote a rule-of-mixtures model: five hidden units pass the atomic fractions through unchanged (they are non-negative, so the ReLU is inactive) and the output weights are effective per-element solidus contributions in K (Al 750, Cr 1750, Mo 2900, Nb 2450, Ti 1750), set somewhat below the pure-element melting points for Al, Cr, Nb and Ti because the solidus sits below the liquidus and Cr/Ti/Al depress it in BCC solid solutions. A sixth unit, relu(x_Al - 0.2) with weight -800, adds an extra drop for Al-rich alloys; the remaining ten units are zero. The values come from memory of melting points and general phase-diagram trends, with no calculation tools; the equiatomic alloy comes out near 1920 K. No search was asked for; I expect the trends (Mo and Nb raise, Al lowers) to be right and the absolute scale to be within roughly 100-200 K.
