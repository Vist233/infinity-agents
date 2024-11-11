/******************************************************************
* Copyright (C) 2009, Beijing Institute of Genomics of CAS
* All rights reserved.
 
* Filename: plot.java
* Abstract: Classification of data and ploting figures based on sliding window.

* Version: 1.0
* Author: Da-Peng Wang(wangdp@big.ac.cn), Yu-Bin Zhang (ybzhang@big.ac.cn)
* Date: Jun.1, 2009
*******************************************************************/

import org.rosuda.REngine.Rserve.RConnection;
import org.rosuda.REngine.Rserve.RserveException;
import org.rosuda.REngine.*;

import java.io.*;
import java.util.Vector;


public class plot {


    public static void main(String[] args) throws IOException {
        String gene_name,method_name,step_length,window_length;
        step_length=args[0].split("\\_")[2].split("\\.")[0];
        window_length=args[0].split("\\_")[1];
        System.out.println("plot version 1.0 tools for Ka/Ks calculator");
        System.out.println("usage: plot  <inputfile>");
        cutFileText(args[0]);
        File filet=new File("temp");
        if  (isDirectory("figure")){deleteDirectory("figure");}
        newFolder("figure");
        File[] tlist=filet.listFiles();

           try{
                RConnection c = new RConnection();

        for (int i=0;i<tlist.length;i++){

           String filep=tlist[i].getName();
            String patht=tlist[i].getCanonicalPath();

            patht=patht.replace("\\","/");
            String pathw=patht.substring(0,patht.lastIndexOf("/"));
            pathw=pathw.substring(0,pathw.lastIndexOf("/"));
            /*pathw=pathw.replace("/","//");
            patht=patht.replace("/","//");*/
            gene_name=filep.substring(0,filep.lastIndexOf("_"));
            method_name=filep.substring(filep.lastIndexOf("_")+1,filep.lastIndexOf("."));

c.eval("m<-read.table(\""+patht+"\",header=FALSE,sep=\"\\t\",quote=\"\");");

c.eval("m<-t(m);");
c.eval("n<-m[1, ];");
c.eval("m1<-m[2, ];");
c.eval("m2<-m[3, ];");
c.eval("m3<-m[4, ];");

c.eval("m4<-rep(1,times=length(m1));");

/*c.eval("assign(\"gene_name\",\""+gene_name+"\");");
c.eval("assign(\"method_name\",\""+method_name+"\");");
c.eval("assign(\"step_length\",\""+step_length+"\");");
c.eval("assign(\"window_length\",\""+window_length+"\");");*/

c.eval("pdf(\""+pathw+"/figure/"+filep+".pdf\",bg = \"white\",width=7,height=6);");

c.eval("xlab<-\"Sliding Window (starting position, bp)\";");
c.eval("ylab<-\"Value\";");

c.eval("plot(n,m1,type=\"l\",lwd=1,col=\"green\",pch=0,xlab=xlab,ylab=ylab,cex=1,ylim=c(0,10));");
c.eval("title(\"Sequence ID=\"~\""+gene_name+"\"~\",Method=\"~\""+method_name+"\",sub=\"Step Length=\"~\""+step_length+"\"~\"bp,Window Length=\"~\""+window_length+"\"~\"bp\",cex.main = 1,font.main= 4,col.main= \"blue\",cex.sub = 0.75, font.sub = 3, col.sub = \"red\");");

c.eval("lines(n,m2,col=\"blue\",lwd=0.5);");

c.eval("lines(n,m3,col=\"purple\",lwd=0.5);");
c.eval("lines(n,m4,col=\"red\",lwd=0.5);");

c.eval("color<-c(\"green\",\"blue\",\"purple\",\"red\");");

c.eval("legend(\"topright\",horiz=FALSE,legend=c(\"Ka\",\"Ks\",\"Ka/Ks\",\"Constant=1\"),col=color,lwd=0.5,box.lty=1,bty = \"o\",inset=0.01,cex = 1);");

c.eval("dev.off();");

        }
if(c.isConnected()){c.close();}
   } catch (RserveException  rse) {
            System.out.println(rse);
              
        }  catch (Exception e) {
            e.printStackTrace();
        }






        }
    

    public static void cutFileText(String fileName) throws IOException {

        BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(fileName)));
        int index = fileName.lastIndexOf(".");
        String ext = "";
        if (index > 0) {
            ext = fileName.substring(index);
            fileName = fileName.substring(0, index);
        }
        String patht="./temp";
           newFolder(patht);
        String tempString = null;
        reader.readLine();
        Vector vectorc = new Vector();
        while ((tempString = reader.readLine()) != null) {
            String[] classname;
            classname = tempString.split("\t");
            String[] seqhead = classname[0].split("\\(");
            String filenamet = seqhead[0] + classname[1];

            if (vectorc.contains(filenamet) == false) {
                vectorc.addElement(filenamet);

                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(patht+"/" + seqhead[0] + "_" + classname[1] +  ext)));
                writer.write(seqhead[1].split("\\-")[0] + "\t" + classname[2] + "\t" + classname[3] + "\t" + classname[4] + "\t" + '\n');
                writer.flush();
                writer.close();
            } else {
                BufferedWriter writer = new BufferedWriter(new FileWriter(patht+"/" + seqhead[0] + "_" + classname[1]  + ext, true));
                writer.write(seqhead[1].split("\\-")[0] + "\t" + classname[2] + "\t" + classname[3] + "\t" + classname[4] + "\t" + '\n');
                writer.flush();
                writer.close();
            }
        }
    }



    /**
    * createdirectory
    */
    public static void newFolder(String folderPath) {
       String filePath = folderPath;
       filePath = filePath.toString();
       java.io.File myFilePath = new java.io.File(filePath);
       try {
        if (!myFilePath.isDirectory()) {
         myFilePath.mkdir();
        }
       } catch (Exception e) {
        System.out.println("error in creating the directory");
        e.printStackTrace();
       }
    }

    /**
    * if the directory  exists
    */
    public static boolean isDirectory(String path) {
       File file = new File(path);
       return file.isDirectory();
    }

    /**
    * if the directory is empty
    */
    public static boolean isEmpty(String path) {
       File f = new File(path);
       if (f.list().length == 0)
        return true;
       else
        return false;
    }
    /**
    * deletedirectory
    */
    public static boolean deleteDirectory(String sPath) {

       if (!sPath.endsWith(File.separator)) {
        sPath = sPath + File.separator;
       }
       File dirFile = new File(sPath);

       if (!dirFile.exists() || !dirFile.isDirectory()) {
        return false;
       }
       boolean flag = true;

       File[] files = dirFile.listFiles();
       for (int i = 0; i < files.length; i++) {

        System.out.println(files[i].getAbsolutePath());
        if (files[i].isFile()) {
         flag = deleteFile(files[i].getAbsolutePath());
         if (!flag)
          break;
        }
        else {
         flag = deleteDirectory(files[i].getAbsolutePath());
         if (!flag)
          break;
        }
       }
       if (!flag)
        return false;

       if (dirFile.delete()) {
        return true;
       } else {
        return false;
       }
    }


    /**
    * delete file
    */
    public static boolean deleteFile(String sPath) {
       boolean flag = false;
       File file = new File(sPath);

       if (file.isFile() && file.exists()) {
        file.delete();
        flag = true;
       }
       return flag;
    }

         


}
