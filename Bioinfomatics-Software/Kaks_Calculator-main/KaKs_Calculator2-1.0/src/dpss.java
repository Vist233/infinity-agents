/******************************************************************
* Copyright (C) 2009, Beijing Institute of Genomics of CAS
* All rights reserved.
 
* Filename: dpss.java
* Abstract: Detection of positive selected sites in sequences.

* Version: 1.0
* Author: Da-Peng Wang(wangdp@big.ac.cn), Yu-Bin Zhang (ybzhang@big.ac.cn)
* Date: Jun.1, 2009
*******************************************************************/

import java.io.*;
import java.util.Vector;


public class dpss {


    public static void main(String[] args) throws IOException {
        String gene_name, method_name, step_length, window_length;
        step_length = args[0].split("\\_")[2].split("\\.")[0];
        window_length = args[0].split("\\_")[1];
        System.out.println("dpss version 1.0 tools for Ka/Ks calculator");
        System.out.println("usage: dpss  <inputfile>");
        cutFileText(args[0]);


    }


    public static void cutFileText(String fileName) throws IOException {

        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(fileName)));
        int index = fileName.lastIndexOf(".");
        String ext = "";
        if (index > 0) {
            ext = fileName.substring(index);
            fileName = fileName.substring(0, index);
        }
        String tempString = null;

        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(fileName + "_DPSS" + ext)));
        writer.write(reader.readLine());
        while ((tempString = reader.readLine()) != null) {
            String[] classname;
            classname = tempString.split("\t");

            if ((!classname[4].equals("NA"))&&(Double.parseDouble(classname[4]) > 1)) {

                writer.write(tempString + '\n');
                writer.flush();

            }
        }
        writer.close();
    }

}
