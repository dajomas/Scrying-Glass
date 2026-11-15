# Vampire statblock diagnostic

No production normalizer exists. JSON depth/value counts and HTML DOM counts are source metrics, NOT normalized node counts/depth. No normalized-limit pass is asserted.

Source responses, datasets and individual creature records are separate measurements. Raw responses are retained for reproducibility; HTML may include surrounding site content.

| Record | Compact source bytes | Largest string bytes | Source values | JSON depth |
|---|---:|---:|---:|---:|
| 001-open5e.json | 8929 | 688 | 270 | 6 |
| 002-open5e.json | 12658 | 620 | 362 | 6 |
| 003-open5e.json | 7658 | 682 | 237 | 6 |
| 004-open5e.json | 9964 | 924 | 297 | 6 |
| 005-fivetools.json | 7209 | 679 | 193 | 7 |
| 006-fivetools.json | 6291 | 656 | 194 | 8 |
| 007-dndbeyond.json | 10895 | 317 | 541 | 3 |
| 008-dndbeyond.json | 12903 | 483 | 557 | 3 |

## Network responses

| Label | HTTP | Response bytes | Above proposed 10 MiB? |
|---|---:|---:|---|
| open5e-list-0 | 200 | 39264 | False |
| open5e-detail-1 | 200 | 8929 | False |
| open5e-detail-2 | 200 | 12658 | False |
| open5e-detail-3 | 200 | 7658 | False |
| open5e-detail-4 | 200 | 9964 | False |
| fivetools-index | 200 | 3569 | False |
| fivetools-dataset-1 | 200 | 1573620 | False |
| fivetools-dataset-2 | 200 | 1281795 | False |
| fivetools-dataset-3 | 200 | 7402 | False |
| fivetools-dataset-4 | 200 | 57897 | False |
| fivetools-dataset-5 | 200 | 3318 | False |
| fivetools-dataset-6 | 200 | 2395 | False |
| dndbeyond-search | 200 | 406055 | False |
| dndbeyond-detail-0 | 200 | 372370 | False |
| dndbeyond-detail-1 | 200 | 375538 | False |

## Failures and limitations


The 512 KiB normalized limit, 4,096 normalized nodes and depth 16 require the actual normalizer or a separately specified faithful model. These measurements alone cannot validate them. A Vampire sample also cannot establish bounds for all monsters.

Timing uses socket timeouts, not an enforced total-operation deadline. This one-off sequential probe is not the proposed production fetcher. No concurrency/cache-capacity validation is performed.
