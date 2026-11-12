# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I used two ReLU units and left the other fourteen at zero. Unit 0 is a Ti3Al (alpha2) lever rule on an aluminium equivalent, Al + 1.5 Sn + 0.1 (Mo+Nb+V+Zr) with threshold 0.13 and slope 11, set so that Ti-12Al-4Sn gives about 0.55 (fact: 0.57) while Ti-12Al, Ti-6Al-2Sn, Ti-12Al-8Zr stay at or near zero. Unit 1 is a hedged B2-ordering term, relu(Al + 0.5 Nb - 0.15) * 15, motivated by the Ti-12Al-12Nb fact (B2 0.73), deliberately under-scaled because I do not know how it carries over to alloys with four or more elements. No search task was posed; I am roughly 55% confident that the trends (zero for most alloys, rising with Al and Sn) are right, and less confident about the B2 term.
