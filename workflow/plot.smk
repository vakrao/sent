NETS = ["y","s","m"]

rule all:
    input: 
        n_files=expand('results/{net}/',net=NETS)

rule plot_ranks:
    input:
        "{seas}"
    output: 
        "results/{seas}/"
    shell: 
        "python3 plot_ranks.py {input}"

rule plot_both_ranks:
    input:
        "both"
    output: 
        "results/all_temp_rank_compare.png"
    shell: 
        "python3 plot_ranks.py {input}"
