/************************************************************
* Copyright (C) 2009, Beijing Institute of Genomics of CAS
* All rights reserved.
 
* Filename: KaKs.h
* Abstract: Declaration of KAKS class including several methods.

* Version: 2.0
* Author: Da-Peng Wang(wangdp@big.ac.cn), Yu-Bin Zhang (zhangyb@big.ac.cn)
* Date: Jun.1, 2009

* Version: 1.0
* Author: Zhang Zhang (zhanghzhang@genomics.org.cn)
* Date: Jan.21, 2005

*************************************************************/
#if !defined(KAKS_H)
#define  KAKS_H

#include "base.h"
#include "NG86.h"
#include "LWL85.h"
#include "LPB93.h"
#include "GY94.h"
#include "YN00.h"
#include "MYN.h"
#include "MSMA.h"

using namespace std;

/* KAKS class */
class KAKS: public Base {
	
public:	
	int tempt; //zhangyubin add for multi-lines data to only gamma 
	KAKS();
	~KAKS();

	/* Main function to call kaks's methods */
	bool Run(int argc, const char* argv[]);		
	/* Read and Calculate seq, called in "Run" main function */
	bool ReadCalculateSeq(string filename);
	
	/* Initialize class, ready for running */
	int Initialize();
	/* Unitialize class, for unloading */
	int Uninitialize();

protected:		
	/* Use several methods to calculate ka/ks */
	bool calculateKaKs();
	/* Show help information */
	void helpInfo();

/* NONE: an in-house algorithm in BGI, that is NG86 without correction */
	void start_NONE(float GAMMA);
	/* NG86 */
	void start_NG86(float GAMMA);
	/* LWL85 */
	void start_LWL85(float GAMMA);
	/* Modified LWL85 */
	void start_MLWL85(float GAMMA);
	/* LPB93 */
	void start_LPB93(float GAMMA);
	/* Modified LPB93 */
	void start_MLPB93(float GAMMA);
	/* GY94 */
	void start_GY94(float GAMMA);	
	/* YN00 */
	void start_YN00(float GAMMA);
	/* MYN */
	void start_MYN(float GAMMA);	
	/* Model Selection and Model Averaging */
	void start_MSMA(float GAMMA);
	
	/* Get GCC of entire sequences and of three codon positions */
	void getGCContent(string str);
	/* Check the sequence whether is valid or not */
	bool checkValid(string name, string str1, string str2);
	/* Parse the input parameters */
	bool parseParameter(int argc, const char* argv[]);
	/* Show input parameters' information on screen */
	void showParaInfo();
	/* Get title information for writing into file */
	string getTitleInfo();

public:
	/* Methods' name and reference */
	vector<string> method_name;
	vector<string> method_ref;
	
	/* Parameters' title in outputing file */
	vector<string> titleInfo;

	/* Results for windows parser that shows results on ListCtrl */
	string result4Win;
	
	/* File name for output */
	string output_filename;
	/* Sequence file name */
	string seq_filename;

	/* Flag for whether to run NG86, MLWL85, MLPB93, GY94, YN00, MYN, MS/A=model selection/averaging */
	bool none, ng86,gng86, lwl85,glwl85, lpb93,glpb93, yn00,gyn00, mlwl85, gmlwl85,mlpb93,gmlpb93, gy94, myn, ms, ma,gmyn;	
	/* Number of compared pairwise sequences */
	unsigned long number;	//Maybe too many

protected:
	/* File name for detailed results for model selection */
	string detail_filename;
	/* Detailed results */
	string details; 
	
private:
	/* The temporary results for write into file */
	string result;
	/* Output stream */
	ofstream os;
	/* A pair of sequence */
	string seq1, seq2;
}; 

#endif



