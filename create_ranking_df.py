import pandas as pd
import numpy as np
import sys



def normalize_sent_metrics(rank_file):
    ranked_data = pd.read_csv(rank_file)
    ranked_data['o_s'] = ranked_data['d_c'] + ranked_data['d_i']
    outbreak_sizes = ranked_data.groupby(["seed"])["o_s"].agg("max")
    new_df = pd.DataFrame()
    new_df["seed"] = outbreak_sizes.index
    # Get Full Outbreak Size
    new_df["real_os"] = list(outbreak_sizes)
    ranked_data = ranked_data.merge(new_df,left_on="seed",right_on="seed")
    #ranked_data = ranked_data[ranked_data["o_s"] > 0]
    #out_sizes = [ x for x in list(outbreak_sizes)  if x > 0 ]
    # Count Number of times
    seed_amount = len(set(ranked_data["seed"]))
    ## if an outbreak occurs - what is probability of detecting it for a given sentinel?
    g_zero = (ranked_data.groupby(["seed"])["real_os"].agg("max"))
    full_time = max(list(ranked_data["d_t"]))
    num_sents = len(list(ranked_data["sent"]))
    ranked_data = ranked_data[ranked_data["d_t"] > 0]
    ranked_data["norm_dt"] = ranked_data["d_t"] / full_time
    ranked_data["norm_di"] = (ranked_data['d_c'])/(ranked_data["o_s"])
    ranked_data["norm_df"] = ((ranked_data["d_f"]) / seed_amount)
    agg = ranked_data.groupby("sent", as_index=True).agg(
        dF_sum=("norm_df", "sum"),     # total detections (higher better)
        dI_mean=("norm_di", "mean"),   # mean infections at detection (lower better)
        dT_mean=("norm_dt", "mean"),   # mean time to detection (lower better)
    )
    # ----------------------------------------------------
    # Compute ranks (1 = best)
    # ----------------------------------------------------
    agg["R_F"] = agg["dF_sum"].rank(ascending=False, method="min")
    agg["R_I"] = agg["dI_mean"].rank(ascending=True,  method="min")
    agg["R_T"] = agg["dT_mean"].rank(ascending=True,  method="min")

    return agg

if __name__ == "__main__":
    # Load Data
    rank_file = sys.argv[1]  # name of saved-run-data to use
    save_file = sys.argv[2]  # save name of saved-run-data
    rank_data = normalize_sent_metrics(rank_file)
    rank_data.to_csv(save_file)



