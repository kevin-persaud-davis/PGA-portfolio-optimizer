import os
from pathlib import Path
import re
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import pandas as pd
pd.options.display.max_columns = 999
import numpy as np

"""
PGATOUR METRICS

General cleaning step: add pgatour stat id into columns

- Rank this week and rank last week: change from str to int
    > replace "T"
    > cast to int


077 : GIR percentage - 75-100 yards
078 :
079 :
- Relative to par:
    > replace E with 0
    > cast str to float

103: Greens in regulation percentage
- Relative to par:
    > replace E with 0
    > cast str to float
- GREENS_HIT:
    > cast str to float
- #_HOLES:
    > cast str to float

190: GIR percentage from fairway
- #_OF_HOLES:
    > cast str to int

199: GIR percentage from other than fairway

326: GIR percentage - 200+ yards
327:
328:
329:
330:
02330:
- Relative to par:
    > replace E with 0
    > cast str to float

02332: GIR percentage - 100+ yards
- TOTAL_HOLES: remove commas
    > replace ","
    > cast str to int
- RELATIVE_TO_PAR: 
    > replace E with 0
    > cast str to float

02434: GIR pct. - fairway bunker
- RELATIVE/PAR:
    > replace E with 0
    > cast str to float

----------------------------------

02437: Greens or fringe in regulation

TOTAL_HIT:
    > replace ","
    > cast str to int
TOTAL_ATTEMPTS:
    > replace ","
    > cast str to int
RTP_SCORE:
    > cast str to float


02568: SG: approach the green (GOOD)
02674: SG: tee-to-green (GOOD)
02674: SG: total (GOOD)

"""






def gir_dist_pct_clean(df, col):
    
    df[col] = df[col].str.replace("E", "0.0")
    df[col] = pd.to_numeric(df[col], downcast="float")

    return df



def main():

    metric_path = str(Path(config.RAW_PGA_METRICS_DIR, "077_2017_2020.csv"))

    pga_077_df = pd.read_csv(metric_path)

    pga_077_df = gir_dist_pct_clean(pga_077_df, "RELATIVE_TO_PAR")

    print(pga_077_df.dtypes)

if __name__ == "__main__":
    main()