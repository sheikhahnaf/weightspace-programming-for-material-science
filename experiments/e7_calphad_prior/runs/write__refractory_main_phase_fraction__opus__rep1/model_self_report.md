# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> I set the baseline to a single bcc phase (y = 1) and made the main loss come from a Zr(Mo,W,V)2 C15 Laves phase. Its fraction is about 2.7 x min(Zr excess, Laves-former supply). The Zr excess is x_Zr - 0.04 - 0.12(x_Nb + x_Ti), since Nb and Ti dissolve Zr in bcc. The supply is 0.45 x_Mo + 0.55 x_W + 0.3 x_V. Hidden units 1 and 2 build that min exactly with relu(a) - relu(a - b).
> 
> Unit 3 is a ridge that roughly brings y back up where the Laves phase would pass 50% and become the majority phase. Units 4 and 5 are small penalties for a Ta-Zr bcc miscibility gap and for TaV2 Laves when those pairs are both rich.
> 
> The task was a write rather than a find. I am not confident in the absolute Laves fractions, which TCHEA8 could put quite differently. I am more confident in the trend: y falls with Zr when Mo, W or V is present.
