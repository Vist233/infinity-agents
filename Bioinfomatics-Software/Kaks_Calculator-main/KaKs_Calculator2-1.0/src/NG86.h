/***************************************************************
* Copyright (C) 2009, Beijing Institute of Genomics of CAS
* All rights reserved.
 
* Filename: NG86.h
* Abstract: Declaration of NG86 class inherited base class.

* Version: 2.0
* Author: Da-Peng Wang(wangdp@big.ac.cn), Yu-Bin Zhang (ybzhang@big.ac.cn)
* Date: Jun.1, 2009

* Version: 1.0
* Author: Zhang Zhang  (zhang.zhang@yale.edu)
* Date: Feb.21, 2005

  References:
  Nei M, Gojobori T  (1986)  Simple methods for estimating the 
  numbers of synonymous and nonsynonymous nucleotide substitutions.
  Mol Biol Evol 3:418-426.
****************************************************************/

#if !defined(NG86_H)
#define  NG86_H

#include "base.h"

using namespace std;
 
/* NG86 class */
class NG86: public Base {
	
public:
	float GAMMA;//zhangyubin added
	NG86();

	/* Main function of calculating kaks */
	string Run(string seq1, string seq2);

protected:
	/* Count codon's sites */
	void getCondonSite(string codon);
	/* Count codon's differences */
	void getCondonDifference(string codon1, string codon2);
	/* Preprocess */
	void PreProcess(string seq1, string seq2);
	/* Jukes and Cantor's one-parameter formula */
	double kaks_formula(double p);

public:	
	/* Proportions of sysnonymous(Ps) and nonsysnonymous(Pn): Ps=Sd/S, Pn=Nd/N  */
	double Ps, Pn;
}; 

class NONE: public NG86 {

public:
	NONE();
	/* Main function of calculating kaks */
	string Run(string seq1, string seq2);
	
};

#endif


