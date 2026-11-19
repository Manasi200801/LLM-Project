# P2 Human Benchmark Reference — QA

Generated from ISSP 2024 Digital Societies Release 2.0.0 (2026-10-16).
Source DTA filename: `ZA10020_v2-0-0.dta` (SHA-256 `95c898282aed0b470a1cc003ea78345c256a6d45b37a38c8ad6a76239ac78d3a`).

Seed: `20261117`; split-half repetitions per country × item × view: `1000`; output rows: `108`.
No weights were applied. The source data and existing workbooks were read only.

## Selected sample and Q10d denominators

| Country | Selected N | Q10d main N | Q10d robustness N | Observed interview-language values in full country sample |
|---|---:|---:|---:|---|
| Germany | 1,399 | 1,252 | 1,289 | deu (German): 1399 |
| Austria | 1,546 | 1,429 | 1,436 | deu (German): 1546 |
| Switzerland | 2,129 | 2,039 | 2,041 | deu (German): 2129; fra (French): 731; ita (Italian): 168 |
| USA | 1,534 | 1,467 | 1,469 | eng (English): 1534; spa (Spanish): 56 |
| Australia | 1,015 | 911 | 917 | eng (English): 1015 |
| Canada | 1,342 | 1,338 | 1,338 | eng (English): 1342; fra (French): 273 |

## Germany routing discrepancy

Observed in the selected source sample: Q1=7 N=67; Q10d=-4 N=56; among Q1=7, Q10d codes 3/4/5 = 3/2/6. These records are retained in the source-based audit; the common main Q10d view excludes Q1=7, while the all-substantive robustness view includes its substantive Q10d answers.

## Weight documentation and data-field audit

| Country | Available fields / selected-sample distinct values | Q10d main field completeness | Documentation summary | Decision |
|---|---|---:|---|---|
| Germany | DWEIGHT_HH: 1 distinct, 1399/1399 nonmissing; DWEIGHT_TS: 2 distinct, 1399/1399 nonmissing; DWEIGHT_COM: 2 distinct, 1399/1399 nonmissing; PSWEIGHT: 1 distinct, 1399/1399 nonmissing; WEIGHT_COM: 2 distinct, 1399/1399 nonmissing | all five complete | ZA10020_backgroundvar_de.pdf, p. 62: weighting/construction statements conflict. | No weight applied; no consistent subset-specific choice established. |
| Austria | DWEIGHT_HH: 1 distinct, 1546/1546 nonmissing; DWEIGHT_TS: 1 distinct, 1546/1546 nonmissing; DWEIGHT_COM: 1 distinct, 1546/1546 nonmissing; PSWEIGHT: 680 distinct, 1546/1546 nonmissing; WEIGHT_COM: 680 distinct, 1546/1546 nonmissing | all five complete | ZA10020_backgroundvar_at.pdf, p. 51: PSWEIGHT listed, but construction note says no weighting. | No weight applied; no consistent subset-specific choice established. |
| Switzerland | DWEIGHT_HH: 1 distinct, 2129/2129 nonmissing; DWEIGHT_TS: 1 distinct, 2129/2129 nonmissing; DWEIGHT_COM: 1 distinct, 2129/2129 nonmissing; PSWEIGHT: 1 distinct, 2129/2129 nonmissing; WEIGHT_COM: 1 distinct, 2129/2129 nonmissing | all five complete | ZA10020_backgroundvar_ch.pdf, pp. 87–88: equal selection probability/no weighting; this does not validate the German-interview restriction as representative. | No weight applied; no consistent subset-specific choice established. |
| USA | DWEIGHT_HH: 6 distinct, 1534/1534 nonmissing; DWEIGHT_TS: 4 distinct, 1534/1534 nonmissing; DWEIGHT_COM: 16 distinct, 1534/1534 nonmissing; PSWEIGHT: 987 distinct, 1534/1534 nonmissing; WEIGHT_COM: 1126 distinct, 1534/1534 nonmissing | all five complete | ZA10020_backgroundvar_us.pdf, pp. 63–64: design/post-stratification material conflicts with construction statements; English-subset suitability is unresolved. | No weight applied; no consistent subset-specific choice established. |
| Australia | DWEIGHT_HH: 1 distinct, 1015/1015 nonmissing; DWEIGHT_TS: 1 distinct, 1015/1015 nonmissing; DWEIGHT_COM: 1 distinct, 1015/1015 nonmissing; PSWEIGHT: 56 distinct, 1015/1015 nonmissing; WEIGHT_COM: 56 distinct, 1015/1015 nonmissing | all five complete | ZA10020_backgroundvar_au.pdf, pp. 60–61: PSWEIGHT listed, but construction note says no weighting. | No weight applied; no consistent subset-specific choice established. |
| Canada | DWEIGHT_HH: 1 distinct, 1342/1342 nonmissing; DWEIGHT_TS: 1 distinct, 1342/1342 nonmissing; DWEIGHT_COM: 1 distinct, 1342/1342 nonmissing; PSWEIGHT: 266 distinct, 1342/1342 nonmissing; WEIGHT_COM: 266 distinct, 1342/1342 nonmissing | all five complete | ZA10020_backgroundvar_ca.pdf, pp. 61–62: PSWEIGHT for ten-province adult population estimates; English-interview-subset calibration is not established. | No weight applied; no consistent subset-specific choice established. |

