# Introduction

CPJSdraw is a software compiled by perl for visualizing chloroplast genome junction sites, which can better identify the position of circular sequences and support more genbank files.
CPJSdraw depends on the MUMmer4 software. 'nucmer' and 'show-coords' need to be added to the environment variables. Perl SVG module is used for drawing. Finally, batik-1.7 (included in CPJSdraw) is called to convert the svg format to png and pdf formats.

# Cite this as

	Li H, Guo Q, Xu L, Gao H, Liu L, Zhou X. 2023. CPJSdraw: analysis and visualization of junction sites of chloroplast genomes. PeerJ 11:e15326 https://doi.org/10.7717/peerj.15326

# link:
	https://peerj.com/articles/15326/
	
# Installation

MUMmer4: https://github.com/mummer4/mummer （Please ensure that nucmer and show-coords can be used directly,unless you customize the configuration file input file）
SVG: cpan SVG
CPJSdraw: git clone https://github.com/xul962464/CPJSdraw.git && chmod a+x CPJSdraw/script/svg_kit/buildInFont


# Quick Start

perl CPJSdraw/bin/CPJSdraw.pl -h

----------------------------------------------------------------------------------------------------------------------------------------------------------
	Program: CPJSdraw.pl
	Version: 0.0.1
	Contact: xul<xul@genepioneer.com> <1275875706@qq.com>
	Description:

	        Draw the junctions site of chloroplast genome.

	Usage:
	        1. perl CPJSdraw.pl -i input.cfg file
	        2. perl CPJSdraw.pl -g file1.gb file2.gb file3.gb

	  Options:
	        -i      <infile>        Input cfg file with two columns.
	                        The first column is the file path and the second column is the region location.
	                        The region location must be in the following format: LSC:1-85855,IRb:85856-111284,SSC:111285-129051,IRa:129052-154480
	                        Regional positions can span the beginning and end of the genome.
	                        The contents of the file are as follows:

	                path/MK036045.1.gbk     LSC:152045-85435,IRb:85436-110178,SSC:110179-127301,IRa:127302-152044
	                path/MK267301.1.gbk     LSC:156436-84674,IRb:84675-112284,SSC:112285-128825,IRa:128826-156435
	                path/MK397858.1.gbk     LSC:154523-85675,IRb:85676-111060,SSC:111061-129137,IRa:129138-154522
	                path/MK397875.1.gbk     LSC:1-85855,IRb:85856-111284,SSC:111285-129051,IRa:129052-154480
	                path/MK622380.1.gbk     LSC:1-85991,IRb:85992-112399,SSC:112400-131478,IRa:131479-157886
	                path/MK817503.1.gbk     LSC:1-91540,IRb:91541-117733,SSC:117734-136982,IRa:136983-163175
	                path/AM087200.3.gbk     LSC:5-85878,IRb:85879-111490,SSC:111491-129853,IRa:129854-4

	        -g      <infiles>       Input genbank files, can be added after '-i'

	        -b      back ground color, defaut: white
	                Use RGB or hexadecimal color codes or simple color description definitions, such as
	                "rgb(240,255,255)" or "#F0FFFF" or "white"

	        -o      <output>        out.name(.svg)  default CPJSDRAW.svg

	        -h                              Help
----------------------------------------------------------------------------------------------------------------------------------------------------------

a) Simple usage

	perl CPJSdraw/bin/CPJSdraw.pl -g CPJSdraw/sample/test_a_start_with_lsc/NC_036102.1.gb  CPJSdraw/sample/test_a_start_with_lsc/NC_056151.1.gb -o CPJSDRAW.svg
	
		In this case, the program will automatically identify the repeat area and plot.

b) Advanced Usage

	perl CPJSdraw/bin/CPJSdraw.pl -i CPJSdraw/sample/merge.cfg -o CPJSDRAW.svg
	
		This method supports the position of the repeat area of user-defined sequences, and is applicable to some special sequences, such as those with multiple repeat areas, or those whose repeat areas are too short to be identified easily.


----------------------------------------------------------------------------------------------------------------------------------------------------------
In addition, we provide online tools in Chinese: http://112.86.217.82:9929/#/tool/alltool/detail/335


