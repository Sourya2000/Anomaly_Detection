# Data Dictionary

| Column | Data type | Semantic context | Non-null | Nulls | Unique | Value range / examples |
| --- | --- | --- | ---: | ---: | ---: | --- |
| ID | int64 | Record identifier | 17,600 | 0 | 160 | range: 1 to 160 |
| Priority | int64 | Scheduling priority | 17,600 | 0 | 19 | range: 1 to 19 |
| Family_type | int64 | Product family category | 17,600 | 0 | 40 | range: 1 to 40 |
| First_stage | str | Production stage label or timing field | 17,600 | 0 | 5 | sample values: SMD_0, SMD_1, SMD_2, SMD_3, SMD_4 |
| Start_time_S1 | int64 | Operational manufacturing attribute | 17,600 | 0 | 8,258 | range: 0 to 17,988 |
| Finish_time_S1 | int64 | Operational manufacturing attribute | 17,600 | 0 | 8,587 | range: 37 to 18,895 |
| Processing_Time_S1 | int64 | Stage processing duration | 17,600 | 0 | 909 | range: 37 to 1,871 |
| Second_stage | str | Production stage label or timing field | 17,600 | 0 | 5 | sample values: AOI_0, AOI_1, AOI_2, AOI_3, AOI_4 |
| Start_time_S2 | int64 | Operational manufacturing attribute | 17,600 | 0 | 8,695 | range: 37 to 18,895 |
| Finish_Time_S2 | int64 | Operational manufacturing attribute | 17,600 | 0 | 8,798 | range: 90 to 19,852 |
| Processing_Time_S2 | int64 | Stage processing duration | 17,600 | 0 | 1,041 | range: 40 to 1,932 |
| Third_stage | str | Production stage label or timing field | 17,600 | 0 | 6 | sample values: 0, SS_0, SS_1, SS_2, SS_3 |
| Start_time_S3 | int64 | Operational manufacturing attribute | 17,600 | 0 | 7,993 | range: 0 to 19,852 |
| Finish_time_S3 | int64 | Operational manufacturing attribute | 17,600 | 0 | 8,114 | range: 0 to 20,222 |
| Processing_Time_S3 | int64 | Stage processing duration | 17,600 | 0 | 937 | range: 0 to 1,666 |
| Fourth_stage | str | Production stage label or timing field | 17,600 | 0 | 3 | sample values: 0, CC_0, CC_1 |
| Start_time_s4 | int64 | Operational manufacturing attribute | 17,600 | 0 | 7,295 | range: 0 to 21,338 |
| Finish_time | int64 | Operational manufacturing attribute | 17,600 | 0 | 7,313 | range: 0 to 21,607 |
| Processing_Time_S4 | int64 | Stage processing duration | 17,600 | 0 | 634 | range: 0 to 1,563 |
| Overall_processing_time | int64 | Job-level aggregate metric | 17,600 | 0 | 2,829 | range: 126 to 5,402 |
| Overall_waiting_time | int64 | Job-level aggregate metric | 17,600 | 0 | 9,199 | range: 0 to 20,350 |
| Tardiness | int64 | Job delay beyond target | 17,600 | 0 | 818 | range: 0 to 3,724 |
| BREAKS | int64 | Target / breakdown count | 17,600 | 0 | 4 | range: 0 to 3 |
