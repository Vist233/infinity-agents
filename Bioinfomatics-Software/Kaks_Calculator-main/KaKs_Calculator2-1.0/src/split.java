/******************************************************************
* Copyright (C) 2009, Beijing Institute of Genomics of CAS
* All rights reserved.
 
* Filename: split.java
* Abstract: Spliting one file into many individual ones.

* Version: 1.0
* Author: Da-Peng Wang(wangdp@big.ac.cn), Yu-Bin Zhang (ybzhang@big.ac.cn)
* Date: Jun.1, 2009
*******************************************************************/

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;

public class split {


    public static void main(String[] args) throws IOException {
		if (args.length!=3)
		{
			 System.out.println("split version 1.0 tools for Ka/Ks calculator");
        System.out.println("usage: split <inputfile> <length> <gap> ");

		}else{
       
        cutFileText(args[0], Integer.parseInt(args[1]), Integer.parseInt(args[2]));}


    }

    /**
     * @param fileName
     * @param size
     * @throws IOException
     */
    public static void cutFileText(String fileName, int size, int gap) throws IOException {
        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(fileName)));
        int index = fileName.lastIndexOf(".");
        String ext = "";
        if (index > 0) {
            ext = fileName.substring(index);
            fileName = fileName.substring(0, index);
        }
        int len;
        int beginIndex = 0;
        int endIndex = 0;
        int line = 0;
        int beginIndexID = 0;

        // char[] cbuf = new char[size];
        String tempString = null;
        String tempName = null;
        String tempLine2 = null;
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(fileName + "split" + "_" + size + "_" + gap + ext)));
        while ((tempString = reader.readLine()) != null) {
            line++;

            if (line % 4 == 1) {
                tempName = tempString;
            }
            if (line % 4 == 2) {
                tempLine2 = tempString;
            }


            if (line % 4 == 3) {
                beginIndex = 0;
                endIndex = 0;
                while (endIndex < tempString.length()) {
                    endIndex = beginIndex + size;
                    beginIndexID = beginIndex + 1;
                    if (endIndex <= tempString.length()) {
                        writer.write(tempName + '(' + beginIndexID + '-' + endIndex + ')' + '\n');
                        writer.write(tempLine2.substring(beginIndex, endIndex) + '\n');
                        writer.write(tempString.substring(beginIndex, endIndex) + '\n');
                        writer.write('\n');
                        writer.flush();
                    }
                    beginIndex += gap;
                }

            }

        }


        writer.close();

    }


}
