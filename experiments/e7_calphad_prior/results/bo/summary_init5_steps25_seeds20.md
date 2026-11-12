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
