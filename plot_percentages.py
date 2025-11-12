all_data= pd.read_csv("results/all_stats.csv")

net_fn = "params/hort365_NZ.csv"
in_bond, out_bond = read_network_data(net_fn)
all_data["s_intra_in"] = (all_data["i_w"] - all_data["FIRST_IN_MOMENT"])/(all_data["w"])
all_data["s_intra_out"] = (all_data["o_w"] - all_data["FIRST_OUT_MOMENT"])/(all_data["w"])
all_data["s_inter_in"] = (all_data["FIRST_IN_MOMENT"])/(all_data["w"])
all_data["s_inter_out"] = (all_data["FIRST_OUT_MOMENT"])/(all_data["w"])
all_data["s_inter"] = all_data["s_inter_in"] + all_data["s_inter_out"]
all_data["s_intra"] = all_data["s_intra_in"] + all_data["s_intra_out"]
all_data["d_intra_in"] = (all_data["i_d"] - all_data["FIRST_IN_DEG_MOMENT"])/(all_data["d"])
all_data["d_intra_out"] = (all_data["o_d"] - all_data["FIRST_OUT_DEG_MOMENT"])/(all_data["d"])
all_data["d_inter_in"] = (all_data["FIRST_IN_DEG_MOMENT"])/(all_data["d"])
all_data["d_inter_out"] = (all_data["FIRST_OUT_DEG_MOMENT"])/(all_data["d"])
all_data["d_inter"] = all_data["d_inter_in"] + all_data["d_inter_out"]
all_data["d_intra"] = all_data["d_intra_in"] + all_data["d_intra_out"]
