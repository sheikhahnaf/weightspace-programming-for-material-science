# Experimental formation enthalpies with structures (experiment E8)

Built by `experiments/e8_formation_enthalpy/build_set.py`.

- `compounds.extxyz`: 800 compounds, a seed-0 sample of the rows of matminer's `expt_formation_enthalpy_kingsbury` that carry a Materials Project id, have at most 40 sites and whose formula matches the Materials Project phase. `H_expt` is the experimental formation enthalpy at 298 K in eV/atom; `E_mp_raw` the uncorrected energy per atom as the Materials Project serves it (not used by the experiment); `H_mp` the Materials Project's own formation energy as served.
- `elements.extxyz`: the lowest-energy Materials Project phase of each of the 78 elements present.
- Enthalpies: Kingsbury et al., matminer dataset `expt_formation_enthalpy_kingsbury` (figshare file 28232538). Structures and energies: Materials Project, CC BY 4.0, fetched 2026-11-12.
