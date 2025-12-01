NETS = ["y","s","m"]

rule all:
    input: 
        n_files=expand('data/{net}_rank.csv',net=NETS),
        c_files=expand('data/{net}_cent.csv',net=NETS)

rule rank_sents:
    input:
        "data/data_{season}_real.csv"
    output:
        "data/{season}_rank.csv"
    log:
        "logs/{season}_rank.log"
    shell:
        "python3 create_ranking_df.py {input} {output}"
        
rule create_centrality:
    input:
        "params/2024_prop_dat.csv"
    output:
        "data/{season}_cent.csv"
    log:
        "logs/{season}_centrality.log"
    shell:
        "python3 gen_cent.py {wildcards.season} {input} {output}"
     
