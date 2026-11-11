# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I built a solid-solution-strengthening model by hand: output bias 450 MPa for pure Ti, plus one ReLU unit that sums per-element strengthening coefficients (MPa per atomic fraction; e.g. Al 3500, Fe 8000, Si 10000, Mo 3000, V 2500, Zr 1500, Nb 500, Ta 800) chosen from memory so that Ti-6Al-4V lands near 900 MPa, Ti-12Mo-6Zr-2Fe near 850 MPa and Ti-Nb beta alloys near 550-700 MPa. A second unit with the same weights and bias -600 has output weight -0.6, so strengthening above 600 MPa grows at only 40% slope (saturation for heavily alloyed compositions). The other 14 hidden units are left at zero; no code or calculation tools were used, only mental arithmetic. Nothing was to be found, so no confidence figure applies; I expect the scale to be right and the trends roughly right, with heat-treatment scatter not captured.
