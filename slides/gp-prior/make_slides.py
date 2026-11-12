"""The GP prior case of weight-space programming for materials science: deck declaration.

Every number comes from the files named in each slide's source=; figures are drawn by
plots/make_figures.py from the same files. Build with: bash build.sh
"""
from deck_lib import (content, conclusions, dark, img, labelled_node, line, node, outline, p,
                      recap, sbox, table_slide, title, write)

NAVY, TEAL, AMBER, PURPLE, RED, MAROON = "#1F3A5F", "#2A8C8C", "#C47F17", "#6B4C9A", "#C0282D", "#500000"
R3 = "docs/results/2026-11-11-round3.md"
WSUM = "experiments/e1_surrogate_head/results/write_arm/summary.json"
BOSUM = "experiments/e1_surrogate_head/results/bo_select/summary_init5_steps25_seeds20.json"
BNN = "experiments/e5_bnn_start/results/bnn_summary.json"


def fig(name, box=None, bx=510, by=110, bw=186, x=24, y=60, w=478, h=322):
    out = img(name, x, y, w, h, halign="left", valign="middle")
    if box:
        out += "\n" + sbox(bx, by, bw, box, size=12.5, lh=17)
    return out


def mono(x, y, w, lines, size=10.5, lh=13.2):
    return "\n".join(
        p("small", x, y + i * lh, w, t, f"font-family:'Courier New',monospace;font-size:{size}pt;line-height:{lh}pt;color:#1F1F1F;white-space:nowrap;")
        for i, t in enumerate(lines))


# ------------------------------------------------------------------ title
title("Weight-Space Programming for Materials Science: The GP Prior Case", "Group meeting, Arróyave group",
      "Sk Md Ahnaf Akif Alvi", "November 2026", ["Sk Md Ahnaf Akif Alvi, Raymundo Arróyave"], """
Good afternoon. This talk covers one case of a larger project on weight-space programming for materials science. A language model writes every weight of a small neural network from what it knows about alloys, with no training data, and I use that network as the prior mean of a Gaussian-process surrogate in Bayesian optimisation. I will set out the problem, define the idea, go through the method step by step, list the controls, and then show the results on five alloy tasks with four models, including the task where it makes things worse. I close with an extension to Bayesian neural networks and with what has not been run.
""")

# ------------------------------------------------------------------ 1. problem
outline(1, """The first section states the problem. A Gaussian process is the usual surrogate in Bayesian optimisation of materials, and a campaign starts with a handful of labelled alloys. I will show how well the plain Gaussian process ranks unseen alloys at 5, 10, 20 and 50 labels on the five tasks used in this talk, and what it gets wrong even with its full training set: it underpredicts the best candidates and its intervals are too narrow in places.""")

content("gp-few-labels", "GP surrogates with few labels", 1,
        fig("gp_rho_vs_labels.png", ["Plain GP, ρ on held-out alloys", "5 labels: 0.06 to 0.63", "10 labels: 0.26 to 0.58", "50 labels: 0.65 to 0.78", "mean of 5 data seeds"]), """
The horizontal axis is the number of labelled alloys given to the Gaussian process, and the vertical axis is the Spearman rank correlation between its predictions and the measured values on held-out alloys, averaged over five data seeds. Each line is one of the five alloy tasks. With 5 labels the correlation runs from 0.06 on hardness of multi-principal-element alloys to 0.63 on titanium hardness. With 50 labels it is 0.65 to 0.78. The acquisition function ranks candidates with this model, so the first steps of a campaign are taken with a surrogate that orders alloys poorly. The model here is a constant-mean Gaussian process fitted by marginal likelihood.
""", source=WSUM + " (gp at n5, n10, n20, n50)")

table_slide("gp-baseline-table", "Baseline GP: coverage and top-decile bias", 1,
            [["Task", "Train / test", "R²", "Spearman ρ", "95% coverage", "Top-decile bias"],
             ["Closed-loop bulk modulus (ORB embeddings)", "500 / 82", "0.81 ± 0.07", "0.88 ± 0.07", "0.79 ± 0.09", "−27.4 ± 5.7 GPa"],
             ["Closed-loop heat capacity (ORB embeddings)", "445 / 35", "0.74 ± 0.16", "0.83 ± 0.05", "0.85 ± 0.06", "−0.120 ± 0.094 J/g/K"],
             ["MPEA yield strength (atomic fractions)", "200 / 522", "0.55 ± 0.06", "0.78 ± 0.02", "0.91 ± 0.01", "−547 ± 58 MPa"],
             ["Ti alloy Young's modulus (atomic fractions)", "120 / 117", "0.59 ± 0.07", "0.75 ± 0.08", "0.89 ± 0.03", "−16.6 ± 6.8 GPa"],
             ["Matbench log bulk modulus (PCA)", "500 / 10,487", "0.57 ± 0.02", "0.79 ± 0.01", "0.93 ± 0.01", "−0.134 ± 0.012"]],
            [3.13, 1.1, 1.05, 1.15, 1.2, 1.7], 11.5, 24, 78, 672, 150, """
This table gives the plain Gaussian process with its full training set on five tasks, as mean and standard deviation over five seeds. The last column is the mean of predicted minus true over the test rows whose true value is in the top tenth. It is negative on every task: the best candidates are underpredicted, by 547 megapascals on alloy yield strength and 16.6 gigapascals on titanium modulus. Part of that is what any regression does to extreme values. The 95 percent intervals cover 79 and 85 percent of the test rows on the two closed-loop tasks, where the test structures come from a generator, and 89 to 93 percent on the random splits.
""", cap="Top-decile bias: mean of (predicted − true) over the test rows whose true value is in the top tenth. Five seeds, mean ± standard deviation.",
            source="experiments/e1_surrogate_head/results/baseline_table.md; docs/results/2026-11-11-e1-pilot.md, Sec. 2")

recap("recap-problem", 1, "With 5 labels the plain GP ranks held-out alloys at ρ 0.06 to 0.63, and with its full training set it still underpredicts the top tenth on every task.", """
The problem in one sentence: at the start of a campaign the surrogate has almost no ranking information, and the constant prior mean carries none. Anything that supplies a trend before the first measurement could help exactly where the Gaussian process is weakest. The question for the rest of the talk is whether a language model can supply that trend as a network, written directly as weights, and whether the gain in ranking carries into the optimisation loop.
""", source=WSUM)

# ------------------------------------------------------------------ 2. WSP
outline(2, """The second section defines weight-space programming and places our use of it. I will give the definition in the narrow sense used in this project, the sizes of network for which it has been reported to work, and the size of the object we ask a model to write. The idea is recent and has no peer-reviewed paper yet, so I will be explicit about what is established elsewhere and what is tested only here.""")

WSP = [("Definition", "Narrow sense", MAROON,
        "A language model reads, writes or edits a network's weights directly, as numbers in text, with no gradient descent."),
       ("Reported sizes", "Blog post, 2 Nov 2026", NAVY,
        "Edited as raw text, no tools: 171,664 weights. Written from zero in one reply, no tools: about 20,500 weights."),
       ("This work", "GP prior mean", TEAL,
        "A d → 16 → 1 network on element fractions: 273 to 417 weights, written with no data and no tools.")]


def wsp(step):
    out = []
    for k in range(step):
        head, kicker, col, body = WSP[k]
        x = 30 + k * 224
        out.append(labelled_node(x, 110, 204, 150, head, body, col, kicker))
        if k:
            out.append(line(x - 20, 184, 20, 1.5))
    if step == 3:
        out.append(p("cap", 30, 284, 660, "Targets reported so far are classifiers, policies and language models; none is a regressor with an uncertainty estimate.", "font-size:13pt;"))
    out.append(p("cite", 300, 368, 396, "Takehi, Teoh, Zhang and Khattab, MIT CSAIL blog post, 2 November 2026"))
    return "\n".join(out)


