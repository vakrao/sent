

rule all:
    input: 
        "y_real.csv"

rule run_year_sent:
    input:
        year_config = "configs/y_sent.yaml"
    output:
        "{network_type}_real.csv"
    shell: 
        "python3 S_runner.py {input}"


rule create_data:
    output:
        "{network_type}_real.csv"
    shell:
        "python3 join_df.py data {input}_real" 
 
