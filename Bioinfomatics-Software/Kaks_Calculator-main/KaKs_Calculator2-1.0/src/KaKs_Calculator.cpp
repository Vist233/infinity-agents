/***************************************************************
* Copyright (C) 2009, Beijing Institute of Genomics of CAS
* All rights reserved.
 
* Filename: KaKs_Calculator.cpp
* Abstract: including maximum-likelihood and approximate methods.


* Version: 2.0
* Author: Da-Peng Wang(wangdp@big.ac.cn), Yu-Bin Zhang (zhangyb@big.ac.cn)
* Date: Jun.1, 2009

* Version: 1.0
* Author: Zhang Zhang (zhanghzhang@genomics.org.cn)
* Date: Jan.21, 2005
****************************************************************/

#include "KaKs.h"

int main(int argc, const char* argv[]) {

	try {
		KAKS kk;
		if(!kk.Run(argc, argv)) throw 1;
	}
	catch (...) {
		
	}
	return 0;
}