WSP_NOTES = ["""Weight-space programming, in the narrow sense I use throughout, means that a language model reads, writes or edits the weights of a network directly. The weights are given and returned as numbers in text, and no gradient descent is involved. The term was introduced by Takehi, Teoh, Zhang and Khattab at MIT CSAIL in a blog post of 2 November 2026. I keep this apart from the broad family of weight-space learning, such as hypernetworks, task vectors and model merging, which this talk does not cover. There are preprints on the idea and no peer-reviewed paper.""",
             """The sizes reported by the authors set the envelope. Editing raw weights as text with no tools was shown on a policy network of 171,664 weights, with 3.5 percent of them changed. Writing a network from zero in a single reply with no tools was shown at about 20,500 weights, on small game-playing policies. With a Python sandbox and up to 50 forward passes the reported sizes are larger. These numbers come from the blog post, and I have not reproduced them. They tell us that a network of a few hundred weights is well inside what has been claimed.""",
             """Our object is small. The prior mean of the surrogate is a network with one hidden layer of 16 units on element atomic fractions. For the titanium tasks it has 15 inputs and 273 weights; for the multi-principal-element tasks it has 22 or 24 inputs and 385 or 417 weights. The model writes all of them from materials knowledge, with no data and no tools. What is new relative to the published targets is the setting: a regressor that feeds an uncertainty-aware surrogate. Every earlier target was a classifier, a policy or a language model."""]
for j in range(1, 4):
    content(f"wsp-{j}", "Weight-space programming", 2, wsp(j), WSP_NOTES[j - 1], kind="build",
            source="docs/research-runs/2026-11-11-where-wsp-fits.md, Sec. 1 and 2; src/wsp/tasks.py")

# ------------------------------------------------------------------ 3. method
outline(3, """The third section is the method. I start with the five alloy tasks and their data, then walk through the pipeline: the prompt, the written network with one real example, how the network enters the Gaussian process as a prior mean with two rules for its slope, how one prior is selected from the first labels, and the optimisation loop with its acquisition function, seeds and statistics.""")

table_slide("tasks-table", "The five alloy tasks", 3,
            [["Task", "Data source", "Alloys", "Inputs (atomic)", "Target and goal", "Best in pool", "Weights"],
             ["Ti alloy Young's modulus", "Salvador et al., Sci. Data (2022)", "237", "15 fractions", "Young's modulus, minimise", "45 GPa", "273"],
             ["Ti alloy yield strength", "Salvador et al. (2022)", "271", "15 fractions", "yield strength, maximise", "1,880 MPa", "273"],
             ["Ti alloy hardness", "Salvador et al. (2022)", "152", "15 fractions", "Vickers hardness, maximise", "560 HV", "273"],
             ["MPEA hardness", "Borg et al., Sci. Data (2020)", "530", "22 fractions", "Vickers hardness, maximise", "1,183 HV", "385"],
             ["MPEA yield strength", "Borg et al. (2020)", "722", "24 fractions", "yield strength at room T, maximise", "3,416 MPa", "417"]],
            [1.75, 2.1, 0.6, 1.15, 2.2, 0.85, 0.68], 11.5, 24, 78, 672, 140, """
All five tasks use measured alloys with element atomic fractions as inputs, so every input has a name a model can reason about. Three come from the titanium alloy set of Salvador and co-workers and two from the multi-principal-element alloy set of Borg and co-workers. Elements that appear in fewer than four or five alloys are summed into one input called other, and each row sums to one. The pool sizes run from 152 to 722 alloys. The goal is the lowest modulus for titanium implants and the highest strength or hardness elsewhere. The last column is the number of weights in the network the model must write.
""", cap="Salvador et al., Sci. Data 9:188 (2022); Borg et al., Sci. Data 7:430 (2020). Rare elements are summed into one 'other' input; each row sums to 1. Ranking tests hold out 52 to 522 alloys; BO uses the whole set as the pool.",
            source="src/wsp/tasks.py; experiments/e1_surrogate_head/run_bo_select.py (GOALS)")

PIPE = [("Prompt", "Step 1", MAROON, "Task in words, input names, an all-zero d → 16 → 1 network. No data."),
        ("Written network", "Step 2", NAVY, "The model returns every weight as text; three replies per model and task."),
        ("GP prior mean", "Step 3", TEAL, "Mean a·m(x) + b; the GP models what the network leaves over."),
        ("Selection", "Step 4", AMBER, "At each step the reply most correlated with the labels so far; none below r = 0.3."),
        ("BO loop", "Step 5", PURPLE, "5 initial labels, 25 steps of expected improvement, 20 seeds.")]


def pipe(step):
    out = []
    for k in range(step):
        head, kicker, col, body = PIPE[k]
        x = 28 + k * 134
        out.append(labelled_node(x, 120, 122, 150, head, body, col, kicker))
        if k:
            out.append(line(x - 12, 194, 12, 1.5))
    return "\n".join(out)


PIPE_NOTES = ["""The pipeline has five steps, and I add them one at a time. The first is the prompt. It describes the task in words, lists the inputs by name in their order, and shows a network of the right shape with every weight set to zero. It contains no training data, no examples of alloys and no measured values. It asks for the weights back in the same text format. The same prompt is given to each of four models: Opus 5.5, Fable 5.2, Sonnet 5.5 and Haiku 5.5.""",
              """The second step is the reply. The model returns the full set of weights as text, and a parser loads them into the network. A reply with the wrong number of entries is rejected and changes nothing. Each model answers the identical prompt three times in separate fresh sessions, because replies are not deterministic. That gives 60 replies over five tasks and four models. The model may not run code, use a calculator or read any other file, and its tool calls are audited from the session transcript afterwards.""",
              """The third step puts the written network into the surrogate. The network's output, which I call m of x, becomes the mean function of the Gaussian process after an affine rescaling with a slope a and an offset b. The Gaussian process then models the residual, which is what the written network leaves unexplained, and the predictive uncertainty is the Gaussian process's own. I come back to the two rules for the slope in a moment.""",
              """The fourth step chooses among the replies. An arm has several candidate priors, for example the three replies of one model. At every step of the optimisation I compute the Pearson correlation between each candidate's output and the labels seen so far, and take the candidate with the highest correlation. If no candidate reaches 0.3, that step uses the plain Gaussian process with no prior. This rule was fixed and committed before the run.""",
              """The fifth step is the loop. Each run starts from 5 randomly chosen labelled alloys, the same 5 for every arm of a seed, and then labels 25 more, one at a time, by expected improvement over the pool. There are 20 seeds. I report regret, the gap between the best alloy in the pool and the best found so far, and its mean over the 25 steps, which I call the area under the regret curve. The next slides take each step in detail."""]
for j in range(1, 6):
    content(f"pipeline-{j}", "Method: from prompt to BO loop", 3, pipe(j), PIPE_NOTES[j - 1], kind="build",
            source="src/wsp/arms.py; experiments/e1_surrogate_head/run_bo_select.py; experiments/e1_surrogate_head/WRAPPER.md")

recap("recap-pipeline", 3, "A network written with no data becomes the GP mean a·m(x) + b; the first labels choose among replies, and a reply correlated below 0.3 is not used.", """
That is the whole method. Two properties matter for what follows. The Gaussian process keeps its own uncertainty, so the written network changes the mean and not the kernel. And the labels have two ways to reject a bad prior: the selection threshold drops it, and a fitted slope near zero switches it off. The next slides show the actual prompt, an actual reply, and the equations.
""", source="src/wsp/arms.py; experiments/e1_surrogate_head/run_bo_select.py")

