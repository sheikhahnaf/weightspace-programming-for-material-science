| Task | Arm | Candidates | Regret after 5 | after 10 | after 25 | Area under regret | vs GP: seeds better / worse | Wilcoxon p (Holm) | Steps with a prior |
|---|---|---|---|---|---|---|---|---|---|
| `cantor_al_solidus` (K) | random |  | 124 | 97.1 | 61.4 | 91.9 ± 6.1 | 4 / 16 |  | 0.00 |
| `cantor_al_solidus` (K) | gp |  | 85.9 | 56 | 6.2 | 50.8 ± 7.2 |  |  | 0.00 |
| `cantor_al_solidus` (K) | rom | 1 | 87.3 | 52 | 9.08 | 52.5 ± 7.5 | 2 / 3 | 0.5 (1) | 0.06 |
| `cantor_al_solidus` (K) | rom_map |  | 87.5 | 52.4 | 6.2 | 49.9 ± 7 | 3 / 2 | 0.686 (1) | 0.05 |
| `cantor_al_solidus` (K) | rom_marginal |  | 84.7 | 50.6 | 6.96 | 48.1 ± 6.8 | 3 / 2 | 0.225 (1) | 0.04 |
| `cantor_al_solidus` (K) | subsystem_extrapolation | 1 | 4.49 | 2.07 | 0 | 8.49 ± 1.2 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.98 |
| `cantor_al_solidus` (K) | subsystem_extrapolation_map |  | 2.51 | 2.07 | 0 | 7.35 ± 1.3 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.98 |
| `cantor_al_solidus` (K) | subsystem_extrapolation_marginal |  | 2.36 | 2.07 | 0 | 6.95 ± 1.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.98 |
| `cantor_al_solidus` (K) | select_opus | 2 | 95.9 | 69.5 | 15.2 | 60.1 ± 5.3 | 7 / 10 | 0.246 (1) | 0.78 |
| `cantor_al_solidus` (K) | select_opus_map |  | 93.8 | 70.3 | 13.3 | 60.3 ± 6.7 | 7 / 11 | 0.17 (1) | 0.81 |
| `cantor_al_solidus` (K) | select_opus_marginal |  | 92.8 | 69.1 | 14 | 58.3 ± 5.6 | 9 / 9 | 0.616 (1) | 0.77 |
| `cantor_al_solidus` (K) | select_opus_pd | 2 | 59.4 | 40.8 | 6.23 | 33.7 ± 3.7 | 14 / 6 | 0.0696 (0.696) | 1.00 |
| `cantor_al_solidus` (K) | select_opus_pd_map |  | 54 | 31.4 | 1.92 | 28.6 ± 2.7 | 14 / 6 | 0.00315 (0.0473) | 1.00 |
| `cantor_al_solidus` (K) | select_opus_pd_marginal |  | 71.2 | 36.6 | 2.36 | 35.3 ± 5.4 | 15 / 5 | 0.0484 (0.581) | 0.97 |
| `cantor_al_solidus` (K) | select_fable | 2 | 95.2 | 67.1 | 11.2 | 56.9 ± 5.3 | 8 / 10 | 0.616 (1) | 0.86 |
| `cantor_al_solidus` (K) | select_fable_map |  | 93.4 | 77.3 | 10.6 | 58.8 ± 5.2 | 8 / 10 | 0.42 (1) | 0.86 |
| `cantor_al_solidus` (K) | select_fable_marginal |  | 96.2 | 73.5 | 10.6 | 55.5 ± 4.9 | 9 / 9 | 0.744 (1) | 0.85 |
| `cantor_al_solidus` (K) | select_fable_pd | 2 | 37.5 | 18.2 | 11.8 | 26.6 ± 2.2 | 15 / 5 | 0.00944 (0.132) | 0.95 |
| `cantor_al_solidus` (K) | select_fable_pd_map |  | 65.8 | 30.9 | 10.6 | 33.1 ± 2.4 | 15 / 5 | 0.0296 (0.384) | 0.93 |
| `cantor_al_solidus` (K) | select_fable_pd_marginal |  | 69.6 | 30.5 | 11.5 | 35.2 ± 3.2 | 15 / 5 | 0.0583 (0.641) | 0.93 |
| `cantor_al_freezing_range` (K) | random |  | 15.5 | 14.7 | 9.75 | 13.5 ± 1.2 | 1 / 19 |  | 0.00 |
| `cantor_al_freezing_range` (K) | gp |  | 12.6 | 5.23 | 1.18 | 6.37 ± 1.1 |  |  | 0.00 |
| `cantor_al_freezing_range` (K) | subsystem_extrapolation | 1 | 1.24 | 0.25 | 0 | 0.555 ± 0.33 | 19 / 0 | 0.000132 (0.00185) | 0.97 |
| `cantor_al_freezing_range` (K) | subsystem_extrapolation_map |  | 1.92 | 0.25 | 0 | 0.944 ± 0.39 | 19 / 0 | 0.000132 (0.00185) | 0.96 |
| `cantor_al_freezing_range` (K) | subsystem_extrapolation_marginal |  | 2.47 | 0.925 | 0 | 1.15 ± 0.43 | 19 / 1 | 3.62e-05 (0.000544) | 0.96 |
| `cantor_al_freezing_range` (K) | select_opus | 2 | 5.83 | 1.67 | 0.55 | 2.83 ± 0.96 | 18 / 0 | 0.000196 (0.00185) | 0.89 |
| `cantor_al_freezing_range` (K) | select_opus_map |  | 6.36 | 1.62 | 0.25 | 2.94 ± 0.89 | 17 / 2 | 0.000724 (0.00215) | 0.88 |
| `cantor_al_freezing_range` (K) | select_opus_marginal |  | 6.31 | 1.69 | 0.25 | 3.06 ± 0.88 | 18 / 1 | 0.00025 (0.00185) | 0.87 |
| `cantor_al_freezing_range` (K) | select_opus_pd | 2 | 1.24 | 0.25 | 0 | 0.58 ± 0.4 | 19 / 0 | 0.000132 (0.00185) | 0.96 |
| `cantor_al_freezing_range` (K) | select_opus_pd_map |  | 0.77 | 0.25 | 0 | 0.671 ± 0.38 | 19 / 0 | 0.000132 (0.00185) | 0.96 |
| `cantor_al_freezing_range` (K) | select_opus_pd_marginal |  | 1.14 | 0.25 | 0 | 0.771 ± 0.37 | 19 / 0 | 0.000132 (0.00185) | 0.96 |
| `cantor_al_freezing_range` (K) | select_fable | 2 | 3.12 | 1.34 | 0 | 1.65 ± 0.65 | 18 / 0 | 0.000196 (0.00185) | 0.95 |
| `cantor_al_freezing_range` (K) | select_fable_map |  | 2.5 | 1.71 | 0 | 2.03 ± 0.81 | 17 / 2 | 0.000539 (0.00215) | 0.95 |
| `cantor_al_freezing_range` (K) | select_fable_marginal |  | 2.08 | 1.04 | 0 | 1.27 ± 0.56 | 18 / 0 | 0.000196 (0.00185) | 0.95 |
| `cantor_al_freezing_range` (K) | select_fable_pd | 2 | 5.52 | 1.04 | 0 | 1.94 ± 0.75 | 18 / 0 | 0.000196 (0.00185) | 0.94 |
| `cantor_al_freezing_range` (K) | select_fable_pd_map |  | 6.62 | 3.54 | 0.31 | 3.49 ± 1.2 | 16 / 3 | 0.00485 (0.00485) | 0.93 |
| `cantor_al_freezing_range` (K) | select_fable_pd_marginal |  | 6.03 | 1.72 | 0 | 2.86 ± 0.99 | 17 / 2 | 0.000539 (0.00215) | 0.92 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | random |  | 0.0157 | 0.00874 | 0.00544 | 0.0132 ± 0.0065 | 2 / 4 |  | 0.00 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | gp |  | 0.00882 | 0 | 0 | 0.00968 ± 0.0055 |  |  | 0.00 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | rom | 1 | 0.00882 | 0 | 0 | 0.0092 ± 0.0056 | 2 / 0 | 0.18 (1) | 0.22 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | rom_map |  | 0.00882 | 0 | 0 | 0.00907 ± 0.0056 | 2 / 0 | 0.18 (1) | 0.15 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0.00882 | 0 | 0 | 0.00907 ± 0.0056 | 2 / 0 | 0.18 (1) | 0.16 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0.0148 | 0 | 0 | 0.0072 ± 0.0053 | 2 / 1 | 0.285 (1) | 0.92 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0.0148 | 0 | 0 | 0.0072 ± 0.0053 | 2 / 1 | 0.285 (1) | 0.91 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0.0148 | 0 | 0 | 0.0072 ± 0.0053 | 2 / 1 | 0.285 (1) | 0.91 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0.00882 | 0 | 0 | 0.00588 ± 0.0044 | 5 / 0 | 0.0431 (0.776) | 0.97 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0.00882 | 0 | 0 | 0.00538 ± 0.0047 | 5 / 0 | 0.0431 (0.776) | 0.98 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0.00882 | 0 | 0 | 0.00429 ± 0.0043 | 5 / 0 | 0.0431 (0.776) | 0.98 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0.0148 | 0 | 0 | 0.00866 ± 0.005 | 2 / 2 | 0.465 (1) | 0.97 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0.0148 | 0 | 0 | 0.0061 ± 0.0046 | 4 / 0 | 0.0679 (0.776) | 0.97 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0.0148 | 0 | 0 | 0.00592 ± 0.0054 | 3 / 2 | 0.345 (1) | 0.97 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0.00544 | 0 | 0 | 0.00446 ± 0.0044 | 5 / 0 | 0.0431 (0.776) | 0.96 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0.0148 | 0 | 0 | 0.00475 ± 0.0048 | 5 / 0 | 0.0431 (0.776) | 0.96 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0.0148 | 0 | 0 | 0.00491 ± 0.0045 | 5 / 0 | 0.0431 (0.776) | 0.96 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0.00882 | 0 | 0 | 0.00457 ± 0.0043 | 5 / 0 | 0.0431 (0.776) | 0.99 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0.00544 | 0 | 0 | 0.00443 ± 0.0042 | 5 / 0 | 0.0431 (0.776) | 0.99 |
| `cantor_al_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0.0113 | 0 | 0 | 0.0048 ± 0.0048 | 5 / 0 | 0.0431 (0.776) | 0.99 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 0.000863 ± 0.00086 | 1 / 1 |  | 0.00 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 0.000632 ± 0.00051 |  |  | 0.00 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | rom | 1 | 0 | 0 | 0 | 0.000632 ± 0.00051 | 0 / 0 | 1 (1) | 0.36 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | rom_map |  | 0 | 0 | 0 | 0.000632 ± 0.00051 | 0 / 0 | 1 (1) | 0.36 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0 | 0 | 0 | 0.000632 ± 0.00051 | 0 / 0 | 1 (1) | 0.36 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 2 / 0 | 0.18 (1) | 0.94 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0.000132 ± 0.00013 | 1 / 0 | 0.317 (1) | 0.94 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0 ± 0 | 2 / 0 | 0.18 (1) | 0.94 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0.00314 | 0 | 0 | 0.00147 ± 0.0013 | 0 / 1 | 0.317 (1) | 0.77 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0.00119 ± 0.00098 | 0 / 2 | 0.18 (1) | 0.75 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0.00176 ± 0.0013 | 0 / 3 | 0.109 (1) | 0.77 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0.000466 ± 0.00047 | 2 / 0 | 0.18 (1) | 0.78 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0.000276 ± 0.00028 | 2 / 0 | 0.18 (1) | 0.85 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.000776 ± 0.00078 | 1 / 1 | 0.655 (1) | 0.86 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0.00559 | 0 | 0 | 0.00204 ± 0.0019 | 0 / 1 | 0.317 (1) | 0.75 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0.0012 ± 0.0011 | 0 / 1 | 0.317 (1) | 0.79 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0.000475 ± 0.00048 | 2 / 0 | 0.18 (1) | 0.66 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 0.000696 ± 0.00057 | 0 / 1 | 0.317 (1) | 0.87 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0.000632 ± 0.00051 | 0 / 0 | 1 (1) | 0.85 |
| `cantor_al_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0.000563 ± 0.00056 | 1 / 1 | 0.655 (1) | 0.86 |
| `ni_superalloy_solidus` (K) | random |  | 50.4 | 37.5 | 25.4 | 39 ± 3.6 | 1 / 19 |  | 0.00 |
| `ni_superalloy_solidus` (K) | gp |  | 23.5 | 3.89 | 0 | 10.7 ± 2 |  |  | 0.00 |
| `ni_superalloy_solidus` (K) | rom | 1 | 23.5 | 3.89 | 0 | 10.7 ± 2 | 0 / 0 | 1 (1) | 0.09 |
| `ni_superalloy_solidus` (K) | rom_map |  | 23.5 | 3.89 | 0 | 10.7 ± 2 | 0 / 1 | 0.317 (0.635) | 0.10 |
| `ni_superalloy_solidus` (K) | rom_marginal |  | 22.2 | 2.93 | 0 | 9.7 ± 1.8 | 5 / 2 | 0.063 (0.189) | 0.09 |
| `ni_superalloy_solidus` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `ni_superalloy_solidus` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0.345 ± 0.17 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `ni_superalloy_solidus` (K) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.728 ± 0.21 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `ni_superalloy_solidus` (K) | select_opus | 2 | 10.9 | 1.56 | 0 | 5.23 ± 1.2 | 16 / 4 | 0.000395 (0.00513) | 0.99 |
| `ni_superalloy_solidus` (K) | select_opus_map |  | 14.2 | 1.04 | 0 | 5.47 ± 1.4 | 15 / 5 | 0.00315 (0.0126) | 0.99 |
| `ni_superalloy_solidus` (K) | select_opus_marginal |  | 9.93 | 0.965 | 0 | 5.28 ± 1.2 | 17 / 3 | 0.00121 (0.0121) | 0.99 |
| `ni_superalloy_solidus` (K) | select_opus_pd | 2 | 6.78 | 5.65 | 0 | 4.09 ± 0.54 | 15 / 5 | 0.00199 (0.0121) | 1.00 |
| `ni_superalloy_solidus` (K) | select_opus_pd_map |  | 6.78 | 5.08 | 0 | 3.85 ± 0.36 | 15 / 5 | 0.000708 (0.00849) | 1.00 |
| `ni_superalloy_solidus` (K) | select_opus_pd_marginal |  | 7.77 | 5.08 | 0 | 3.78 ± 0.38 | 14 / 6 | 0.00199 (0.0121) | 1.00 |
| `ni_superalloy_solidus` (K) | select_fable | 2 | 11.6 | 0.52 | 0 | 5.02 ± 1.2 | 15 / 4 | 0.00148 (0.0121) | 0.99 |
| `ni_superalloy_solidus` (K) | select_fable_map |  | 13.6 | 1.08 | 0 | 5.85 ± 1.5 | 16 / 4 | 0.00169 (0.0121) | 0.99 |
| `ni_superalloy_solidus` (K) | select_fable_marginal |  | 13.6 | 1.65 | 0 | 5.57 ± 1.2 | 16 / 4 | 0.00121 (0.0121) | 0.99 |
| `ni_superalloy_solidus` (K) | select_fable_pd | 2 | 5.65 | 0 | 0 | 1.84 ± 0.3 | 19 / 1 | 5.72e-06 (8.58e-05) | 1.00 |
| `ni_superalloy_solidus` (K) | select_fable_pd_map |  | 6.78 | 0.565 | 0 | 2.87 ± 0.34 | 17 / 3 | 0.000134 (0.00187) | 1.00 |
| `ni_superalloy_solidus` (K) | select_fable_pd_marginal |  | 8.71 | 1.08 | 0 | 3.47 ± 0.4 | 15 / 5 | 0.00102 (0.0112) | 1.00 |
| `ni_superalloy_freezing_range` (K) | random |  | 10.6 | 5.89 | 3.98 | 7.01 ± 0.83 | 1 / 19 |  | 0.00 |
| `ni_superalloy_freezing_range` (K) | gp |  | 4.81 | 2.67 | 0.99 | 3.45 ± 0.35 |  |  | 0.00 |
| `ni_superalloy_freezing_range` (K) | subsystem_extrapolation | 1 | 2.2 | 2.2 | 0.88 | 2.03 ± 0.16 | 16 / 4 | 0.000168 (0.00218) | 1.00 |
| `ni_superalloy_freezing_range` (K) | subsystem_extrapolation_map |  | 2.69 | 2.35 | 0.55 | 2.2 ± 0.26 | 16 / 4 | 0.00639 (0.00972) | 1.00 |
| `ni_superalloy_freezing_range` (K) | subsystem_extrapolation_marginal |  | 2.85 | 2.36 | 0.44 | 2.1 ± 0.18 | 15 / 5 | 0.000708 (0.00566) | 1.00 |
| `ni_superalloy_freezing_range` (K) | select_opus | 2 | 2.77 | 2.2 | 0.44 | 2.31 ± 0.3 | 17 / 3 | 0.000261 (0.00287) | 0.99 |
| `ni_superalloy_freezing_range` (K) | select_opus_map |  | 3.23 | 2.27 | 0.33 | 2.2 ± 0.32 | 19 / 1 | 2.67e-05 (0.000401) | 0.99 |
| `ni_superalloy_freezing_range` (K) | select_opus_marginal |  | 3.08 | 2.42 | 0.55 | 2.33 ± 0.33 | 18 / 2 | 0.00116 (0.00697) | 0.99 |
| `ni_superalloy_freezing_range` (K) | select_opus_pd | 2 | 2.75 | 2.25 | 0.66 | 2.08 ± 0.078 | 18 / 2 | 0.000708 (0.00566) | 1.00 |
| `ni_superalloy_freezing_range` (K) | select_opus_pd_map |  | 3.2 | 2.42 | 0 | 2.06 ± 0.15 | 17 / 3 | 0.00121 (0.00697) | 1.00 |
| `ni_superalloy_freezing_range` (K) | select_opus_pd_marginal |  | 3.36 | 2.42 | 0.44 | 2.15 ± 0.12 | 16 / 4 | 0.00169 (0.00697) | 1.00 |
| `ni_superalloy_freezing_range` (K) | select_fable | 2 | 2.33 | 1.76 | 0.44 | 2.03 ± 0.2 | 17 / 3 | 0.00021 (0.00252) | 0.99 |
| `ni_superalloy_freezing_range` (K) | select_fable_map |  | 3.09 | 2.35 | 0.33 | 2.29 ± 0.28 | 16 / 4 | 0.00199 (0.00697) | 0.99 |
| `ni_superalloy_freezing_range` (K) | select_fable_marginal |  | 2.69 | 1.97 | 0.55 | 2.14 ± 0.3 | 15 / 5 | 0.00486 (0.00972) | 0.99 |
| `ni_superalloy_freezing_range` (K) | select_fable_pd | 2 | 3.11 | 1.98 | 0.77 | 1.96 ± 0.12 | 16 / 4 | 8.2e-05 (0.00115) | 1.00 |
| `ni_superalloy_freezing_range` (K) | select_fable_pd_map |  | 3.14 | 2.2 | 0.33 | 1.86 ± 0.13 | 16 / 4 | 0.000261 (0.00287) | 1.00 |
| `ni_superalloy_freezing_range` (K) | select_fable_pd_marginal |  | 3.21 | 1.98 | 0.55 | 1.84 ± 0.14 | 17 / 3 | 0.000261 (0.00287) | 1.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | random |  | 0.184 | 0.101 | 0.0264 | 0.0934 ± 0.018 | 1 / 16 |  | 0.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | gp |  | 0.0163 | 0 | 0 | 0.016 ± 0.0044 |  |  | 0.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0.0209 | 0 | 0 | 0.0179 ± 0.0029 | 6 / 11 | 0.523 (1) | 0.97 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0.0121 | 0 | 0 | 0.0145 ± 0.0022 | 7 / 10 | 0.943 (1) | 0.97 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0.0121 | 0.00223 | 0 | 0.014 ± 0.0023 | 7 / 10 | 0.981 (1) | 0.97 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0.0538 | 0.00223 | 0 | 0.0233 ± 0.0038 | 6 / 10 | 0.0494 (0.692) | 0.93 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0.0321 | 0.00223 | 0 | 0.017 ± 0.0028 | 7 / 9 | 0.642 (1) | 0.93 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0.0308 | 0.00331 | 0 | 0.0169 ± 0.0031 | 7 / 9 | 0.756 (1) | 0.95 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0.00223 | 0 | 0 | 0.0126 ± 0.0023 | 6 / 11 | 0.795 (1) | 1.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0.0174 | 0 | 0 | 0.0115 ± 0.0026 | 8 / 8 | 0.301 (1) | 1.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0.00865 | 0 | 0 | 0.0109 ± 0.0023 | 7 / 9 | 0.408 (1) | 1.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0.0621 | 0.00555 | 0 | 0.0292 ± 0.0057 | 3 / 13 | 0.00192 (0.0288) | 0.97 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0.0242 | 0 | 0 | 0.0181 ± 0.0029 | 7 / 9 | 0.679 (1) | 0.96 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0.0256 | 0.00223 | 0 | 0.0175 ± 0.0026 | 7 / 9 | 0.679 (1) | 0.97 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0.00447 | 0 | 0 | 0.0108 ± 0.0023 | 10 / 6 | 0.179 (1) | 1.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0.0174 | 0 | 0 | 0.0138 ± 0.0044 | 9 / 7 | 0.569 (1) | 1.00 |
| `ni_superalloy_gamma_prime_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0.00757 | 0 | 0 | 0.00969 ± 0.0025 | 9 / 7 | 0.148 (1) | 1.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 1.26e-05 ± 1.3e-05 | 1 / 1 |  | 0.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 1.72e-05 ± 1.7e-05 |  |  | 0.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 1.72e-05 ± 1.7e-05 | 0 / 0 | 1 (1) | 0.56 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 1.72e-05 ± 1.7e-05 | 0 / 0 | 1 (1) | 0.57 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 1.72e-05 ± 1.7e-05 | 0 / 0 | 1 (1) | 0.59 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.99 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.99 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.99 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.99 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.99 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 1.72e-05 ± 1.7e-05 | 0 / 0 | 1 (1) | 0.97 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.94 |
| `ni_superalloy_other_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.97 |
| `ti_alloy_solidus` (K) | random |  | 91.9 | 72.4 | 54.3 | 72.5 ± 8.4 | 2 / 17 |  | 0.00 |
| `ti_alloy_solidus` (K) | gp |  | 50.4 | 31.8 | 0 | 27.2 ± 4.4 |  |  | 0.00 |
| `ti_alloy_solidus` (K) | rom | 1 | 50.4 | 31.8 | 0 | 27.2 ± 4.4 | 0 / 0 | 1 (1) | 0.05 |
| `ti_alloy_solidus` (K) | rom_map |  | 51.4 | 32.8 | 0 | 27.6 ± 4.4 | 1 / 1 | 0.655 (1) | 0.04 |
| `ti_alloy_solidus` (K) | rom_marginal |  | 50.1 | 32.8 | 0 | 27.4 ± 4.4 | 2 / 2 | 0.715 (1) | 0.05 |
| `ti_alloy_solidus` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | subsystem_extrapolation_marginal |  | 3.42 | 0 | 0 | 0.956 ± 0.82 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_opus | 2 | 30.4 | 9.21 | 0 | 13.1 ± 2.3 | 15 / 3 | 0.00184 (0.0129) | 1.00 |
| `ti_alloy_solidus` (K) | select_opus_map |  | 40 | 21.5 | 0 | 18.7 ± 3.4 | 14 / 5 | 0.0401 (0.161) | 1.00 |
| `ti_alloy_solidus` (K) | select_opus_marginal |  | 37.3 | 21.8 | 0 | 18.1 ± 3.3 | 15 / 4 | 0.00549 (0.0275) | 1.00 |
| `ti_alloy_solidus` (K) | select_opus_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_opus_pd_map |  | 3.42 | 3.07 | 0 | 1.69 ± 1.7 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_fable | 2 | 9.56 | 0 | 0 | 6.75 ± 1.4 | 17 / 1 | 0.000233 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_fable_map |  | 28 | 14 | 0 | 13.9 ± 3 | 17 / 1 | 0.000233 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_fable_marginal |  | 31.8 | 17.1 | 0 | 16.6 ± 3.5 | 16 / 2 | 0.00378 (0.0227) | 1.00 |
| `ti_alloy_solidus` (K) | select_fable_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_solidus` (K) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0.137 ± 0.14 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `ti_alloy_freezing_range` (K) | random |  | 35.1 | 24.9 | 10.3 | 25.1 ± 4.4 | 0 / 19 |  | 0.00 |
| `ti_alloy_freezing_range` (K) | gp |  | 8.09 | 0.145 | 0 | 5.63 ± 1.6 |  |  | 0.00 |
| `ti_alloy_freezing_range` (K) | subsystem_extrapolation | 1 | 0.5 | 0 | 0 | 0.469 ± 0.37 | 18 / 0 | 0.000196 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | subsystem_extrapolation_map |  | 0.635 | 0.145 | 0 | 0.619 ± 0.35 | 16 / 3 | 0.000398 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | subsystem_extrapolation_marginal |  | 0.345 | 0 | 0 | 0.531 ± 0.3 | 18 / 1 | 0.000155 (0.00233) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_opus | 2 | 0.87 | 0.145 | 0 | 0.383 ± 0.062 | 17 / 2 | 0.000214 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_opus_map |  | 4.06 | 0.145 | 0 | 2.49 ± 1.4 | 15 / 4 | 0.00331 (0.00661) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_opus_marginal |  | 0.435 | 0 | 0 | 0.516 ± 0.16 | 17 / 2 | 0.000214 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_opus_pd | 2 | 0.3 | 0 | 0 | 0.636 ± 0.57 | 18 / 0 | 0.000196 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_opus_pd_map |  | 0.7 | 0.145 | 0 | 0.636 ± 0.38 | 18 / 1 | 0.000197 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_opus_pd_marginal |  | 0.345 | 0 | 0 | 0.48 ± 0.29 | 18 / 1 | 0.000182 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_fable | 2 | 1.45 | 0.435 | 0 | 1.07 ± 0.32 | 16 / 2 | 0.000386 (0.00237) | 0.99 |
| `ti_alloy_freezing_range` (K) | select_fable_map |  | 8.28 | 0.145 | 0 | 4.22 ± 1.6 | 12 / 6 | 0.0642 (0.0642) | 0.99 |
| `ti_alloy_freezing_range` (K) | select_fable_marginal |  | 0.635 | 0 | 0 | 1.25 ± 0.35 | 14 / 4 | 0.00159 (0.00478) | 0.99 |
| `ti_alloy_freezing_range` (K) | select_fable_pd | 2 | 0.2 | 0 | 0 | 0.623 ± 0.47 | 18 / 0 | 0.000196 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_fable_pd_map |  | 0.435 | 0 | 0 | 0.527 ± 0.31 | 17 / 2 | 0.000293 (0.00237) | 1.00 |
| `ti_alloy_freezing_range` (K) | select_fable_pd_marginal |  | 0.29 | 0 | 0 | 0.453 ± 0.3 | 18 / 1 | 0.000155 (0.00233) | 1.00 |
| `ti_alloy_alpha_transus` (K) | random |  | 26.2 | 16.4 | 3.44 | 14.9 ± 4.6 | 4 / 9 |  | 0.00 |
| `ti_alloy_alpha_transus` (K) | gp |  | 15.7 | 5.16 | 0.675 | 9.33 ± 2.2 |  |  | 0.00 |
| `ti_alloy_alpha_transus` (K) | rom | 1 | 15.7 | 5.16 | 0.675 | 9.33 ± 2.2 | 0 / 0 | 1 (1) | 0.06 |
| `ti_alloy_alpha_transus` (K) | rom_map |  | 15.7 | 5.16 | 0.675 | 9.04 ± 2.2 | 2 / 0 | 0.18 (1) | 0.06 |
| `ti_alloy_alpha_transus` (K) | rom_marginal |  | 15.7 | 5.16 | 0.675 | 9.4 ± 2.2 | 1 / 1 | 0.655 (1) | 0.07 |
| `ti_alloy_alpha_transus` (K) | subsystem_extrapolation | 1 | 14.5 | 9.21 | 3.38 | 10.9 ± 2.2 | 4 / 8 | 0.272 (1) | 0.53 |
| `ti_alloy_alpha_transus` (K) | subsystem_extrapolation_map |  | 12.2 | 7.42 | 2.7 | 9.86 ± 1.9 | 5 / 7 | 0.695 (1) | 0.50 |
| `ti_alloy_alpha_transus` (K) | subsystem_extrapolation_marginal |  | 12.9 | 7.19 | 2.7 | 9.1 ± 1.9 | 7 / 5 | 0.695 (1) | 0.49 |
| `ti_alloy_alpha_transus` (K) | select_opus | 2 | 8.49 | 7.42 | 0.675 | 6.35 ± 1.3 | 8 / 2 | 0.0218 (0.371) | 0.57 |
| `ti_alloy_alpha_transus` (K) | select_opus_map |  | 8.49 | 6.75 | 0 | 5.89 ± 1.2 | 8 / 3 | 0.0262 (0.393) | 0.53 |
| `ti_alloy_alpha_transus` (K) | select_opus_marginal |  | 12.8 | 4.05 | 0.675 | 6.24 ± 1.4 | 9 / 2 | 0.0128 (0.23) | 0.55 |
| `ti_alloy_alpha_transus` (K) | select_opus_pd | 2 | 16.1 | 7.14 | 4.05 | 11.2 ± 2.5 | 4 / 6 | 0.139 (1) | 0.42 |
| `ti_alloy_alpha_transus` (K) | select_opus_pd_map |  | 12.7 | 7.86 | 2.02 | 10.1 ± 2.3 | 3 / 7 | 0.575 (1) | 0.43 |
| `ti_alloy_alpha_transus` (K) | select_opus_pd_marginal |  | 16.4 | 7.58 | 2.7 | 11.3 ± 2.7 | 3 / 7 | 0.169 (1) | 0.41 |
| `ti_alloy_alpha_transus` (K) | select_fable | 2 | 13 | 7.42 | 1.35 | 6.91 ± 1.8 | 7 / 4 | 0.0619 (0.866) | 0.51 |
| `ti_alloy_alpha_transus` (K) | select_fable_map |  | 9.6 | 6.51 | 1.35 | 6.42 ± 1.7 | 8 / 2 | 0.0218 (0.371) | 0.48 |
| `ti_alloy_alpha_transus` (K) | select_fable_marginal |  | 9.6 | 7.86 | 1.35 | 6.93 ± 1.9 | 8 / 3 | 0.0619 (0.866) | 0.54 |
| `ti_alloy_alpha_transus` (K) | select_fable_pd | 2 | 16.3 | 8.18 | 2.02 | 9.93 ± 2 | 5 / 7 | 0.695 (1) | 0.55 |
| `ti_alloy_alpha_transus` (K) | select_fable_pd_map |  | 14.1 | 8.54 | 2.02 | 9.41 ± 1.9 | 6 / 6 | 0.875 (1) | 0.52 |
| `ti_alloy_alpha_transus` (K) | select_fable_pd_marginal |  | 12.9 | 8.56 | 2.02 | 9.02 ± 1.8 | 6 / 6 | 0.754 (1) | 0.51 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 |  | 0.00 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 0 ± 0 |  |  | 0.00 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | rom | 1 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.23 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | rom_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.20 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.17 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.80 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.77 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.71 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.81 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.82 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.78 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.73 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.79 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.75 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.86 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.78 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.81 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.76 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.75 |
| `ti_alloy_alpha_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.80 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | random |  | 0.00063 | 0 | 0 | 0.000176 ± 0.00018 | 0 / 1 |  | 0.00 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 2.52e-05 ± 2.5e-05 |  |  | 0.00 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.92 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.93 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 1.6e-05 ± 1.6e-05 | 1 / 0 | 0.317 (1) | 0.93 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 7.56e-05 ± 7.6e-05 | 0 / 1 | 0.317 (1) | 0.92 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.92 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.87 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.98 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.98 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.98 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.96 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.97 |
| `ti_alloy_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 2.52e-05 ± 2.5e-05 | 0 / 0 | 1 (1) | 0.97 |
| `refractory_solidus` (K) | random |  | 257 | 234 | 182 | 231 ± 22 | 0 / 20 |  | 0.00 |
| `refractory_solidus` (K) | gp |  | 80.3 | 0 | 0 | 46.9 ± 8.4 |  |  | 0.00 |
| `refractory_solidus` (K) | rom | 1 | 43.3 | 2.55 | 0 | 36.3 ± 5.9 | 14 / 6 | 0.0333 (0.0333) | 0.91 |
| `refractory_solidus` (K) | rom_map |  | 65.3 | 2.55 | 0 | 35.1 ± 7.7 | 16 / 4 | 0.00143 (0.00286) | 0.95 |
| `refractory_solidus` (K) | rom_marginal |  | 21.9 | 2.55 | 0 | 29.2 ± 5.9 | 17 / 3 | 0.000586 (0.00176) | 0.96 |
| `refractory_solidus` (K) | subsystem_extrapolation | 1 | 2.55 | 0 | 0 | 3.99 ± 3.7 | 20 / 0 | 8.84e-05 (0.000442) | 0.99 |
| `refractory_solidus` (K) | subsystem_extrapolation_map |  | 19.3 | 0 | 0 | 5.96 ± 4.3 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | subsystem_extrapolation_marginal |  | 11.9 | 0 | 0 | 6.55 ± 4.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_opus | 2 | 16.8 | 0 | 0 | 6.87 ± 4.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_opus_map |  | 21.9 | 0 | 0 | 7.46 ± 4.4 | 19 / 1 | 3.81e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_opus_marginal |  | 19.3 | 2.55 | 0 | 8.79 ± 5.2 | 18 / 2 | 9.54e-06 (7.63e-05) | 0.99 |
| `refractory_solidus` (K) | select_opus_pd | 2 | 14.2 | 0 | 0 | 4.67 ± 4.3 | 20 / 0 | 8.84e-05 (0.000442) | 0.99 |
| `refractory_solidus` (K) | select_opus_pd_map |  | 19.3 | 0 | 0 | 5.48 ± 4.5 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_opus_pd_marginal |  | 14.5 | 0 | 0 | 6.34 ± 4.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_fable | 2 | 14.2 | 0 | 0 | 7.48 ± 4.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_fable_map |  | 16.8 | 0 | 0 | 9.92 ± 4.6 | 19 / 1 | 1.34e-05 (8.01e-05) | 0.99 |
| `refractory_solidus` (K) | select_fable_marginal |  | 19.3 | 2.55 | 0 | 12.3 ± 4.5 | 19 / 1 | 9.54e-06 (7.63e-05) | 0.99 |
| `refractory_solidus` (K) | select_fable_pd | 2 | 14.2 | 0 | 0 | 4.97 ± 4.2 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_fable_pd_map |  | 14.2 | 0 | 0 | 5.58 ± 4.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_solidus` (K) | select_fable_pd_marginal |  | 11.9 | 0 | 0 | 6.17 ± 4.5 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `refractory_freezing_range` (K) | random |  | 112 | 76.1 | 48.2 | 79.1 ± 11 | 1 / 19 |  | 0.00 |
| `refractory_freezing_range` (K) | gp |  | 59.8 | 12 | 0.7 | 28.8 ± 6 |  |  | 0.00 |
| `refractory_freezing_range` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.965 ± 0.9 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | subsystem_extrapolation_map |  | 0.35 | 0 | 0 | 1.09 ± 1.1 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | subsystem_extrapolation_marginal |  | 0.7 | 0 | 0 | 1.44 ± 0.99 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | select_opus | 2 | 4.9 | 1.05 | 0 | 6.41 ± 2.5 | 19 / 0 | 0.000132 (0.00185) | 0.99 |
| `refractory_freezing_range` (K) | select_opus_map |  | 17.4 | 0.35 | 0 | 7.16 ± 4.7 | 18 / 1 | 0.000155 (0.00185) | 0.99 |
| `refractory_freezing_range` (K) | select_opus_marginal |  | 2.1 | 0.35 | 0 | 5.38 ± 2.8 | 19 / 0 | 0.000132 (0.00185) | 0.99 |
| `refractory_freezing_range` (K) | select_opus_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | select_opus_pd_marginal |  | 0.35 | 0 | 0 | 0.287 ± 0.29 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | select_fable | 2 | 34.8 | 6.97 | 0 | 18.6 ± 4.7 | 14 / 6 | 0.04 (0.04) | 0.99 |
| `refractory_freezing_range` (K) | select_fable_map |  | 15.8 | 1.99 | 0 | 12.2 ± 4.1 | 18 / 1 | 0.000155 (0.00185) | 0.99 |
| `refractory_freezing_range` (K) | select_fable_marginal |  | 13.3 | 2.1 | 0 | 11.7 ± 4 | 17 / 3 | 0.000105 (0.00157) | 0.99 |
| `refractory_freezing_range` (K) | select_fable_pd | 2 | 4.63 | 0 | 0 | 2.73 ± 0.97 | 18 / 1 | 0.000155 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | select_fable_pd_map |  | 1.05 | 0 | 0 | 1.97 ± 0.9 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_freezing_range` (K) | select_fable_pd_marginal |  | 0 | 0 | 0 | 1.89 ± 0.9 | 19 / 0 | 0.000132 (0.00185) | 1.00 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 |  | 0.00 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 0 ± 0 |  |  | 0.00 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | rom | 1 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.76 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | rom_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.74 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.69 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.91 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.91 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.91 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.81 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.83 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.83 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 0.000297 ± 0.0003 | 1 / 1 |  | 0.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 |  |  | 0.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom | 1 | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 | 0 / 0 | 1 (1) | 0.05 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom_map |  | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 | 0 / 0 | 1 (1) | 0.07 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 0.06 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 | 0 / 0 | 1 (1) | 0.93 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 | 0 / 0 | 1 (1) | 0.93 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 | 0 / 0 | 1 (1) | 0.92 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 6.82e-05 ± 6.8e-05 | 0 / 0 | 1 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.000136 ± 0.00014 | 0 / 1 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 1 / 0 | 0.317 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 7.42e-05 ± 7.4e-05 | 1 / 1 | 0.655 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 7.42e-05 ± 7.4e-05 | 1 / 1 | 0.655 (1) | 1.00 |
| `refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 7.42e-05 ± 7.4e-05 | 1 / 1 | 0.655 (1) | 1.00 |
| `steel_solidus` (K) | random |  | 62.4 | 49.8 | 29.4 | 46.6 ± 7.3 | 2 / 17 |  | 0.00 |
| `steel_solidus` (K) | gp |  | 32.4 | 10.8 | 0 | 16.2 ± 4.4 |  |  | 0.00 |
| `steel_solidus` (K) | rom | 1 | 32.4 | 10.8 | 0 | 16.2 ± 4.4 | 0 / 0 | 1 (1) | 0.20 |
| `steel_solidus` (K) | rom_map |  | 34.7 | 10.8 | 0 | 16.7 ± 4.4 | 0 / 2 | 0.18 (0.539) | 0.18 |
| `steel_solidus` (K) | rom_marginal |  | 37.6 | 10.8 | 0 | 17.2 ± 4.4 | 3 / 4 | 0.735 (1) | 0.19 |
| `steel_solidus` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 1.66 ± 1.7 | 18 / 0 | 0.000196 (0.00354) | 0.99 |
| `steel_solidus` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 1.66 ± 1.7 | 18 / 0 | 0.000196 (0.00354) | 0.99 |
| `steel_solidus` (K) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 1.77 ± 1.7 | 18 / 0 | 0.000196 (0.00354) | 0.99 |
| `steel_solidus` (K) | select_opus | 2 | 7.73 | 0 | 0 | 2.2 ± 2 | 18 / 0 | 0.000196 (0.00354) | 0.99 |
| `steel_solidus` (K) | select_opus_map |  | 7.73 | 0 | 0 | 2.2 ± 2 | 18 / 0 | 0.000196 (0.00354) | 0.99 |
| `steel_solidus` (K) | select_opus_marginal |  | 7.73 | 0 | 0 | 2.04 ± 1.9 | 18 / 0 | 0.000196 (0.00354) | 0.99 |
| `steel_solidus` (K) | select_opus_pd | 2 | 0 | 0 | 0 | 0.0174 ± 0.017 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.0978 ± 0.057 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_fable_marginal |  | 0 | 0 | 0 | 0.0348 ± 0.035 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_fable_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 18 / 0 | 0.000196 (0.00354) | 1.00 |
| `steel_solidus` (K) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0.28 ± 0.15 | 17 / 1 | 0.000233 (0.00354) | 1.00 |
| `steel_freezing_range` (K) | random |  | 14 | 10.4 | 5.65 | 10.5 ± 1.6 | 4 / 14 |  | 0.00 |
| `steel_freezing_range` (K) | gp |  | 14.7 | 1.31 | 0.03 | 5.84 ± 1.7 |  |  | 0.00 |
| `steel_freezing_range` (K) | subsystem_extrapolation | 1 | 8.19 | 0.715 | 0 | 2.98 ± 1.4 | 18 / 0 | 0.000196 (0.00295) | 0.96 |
| `steel_freezing_range` (K) | subsystem_extrapolation_map |  | 8.42 | 1.69 | 0 | 3.14 ± 1.5 | 17 / 1 | 0.000863 (0.00518) | 0.96 |
| `steel_freezing_range` (K) | subsystem_extrapolation_marginal |  | 8.19 | 0.545 | 0 | 2.95 ± 1.4 | 18 / 0 | 0.000196 (0.00295) | 0.96 |
| `steel_freezing_range` (K) | select_opus | 2 | 0.35 | 0 | 0 | 0.634 ± 0.3 | 17 / 1 | 0.000233 (0.00295) | 1.00 |
| `steel_freezing_range` (K) | select_opus_map |  | 1.12 | 0.06 | 0 | 0.845 ± 0.33 | 17 / 1 | 0.000233 (0.00295) | 1.00 |
| `steel_freezing_range` (K) | select_opus_marginal |  | 1.18 | 0 | 0 | 0.858 ± 0.32 | 16 / 2 | 0.000327 (0.00295) | 1.00 |
| `steel_freezing_range` (K) | select_opus_pd | 2 | 5.78 | 0.03 | 0 | 2.04 ± 1.2 | 18 / 0 | 0.000196 (0.00295) | 0.98 |
| `steel_freezing_range` (K) | select_opus_pd_map |  | 5.71 | 1.43 | 0 | 2.3 ± 1.3 | 15 / 3 | 0.00101 (0.00518) | 0.98 |
| `steel_freezing_range` (K) | select_opus_pd_marginal |  | 5.46 | 0.06 | 0 | 2.23 ± 1.2 | 13 / 4 | 0.0036 (0.0144) | 0.98 |
| `steel_freezing_range` (K) | select_fable | 2 | 11.3 | 1.85 | 0 | 4.42 ± 1.5 | 9 / 9 | 0.286 (0.419) | 0.96 |
| `steel_freezing_range` (K) | select_fable_map |  | 10.3 | 1.72 | 0 | 4.27 ± 1.7 | 9 / 8 | 0.21 (0.419) | 0.96 |
| `steel_freezing_range` (K) | select_fable_marginal |  | 10.5 | 1.13 | 0 | 4.11 ± 1.5 | 10 / 8 | 0.0936 (0.281) | 0.96 |
| `steel_freezing_range` (K) | select_fable_pd | 2 | 5.23 | 1.21 | 0 | 2.03 ± 1.3 | 18 / 0 | 0.000196 (0.00295) | 0.98 |
| `steel_freezing_range` (K) | select_fable_pd_map |  | 5.56 | 1.73 | 0 | 2.15 ± 1.3 | 18 / 0 | 0.000196 (0.00295) | 0.98 |
| `steel_freezing_range` (K) | select_fable_pd_marginal |  | 5.26 | 1.06 | 0 | 2.16 ± 1.3 | 18 / 0 | 0.000196 (0.00295) | 0.98 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | random |  | 0.00192 | 0.000815 | 0 | 0.00146 ± 0.00053 | 6 / 1 |  | 0.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | gp |  | 0.00317 | 0 | 0 | 0.00164 ± 0.00053 |  |  | 0.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0.00317 | 0 | 0 | 0.00164 ± 0.00053 | 0 / 0 | 1 (1) | 0.32 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0.00317 | 0 | 0 | 0.00164 ± 0.00053 | 0 / 0 | 1 (1) | 0.24 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0.00317 | 0 | 0 | 0.00164 ± 0.00053 | 0 / 0 | 1 (1) | 0.25 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0.000835 | 0 | 0 | 0.0007 ± 0.00042 | 6 / 2 | 0.123 (1) | 1.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0.00091 | 0 | 0 | 0.00067 ± 0.00045 | 5 / 2 | 0.063 (0.819) | 1.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0.000569 ± 0.00039 | 6 / 2 | 0.0499 (0.699) | 1.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0.00213 | 0.00126 | 0 | 0.0013 ± 0.00072 | 6 / 2 | 0.327 (1) | 1.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0.00264 | 0.0003 | 0 | 0.000807 ± 0.00073 | 7 / 1 | 0.161 (1) | 1.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0.000695 | 0 | 0 | 0.000685 ± 0.00036 | 7 / 1 | 0.0173 (0.259) | 1.00 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0.00159 | 0.0007 | 0 | 0.000875 ± 0.00041 | 6 / 2 | 0.123 (1) | 0.98 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0.00351 | 0 | 0 | 0.00138 ± 0.0006 | 5 / 2 | 0.612 (1) | 0.98 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0.00104 | 0 | 0 | 0.000838 ± 0.00032 | 5 / 3 | 0.0929 (1) | 0.98 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0.00282 | 0.000995 | 0 | 0.00126 ± 0.00055 | 4 / 4 | 0.484 (1) | 0.99 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0.00232 | 0 | 0 | 0.000874 ± 0.00045 | 6 / 2 | 0.161 (1) | 0.98 |
| `steel_austenite_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0.00032 | 0 | 0 | 0.00106 ± 0.00036 | 5 / 3 | 0.0929 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 0.000166 ± 0.00012 | 1 / 2 |  | 0.00 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 0.000247 ± 0.00016 |  |  | 0.00 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.000186 ± 0.00015 | 2 / 0 | 0.18 (1) | 0.98 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0.000174 ± 0.00015 | 2 / 0 | 0.18 (1) | 0.97 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.000162 ± 0.00015 | 2 / 0 | 0.18 (1) | 0.95 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0.000119 ± 0.00012 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0.000189 ± 0.00016 | 2 / 1 | 0.285 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 9.58e-05 ± 7.2e-05 | 3 / 0 | 0.109 (1) | 0.95 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0.00012 ± 8.9e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 3.68e-05 ± 3.7e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 7.16e-05 ± 7.2e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 3.56e-05 ± 3.6e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 3.56e-05 ± 3.6e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 3.56e-05 ± 3.6e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 0.96 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 0.99 |
| `steel_carbide_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 3.68e-05 ± 3.7e-05 | 3 / 0 | 0.109 (1) | 0.99 |
| `al_alloy_solidus` (K) | random |  | 39.7 | 33 | 22 | 32.3 ± 5.2 | 0 / 18 |  | 0.00 |
| `al_alloy_solidus` (K) | gp |  | 20.7 | 9.55 | 1.09 | 10.8 ± 2.4 |  |  | 0.00 |
| `al_alloy_solidus` (K) | rom | 1 | 20.7 | 9.55 | 1.09 | 10.8 ± 2.4 | 0 / 0 | 1 (1) | 0.02 |
| `al_alloy_solidus` (K) | rom_map |  | 20.7 | 9.55 | 1.09 | 10.8 ± 2.4 | 0 / 0 | 1 (1) | 0.02 |
| `al_alloy_solidus` (K) | rom_marginal |  | 20.7 | 9 | 1.09 | 10.4 ± 2.4 | 1 / 1 | 0.655 (1) | 0.02 |
| `al_alloy_solidus` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.0352 ± 0.024 | 17 / 1 | 0.000233 (0.0042) | 1.00 |
| `al_alloy_solidus` (K) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_opus_marginal |  | 0 | 0 | 0 | 0.0218 ± 0.022 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_opus_pd | 2 | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_fable | 2 | 1.43 | 0.58 | 0 | 2.08 ± 0.58 | 16 / 2 | 0.000327 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_fable_map |  | 1.9 | 0.58 | 0 | 2.21 ± 0.66 | 17 / 1 | 0.000276 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_fable_marginal |  | 0 | 0 | 0 | 1.37 ± 0.45 | 17 / 1 | 0.000233 (0.0042) | 1.00 |
| `al_alloy_solidus` (K) | select_fable_pd | 2 | 0 | 0 | 0 | 0.46 ± 0.077 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_fable_pd_map |  | 0.44 | 0 | 0 | 0.629 ± 0.16 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_solidus` (K) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0.465 ± 0.14 | 17 / 0 | 0.000293 (0.00442) | 1.00 |
| `al_alloy_freezing_range` (K) | random |  | 37.2 | 30.6 | 18.3 | 29.1 ± 4.6 | 2 / 16 |  | 0.00 |
| `al_alloy_freezing_range` (K) | gp |  | 25.7 | 14.3 | 0.7 | 13.2 ± 2.1 |  |  | 0.00 |
| `al_alloy_freezing_range` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.567 ± 0.43 | 17 / 0 | 0.000293 (0.00381) | 0.99 |
| `al_alloy_freezing_range` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0.567 ± 0.43 | 17 / 0 | 0.000293 (0.00381) | 0.99 |
| `al_alloy_freezing_range` (K) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.6 ± 0.43 | 17 / 0 | 0.000293 (0.00381) | 0.99 |
| `al_alloy_freezing_range` (K) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_opus_map |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_opus_marginal |  | 0 | 0 | 0 | 0.0152 ± 0.015 | 17 / 1 | 0.000233 (0.0035) | 1.00 |
| `al_alloy_freezing_range` (K) | select_opus_pd | 2 | 0 | 0 | 0 | 0.0446 ± 0.045 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_opus_pd_map |  | 0.825 | 0 | 0 | 0.322 ± 0.2 | 16 / 2 | 0.000327 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.265 ± 0.095 | 17 / 1 | 0.000233 (0.0035) | 1.00 |
| `al_alloy_freezing_range` (K) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_fable_pd | 2 | 0 | 0 | 0 | 0.106 ± 0.074 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_fable_pd_map |  | 0.35 | 0 | 0 | 0.175 ± 0.11 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_freezing_range` (K) | select_fable_pd_marginal |  | 0.38 | 0 | 0 | 0.187 ± 0.096 | 17 / 0 | 0.000293 (0.00381) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | random |  | 0.0456 | 0.0376 | 0.0201 | 0.0356 ± 0.0041 | 0 / 20 |  | 0.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0.0056 | 0 | 0 | 0.0043 ± 0.00086 |  |  | 0.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0.00419 | 0 | 0 | 0.00379 ± 0.00095 | 10 / 5 | 0.307 (0.307) | 0.92 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0.000795 | 0 | 0 | 0.0027 ± 0.00066 | 11 / 1 | 0.0037 (0.0111) | 0.93 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0.000795 | 0 | 0 | 0.00241 ± 0.00059 | 11 / 3 | 0.011 (0.022) | 0.93 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 1.52e-05 ± 1.5e-05 | 17 / 0 | 0.000293 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 4.32e-05 ± 3.1e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 4.32e-05 ± 3.1e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 7.6e-05 ± 3e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 7.6e-05 ± 3e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 9.12e-05 ± 3.9e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0.000137 ± 3.5e-05 | 17 / 2 | 0.000213 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0.000137 ± 3.5e-05 | 17 / 2 | 0.000213 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0.000122 ± 3.4e-05 | 17 / 2 | 0.000213 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 7.6e-05 ± 3e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 7.6e-05 ± 3e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `al_alloy_second_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0.000106 ± 4e-05 | 17 / 1 | 0.000233 (0.0032) | 1.00 |
| `hf_refractory_solidus` (K) | random |  | 187 | 118 | 75.7 | 127 ± 15 | 0 / 20 |  | 0.00 |
| `hf_refractory_solidus` (K) | gp |  | 46.7 | 9.06 | 0 | 26.7 ± 5.7 |  |  | 0.00 |
| `hf_refractory_solidus` (K) | rom | 1 | 39.2 | 7.83 | 0 | 16.1 ± 2.1 | 12 / 8 | 0.104 (0.104) | 1.00 |
| `hf_refractory_solidus` (K) | rom_map |  | 24.3 | 0 | 0 | 12.7 ± 2.4 | 16 / 4 | 0.000586 (0.00351) | 1.00 |
| `hf_refractory_solidus` (K) | rom_marginal |  | 31.7 | 0 | 0 | 13.2 ± 1.7 | 13 / 7 | 0.0215 (0.043) | 1.00 |
| `hf_refractory_solidus` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.935 ± 0.13 | 19 / 1 | 0.000103 (0.00186) | 1.00 |
| `hf_refractory_solidus` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 1.21 ± 0.29 | 19 / 0 | 0.000132 (0.00224) | 1.00 |
| `hf_refractory_solidus` (K) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.64 ± 0.18 | 19 / 0 | 0.000132 (0.00224) | 1.00 |
| `hf_refractory_solidus` (K) | select_opus | 2 | 1.23 | 0 | 0 | 5.66 ± 1.2 | 18 / 2 | 0.000293 (0.00264) | 1.00 |
| `hf_refractory_solidus` (K) | select_opus_map |  | 9.06 | 0 | 0 | 6.62 ± 1.5 | 17 / 3 | 0.000168 (0.00235) | 1.00 |
| `hf_refractory_solidus` (K) | select_opus_marginal |  | 6.15 | 0 | 0 | 6.8 ± 1.3 | 16 / 4 | 0.000261 (0.00261) | 1.00 |
| `hf_refractory_solidus` (K) | select_opus_pd | 2 | 0 | 0 | 0 | 1.4 ± 0.43 | 19 / 0 | 0.000132 (0.00224) | 1.00 |
| `hf_refractory_solidus` (K) | select_opus_pd_map |  | 0 | 0 | 0 | 1.79 ± 0.45 | 18 / 0 | 0.000196 (0.00236) | 1.00 |
| `hf_refractory_solidus` (K) | select_opus_pd_marginal |  | 0 | 0 | 0 | 1.35 ± 0.43 | 18 / 0 | 0.000196 (0.00236) | 1.00 |
| `hf_refractory_solidus` (K) | select_fable | 2 | 16.4 | 0 | 0 | 9.42 ± 1.4 | 15 / 5 | 0.00169 (0.00605) | 1.00 |
| `hf_refractory_solidus` (K) | select_fable_map |  | 15.2 | 0 | 0 | 9.49 ± 1.3 | 16 / 4 | 0.00121 (0.00605) | 1.00 |
| `hf_refractory_solidus` (K) | select_fable_marginal |  | 16.9 | 0 | 0 | 9.05 ± 1.6 | 16 / 4 | 0.00121 (0.00605) | 1.00 |
| `hf_refractory_solidus` (K) | select_fable_pd | 2 | 3.69 | 0 | 0 | 5.99 ± 0.57 | 17 / 3 | 0.000168 (0.00235) | 1.00 |
| `hf_refractory_solidus` (K) | select_fable_pd_map |  | 4.92 | 0 | 0 | 6.58 ± 0.68 | 17 / 3 | 0.000322 (0.00264) | 1.00 |
| `hf_refractory_solidus` (K) | select_fable_pd_marginal |  | 2.46 | 0 | 0 | 6.36 ± 0.74 | 17 / 3 | 0.000395 (0.00276) | 1.00 |
| `hf_refractory_freezing_range` (K) | random |  | 54 | 27.3 | 13.5 | 31.2 ± 4.5 | 1 / 19 |  | 0.00 |
| `hf_refractory_freezing_range` (K) | gp |  | 16.8 | 2.41 | 0 | 8.37 ± 2.4 |  |  | 0.00 |
| `hf_refractory_freezing_range` (K) | subsystem_extrapolation | 1 | 3.9 | 0 | 0 | 1.41 ± 0.1 | 18 / 2 | 1.91e-05 (0.000286) | 1.00 |
| `hf_refractory_freezing_range` (K) | subsystem_extrapolation_map |  | 6.35 | 0.78 | 0 | 2.12 ± 0.16 | 17 / 3 | 0.000586 (0.00703) | 1.00 |
| `hf_refractory_freezing_range` (K) | subsystem_extrapolation_marginal |  | 7.13 | 0.425 | 0 | 2.33 ± 0.15 | 16 / 4 | 0.00102 (0.0105) | 1.00 |
| `hf_refractory_freezing_range` (K) | select_opus | 2 | 7.28 | 4.68 | 1.17 | 7.2 ± 1.6 | 7 / 9 | 0.717 (1) | 0.72 |
| `hf_refractory_freezing_range` (K) | select_opus_map |  | 7.48 | 3.51 | 0 | 6.37 ± 1.6 | 10 / 4 | 0.245 (1) | 0.65 |
| `hf_refractory_freezing_range` (K) | select_opus_marginal |  | 7.65 | 3.55 | 0 | 6.36 ± 1.6 | 8 / 6 | 0.272 (1) | 0.67 |
| `hf_refractory_freezing_range` (K) | select_opus_pd | 2 | 3.6 | 0 | 0 | 1.33 ± 0.2 | 18 / 2 | 2.67e-05 (0.000374) | 1.00 |
| `hf_refractory_freezing_range` (K) | select_opus_pd_map |  | 3.67 | 0 | 0 | 1.54 ± 0.23 | 18 / 2 | 0.000261 (0.0034) | 1.00 |
| `hf_refractory_freezing_range` (K) | select_opus_pd_marginal |  | 2.34 | 0.39 | 0 | 1.4 ± 0.27 | 17 / 3 | 0.000952 (0.0105) | 1.00 |
| `hf_refractory_freezing_range` (K) | select_fable | 2 | 12.4 | 3.12 | 0 | 7.47 ± 2.1 | 11 / 5 | 0.0879 (0.616) | 0.81 |
| `hf_refractory_freezing_range` (K) | select_fable_map |  | 12.1 | 2.34 | 0 | 7 ± 2.2 | 16 / 1 | 0.00193 (0.0174) | 0.86 |
| `hf_refractory_freezing_range` (K) | select_fable_marginal |  | 12 | 2.34 | 0 | 6.41 ± 2 | 12 / 4 | 0.034 (0.272) | 0.81 |
| `hf_refractory_freezing_range` (K) | select_fable_pd | 2 | 9.42 | 5.46 | 0 | 4.93 ± 0.52 | 8 / 11 | 0.717 (1) | 0.99 |
| `hf_refractory_freezing_range` (K) | select_fable_pd_map |  | 8.7 | 3.9 | 0 | 4.14 ± 0.49 | 12 / 8 | 0.231 (1) | 0.99 |
| `hf_refractory_freezing_range` (K) | select_fable_pd_marginal |  | 8.72 | 5.49 | 0 | 4.6 ± 0.49 | 10 / 10 | 0.622 (1) | 0.99 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | random |  | 0 | 0 | 0 | 0 ± 0 | 3 / 0 |  | 0.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 0.000667 ± 0.00044 |  |  | 0.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom | 1 | 0 | 0 | 0 | 0.000667 ± 0.00044 | 0 / 0 | 1 (1) | 0.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom_map |  | 0 | 0 | 0 | 0.000667 ± 0.00044 | 0 / 0 | 1 (1) | 0.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0 | 0 | 0 | 0.000667 ± 0.00044 | 0 / 0 | 1 (1) | 0.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.000419 ± 0.00042 | 2 / 0 | 0.18 (1) | 0.95 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0.000419 ± 0.00042 | 2 / 0 | 0.18 (1) | 0.95 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.000419 ± 0.00042 | 2 / 0 | 0.18 (1) | 0.95 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0.000737 ± 0.00046 | 1 / 1 | 0.655 (1) | 0.73 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0.000615 ± 0.00045 | 1 / 1 | 0.655 (1) | 0.69 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0.00163 | 0 | 0 | 0.000811 ± 0.00056 | 1 / 1 | 0.655 (1) | 0.72 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0.000232 ± 0.00023 | 2 / 1 | 0.285 (1) | 1.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 0.99 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 1.00 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 0.98 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 0.98 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0 ± 0 | 3 / 0 | 0.109 (1) | 0.98 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 0.000419 ± 0.00042 | 2 / 0 | 0.18 (1) | 0.99 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 0.000419 ± 0.00042 | 2 / 0 | 0.18 (1) | 0.98 |
| `hf_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 0.000419 ± 0.00042 | 2 / 0 | 0.18 (1) | 0.98 |
| `cu_ti_3d_solidus` (K) | random |  | 241 | 217 | 184 | 217 ± 14 | 3 / 16 |  | 0.00 |
| `cu_ti_3d_solidus` (K) | gp |  | 221 | 171 | 136 | 174 ± 12 |  |  | 0.00 |
| `cu_ti_3d_solidus` (K) | rom | 1 | 196 | 155 | 103 | 144 ± 11 | 12 / 2 | 0.00189 (0.00566) | 0.63 |
| `cu_ti_3d_solidus` (K) | rom_map |  | 206 | 156 | 91.6 | 151 ± 14 | 9 / 4 | 0.0464 (0.0928) | 0.51 |
| `cu_ti_3d_solidus` (K) | rom_marginal |  | 181 | 139 | 119 | 151 ± 13 | 9 / 4 | 0.0464 (0.0928) | 0.45 |
| `cu_ti_3d_solidus` (K) | subsystem_extrapolation | 1 | 14 | 8.75 | 0 | 9.46 ± 6.3 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.97 |
| `cu_ti_3d_solidus` (K) | subsystem_extrapolation_map |  | 14 | 0 | 0 | 8.74 ± 4.9 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.97 |
| `cu_ti_3d_solidus` (K) | subsystem_extrapolation_marginal |  | 14 | 0 | 0 | 8.54 ± 4.9 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.97 |
| `cu_ti_3d_solidus` (K) | select_opus | 2 | 0 | 0 | 0 | 5.9 ± 2.7 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `cu_ti_3d_solidus` (K) | select_opus_map |  | 0 | 0 | 0 | 6.45 ± 3 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.99 |
| `cu_ti_3d_solidus` (K) | select_opus_marginal |  | 0 | 0 | 0 | 4.9 ± 2.3 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.98 |
| `cu_ti_3d_solidus` (K) | select_opus_pd | 2 | 9.89 | 8.75 | 0 | 13.1 ± 6.5 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `cu_ti_3d_solidus` (K) | select_opus_pd_map |  | 18.9 | 14.9 | 0 | 17 ± 6.5 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `cu_ti_3d_solidus` (K) | select_opus_pd_marginal |  | 23.1 | 8.75 | 5.9 | 16.8 ± 8 | 19 / 1 | 3.81e-06 (3.43e-05) | 1.00 |
| `cu_ti_3d_solidus` (K) | select_fable | 2 | 14 | 0 | 0 | 7.27 ± 4.8 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.97 |
| `cu_ti_3d_solidus` (K) | select_fable_map |  | 26.9 | 12.9 | 0 | 11.3 ± 7.3 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.97 |
| `cu_ti_3d_solidus` (K) | select_fable_marginal |  | 14 | 0 | 0 | 6.92 ± 4.5 | 20 / 0 | 1.91e-06 (3.43e-05) | 0.97 |
| `cu_ti_3d_solidus` (K) | select_fable_pd | 2 | 0 | 0 | 0 | 1.77 ± 1.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `cu_ti_3d_solidus` (K) | select_fable_pd_map |  | 0 | 0 | 0 | 2.47 ± 1.7 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `cu_ti_3d_solidus` (K) | select_fable_pd_marginal |  | 0 | 0 | 0 | 1.42 ± 1.4 | 20 / 0 | 1.91e-06 (3.43e-05) | 1.00 |
| `cu_ti_3d_freezing_range` (K) | random |  | 53.2 | 48.2 | 35.1 | 45.6 ± 4.6 | 4 / 15 |  | 0.00 |
| `cu_ti_3d_freezing_range` (K) | gp |  | 43.8 | 33.4 | 20.3 | 32.7 ± 3.2 |  |  | 0.00 |
| `cu_ti_3d_freezing_range` (K) | subsystem_extrapolation | 1 | 33.4 | 19.8 | 11.9 | 22.6 ± 3.4 | 9 / 4 | 0.0159 (0.127) | 0.41 |
| `cu_ti_3d_freezing_range` (K) | subsystem_extrapolation_map |  | 33.9 | 22.9 | 14.2 | 24.2 ± 3.3 | 9 / 3 | 0.0121 (0.121) | 0.35 |
| `cu_ti_3d_freezing_range` (K) | subsystem_extrapolation_marginal |  | 31.2 | 20.6 | 13.2 | 23.9 ± 3.5 | 10 / 4 | 0.0132 (0.121) | 0.35 |
| `cu_ti_3d_freezing_range` (K) | select_opus | 2 | 22.5 | 14.6 | 7.37 | 14.5 ± 4 | 15 / 0 | 0.000653 (0.0098) | 0.34 |
| `cu_ti_3d_freezing_range` (K) | select_opus_map |  | 25 | 19.8 | 11 | 18.3 ± 4 | 12 / 3 | 0.0064 (0.0767) | 0.29 |
| `cu_ti_3d_freezing_range` (K) | select_opus_marginal |  | 28.2 | 18.6 | 10.4 | 19.1 ± 3.9 | 14 / 1 | 0.00147 (0.0205) | 0.27 |
| `cu_ti_3d_freezing_range` (K) | select_opus_pd | 2 | 29.1 | 21.5 | 13.2 | 23.1 ± 3.8 | 8 / 2 | 0.0217 (0.145) | 0.26 |
| `cu_ti_3d_freezing_range` (K) | select_opus_pd_map |  | 29.9 | 22.2 | 13.2 | 23.4 ± 3.8 | 9 / 2 | 0.0207 (0.145) | 0.35 |
| `cu_ti_3d_freezing_range` (K) | select_opus_pd_marginal |  | 31.6 | 23.8 | 13.2 | 23.5 ± 4.3 | 8 / 3 | 0.0329 (0.145) | 0.30 |
| `cu_ti_3d_freezing_range` (K) | select_fable | 2 | 31.3 | 24.5 | 14.3 | 25 ± 3.7 | 7 / 2 | 0.0208 (0.145) | 0.30 |
| `cu_ti_3d_freezing_range` (K) | select_fable_map |  | 37.3 | 28.2 | 15.9 | 27.2 ± 3.9 | 7 / 2 | 0.0208 (0.145) | 0.22 |
| `cu_ti_3d_freezing_range` (K) | select_fable_marginal |  | 37.1 | 24.2 | 14.8 | 25.5 ± 3.7 | 7 / 2 | 0.0283 (0.145) | 0.27 |
| `cu_ti_3d_freezing_range` (K) | select_fable_pd | 2 | 26.7 | 20.4 | 11.7 | 20.3 ± 4.1 | 10 / 1 | 0.00442 (0.0575) | 0.26 |
| `cu_ti_3d_freezing_range` (K) | select_fable_pd_map |  | 30.3 | 23.9 | 14.5 | 23.9 ± 4.2 | 8 / 2 | 0.0365 (0.145) | 0.29 |
| `cu_ti_3d_freezing_range` (K) | select_fable_pd_marginal |  | 30.4 | 21.8 | 12.5 | 22.2 ± 3.8 | 9 / 1 | 0.00687 (0.0767) | 0.24 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | random |  | 0.0368 | 0.0176 | 0.00109 | 0.0191 ± 0.0061 | 1 / 13 |  | 0.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | gp |  | 0 | 0 | 0 | 0.00317 ± 0.0018 |  |  | 0.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 4.34e-05 ± 4.3e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 4.34e-05 ± 4.3e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 4.34e-05 ± 4.3e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0 ± 0 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 8.94e-05 ± 8.9e-05 | 6 / 1 | 0.0425 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0 ± 0 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0.000776 ± 0.00061 | 6 / 1 | 0.063 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0.00143 ± 0.00087 | 5 / 3 | 0.183 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.000133 ± 9.7e-05 | 6 / 1 | 0.063 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 8.68e-05 ± 8.7e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0.00022 ± 0.00013 | 6 / 2 | 0.0797 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 8.68e-05 ± 8.7e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0 | 0 | 0 | 8.68e-05 ± 8.7e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0 | 0 | 0 | 8.68e-05 ± 8.7e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0 | 0 | 0 | 8.68e-05 ± 8.7e-05 | 6 / 0 | 0.0277 (0.416) | 1.00 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | random |  | 0.156 | 0.121 | 0.0985 | 0.126 ± 0.012 | 2 / 18 |  | 0.00 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0.0701 | 0.0332 | 0.00837 | 0.0437 ± 0.01 |  |  | 0.00 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | rom | 1 | 0.0701 | 0.0332 | 0.00837 | 0.0437 ± 0.01 | 0 / 0 | 1 (1) | 0.08 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | rom_map |  | 0.0732 | 0.0332 | 0.00699 | 0.0435 ± 0.01 | 1 / 1 | 0.655 (1) | 0.06 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0.0687 | 0.0263 | 0.00699 | 0.0391 ± 0.0085 | 3 / 0 | 0.109 (0.544) | 0.10 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0.0356 | 0.0164 | 0 | 0.0272 ± 0.0097 | 17 / 3 | 0.000395 (0.00553) | 0.88 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0.0346 | 0.0208 | 0.00166 | 0.0275 ± 0.0099 | 16 / 3 | 0.000539 (0.007) | 0.84 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0.038 | 0.0253 | 0.00166 | 0.0283 ± 0.01 | 17 / 2 | 0.00194 (0.0194) | 0.84 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0.0333 | 0.0274 | 0.00276 | 0.0258 ± 0.0026 | 12 / 8 | 0.0897 (0.538) | 0.98 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0.0314 | 0.0191 | 0.00414 | 0.0221 ± 0.0031 | 14 / 6 | 0.0121 (0.0966) | 0.98 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0.0341 | 0.0205 | 0.00276 | 0.0199 ± 0.0025 | 15 / 5 | 0.00422 (0.038) | 0.98 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0.0222 | 0.0108 | 0.00394 | 0.014 ± 0.0039 | 18 / 1 | 0.000182 (0.00291) | 0.94 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0.0214 | 0.0129 | 0.00532 | 0.0166 ± 0.0041 | 16 / 3 | 0.000967 (0.0106) | 0.94 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0.0205 | 0.0108 | 0.00532 | 0.0154 ± 0.0039 | 17 / 2 | 0.00025 (0.00375) | 0.94 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0.0355 | 0.0152 | 0.00138 | 0.0172 ± 0.0062 | 19 / 1 | 3.62e-05 (0.000652) | 0.95 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0.0329 | 0.0193 | 0.00276 | 0.0192 ± 0.0063 | 16 / 4 | 0.000708 (0.00849) | 0.95 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0.0323 | 0.0152 | 0.00138 | 0.0175 ± 0.0065 | 17 / 3 | 0.000168 (0.00285) | 0.95 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0.0371 | 0.0235 | 0.00552 | 0.0268 ± 0.0039 | 12 / 8 | 0.33 (0.99) | 1.00 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0.0254 | 0.0179 | 0.00276 | 0.0208 ± 0.0027 | 12 / 7 | 0.0364 (0.255) | 1.00 |
| `cu_ti_3d_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0.0375 | 0.021 | 0.0069 | 0.0255 ± 0.0041 | 12 / 8 | 0.143 (0.572) | 1.00 |
| `al_refractory_solidus` (K) | random |  | 220 | 190 | 108 | 176 ± 28 | 3 / 16 |  | 0.00 |
| `al_refractory_solidus` (K) | gp |  | 139 | 26.5 | 0 | 58.6 ± 15 |  |  | 0.00 |
| `al_refractory_solidus` (K) | rom | 1 | 135 | 45.7 | 0 | 56.3 ± 14 | 7 / 10 | 0.831 (1) | 0.81 |
| `al_refractory_solidus` (K) | rom_map |  | 96.6 | 26.4 | 0 | 51 ± 14 | 8 / 8 | 0.569 (1) | 0.83 |
| `al_refractory_solidus` (K) | rom_marginal |  | 97.5 | 27.8 | 0 | 48.3 ± 14 | 7 / 8 | 0.427 (1) | 0.83 |
| `al_refractory_solidus` (K) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0 ± 0 | 17 / 0 | 0.000293 (0.00527) | 1.00 |
| `al_refractory_solidus` (K) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 1.64 ± 1.2 | 17 / 2 | 0.000293 (0.00527) | 1.00 |
| `al_refractory_solidus` (K) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 1.07 ± 0.58 | 17 / 1 | 0.000327 (0.00527) | 1.00 |
| `al_refractory_solidus` (K) | select_opus | 2 | 73.9 | 23.4 | 0 | 37.9 ± 15 | 12 / 4 | 0.00613 (0.0552) | 0.92 |
| `al_refractory_solidus` (K) | select_opus_map |  | 81.1 | 23.4 | 0 | 38.5 ± 15 | 12 / 5 | 0.0113 (0.0906) | 0.92 |
| `al_refractory_solidus` (K) | select_opus_marginal |  | 84 | 22 | 0 | 40.5 ± 15 | 10 / 7 | 0.0615 (0.369) | 0.92 |
| `al_refractory_solidus` (K) | select_opus_pd | 2 | 2.94 | 0 | 0 | 8.91 ± 3.2 | 15 / 3 | 0.000863 (0.0104) | 0.99 |
| `al_refractory_solidus` (K) | select_opus_pd_map |  | 10.1 | 0 | 0 | 10.4 ± 3.3 | 15 / 3 | 0.00159 (0.0159) | 0.99 |
| `al_refractory_solidus` (K) | select_opus_pd_marginal |  | 7.28 | 0 | 0 | 9.65 ± 2.6 | 15 / 2 | 0.0014 (0.0154) | 0.99 |
| `al_refractory_solidus` (K) | select_fable | 2 | 53.2 | 24.8 | 0 | 35.5 ± 13 | 13 / 6 | 0.0364 (0.255) | 0.95 |
| `al_refractory_solidus` (K) | select_fable_map |  | 43 | 22 | 0 | 33.6 ± 13 | 11 / 8 | 0.0702 (0.369) | 0.95 |
| `al_refractory_solidus` (K) | select_fable_marginal |  | 39.4 | 23.4 | 0 | 31.5 ± 13 | 10 / 8 | 0.102 (0.41) | 0.95 |
| `al_refractory_solidus` (K) | select_fable_pd | 2 | 31.1 | 0 | 0 | 12.2 ± 8 | 17 / 0 | 0.000293 (0.00527) | 0.97 |
| `al_refractory_solidus` (K) | select_fable_pd_map |  | 35.3 | 2.8 | 0 | 17.7 ± 8.6 | 15 / 2 | 0.000503 (0.00653) | 0.97 |
| `al_refractory_solidus` (K) | select_fable_pd_marginal |  | 33.9 | 0 | 0 | 13.5 ± 8 | 16 / 1 | 0.000421 (0.00589) | 0.97 |
| `al_refractory_freezing_range` (K) | random |  | 52.9 | 42.8 | 22.5 | 36.3 ± 3.8 | 3 / 16 |  | 0.00 |
| `al_refractory_freezing_range` (K) | gp |  | 30.6 | 26.4 | 13.8 | 23.5 ± 2.6 |  |  | 0.00 |
| `al_refractory_freezing_range` (K) | subsystem_extrapolation | 1 | 33.6 | 28.7 | 17.2 | 27.9 ± 2.7 | 3 / 13 | 0.0386 (0.502) | 0.68 |
| `al_refractory_freezing_range` (K) | subsystem_extrapolation_map |  | 39.4 | 27.7 | 17.8 | 28.2 ± 3 | 1 / 14 | 0.00451 (0.0676) | 0.64 |
| `al_refractory_freezing_range` (K) | subsystem_extrapolation_marginal |  | 37 | 29.9 | 20.9 | 29.9 ± 2.3 | 2 / 13 | 0.00898 (0.126) | 0.68 |
| `al_refractory_freezing_range` (K) | select_opus | 2 | 26.8 | 21.7 | 14.7 | 20.7 ± 2.2 | 8 / 5 | 0.208 (1) | 0.41 |
| `al_refractory_freezing_range` (K) | select_opus_map |  | 29.3 | 23.3 | 14.2 | 22.9 ± 2.9 | 11 / 3 | 0.245 (1) | 0.44 |
| `al_refractory_freezing_range` (K) | select_opus_marginal |  | 30.8 | 23.8 | 14.7 | 22.2 ± 2.5 | 9 / 4 | 0.249 (1) | 0.43 |
| `al_refractory_freezing_range` (K) | select_opus_pd | 2 | 36.1 | 29.1 | 16.6 | 26.2 ± 2.1 | 5 / 12 | 0.21 (1) | 0.86 |
| `al_refractory_freezing_range` (K) | select_opus_pd_map |  | 32.9 | 29.6 | 15.5 | 26.9 ± 1.8 | 5 / 12 | 0.124 (1) | 0.86 |
| `al_refractory_freezing_range` (K) | select_opus_pd_marginal |  | 32.1 | 27.9 | 13.9 | 26.7 ± 2 | 6 / 11 | 0.193 (1) | 0.85 |
| `al_refractory_freezing_range` (K) | select_fable | 2 | 29.5 | 22.2 | 8.97 | 23.2 ± 2.6 | 9 / 8 | 0.981 (1) | 0.91 |
| `al_refractory_freezing_range` (K) | select_fable_map |  | 35.5 | 24.7 | 8.16 | 23.7 ± 2.6 | 8 / 10 | 0.845 (1) | 0.91 |
| `al_refractory_freezing_range` (K) | select_fable_marginal |  | 29.6 | 24.5 | 14.4 | 24.4 ± 2.7 | 8 / 9 | 0.619 (1) | 0.90 |
| `al_refractory_freezing_range` (K) | select_fable_pd | 2 | 24.5 | 22.2 | 18.5 | 21.8 ± 1.9 | 10 / 6 | 0.501 (1) | 0.79 |
| `al_refractory_freezing_range` (K) | select_fable_pd_map |  | 25.1 | 23.4 | 16.7 | 22.3 ± 2.2 | 10 / 6 | 0.535 (1) | 0.80 |
| `al_refractory_freezing_range` (K) | select_fable_pd_marginal |  | 26.7 | 23.1 | 17.9 | 22.2 ± 2.1 | 9 / 7 | 0.717 (1) | 0.77 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | random |  | 0.0696 | 0.0543 | 0.0027 | 0.0442 ± 0.012 | 5 / 7 |  | 0.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | gp |  | 0.0409 | 0 | 0 | 0.023 ± 0.0087 |  |  | 0.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.000434 ± 0.00043 | 12 / 0 | 0.00222 (0.0333) | 1.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0 | 0 | 0 | 0.000598 ± 0.00046 | 12 / 0 | 0.00222 (0.0333) | 1.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.000926 ± 0.00049 | 12 / 0 | 0.00222 (0.0333) | 1.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0.00662 ± 0.0046 | 11 / 0 | 0.00335 (0.0333) | 0.99 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0 | 0 | 0 | 0.00737 ± 0.0046 | 11 / 0 | 0.00335 (0.0333) | 0.99 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0.00744 ± 0.0046 | 11 / 0 | 0.00335 (0.0333) | 0.99 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0.000242 ± 0.00014 | 12 / 0 | 0.00222 (0.0333) | 1.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0.000241 ± 0.00017 | 12 / 0 | 0.00222 (0.0333) | 1.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.000349 ± 0.00019 | 12 / 0 | 0.00222 (0.0333) | 1.00 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0 | 0 | 0 | 0.00677 ± 0.0046 | 11 / 0 | 0.00335 (0.0333) | 0.99 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0 | 0 | 0 | 0.00677 ± 0.0046 | 11 / 0 | 0.00335 (0.0333) | 0.99 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0 | 0 | 0 | 0.00662 ± 0.0046 | 11 / 0 | 0.00335 (0.0333) | 0.99 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0.0231 | 0 | 0 | 0.0111 ± 0.008 | 10 / 0 | 0.00506 (0.0333) | 0.98 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0.0231 | 0 | 0 | 0.0112 ± 0.008 | 10 / 0 | 0.00506 (0.0333) | 0.98 |
| `al_refractory_intermetallic_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0.0231 | 0 | 0 | 0.0108 ± 0.0081 | 10 / 0 | 0.00506 (0.0333) | 0.98 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | random |  | 0.0333 | 0.0135 | 0 | 0.0168 ± 0.0063 | 6 / 5 |  | 0.00 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | gp |  | 0.0242 | 0.00178 | 0 | 0.0118 ± 0.0036 |  |  | 0.00 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom | 1 | 0.0246 | 0 | 0 | 0.01 ± 0.0036 | 4 / 2 | 0.6 (1) | 0.80 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom_map |  | 0.0246 | 0 | 0 | 0.0108 ± 0.0037 | 4 / 3 | 0.735 (1) | 0.79 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | rom_marginal |  | 0.012 | 0 | 0 | 0.00734 ± 0.0024 | 5 / 3 | 0.0929 (0.279) | 0.79 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation | 1 | 0 | 0 | 0 | 0.0031 ± 0.0017 | 9 / 0 | 0.00769 (0.115) | 0.95 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_map |  | 0.0041 | 0 | 0 | 0.00342 ± 0.0018 | 9 / 0 | 0.00769 (0.115) | 0.95 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | subsystem_extrapolation_marginal |  | 0 | 0 | 0 | 0.0031 ± 0.0017 | 9 / 0 | 0.00769 (0.115) | 0.95 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus | 2 | 0 | 0 | 0 | 0.00379 ± 0.0019 | 8 / 2 | 0.0125 (0.115) | 0.99 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_map |  | 0.00173 | 0 | 0 | 0.00362 ± 0.0021 | 9 / 0 | 0.00769 (0.115) | 0.99 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_marginal |  | 0 | 0 | 0 | 0.00331 ± 0.0019 | 9 / 0 | 0.00769 (0.115) | 0.99 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd | 2 | 0 | 0 | 0 | 0.00241 ± 0.0017 | 10 / 0 | 0.00506 (0.0911) | 0.99 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_map |  | 0 | 0 | 0 | 0.00241 ± 0.0017 | 10 / 0 | 0.00506 (0.0911) | 0.99 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_opus_pd_marginal |  | 0 | 0 | 0 | 0.00257 ± 0.0017 | 10 / 0 | 0.00506 (0.0911) | 0.99 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable | 2 | 0.0052 | 0.00178 | 0 | 0.00834 ± 0.0032 | 6 / 0 | 0.0277 (0.166) | 0.91 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_map |  | 0.0052 | 0.00178 | 0 | 0.00841 ± 0.0032 | 6 / 0 | 0.0277 (0.166) | 0.90 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_marginal |  | 0.0052 | 0.00178 | 0 | 0.00834 ± 0.0032 | 6 / 0 | 0.0277 (0.166) | 0.91 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd | 2 | 0.00356 | 0.00178 | 0 | 0.00584 ± 0.0028 | 8 / 0 | 0.0117 (0.115) | 0.95 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_map |  | 0.00356 | 0.00178 | 0 | 0.00627 ± 0.0029 | 8 / 0 | 0.0117 (0.115) | 0.95 |
| `al_refractory_main_phase_fraction` (mole fraction between 0 and 1) | select_fable_pd_marginal |  | 0.00356 | 0.00178 | 0 | 0.00586 ± 0.0028 | 8 / 1 | 0.0109 (0.115) | 0.95 |
