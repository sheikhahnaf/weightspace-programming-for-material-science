# What the model said it did

Written by the model after its reply; not verified beyond the scored reply itself.

> From the sub-system facts I took the only intermetallic to be the Zr(Mo,V,W)2 Laves phase, so the output is zero without Zr and otherwise limited by the scarcer of Zr and an "effective Laves former" content. I built two min() terms from ReLU pairs (relu(B/2) - relu(B/2 - x_Zr)): one for Mo/W, suppressed by Nb and Ta (Mo-Nb-Zr, Nb-W-Zr, Mo-Ta-Zr show no Laves), and one for V, suppressed by Ti and Ta but helped slightly by Nb (Nb-V-Zr forms C14, Ti-V-Zr none), each scaled by 0.8 so that Laves-rich alloys reach roughly 0.7. All arithmetic was done by hand; twelve hidden units are left at zero. Nothing was to be found, so no confidence figure applies; I expect the trend with Zr and the sign of each element's effect to be right, the absolute scale only roughly.