content("architecture", "Architecture of the written network", 3,
        img("network_architecture.png", 24, 60, 672, 282, halign="center", valign="middle") + "\n" +
        sbox(24, 346, 672, ["h1 = relu(net.0.weight · x + net.0.bias);   y = net.2.weight · h1 + net.2.bias;   15 → 16 → 1,  273 weights  (MPEA tasks: 385 and 417)"], size=12, lh=16, pad=6), """
This is the network the model writes, drawn for the titanium modulus task. On the left are the 15 inputs with the names the prompt gives them: the atomic fractions of fourteen elements and one input for all other elements. In the middle is one hidden layer of 16 ReLU units, and on the right a single linear output in gigapascals. The four tensors carry the names used in the prompt: a 16 by 15 weight matrix, 16 biases, 16 output weights and one output bias, 273 numbers in total. Colour shows what one reply of Opus 5.5 filled in: unit zero as a rule of mixtures and units one to four as hinges on a beta-stability index.
""", source="src/wsp/heads.py (MLPHead); src/wsp/arms.py (WRITE_HIDDEN, write_prompt); src/wsp/tasks.py; experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1/ (reply.txt, self_report.txt)")

CHAIN = [("Alloy x", "Input", NAVY, "15 to 24 atomic fractions of a candidate in the pool"),
         ("Written network", "m(x)", MAROON, "d → 16 → 1 ReLU network; weights fixed as written, never trained"),
         ("GP mean", "a·m(x) + b", TEAL, "a and b from least squares on the labelled alloys"),
         ("GP posterior", "mean and std", AMBER, "exact GP on the residual y − (a·m(x) + b); mean adds a·m(x) + b back"),
         ("Expected improvement", "Acquisition", PURPLE, "computed for every unlabelled alloy; the highest is labelled next")]
content("surrogate-chain", "The written network inside the surrogate", 3,
        "\n".join(labelled_node(28 + k * 134, 72, 122, 146, h, b, c, kk) + ("\n" + line(16 + k * 134, 144, 12, 1.5) if k else "")
                  for k, (h, kk, c, b) in enumerate(CHAIN)) + "\n" +
        line(89, 218, 1.5, 22) + "\n" + line(89, 240, 537, 1.5) + "\n" + line(625, 218, 1.5, 22) + "\n" +
        p("small", 150, 245, 420, "the new label joins the labelled set; a, b and the GP are refitted at every step", "text-align:center;font-size:12pt;line-height:15pt;") + "\n" +
        sbox(150, 274, 420, ["the written weights are never updated by the labels", "the labels enter through a, b and the GP on the residual", "uncertainty comes from the GP alone"], size=13, lh=18), """
This slide places that network inside the surrogate. A candidate alloy enters as its vector of atomic fractions. The written network maps it to m of x, a property estimate in physical units, and its weights stay exactly as the model wrote them. The Gaussian process takes a times m of x plus b as its mean, with a and b fitted on the labelled alloys, and models the residual. Its posterior mean and standard deviation go into expected improvement, which is evaluated for every unlabelled alloy in the pool, and the highest one is labelled next. Then the slope, the offset and the Gaussian process are refitted with the new label. The labels never change the written weights.
""", source="src/wsp/arms.py (gp_with_prior); experiments/e1_surrogate_head/run_bo_select.py (trace, expected_improvement)")

PROMPT = ["You are given a small neural network as its raw weights.",
          "You cannot run it and you cannot train it.",
          "# Task",
          "Write the weights of this network from what you know about materials.",
          "No training data is given. Inputs are atomic fractions of Al, Cr, Cu, Fe, Hf,",
          "Mn, Mo, Nb, Si, Sn, Ta, Ti, V, Zr, and the summed fraction of all other",
          "elements; each row sums to 1. The target is Young's modulus in GPa. [...]",
          "The network will be used as the prior mean of a Gaussian process that is then",
          "given a few measured alloys, so getting the trends and the rough scale right",
          "matters more than exact values.",
          "# Architecture",
          "Input x has 15 entries. h0 = x.",
          "h1 = relu(net.0.weight @ h0 + net.0.bias)   (net.0.weight is 16 x 15 ...)",
          "y = net.2.weight @ h1 + net.2.bias   (net.2.weight is 1 x 16 ...)",
          "# Weights",
          "## net.0.weight shape=(16, 15)",
          "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0      [16 rows of zeros, then biases and output layer]",
          "# Reply format",
          "Reply with the complete weights in exactly the format shown above [...]"]
content("prompt", "The prompt: Ti alloy Young's modulus", 3,
        node(24, 62, 520, 266, "#8A8F98", 1) + "\n" + mono(32, 68, 506, PROMPT) + "\n" +
        sbox(554, 62, 142, ["2,021 characters", "no data rows", "inputs named", "zero network", "same for 4 models"], size=12.5, lh=17) + "\n" +
        p("small", 24, 336, 672, "Excerpt of the prompt as sent; [...] marks text left out here. The other four tasks differ only in the inputs, target and data source."), """
This is the prompt for the titanium modulus task, shortened where the brackets show. It names the fifteen inputs in order, states the target and its unit, and names the data set and its size. It tells the model what the network is for: a prior mean for a Gaussian process, so trends and rough scale matter more than exact values. Then it gives the architecture as two lines of algebra and the network itself with every weight at zero, and asks for the complete weights back in the same format with no other text. The full prompt is 2,021 characters. No alloy and no measured value appears in it.
""", source="experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1/prompt.txt; meta.json; src/wsp/arms.py (write_prompt)")

RUNP = [("Read", "1", NAVY, "The model reads prompt.txt once."),
        ("Think", "2", NAVY, "No code, no calculator, no web, no other file."),
        ("Reply", "3", NAVY, "It writes reply.txt: weights only, in the given format."),
        ("Self-report", "4", NAVY, "Two to four sentences on how it arrived at the reply."),
        ("Audit", "After", RED, "Tool calls checked from the session transcript.")]
content("run-protocol", "Run protocol for a model", 3,
        "\n".join(labelled_node(28 + k * 134, 96, 122, 124, h, b, c, kk) + ("\n" + line(16 + k * 134, 158, 12, 1.5) if k else "")
                  for k, (h, kk, c, b) in enumerate(RUNP)) + "\n" +
        sbox(170, 250, 380, ["60 write runs: 15 per model, each a fresh session", "0 forward passes, 0 training rows", "all 60 passed the tool-call audit", "3 replies invalid: wrong row length, rejected"], size=13, lh=18), """
Each run is a fresh session of one model with no memory of other runs. The model reads the prompt file once, does the task by reasoning alone, writes the reply file, and writes a short self-report of how it arrived at the reply. It is told not to run code, use a calculator, search the web or open any other file. After the run the tool calls are read from the session transcript and checked against that rule. The restriction is by instruction and audit; it is not a sandbox. All 60 write runs passed. Three replies had rows of the wrong length and were rejected by the parser: two from Sonnet 5.5 and one from Haiku 5.5.
""", source="experiments/e1_surrogate_head/WRAPPER.md; experiments/runs_audit.json; experiments/e1_surrogate_head/results/write_arm/per_run.json")

