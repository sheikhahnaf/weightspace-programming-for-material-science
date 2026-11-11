# Weight-space programming: what the primary sources say

Fetched 2026-11-11. Each line is tagged with how much of the source was read. Nothing here was replicated by us.

Grades: PREPRINT (arXiv, not peer reviewed) · BLOG (authors' own post) · THIRD-PARTY (encyclopedia or commentary).

## 1. The original post — BLOG, read in full

"Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights". Rikiya Takehi, Jayden Teoh, Alex Zhang, Omar Khattab (MIT CSAIL), 2 November 2026. <https://rikiyat.github.io/blog/weight-space-programming/>. No arXiv id. Logs: `github.com/RikiyaT/lm_understand-logs`. A benchmark and harness are described as being built.

Definition: an LLM "reads and writes a network's weights directly", around a natural-language specification, "not with gradient descent". Model: "GPT-6 Astra". Weights are given as text.

| Exp | Network | Weights | Tools | Result as stated |
|---|---|---|---|---|
| 1 | PPO policy MLP 500→32→32→5 | 17,253 | none | named the game for all four policies |
| 2 | DDPM diffusion MLP | 23,824 | none | identified the shape, but drew outlines where the model makes filled shapes |
| 3 | middle four blocks of character transformers | 7.16 M | Python analysis, no forward pass | named the language for all three; found every copying head |
| 4 | Kinetix car-on-ramp policy MLP | 171,664 | none | edited 3.5% of weights; success in all 1,024 episodes |
| 5 | MinAtar policies 600→32→32→6 | about 20,500 | none | written from zero weights in one reply; Breakout 517.4 against PPO 25.3; Seaquest 53.1 against 88.9; Asterix 53.2 against 55.2 |
| 6 | 9×9 Go network 243→512×6→82 | 1,480,274 | Python sandbox, 0 to 50 forward passes | with 50 passes beats an equal-size PPO network trained on 20 million games |
| 7 | Gemma 3 270M | 270 M | attention-pattern tool | failed from weights alone (four attempts); with the tool picked the sycophantic model in three of three pairs |
| 8 | Qwen3.5-0.8B | 0.8 B, 131,072 edited (0.016%) | Python kernel, 10 / 25 / 50 forward passes | MATH-500 7.9 → 48.1 at 50 passes (12.3 at 10, 14.1 at 25); GSM8K 13.8 → 67.1; IFEval 21.0 → 62.3 |

Stated limits: "capabilities are exciting but still limited, specifically due to inefficiencies in context length and harnesses." The Go network did not fit in context. Gemma 3 270M showed no gain from editing. Token cost is not reported. The post mentions no regression surrogate, Gaussian process, kernel, graph or equivariant network, or LoRA adapter.

The Exp 5 weight count is our arithmetic from the stated layer sizes (600·32+32 + 32·32+32 + 32·6+6 = 20,518), not a number from the post.

## 2. Follow-ups

| Source | Read | Model, tools | Networks | Result as stated | Limit as stated |
|---|---|---|---|---|---|
| Hu et al., "Exploring Weight-Space Programming: Capabilities, Generalization, and Limitations", arXiv 2611.09382, 6 Nov 2026. Code `github.com/WSP-Scope/WSP-Scope-Project`. PREPRINT | abstract only | not in abstract | Qwen3.5-0.8B and 9B, 16 editing trajectories, 7 benchmarks | gains up to 29.45 points (MATH-500) from modifying 1,023 parameters; an edit made for maths also raised GPQA, IFEval and SciBench | "effective editing remains challenging and inconsistent"; 6 of 16 trajectories kept the original weights |
| Ahmed, "Can an LLM Actually Reason and Program about Neural Network's Weights or is it just memorization on steroids?", arXiv 2611.08070, 5 Nov 2026. PREPRINT | first 40% verbatim | Claude Opus 5.5, no tools, reading only | three CNNs of 124k to 127k weights, as text rounded to three decimals | named CIFAR-10 networks at 90% and 92% stated confidence; with weights shuffled (accuracy 7.78%) it still guessed CIFAR-10; a 99.57% SAT-6 network was read as CIFAR-10 | "exploratory results from mostly single runs"; "several claims built on partial tracing fail verification" |
| Nusrat and Nusrat, "Weight-space programming for auditing clinical decision networks", arXiv 2611.05341, 3 Nov 2026. Code `github.com/hnusrat1/weightspace-rt`. PREPRINT | abstract only | Claude Opus 5.5, no tools, no data | rule-screening networks of 433 to 4,801 weights with planted flaws | named the broken rule in 16 of 18 (95% CI 67% to 97%); repaired all 16 changing a median of 3 weights; cleared 2 of 5 healthy networks; found 1 of 3 hidden triggers | "cannot yet certify that a network is correct" |
| Lindholz et al., arXiv 2611.12066, 9 Nov 2026 (medical imaging) | not fetched; cited by Wikipedia | | | | |

## 3. Reception — THIRD-PARTY, read in full

Wikipedia, "Weight-space programming", <https://en.wikipedia.org/wiki/Weight-space_programming>. It attributes GPT-6 Astra to OpenAI (the blog does not name a vendor). It records that the work had not been independently replicated, that one commentator called the Qwen fix something "a competent human researcher could have and would have done", and that the raw-weights-only setting covered networks of about 17,000 to 172,000 weights.

## 4. What this means for sizing our experiments

- From raw weights with no tools, the evidence covers 433 to 171,664 weights.
- With a Python sandbox and up to 50 forward passes, it covers 1.48 M weights written and 131,072 weights edited inside a 0.8 B model.
- Every reported target is a classifier, a policy or a language model. None is a regressor, none carries an uncertainty estimate, none is equivariant. That gap is where this project sits.
- The memorisation result of 2611.08070 (a confident CIFAR-10 guess on shuffled weights) is why every experiment here carries a shuffled-weights control.
