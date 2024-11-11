# Kaks_Calculator
Ka/Ks is an imporant term in molecular evolution. It is the ratio of the number of nonsynonymous substitutions per nonsynonymous site (Ka) to the number of synonymous substitutions per synonymous site (Ks). It is equivalent to dN/dS.

This folder includes Kaks Calculator , which was originally published by Wang et al. PMID: 20451164 DOI: 10.1016/S1672-0229(10)60008-3.

A custom script is also included for sliding window analysis of Ka/Ks.

Example:

Ka/Ks analysis

./KaKs_Calculator2-1.0/bin/Linux/./KaKs_Calculator -i example.alignment2.fa -o example.alignment2.fa.kaks -m YN

sliding window analysis

perl kaks_slidingwindow.pl ./example/example.alignment.fa -s1 y -k1 34 -k3 3 

Please run the scripts in an Linux environment.