REPLY = ["## net.0.weight shape=(16, 15)",
         "2.16 4.06 2.36 4.06 1.06 4.06 3.06 1.46 2.56 0.36 2.06 1.56 2.06 0.96 2.56",
         "-5.6 17.3 6.0 34.0 0 19.5 20.0 5.4 0 10.0 8.3 0 7.1 0 5.0",
         "-5.6 17.3 6.0 34.0 0 19.5 20.0 5.4 0 10.0 8.3 0 7.1 0 5.0",
         "-5.6 17.3 6.0 34.0 0 19.5 20.0 5.4 0 10.0 8.3 0 7.1 0 5.0",
         "-5.6 17.3 6.0 34.0 0 19.5 20.0 5.4 0 10.0 8.3 0 7.1 0 5.0",
         "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0            [11 rows of zeros]",
         "## net.0.bias shape=(16,)",
         "0 0 -0.5 -1.2 -1.6 0 0 0 0 0 0 0 0 0 0 0",
         "## net.2.weight shape=(1, 16)",
         "100 -50 20 30 20 0 0 0 0 0 0 0 0 0 0 0",
         "## net.2.bias shape=(1,)",
         "-50"]
content("reply-text", "A written network: the reply of Opus 5.5", 3,
        node(24, 62, 520, 184, "#8A8F98", 1) + "\n" + mono(32, 68, 506, REPLY) + "\n" +
        sbox(554, 62, 142, ["273 weights", "5 of 16 units used", "ρ alone: 0.66", "RMSE: 19.8 GPa", "229 s, 0 passes"], size=12.5, lh=17) + "\n" +
        p("lab", 24, 256, 672, "The model's own account (self-report, not verified beyond the scored reply)") + "\n" +
        p("small", 24, 276, 672, "Unit 0: rule of mixtures, pure Ti at 106 GPa, a slope per element in GPa per at% (Fe, Cr, Mn +2.5; Mo +1.5; Sn −1.2). "
          "Units 1 to 4: ReLUs sharing one beta-stability index, a molybdenum equivalent (Mo 2.0, Fe 3.4, Cr 1.73, Nb 0.54, Al −0.56), "
          "with hinges at 0, 5, 12 and 16: a piecewise-linear drop toward a metastable-beta minimum near 60 GPa, a plateau, "
          "then a rise for strongly stabilised beta.", "font-size:11.5pt;line-height:14.5pt;"), """
This is the reply of Opus 5.5 to that prompt, first of three, with the eleven all-zero rows collapsed. Five of the sixteen hidden units are used. In its self-report the model describes unit zero as a rule of mixtures that starts from pure titanium at 106 gigapascals, and units one to four as hinges on a molybdenum-equivalent index of beta stability, which together make the modulus fall toward a minimum near 60 gigapascals and rise again. That is the textbook picture of low-modulus beta titanium alloys. With no labels this network ranks the held-out alloys at a Spearman correlation of 0.66, with a root-mean-square error of 19.8 gigapascals.
""", source="experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1/ (reply.txt, self_report.txt, score.json, meta.json)")

content("reply-weights", "A written network: first-layer weights", 3,
        img("written_network_weights.png", 24, 62, 672, 262, halign="center", valign="middle") + "\n" +
        sbox(24, 332, 672, ["Opus 5.5, Ti Young's modulus, reply 1: units 1 to 4 share one row (Fe 34, Mo 20, Mn 19.5, Cr 17.3, Al −5.6) and differ only in bias"], size=12, lh=16, pad=6), """
The same reply drawn as a matrix. Columns are the fifteen element fractions, rows are the five hidden units the model used, and the two narrow columns on the right are each unit's bias and its output weight. Red is positive and blue is negative. Units one to four carry the identical row of weights: iron 34, molybdenum 20, manganese 19.5, chromium 17.3, and aluminium minus 5.6, which is the sign an alpha stabiliser should have. They differ only in bias, 0, minus 0.5, minus 1.2 and minus 1.6, so they switch on at successive values of the index. The output weights of minus 50, then plus 20, 30 and 20, make the curve fall and then turn up.
""", source="experiments/e1_surrogate_head/runs/write__ti_alloy_youngs_modulus__opus__rep1/reply.txt")

GPM = [(24, 70, 672, 62, "Prior mean", MAROON, "μ(x) = a · m(x) + b,   where m(x) is the written network's output in physical units"),
       (24, 144, 672, 78, "GP on the residual", NAVY,
        "r = y − (a · m(x) + b) on the labelled alloys;  exact GP fitted to r by marginal likelihood;<br>prediction = GP mean of r + a · m(x) + b;  predictive standard deviation = the GP's own"),
       (24, 234, 330, 128, "Slope fitted", TEAL,
        "a and b by least squares on the labelled alloys.<br>An uninformative network drives a toward 0,<br>which gives back the constant-mean GP.<br>Unstable on about ten rows."),
       (366, 234, 330, 128, "Slope fixed at one", AMBER,
        "a = 1;  b = mean of y − m(x).<br>Trusts the scale of the written network.<br>Only the offset is taken from the labels.")]


def gpm(step):
    out = []
    n = {1: 2, 2: 4}[step]
    for (x, y, w, h, head, col, body) in GPM[:n]:
        out.append(node(x, y, w, h, col, 2))
        out.append(p("lab", x + 10, y + 6, w - 20, head, f"color:{col};"))
        out.append(p("cap", x + 10, y + 26, w - 20, body, "font-size:13pt;line-height:17pt;color:#1F1F1F;"))
    return "\n".join(out)


GPM_NOTES = ["""The written network enters the Gaussian process as its mean function. I write m of x for the network's output, which is already in physical units. The mean is a times m of x plus b, so the labelled alloys can correct the scale and level of what the model wrote while keeping its ordering. I subtract that mean from the labels and fit an exact Gaussian process to the residual: a single-task Gaussian process from BoTorch, fitted by marginal likelihood. The prediction is the residual mean plus the prior mean, and the standard deviation is the Gaussian process's own. The uncertainty in a and b is not carried into it, which matters later for calibration.""",
             """There are two rules for the slope. With the fitted rule, a and b come from least squares on the labelled alloys. If the written network is uninformative, the fit drives a toward zero and the model reduces to the constant-mean Gaussian process, but two parameters fitted on five or ten points are unstable, and the slope can even come out negative. With the second rule the slope is fixed at one and only the offset is fitted, which trusts the network's scale. I report ranking under both rules; the optimisation loop uses the fitted rule."""]
for j in range(1, 3):
    content(f"gp-mean-{j}", "GP prior mean a·m(x) + b and the two slope rules", 3, gpm(j), GPM_NOTES[j - 1], kind="build",
            source="src/wsp/arms.py (gp_with_prior); src/wsp/baselines.py (fit_gp)")

SEL = [("Candidates", "Per arm", NAVY, "The valid replies of one model (2 or 3), or of all models (11 or 12)."),
       ("Correlation", "Each BO step", TEAL, "Pearson r between each candidate's output and the labels so far."),
       ("Choice", "Threshold 0.3", AMBER, "Highest r is used; if none exceeds 0.3, the plain GP is used."),
       ("Use", "Slope fitted", MAROON, "The chosen reply enters as a·m(x) + b with a, b fitted on the labels.")]
content("selection", "Selection of a prior from the first labels", 3,
        "\n".join(labelled_node(30 + k * 168, 96, 150, 136, h, b, c, kk) + ("\n" + line(12 + k * 168, 164, 18, 1.5) if k else "")
                  for k, (h, kk, c, b) in enumerate(SEL)) + "\n" +
        sbox(150, 262, 420, ["rule fixed and committed before the run", "re-evaluated at every one of the 25 steps", "Opus 5.5 arm: a prior used on 89 to 100% of steps", "handbook rule on Ti hardness: used on 0% of steps"], size=13, lh=18), """
Replies to the same prompt differ, so the method needs a way to choose among them that uses only the labels already measured. An arm holds its candidates: the valid replies of one model, or all valid replies pooled. At each step I compute the Pearson correlation of each candidate's output with the labels so far, in the direction of improvement, and use the one with the highest value. If none exceeds 0.3, that step uses the plain Gaussian process. The rule was fixed before any result of this run was seen. For the Opus 5.5 arm a prior was in use on 89 to 100 percent of steps, depending on the task.
""", source="experiments/e1_surrogate_head/run_bo_select.py (trace, THRESHOLD); " + BOSUM + " (share_of_steps_with_a_prior)")