The six official background-variable documents are: `ZA10020_backgroundvar_de.pdf`, `_at.pdf`, `_ch.pdf`, `_us.pdf`, `_au.pdf`, and `_ca.pdf` (filenames as present in the local documentation/download folders). The field audit establishes availability/completeness, not that a weight is valid for these estimands. Canada’s `PSWEIGHT` recommendation applies to the documented ten-province adult population; its validity for the English-interview subset is not established. The German-interview Swiss and English-interview US/Canadian subset weight suitability likewise remains unresolved.

## Validation checks

| Check | Result | Evidence |
|---|---|---|
| Germany Q1 substantive_responses: response counts sum to denominator | PASS | count sum=1368; denominator=1368 |
| Germany Q1 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q1 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.240542688; split-half range=0.000336162936–0.0119165414 |
| Germany Q1 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q10d main_q1_1_6_and_q10d_1_5: response counts sum to denominator | PASS | count sum=1252; denominator=1252 |
| Germany Q10d main_q1_1_6_and_q10d_1_5: survey probabilities sum to one | PASS | sum=1 |
| Germany Q10d main_q1_1_6_and_q10d_1_5: JSD values within [0,1] bits | PASS | uniform=0.072246742; split-half range=2.68060845e-05–0.012653909 |
| Germany Q10d main_q1_1_6_and_q10d_1_5: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q10d main_q1_1_6_and_q10d_1_5: expected denominator | PASS | observed=1252; expected=1252 |
| Germany Q10d robustness_all_substantive_q10d: response counts sum to denominator | PASS | count sum=1289; denominator=1289 |
| Germany Q10d robustness_all_substantive_q10d: survey probabilities sum to one | PASS | sum=1 |
| Germany Q10d robustness_all_substantive_q10d: JSD values within [0,1] bits | PASS | uniform=0.0676897505; split-half range=7.18287224e-05–0.0104591163 |
| Germany Q10d robustness_all_substantive_q10d: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q10d robustness_all_substantive_q10d: expected denominator | PASS | observed=1289; expected=1289 |
| Germany Q17a substantive_responses: response counts sum to denominator | PASS | count sum=1338; denominator=1338 |
| Germany Q17a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q17a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.222200667; split-half range=6.58744339e-05–0.0095672945 |
| Germany Q17a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q20 substantive_responses: response counts sum to denominator | PASS | count sum=1235; denominator=1235 |
| Germany Q20 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q20 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.10345753; split-half range=5.17306284e-05–0.0102654383 |
| Germany Q20 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q23a substantive_responses: response counts sum to denominator | PASS | count sum=1347; denominator=1347 |
| Germany Q23a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q23a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.149770192; split-half range=2.74507073e-05–0.00923539952 |
| Germany Q23a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q28a substantive_responses: response counts sum to denominator | PASS | count sum=1338; denominator=1338 |
| Germany Q28a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q28a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0618616456; split-half range=1.40730805e-05–0.00791770289 |
| Germany Q28a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q34 substantive_responses: response counts sum to denominator | PASS | count sum=1236; denominator=1236 |
| Germany Q34 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q34 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.167662191; split-half range=2.17080509e-06–0.00931812824 |
| Germany Q34 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q36a substantive_responses: response counts sum to denominator | PASS | count sum=1323; denominator=1323 |
| Germany Q36a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Germany Q36a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.056701574; split-half range=0.000936146019–0.0191013641 |
| Germany Q36a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q1 substantive_responses: response counts sum to denominator | PASS | count sum=1538; denominator=1538 |
| Austria Q1 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q1 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.203517502; split-half range=0.000112171718–0.0110883301 |
| Austria Q1 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q10d main_q1_1_6_and_q10d_1_5: response counts sum to denominator | PASS | count sum=1429; denominator=1429 |
| Austria Q10d main_q1_1_6_and_q10d_1_5: survey probabilities sum to one | PASS | sum=1 |
| Austria Q10d main_q1_1_6_and_q10d_1_5: JSD values within [0,1] bits | PASS | uniform=0.0514785105; split-half range=2.04097025e-05–0.010280242 |
| Austria Q10d main_q1_1_6_and_q10d_1_5: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q10d main_q1_1_6_and_q10d_1_5: expected denominator | PASS | observed=1429; expected=1429 |
| Austria Q10d robustness_all_substantive_q10d: response counts sum to denominator | PASS | count sum=1436; denominator=1436 |
| Austria Q10d robustness_all_substantive_q10d: survey probabilities sum to one | PASS | sum=1 |
| Austria Q10d robustness_all_substantive_q10d: JSD values within [0,1] bits | PASS | uniform=0.0507349392; split-half range=1.00442732e-05–0.0120388953 |
| Austria Q10d robustness_all_substantive_q10d: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q10d robustness_all_substantive_q10d: expected denominator | PASS | observed=1436; expected=1436 |
| Austria Q17a substantive_responses: response counts sum to denominator | PASS | count sum=1500; denominator=1500 |
| Austria Q17a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q17a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.210508463; split-half range=5.69395937e-05–0.00962437425 |
| Austria Q17a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q20 substantive_responses: response counts sum to denominator | PASS | count sum=1471; denominator=1471 |
| Austria Q20 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q20 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.091704966; split-half range=5.36865112e-05–0.0117414085 |
| Austria Q20 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q23a substantive_responses: response counts sum to denominator | PASS | count sum=1496; denominator=1496 |
| Austria Q23a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q23a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0979347648; split-half range=7.58487551e-06–0.00730317793 |
| Austria Q23a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q28a substantive_responses: response counts sum to denominator | PASS | count sum=1483; denominator=1483 |
| Austria Q28a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q28a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.037163592; split-half range=4.37726719e-06–0.00827993522 |
| Austria Q28a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q34 substantive_responses: response counts sum to denominator | PASS | count sum=1331; denominator=1331 |
| Austria Q34 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q34 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.19289644; split-half range=3.08203581e-05–0.0101029131 |
| Austria Q34 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Austria Q36a substantive_responses: response counts sum to denominator | PASS | count sum=1484; denominator=1484 |
| Austria Q36a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Austria Q36a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0418655897; split-half range=0.000781134555–0.0161593018 |
| Austria Q36a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q1 substantive_responses: response counts sum to denominator | PASS | count sum=2123; denominator=2123 |
| Switzerland Q1 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q1 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.252723743; split-half range=4.10443906e-05–0.00776905264 |
| Switzerland Q1 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q10d main_q1_1_6_and_q10d_1_5: response counts sum to denominator | PASS | count sum=2039; denominator=2039 |
| Switzerland Q10d main_q1_1_6_and_q10d_1_5: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q10d main_q1_1_6_and_q10d_1_5: JSD values within [0,1] bits | PASS | uniform=0.0832817506; split-half range=1.02830883e-05–0.00838984107 |
| Switzerland Q10d main_q1_1_6_and_q10d_1_5: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q10d main_q1_1_6_and_q10d_1_5: expected denominator | PASS | observed=2039; expected=2039 |
| Switzerland Q10d robustness_all_substantive_q10d: response counts sum to denominator | PASS | count sum=2041; denominator=2041 |
| Switzerland Q10d robustness_all_substantive_q10d: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q10d robustness_all_substantive_q10d: JSD values within [0,1] bits | PASS | uniform=0.0832976472; split-half range=2.53162892e-05–0.00601145688 |
| Switzerland Q10d robustness_all_substantive_q10d: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q10d robustness_all_substantive_q10d: expected denominator | PASS | observed=2041; expected=2041 |
| Switzerland Q17a substantive_responses: response counts sum to denominator | PASS | count sum=2094; denominator=2094 |
| Switzerland Q17a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q17a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.201315992; split-half range=1.94220987e-05–0.00668708057 |
| Switzerland Q17a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q20 substantive_responses: response counts sum to denominator | PASS | count sum=2034; denominator=2034 |
| Switzerland Q20 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q20 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0869858351; split-half range=3.61756974e-05–0.0101070602 |
| Switzerland Q20 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q23a substantive_responses: response counts sum to denominator | PASS | count sum=2062; denominator=2062 |
| Switzerland Q23a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q23a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0704612958; split-half range=1.10561202e-06–0.00546726363 |
| Switzerland Q23a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q28a substantive_responses: response counts sum to denominator | PASS | count sum=2048; denominator=2048 |
| Switzerland Q28a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q28a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.034783951; split-half range=2.0437543e-05–0.00712186521 |
| Switzerland Q28a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q34 substantive_responses: response counts sum to denominator | PASS | count sum=1907; denominator=1907 |
| Switzerland Q34 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q34 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.18158248; split-half range=1.07145193e-05–0.00643759572 |
| Switzerland Q34 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Switzerland Q36a substantive_responses: response counts sum to denominator | PASS | count sum=2059; denominator=2059 |
| Switzerland Q36a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Switzerland Q36a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0775793143; split-half range=0.000508491073–0.00993009458 |
| Switzerland Q36a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q1 substantive_responses: response counts sum to denominator | PASS | count sum=1531; denominator=1531 |
| USA Q1 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q1 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.261583324; split-half range=0.000117640748–0.0111205453 |
| USA Q1 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q10d main_q1_1_6_and_q10d_1_5: response counts sum to denominator | PASS | count sum=1467; denominator=1467 |
| USA Q10d main_q1_1_6_and_q10d_1_5: survey probabilities sum to one | PASS | sum=1 |
| USA Q10d main_q1_1_6_and_q10d_1_5: JSD values within [0,1] bits | PASS | uniform=0.072234622; split-half range=2.13392424e-05–0.0084594978 |
| USA Q10d main_q1_1_6_and_q10d_1_5: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q10d main_q1_1_6_and_q10d_1_5: expected denominator | PASS | observed=1467; expected=1467 |
| USA Q10d robustness_all_substantive_q10d: response counts sum to denominator | PASS | count sum=1469; denominator=1469 |
| USA Q10d robustness_all_substantive_q10d: survey probabilities sum to one | PASS | sum=1 |
| USA Q10d robustness_all_substantive_q10d: JSD values within [0,1] bits | PASS | uniform=0.071832878; split-half range=8.92974205e-05–0.00813641976 |
| USA Q10d robustness_all_substantive_q10d: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q10d robustness_all_substantive_q10d: expected denominator | PASS | observed=1469; expected=1469 |
| USA Q17a substantive_responses: response counts sum to denominator | PASS | count sum=1506; denominator=1506 |
| USA Q17a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q17a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.177528427; split-half range=1.33778163e-05–0.0104942376 |
| USA Q17a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q20 substantive_responses: response counts sum to denominator | PASS | count sum=1425; denominator=1425 |
| USA Q20 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q20 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0892826702; split-half range=0.000114150244–0.0114496183 |
| USA Q20 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q23a substantive_responses: response counts sum to denominator | PASS | count sum=1440; denominator=1440 |
| USA Q23a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q23a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.10287154; split-half range=2.94014135e-06–0.00728731832 |
| USA Q23a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q28a substantive_responses: response counts sum to denominator | PASS | count sum=1429; denominator=1429 |
| USA Q28a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q28a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0174051957; split-half range=1.37582314e-05–0.00928434558 |
| USA Q28a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q34 substantive_responses: response counts sum to denominator | PASS | count sum=1359; denominator=1359 |
| USA Q34 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q34 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.138942246; split-half range=2.00090805e-05–0.00995183194 |
| USA Q34 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| USA Q36a substantive_responses: response counts sum to denominator | PASS | count sum=1480; denominator=1480 |
| USA Q36a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| USA Q36a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0983475883; split-half range=0.00046411309–0.0157040404 |
| USA Q36a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q1 substantive_responses: response counts sum to denominator | PASS | count sum=1007; denominator=1007 |
| Australia Q1 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q1 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.278936717; split-half range=0.000230297852–0.0189630645 |
| Australia Q1 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q10d main_q1_1_6_and_q10d_1_5: response counts sum to denominator | PASS | count sum=911; denominator=911 |
| Australia Q10d main_q1_1_6_and_q10d_1_5: survey probabilities sum to one | PASS | sum=1 |
| Australia Q10d main_q1_1_6_and_q10d_1_5: JSD values within [0,1] bits | PASS | uniform=0.0543566137; split-half range=0.000178239792–0.0162262257 |
| Australia Q10d main_q1_1_6_and_q10d_1_5: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q10d main_q1_1_6_and_q10d_1_5: expected denominator | PASS | observed=911; expected=911 |
| Australia Q10d robustness_all_substantive_q10d: response counts sum to denominator | PASS | count sum=917; denominator=917 |
| Australia Q10d robustness_all_substantive_q10d: survey probabilities sum to one | PASS | sum=1 |
| Australia Q10d robustness_all_substantive_q10d: JSD values within [0,1] bits | PASS | uniform=0.054538315; split-half range=7.81924719e-05–0.0136010618 |
| Australia Q10d robustness_all_substantive_q10d: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q10d robustness_all_substantive_q10d: expected denominator | PASS | observed=917; expected=917 |
| Australia Q17a substantive_responses: response counts sum to denominator | PASS | count sum=999; denominator=999 |
| Australia Q17a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q17a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.170554122; split-half range=4.69086033e-05–0.012134779 |
| Australia Q17a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q20 substantive_responses: response counts sum to denominator | PASS | count sum=935; denominator=935 |
| Australia Q20 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q20 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0998545064; split-half range=0.000103834901–0.0213574462 |
| Australia Q20 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q23a substantive_responses: response counts sum to denominator | PASS | count sum=968; denominator=968 |
| Australia Q23a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q23a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0686934219; split-half range=2.76345479e-05–0.0120542363 |
| Australia Q23a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q28a substantive_responses: response counts sum to denominator | PASS | count sum=962; denominator=962 |
| Australia Q28a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q28a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0494839448; split-half range=4.60271705e-06–0.0115210759 |
| Australia Q28a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q34 substantive_responses: response counts sum to denominator | PASS | count sum=914; denominator=914 |
| Australia Q34 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q34 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.237823294; split-half range=6.44745552e-05–0.0128234318 |
| Australia Q34 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Australia Q36a substantive_responses: response counts sum to denominator | PASS | count sum=982; denominator=982 |
| Australia Q36a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Australia Q36a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0435245106; split-half range=0.000963418966–0.0208318115 |
| Australia Q36a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q1 substantive_responses: response counts sum to denominator | PASS | count sum=1342; denominator=1342 |
| Canada Q1 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q1 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.430217701; split-half range=0.000777522907–0.0126704168 |
| Canada Q1 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q10d main_q1_1_6_and_q10d_1_5: response counts sum to denominator | PASS | count sum=1338; denominator=1338 |
| Canada Q10d main_q1_1_6_and_q10d_1_5: survey probabilities sum to one | PASS | sum=1 |
| Canada Q10d main_q1_1_6_and_q10d_1_5: JSD values within [0,1] bits | PASS | uniform=0.112348952; split-half range=2.33277001e-05–0.00971996661 |
| Canada Q10d main_q1_1_6_and_q10d_1_5: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q10d main_q1_1_6_and_q10d_1_5: expected denominator | PASS | observed=1338; expected=1338 |
| Canada Q10d robustness_all_substantive_q10d: response counts sum to denominator | PASS | count sum=1338; denominator=1338 |
| Canada Q10d robustness_all_substantive_q10d: survey probabilities sum to one | PASS | sum=1 |
| Canada Q10d robustness_all_substantive_q10d: JSD values within [0,1] bits | PASS | uniform=0.112348952; split-half range=1.99218099e-05–0.0109117922 |
| Canada Q10d robustness_all_substantive_q10d: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q10d robustness_all_substantive_q10d: expected denominator | PASS | observed=1338; expected=1338 |
| Canada Q17a substantive_responses: response counts sum to denominator | PASS | count sum=1338; denominator=1338 |
| Canada Q17a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q17a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.176108637; split-half range=9.54871025e-05–0.0110066185 |
| Canada Q17a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q20 substantive_responses: response counts sum to denominator | PASS | count sum=1310; denominator=1310 |
| Canada Q20 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q20 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.073786072; split-half range=0.000143198317–0.0109141614 |
| Canada Q20 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q23a substantive_responses: response counts sum to denominator | PASS | count sum=1331; denominator=1331 |
| Canada Q23a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q23a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0835677513; split-half range=1.16765196e-05–0.00738511177 |
| Canada Q23a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q28a substantive_responses: response counts sum to denominator | PASS | count sum=1310; denominator=1310 |
| Canada Q28a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q28a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.0225304541; split-half range=3.13237228e-05–0.00971393083 |
| Canada Q28a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q34 substantive_responses: response counts sum to denominator | PASS | count sum=1264; denominator=1264 |
| Canada Q34 substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q34 substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.232806025; split-half range=3.27289368e-05–0.0075729316 |
| Canada Q34 substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Canada Q36a substantive_responses: response counts sum to denominator | PASS | count sum=1333; denominator=1333 |
| Canada Q36a substantive_responses: survey probabilities sum to one | PASS | sum=1 |
| Canada Q36a substantive_responses: JSD values within [0,1] bits | PASS | uniform=0.047828805; split-half range=0.000861702105–0.0161563012 |
| Canada Q36a substantive_responses: deterministic uniform row has no split metadata | PASS | Split-only metadata fields are blank on deterministic uniform row. |
| Germany Q10d routing discrepancy preserved | PASS | observed={'q1_7': 67, 'v26_-4': 56, 'v26_3_among_q1_7': 3, 'v26_4_among_q1_7': 2, 'v26_5_among_q1_7': 6}; expected={'q1_7': 67, 'v26_-4': 56, 'v26_3_among_q1_7': 3, 'v26_4_among_q1_7': 2, 'v26_5_among_q1_7': 6} |
| Output row count | PASS | observed=108; expected=108 |
| Output keys unique | PASS | rows=108; unique=108 |

