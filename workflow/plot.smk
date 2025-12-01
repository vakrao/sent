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