table_slide("bo-settings", "BO loop, acquisition, seeds and statistics", 3,
            [["Setting", "Value"],
             ["Search", "pool-based: every alloy of the data set is a candidate; a step labels one alloy"],
             ["Initial labels", "5 alloys drawn at random; the same 5 for every arm of a seed"],
             ["Steps and acquisition", "25 steps; expected improvement on the GP posterior, target signed so that higher is better"],
             ["Surrogate", "exact GP (BoTorch SingleTaskGP), refitted at every step, with or without the selected prior mean"],
             ["Seeds", "20 per task and arm"],
             ["Regret", "best value in the pool minus best value found so far"],
             ["Area under regret", "mean regret over steps 1 to 25, one number per seed"],
             ["Test", "paired Wilcoxon signed-rank against the plain GP over the 20 seeds, on the area"],
             ["Correction", "Holm, across the six non-random arms of a task"]],
            [2.1, 7.23], 12, 24, 68, 672, 236, """
These are the settings of the optimisation. It is pool-based: the data set is the pool, and each step reveals the measured value of one alloy. A run starts from 5 random alloys, identical across the arms of a seed, so that differences between arms are paired. Twenty-five steps follow, each choosing the alloy with the highest expected improvement under a Gaussian process refitted at that step. There are 20 seeds per task and arm. The summary number is the area under the regret curve, the mean regret over the 25 steps. Each arm is tested against the plain Gaussian process with a paired Wilcoxon signed-rank test over seeds, Holm-corrected across the six arms within a task.
""", source="experiments/e1_surrogate_head/run_bo_select.py")

# ------------------------------------------------------------------ 4. controls
outline(4, """The fourth section is short: the controls and baselines. There are two questions a control has to answer here. Does the prior help relative to a Gaussian process with no prior and to random search? And does the language model contribute anything beyond a rule of mixtures that a person could type in from a table of elemental properties? I also say which controls the sources do not contain.""")

table_slide("controls-table", "Arms, baselines and controls", 4,
            [["Arm", "Prior mean", "Language model", "Candidates per task"],
             ["Random search", "none; the next alloy is drawn at random", "no", "none"],
             ["Plain GP", "constant; expected improvement", "no", "none"],
             ["Handbook rule of mixtures", "x · elemental table from pymatgen: Young's modulus for the modulus task, Vickers hardness for strength and hardness tasks", "no", "1"],
             ["Opus 5.5, Fable 5.2, Sonnet 5.5, Haiku 5.5 (one arm each)", "that model's valid replies, selected by the labels", "yes", "2 or 3"],
             ["All replies", "every valid reply of every model, selected by the labels", "yes", "11 or 12"],
             ["Written network alone", "no GP: alloys taken in the order of m(x); 8 seeds, two tasks, Fable 5.2 replies", "yes", "1"]],
            [2.5, 4.4, 1.2, 1.23], 11.5, 24, 70, 672, 214, """
Random search and the plain Gaussian process bound the comparison from below. The handbook arm is the control for the language model: a rule of mixtures from pymatgen's elemental tables, Young's modulus for the modulus task and Vickers hardness of the elements for the strength and hardness tasks entering the Gaussian process exactly as a written network does. Then one arm per model, and one arm that pools all valid replies. The last row uses the written network with no Gaussian process at all, in a smaller run of 8 seeds on two tasks. A control with shuffled weights does not apply to this arm, because the model is given a network of zeros and no weights to read.
""", source="experiments/e1_surrogate_head/run_bo_select.py (ARMS, candidates); src/wsp/arms.py (handbook_prior); experiments/e1_surrogate_head/results/bo/")

# ------------------------------------------------------------------ 5. results
outline(5, """The fifth section is the results, in the order of the method. First, how well the written networks rank alloys with no data at all. Second, how a Gaussian process ranks with and without the prior as labels are added, under both slope rules. Third, the optimisation: regret curves and the area under them for all five tasks and four models, with the tests. Then the task where the prior hurts, the agreement between replicate replies, and the cost.""")

content("rho-alone", "Ranking with no data, by model and task", 5,
        fig("rho_alone_bars.png", ["ρ of the prior alone", "Opus 5.5: 0.64 to 0.79", "Fable 5.2: 0.53 to 0.76", "Sonnet 5.5: 0.46 to 0.67", "Haiku 5.5: 0.00 to 0.59", "handbook: −0.75 to 0.27"]), """
Each group of bars is one task. The grey bar is the handbook rule of mixtures and the coloured bars are the four models. The height is the Spearman correlation between the prior alone, with no labels, and the measured values on held-out alloys, averaged over a model's valid replies and five data seeds. The networks written by Opus 5.5 rank alloys at 0.64 to 0.79 on every task, and those of Fable 5.2 at 0.53 to 0.76. Sonnet 5.5 and Haiku 5.5 are weaker: Haiku's titanium hardness networks carry no ranking information, at 0.00. The handbook rule ranges from minus 0.75 to 0.27; on three tasks it orders alloys the wrong way round.
""", source=WSUM + " (alone_spearman)")

content("rho-labels", "GP ranking against labels, with and without the prior", 5,
        fig("rho_vs_labels_slope_fitted.png", ["Slope fitted; ρ at 5 labels", "Ti yield: 0.26 → 0.70 (Opus)", "MPEA HV: 0.06 → 0.66 (Opus)", "Ti HV: 0.63 → 0.34 (Haiku)", "At 50 labels, Opus", "Ti HV: 0.78 → 0.85"], bx=506, bw=190, w=474), """
Each panel is one task. The horizontal axis is the number of labelled alloys and the vertical axis the Spearman correlation on held-out alloys. The dashed black line is the plain Gaussian process; the solid lines add a prior mean with a fitted slope, grey for the handbook rule and one colour per model. With an Opus 5.5 or Fable 5.2 prior the Gaussian process ranks better at 5 and 10 labels on all five tasks: for example 0.26 to 0.70 on titanium yield strength and 0.06 to 0.66 on alloy hardness with Opus. A weak prior can hurt: Haiku's titanium hardness networks lower the correlation at 5 labels from 0.63 to 0.34. By 50 labels the lines converge.
""", source=WSUM + " (n5 to n50: gp, prior_fitted)")

content("bo-ti", "BO regret: titanium alloy tasks", 5,
        fig("bo_regret_ti.png", ["Regret after 25 steps", "Ti modulus, GPa:", "GP 5.6, Opus 1.6, Fable 3.5", "Ti yield strength, MPa:", "GP 114, Opus 17, Fable 0", "Ti hardness: 2 HV by step 5 (Opus)"], bx=500, bw=196, w=470), """
Three panels, one per titanium task: optimisation step on the horizontal axis, regret averaged over 20 seeds on the vertical. The dotted line is random search, the dashed black line the plain Gaussian process, the dash-dotted grey line the handbook rule, and the solid lines the four models. Bands are one standard error. On modulus the Opus arm ends at 1.6 gigapascals against 5.6. On yield strength it ends at 17 megapascals against 114, and Fable reaches zero. On hardness the Opus arm is within 2 units of the best alloy after five steps; the handbook arm coincides with the Gaussian process because its prior never passes the threshold.
""", source="experiments/e1_surrogate_head/results/bo_select/init5_steps25/ti_alloy_*/; " + BOSUM)