## Limitations and interpretation

- Human-human split-half JSD is a within-survey sampling variability reference, not a theoretical upper bound. Each repetition independently permutes the substantive respondent records; when N is odd, one randomly selected record is omitted from that repetition so group sizes are exactly equal.
- JSD uses base-2 logarithms. The inspected repository contains no implemented main-analysis JSD function or documented logarithm base, so base 2 is an explicit conventional choice for these new references and needs team confirmation before cross-project metric comparisons.
- The uniform baseline assigns probability `1/k` to each declared substantive response category, including categories with zero observed frequency. It is a descriptive reference, not a mathematical lower bound.
- The source samples and current unweighted benchmark definitions are preserved. No weighted estimates, LLM inference, or model-output comparisons were produced.
- Q10d compares a human denominator defined by observed Q1 codes 1–6 and substantive Q10d codes 1–5 with an LLM prompt condition that states recent internet use (`You have used the Internet in the last 12 months.` / `Sie haben in den letzten 12 Monaten das Internet genutzt.`). The prompt does not operationalize the respondent-level Q1 code filter; this is an interpretation limitation, not changed here.
- An optional empirical resampling sensitivity analysis could repeatedly draw `n` responses from the observed country-item empirical probabilities and compare each draw with the original distribution. It is not included in the uniform baseline or this CSV.
