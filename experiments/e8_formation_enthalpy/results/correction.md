**mace: 400 held-out compounds, 78 elements**

| No experimental labels | MAE, eV/atom | Bias, eV/atom | MAE with the weights shuffled over elements |
|---|---|---|---|
| potential as shipped | 0.195 | +0.154 |  |

| With n labels: MAE, eV/atom | n = 10 | n = 20 | n = 50 | n = 100 | n = 200 | n = 400 |
|---|---|---|---|---|---|---|
| fitted, shrunk toward zero | 0.192 | 0.211 | 0.255 | 0.222 | 0.187 | 0.158 |
| offset only | 0.196 | 0.190 | 0.186 | 0.183 | 0.184 | 0.183 |

Labels are drawn from the training half, 20 draws; ridge strength 0.01.