content("bo-mpea-hv", "BO regret: MPEA hardness", 5,
        fig("bo_regret_mpea_hardness.png", ["Regret, HV", "after 5 steps:", "GP 296, Opus 178, Fable 118", "after 25 steps:", "GP 112, Opus 94, Fable 99", "Sonnet 147, Haiku 140"], bx=506, bw=190, w=474), """
The same plot for hardness of multi-principal-element alloys, with the same line styles. The Fable 5.2 and Opus 5.5 arms drop fast: after five steps the regret is 118 and 178 Vickers units against 296 for the plain Gaussian process. They then stay near 99 for the rest of the run, and the plain Gaussian process reaches 112 only at the end. Neither arm closes the remaining gap of about 100 units within 25 steps. The Sonnet 5.5 and Haiku 5.5 arms end at 147 and 140, above the Gaussian process. Random search ends at 251.
""", source="experiments/e1_surrogate_head/results/bo_select/init5_steps25/mpea_hardness/; " + BOSUM)

content("auc-ratio", "Area under regret relative to the plain GP", 5,
        fig("auc_relative_to_gp.png", ["Area ÷ plain GP's", "Opus: 0.72, 0.49, 0.15, 0.61", "and 1.17 on MPEA yield", "Fable: 0.90, 0.47, 0.25, 0.53", "and 1.25 on MPEA yield", "Haiku: no significant task"], bx=506, bw=190, w=474), """
This figure puts all five tasks on one scale. Each bar is an arm's mean area under the regret curve divided by the plain Gaussian process's, so one is no change and lower is better. A star marks a Holm-corrected p below 0.05. The Opus 5.5 arm is at 0.72, 0.49, 0.15 and 0.61 on the first four tasks, all with a star, and at 1.17 on yield strength of multi-principal-element alloys. Fable 5.2 has stars on three tasks and is at 1.25 on that last one. Sonnet 5.5 has two stars and Haiku 5.5 none. The handbook rule stays between 0.88 and 1.04 with no star anywhere.
""", source=BOSUM + " (auc_mean, wilcoxon_p_holm)")

table_slide("auc-table", "Area under regret: five tasks, four models", 5,
            [["Task (unit)", "Plain GP", "Handbook", "Opus 5.5", "Fable 5.2", "Sonnet 5.5", "Haiku 5.5", "All replies"],
             ["Ti Young's modulus (GPa)", "7.68", "7.02", "5.55 * (0.004)", "6.92", "7.34", "7.61", "5.41 * (0.004)"],
             ["Ti yield strength (MPa)", "314", "327", "153 * (0.047)", "148 * (0.026)", "216 * (0.043)", "255", "139 * (0.026)"],
             ["Ti hardness (HV)", "40.1", "40.1", "5.95 * (0.003)", "10.0 * (0.003)", "11.3 * (0.003)", "27.2", "6.13 * (0.003)"],
             ["MPEA hardness (HV)", "226", "216", "137 * (0.006)", "120 * (0.006)", "247", "259", "144 * (0.010)"],
             ["MPEA yield strength (MPa)", "772", "676", "900", "966", "735", "641", "935"]],
            [1.93, 0.8, 0.85, 1.2, 1.2, 1.2, 0.95, 1.2], 11.5, 24, 74, 672, 150, """
The same result as numbers. Each cell is the mean area under the regret curve over 20 seeds, in the unit of the task; lower is better. A star marks an arm below the plain Gaussian process with a Holm-corrected p under 0.05, and the p value is in brackets. Opus 5.5 is significant on four of five tasks, with corrected p values from 0.003 to 0.047. Fable 5.2 is significant on three, Sonnet 5.5 on two, Haiku 5.5 on none. The pooled arm, where the labels choose among every model's replies, matches the best single model on four tasks. The bottom row is the exception: there the Opus, Fable and pooled arms are above the plain Gaussian process.
""", cap="Star: lower than the plain GP, Holm-corrected p < 0.05 (in brackets); paired Wilcoxon over 20 seeds. Random search: 8.37, 392, 66.9, 338 and 1,010 in the same row order.",
            source="experiments/e1_surrogate_head/results/bo_select/summary_init5_steps25_seeds20.md")

recap("recap-bo", 5, "Opus 5.5 priors lower the area under regret on 4 of 5 tasks (Holm p ≤ 0.047), Fable 5.2 on 3, Sonnet 5.5 on 2, Haiku 5.5 on none; the handbook rule on none.", """
On the four tasks where it works, the benefit is consistent across seeds: the Opus arm is better than the plain Gaussian process in 12 to 16 of 20 seeds. The pooled arm shows that the selection rule protects against the weaker models' replies on those tasks. The fifth task goes the other way, and I show it separately now, because the static ranking results did not predict it.
""", source="experiments/e1_surrogate_head/results/bo_select/summary_init5_steps25_seeds20.md")

content("mpea-ys-regret", "MPEA yield strength: BO regret", 5,
        fig("bo_regret_mpea_yield_strength.png", ["Area under regret, MPa", "plain GP: 772", "Opus 5.5: 900", "Fable 5.2: 966", "Haiku 5.5: 641", "handbook: 676"], bx=506, bw=190, w=474), """
This is the task where the prior fails. Same axes and line styles as before, for yield strength of multi-principal-element alloys, where the best alloy in the pool is at 3,416 megapascals. From about step 10 the plain Gaussian process, the dashed black line, moves ahead of the Opus 5.5 and Fable 5.2 arms and stays ahead until the last steps. The area under the curve is 772 megapascals for the plain Gaussian process, 900 with Opus priors and 966 with Fable priors. The arms that do better here are the weak ones: Haiku 5.5 at 641 and the handbook rule at 676, neither significant. Random search is at 1,010.
""", source="experiments/e1_surrogate_head/results/bo_select/init5_steps25/mpea_yield_strength/; " + BOSUM)

content("mpea-ys-seeds", "MPEA yield strength: differences by seed", 5,
        fig("auc_seed_differences_mpea_yield_strength.png", ["Opus: 4 better, 14 worse", "p 0.033, Holm 0.149", "Fable: 4 better, 14 worse", "p 0.018, Holm 0.106", "ρ at 5 labels still rose:", "0.40 → 0.66 with Opus"], bx=506, bw=190, w=474), """
Each dot is one seed: an arm's area under regret minus the plain Gaussian process's for the same initial labels, so a dot above zero is a seed where the prior hurt. The black bar is the mean. For both the Opus 5.5 and the Fable 5.2 arm, 4 seeds are better and 14 are worse. The uncorrected p values are 0.033 and 0.018; after Holm correction they are 0.149 and 0.106, so the harm is not significant. The same networks improved static ranking on this task, from 0.40 to 0.66 at 5 labels. The cause is not diagnosed. One candidate: the best alloys in this pool are outliers that a smooth written trend ranks low.
""", source=BOSUM + " (seeds_better_than_gp, seeds_worse_than_gp, wilcoxon_p, wilcoxon_p_holm); " + R3 + ", Sec. 2")

recap("recap-mpea-ys", 5, "On MPEA yield strength the Opus 5.5 and Fable 5.2 arms are worse than the plain GP in 14 of 20 seeds (Holm p 0.149 and 0.106), although the same networks raise static ranking. The cause is not diagnosed.", """
I take two things from this. A gain in rank correlation on held-out alloys did not predict a gain in the optimisation here, so ranking alone is not a sufficient test of a prior. And the selection rule did not protect this task: it checks correlation with the labels so far, and these priors do correlate with them. Until the cause is found, a written prior should be run beside a plain Gaussian process, not in place of it.
""", source=R3 + ", Sec. 2")

content("replicates", "Agreement across replicate replies", 5,
        fig("replicate_replies.png", ["Range of ρ over a model's replies", "Opus: ≤ 0.05 on 4 tasks,", "0.57 to 0.72 on Ti hardness", "Haiku, Ti hardness: −0.15 to 0.10", "3 of 60 replies invalid", "(Sonnet 2, Haiku 1)"], bx=500, bw=196, w=470), """
Each model answered the identical prompt three times. Every dot is one valid reply: its Spearman correlation alone, with no labels, averaged over five data seeds. Groups are tasks and colours are models; a vertical line joins a model's replies. For Opus 5.5 the three replies lie within 0.05 of each other on four tasks, and spread from 0.57 to 0.72 on titanium hardness. Fable 5.2 spreads by at most 0.10. Haiku 5.5 on titanium hardness scatters around zero, from minus 0.15 to 0.10. Three of the 60 replies were invalid, with rows of the wrong length, two from Sonnet 5.5 and one from Haiku 5.5; they were rejected and are not candidates.
""", source=WSUM + " (alone_spearman_per_reply); experiments/e1_surrogate_head/results/write_arm/per_run.json (invalid)")

content("cost", "Cost of a written network", 5,
        fig("cost_per_reply.png", ["Median per reply", "Opus 5.5: 73 k tokens, 229 s", "Fable 5.2: 9.4 k tokens, 47 s", "Sonnet 5.5: 5.8 k tokens, 16 s", "Haiku 5.5: 12 k tokens, 21 s", "0 forward passes, 0 labels"], bx=500, bw=196, w=470), """
The left panel is output tokens per reply in thousands and the right panel is wall-clock seconds per reply. Each bar is the median of a model's 15 write runs and the whisker runs from the smallest to the largest. Output tokens include the model's reasoning. Opus 5.5 used a median of 73 thousand output tokens and 229 seconds, with a maximum of 119 thousand and 373 seconds. Fable 5.2 used 9.4 thousand tokens and 47 seconds; Sonnet 5.5 and Haiku 5.5 took 16 and 21 seconds. Prompt and reply tokens were not counted separately with the model's tokenizer. A prior is written once per task, before any measurement.
""", source="experiments/runs_audit.json (write__ runs: output_tokens, duration_ms)")

# ------------------------------------------------------------------ 6. BNN
outline(6, """The sixth section asks whether the same written network helps a Bayesian neural network. A written network can be used in three ways there: as a prior mean in function space, as it was for the Gaussian process; as the starting point of training or of a sampling chain; or as the centre of a prior over the weights. I compare the three on MC dropout, a deep ensemble and Hamiltonian Monte Carlo, with ranking and 95 percent coverage as the measures.""")

content("bnn-ranking", "BNN extension: prior mean, start or weight prior", 6,
        fig("bnn_ranking.png", ["ρ at 10 or 20 labels", "GP: 0.53 → 0.69 (prior mean)", "MC dropout: 0.54 → 0.65", "ensemble start: 0.50 → 0.57", "HMC start: 0.45 → 0.40", "HMC weight prior: 0.21"], bx=506, bw=190, w=474), """
Each bar is the mean Spearman correlation over model and task cells: the Opus 5.5 and Fable 5.2 networks on six tasks, the five alloy tasks and Matbench bulk modulus. The left panel is 10 or 20 labels and the right panel 50 or 200. Pale bars are each family's baseline and dark bars use the written network. As a prior mean the network helps at few labels: the Gaussian process goes from 0.53 to 0.69 and MC dropout from 0.54 to 0.65. As a starting point it does not improve MC dropout, gives a deep ensemble 0.50 to 0.57, and gives Hamiltonian Monte Carlo nothing. Centring the weight prior on it is the worst arm, at 0.21.
""", source=BNN + " (spearman); docs/results/2026-11-11-round4.md, Sec. 3")

content("bnn-coverage", "BNN extension: 95% interval coverage", 6,
        fig("bnn_coverage.png", ["Coverage at 10 or 20 labels", "GP: 0.71 → 0.66 (prior mean)", "MC dropout: 0.45 → 0.39", "MC dropout, start: 0.88", "HMC: 0.90 to 0.94", "nominal: 0.95"], bx=506, bw=190, w=474), """
The same arms, now with the share of held-out values that fall inside the 95 percent interval; the dashed line marks 0.95. This is the caveat on the prior mean. At 10 or 20 labels the plain Gaussian process already covers only 0.71, and with the written prior mean it covers 0.66. MC dropout goes from 0.45 to 0.39. The slope and offset of the prior are fitted on the same few labels, and that uncertainty is not propagated into the interval. Starting MC dropout at the written weights does the opposite: ranking does not improve but coverage rises from 0.45 to 0.88. Hamiltonian Monte Carlo is near nominal in every arm at few labels.
""", source=BNN + " (coverage95); docs/results/2026-11-11-round4.md, Sec. 3")

recap("recap-bnn", 6, "As a prior mean the written network raises ranking at 10 to 20 labels (GP 0.53 → 0.69, MC dropout 0.54 → 0.65) but the intervals are overconfident (coverage 0.66 and 0.39); as a weight-space prior for HMC it is the worst arm (ρ 0.21).", """
The written networks use three to seven hidden units with large weights. A unit-variance prior centred on them pins the rest of the network at zero, and the chain cannot use the data, which explains the weight-prior result. The Hamiltonian Monte Carlo here follows the study of Li, Rudner and Wilson and is a small implementation: fixed noise level, one chain, 200 kept samples. The useful place for the written network is the function-space mean, and its calibration needs work.
""", source="docs/results/2026-11-11-round4.md, Sec. 3")

# ------------------------------------------------------------------ 7. limits
outline(7, """The last section states the limits of the evidence and what has not been run, and then closes. I separate three kinds of limit: the scope of what was tested, the known faults of the method as it stands, and the comparisons that are missing. The closing slide then summarises what was done, what was found and what comes next.""")

table_slide("limits", "Limits and what is not yet run", 7,
            [["Kind", "Limit"],
             ["Scope", "one pool per task; pool-based BO on existing measurements, no real closed loop"],
             ["Scope", "four models from one vendor; three replies per model and task"],
             ["Scope", "inputs are named element fractions; no structure-based surrogate, where inputs have no names"],
             ["Known fault", "MPEA yield strength: Opus 5.5 and Fable 5.2 priors worse than the plain GP in 14 of 20 seeds; cause not diagnosed"],
             ["Known fault", "intervals overconfident with the prior mean at few labels (coverage 0.66 against 0.71); slope and offset uncertainty not propagated"],
             ["Known fault", "fitted slope unstable on 5 to 10 labels; weak priors (Haiku 5.5, Ti hardness) lower ranking"],
             ["Not run", "a mean network of the same shape fitted by gradient descent on the first labels"],
             ["Not run", "prompt and reply tokens from the model's tokenizer; tool use limited by instruction and audit, not by a sandbox"],
             ["Not run", "for the BNNs: SGHMC, linearised Laplace, a tuned HMC"]],
            [1.3, 8.03], 11.5, 24, 66, 672, 262, """
These are the limits. On scope: each task has one pool of existing measurements, so this is a retrospective benchmark and not a closed loop; the four models come from one vendor; and the inputs are named element fractions, which is the easy case for a model that reasons from names. On known faults: the yield strength failure is unexplained, the intervals with a prior mean are overconfident at few labels, and the fitted slope is unstable on five to ten points. On what is missing: a gradient-fitted mean network on the same first labels, token counts from the model's own tokenizer, a sandbox in place of an audit, and tuned Bayesian neural network baselines.
""", source=R3 + ", Sec. 2 and 6; docs/results/2026-11-11-round4.md, Sec. 3; docs/results/2026-11-11-e1-pilot.md, Sec. 5")

conclusions("conclusions", "Conclusions", 7,
            [("Done", ["written_network_weights.png", "rho_alone_bars.png"],
              ["60 networks written with no data", "4 models, 5 alloy tasks", "used as GP mean a·m(x) + b"]),
             ("Found", ["auc_relative_to_gp.png", "bo_regret_mpea_yield_strength.png"],
              ["Opus 5.5: better BO on 4 of 5 tasks", "worse on MPEA yield strength", "handbook rule: no gain"]),
             ("Next", ["bnn_coverage.png", "auc_seed_differences_mpea_yield_strength.png"],
              ["diagnose MPEA yield strength", "propagate slope uncertainty", "second pool; a real closed loop"])], """
To close. Four models wrote 60 small networks from materials knowledge with no data, and I used them as the prior mean of a Gaussian process. With no labels the Opus 5.5 networks rank alloys at 0.64 to 0.79. In Bayesian optimisation over 20 seeds the Opus priors lower the area under regret on four of five tasks with corrected p values at or below 0.047, and make yield strength of multi-principal-element alloys worse. A handbook rule of mixtures gives no gain. Next come the diagnosis of that failure, intervals that carry the uncertainty of the slope, a second pool per task and a real closed loop. Thank you; I am glad to take questions.
""", source=R3 + ", Sec. 2 and 6")

# ------------------------------------------------------------------ backup
dark("backup-divider", "Backup", ["The two slope rules; regret by step; the written network with no GP"], """
The slides after this divider are kept for questions. They use the same figures and tables as the main deck and come in the order of the talk: the ranking against labels with the slope fixed at one, the two slope rules side by side at 5 labels, the regret after 5, 10 and 25 steps for the plain Gaussian process and the two stronger models, and the smaller run in which the written network is used with no Gaussian process at all. Each carries its source in the notes, like the main slides.
""")

content("b-rho-labels-one", "GP ranking against labels: slope fixed at one", 99,
        fig("rho_vs_labels_slope_one.png", ["Slope a = 1; ρ at 5 labels", "MPEA HV: 0.06 → 0.78 (Opus)", "Ti HV: 0.63 → 0.52 (Haiku)", "handbook, Ti HV: 0.18", "handbook, MPEA HV: −0.24", "at 50 labels, Ti HV: 0.55"], bx=506, bw=190, w=474), """
This is the ranking figure from the results with the slope fixed at one. Panels, axes and colours are the same: the dashed black line is the plain Gaussian process and the solid lines add a prior mean. For the model-written networks the fixed slope is close to or above the fitted slope. For the handbook rule it is much worse, because the rule orders alloys the wrong way round on three tasks and a fixed positive slope cannot flip it: titanium hardness is at 0.18 with 5 labels and still at 0.55 with 50, against 0.78 for the plain Gaussian process.
""", kind="backup", source=WSUM + " (n5 to n50: gp, prior_one)")

content("b-slope-rules", "The two slope rules at 5 labels", 99,
        fig("slope_rules_5_labels.png", ["MPEA hardness, 5 labels", "plain GP: 0.06", "Opus: 0.66 fitted, 0.78 one", "Fable: 0.55 fitted, 0.76 one", "Ti hardness, Haiku", "0.34 fitted, 0.52 one"], bx=506, bw=190, w=474), """
This figure compares the two slope rules where they differ most, at 5 labels. Each panel is one model, each group one task. The light grey bar is the plain Gaussian process, the solid bar the prior with a fitted slope, and the hatched bar the prior with the slope fixed at one. Fixing the slope is at least as good as fitting it in most cells, and clearly better on alloy hardness: 0.78 against 0.66 for Opus 5.5 and 0.76 against 0.55 for Fable 5.2. For weak priors the fixed slope limits the damage on titanium hardness, 0.52 against 0.34 for Haiku 5.5, but still falls below the plain Gaussian process at 0.63.
""", kind="backup", source=WSUM + " (n5: gp, prior_fitted, prior_one)")

table_slide("b-regret-steps", "Regret after 5, 10 and 25 steps", 99,
            [["Task (unit)", "Plain GP: 5 / 10 / 25", "Opus 5.5: 5 / 10 / 25", "Fable 5.2: 5 / 10 / 25", "All replies: 5 / 10 / 25"],
             ["Ti Young's modulus (GPa)", "8.9 / 8.1 / 5.6", "9.1 / 6.4 / 1.6", "9.7 / 7.5 / 3.5", "8.9 / 6.4 / 1.5"],
             ["Ti yield strength (MPa)", "479 / 324 / 114", "331 / 114 / 17", "317 / 164 / 0", "335 / 124 / 9"],
             ["Ti hardness (HV)", "81.8 / 41.0 / 1.6", "2.0 / 2.0 / 2.0", "13.0 / 2.0 / 2.0", "7.5 / 2.0 / 1.9"],
             ["MPEA hardness (HV)", "296 / 227 / 112", "178 / 99 / 94", "118 / 109 / 99", "203 / 124 / 99"],
             ["MPEA yield strength (MPa)", "1,138 / 753 / 522", "1,118 / 988 / 499", "1,181 / 1,024 / 698", "1,173 / 1,067 / 588"]],
            [2.13, 1.8, 1.8, 1.8, 1.8], 12, 24, 78, 672, 150, """
This table gives the mean regret over 20 seeds after 5, 10 and 25 steps for the plain Gaussian process, the Opus 5.5 arm, the Fable 5.2 arm and the pooled arm. On titanium modulus the arms are level at step 5 and separate later. On titanium yield strength and both hardness tasks the priors are ahead from step 5. On yield strength of multi-principal-element alloys the Opus arm is behind at step 10, 988 against 753 megapascals, and level at step 25, 499 against 522, while the Fable arm is behind throughout. On titanium hardness the Gaussian process also reaches a regret near 2 by the end.
""", kind="backup", cap="Mean over 20 seeds; 5 initial labels are given before step 1.",
            source="experiments/e1_surrogate_head/results/bo_select/summary_init5_steps25_seeds20.md")

table_slide("b-written-alone", "The written network with no GP (8 seeds)", 99,
            [["Task", "Arm", "Regret after 10", "Regret after 25", "Seeds reaching the top 5%"],
             ["MPEA yield strength (MPa)", "random search", "960", "740", "7 of 8"],
             ["", "plain GP", "393", "351", "8 of 8"],
             ["", "written network alone, replies 1 / 2 / 3", "1,070 / 1,083 / 1,086", "584 / 753 / 773", "8 / 8 / 8"],
             ["Ti Young's modulus (GPa)", "random search", "10.4", "7.5", "4 of 8"],
             ["", "plain GP", "8.4", "6.0", "7 of 8"],
             ["", "written network alone, replies 1 / 2 / 3", "13.4 / 0.0 / 13.0", "7.0 / 0.0 / 10.0", "8 / 8 / 0"]],
            [2.2, 2.9, 1.6, 1.4, 1.23], 11.5, 24, 78, 672, 176, """
This control uses the written network with no Gaussian process: alloys are taken in the order the network ranks them. It is a smaller run, 8 seeds on two tasks with three Fable 5.2 replies. On alloy yield strength the network alone is worse than the plain Gaussian process and, at 10 steps, worse than random search. On titanium modulus the outcome depends on the reply: the second reply puts a best-in-pool alloy among its first picks, with zero regret in every seed, while the third never reaches the top 5 percent. A written network is therefore not a substitute for the surrogate, and replies that look alike on average ranking can differ on the few best alloys.
""", kind="backup", cap="Pool-based BO, 5 initial labels, 25 steps, 8 seeds; replies of Fable 5.2.",
            source="experiments/e1_surrogate_head/results/bo/mpea_yield_strength.json; results/bo/ti_alloy_youngs_modulus.json; docs/results/2026-11-11-round2.md, Sec. 3")

if __name__ == "__main__":
    write()
