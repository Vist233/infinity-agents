#!/usr//bin/env perl
use warnings;
use strict;												
use Getopt::Long;		 

my $BEGIN_TIME=time();	   
my $version="1.0.0";

#######################################################################################
#soft path and parameter

my $nucmer = "nucmer";
my $show_coords = "show-coords";
my $breaklen = 200;		#mummer nucmer breaklen
my $kmer_len = 55;		#Inverted repeat region, allowing for mismatches, the shortest exact sequence at both ends
my $max_gap_nu = 90;
#######################################################################################

my @infiles;
my $outdir;
my $min_ir_len;
my $is_circular;

GetOptions(		
				"help|?" =>\&USAGE,			
				"i:s{1,}"=>\@infiles,
				"c:s"=>\$is_circular,
				"m:s"=>\$min_ir_len,
				) or &USAGE;
&USAGE unless (@infiles);		

#######################################################################################
$outdir //= ".";
mkdir $outdir unless(-d $outdir);


$min_ir_len ||= 100;	#shortest inverted repeat region
$is_circular //= 1;

#######################################################################################

for my $infile(@infiles){

	my $seq;

	#Determine file type

	if(judge_file_type($infile) eq "fasta"){
		
		$seq = get_fasta_seq($infile);
		
	}elsif(judge_file_type($infile) eq "gb"){

		$seq = get_genbank_seq($infile);

	}else{

		print "File type not recognized: only fasta and genbank format can be recognized\n";
		exit;

	}

	my $info = get_region_info($seq,$outdir,$is_circular);

	print "Infile:$infile\n$info\n";
}

#sub

sub get_region_info{

	my $seq = shift;
	my $outdir = shift;
	my $is_circular = shift;

	mkdir $outdir unless(-d $outdir);

	my $seq_len = length $seq;


	#Make sure repeats don't cross the beginning and end
	my ($new_seq,$start) = get_single_copy_start($seq,$kmer_len,$is_circular);

	#save new sequence
	my $tmp_outfile = "$outdir/new_start.fasta";

	open TMPOUT,"> $tmp_outfile" or die "cannot create $tmp_outfile file";
	print TMPOUT ">newgenome start $start\n$new_seq\n";


	#Find new inverted repeats
	my ($ir,$ir_len,$ir_idy) = find_ir_in_linear_seq($tmp_outfile,$outdir);	#return (ir,ir_len,ir_idy);

	if($ir){
		$ir = judge_linear_seq_ir_boundary($tmp_outfile,$ir,$ir_idy,$kmer_len);	#fasta_file,ir,idy,kmer_len
		
		unlink $tmp_outfile;

		return 0 unless($ir);

		my $region_info = map_to_the_original_location($ir,$start,$seq_len);

		return $region_info;
	}else{
		return "0";
	}

}


sub map_to_the_original_location{
	
	my $ir = shift;
	my $start = shift;
	my $len = shift;

	$ir =~ s/(\d+)/$1+$start-1/eg;

	my ($s1,$e1,$s2,$e2) = $ir =~ /(\d+)-(\d+),(\d+)-(\d+)/;
	
	my $ir1_len = $e1 - $s1 + 1;
	my $ir2_len = $e2 - $s2 + 1;
	my $single1_len = $s2 - 1 - ($e1 + 1) + 1;	#inter
	my $single2_len = $len - $ir1_len - $ir2_len - $single1_len;
	
	if($single1_len < 1 or $single2_len < 1){	#²»´æÔÚµ¥¿½±´Çø
		warn "WARN:length single copy region is 0 bp.\nWARN:total length : $len\nWARN:ir : $ir\n";
		return 0;
	}


	my $ira_start;
	my $ira_end;
	my $irb_start;
	my $irb_end;

	if($single1_len < $single2_len){
		$irb_start = $s1 > $len ? $s1 - $len : $s1;
		$irb_end = $e1 > $len ? $e1 - $len : $e1;
		$ira_start = $s2 > $len ? $s2 - $len : $s2;
		$ira_end = $e2 > $len ? $e2 - $len : $e2;
	}else{
		$irb_start = $s2 > $len ? $s2 - $len : $s2;
		$irb_end = $e2 > $len ? $e2 - $len : $e2;
		$ira_start = $s1 > $len ? $s1 - $len : $s1;
		$ira_end = $e1 > $len ? $e1 - $len : $e1;
	}
	
	my $lsc_start = $ira_end + 1 > $len ? $ira_end + 1 - $len : $ira_end + 1 ;
	my $lsc_end = $irb_start - 1 > $len ? $irb_start - 1 - $len : $irb_start - 1;
	my $ssc_start = $irb_end + 1 > $len ? $irb_end + 1 - $len : $irb_end + 1;
	my $ssc_end = $ira_start - 1 > $len ? $ira_start - 1 - $len: $ira_start - 1;

	$lsc_end ||= $len;	#0
	$ssc_end ||= $len;	#0

	my $lsc_pos = "$lsc_start-$lsc_end";
	my $irb_pos = "$irb_start-$irb_end";
	my $ssc_pos = "$ssc_start-$ssc_end";
	my $ira_pos = "$ira_start-$ira_end";

	return "Len:$len\nLSC:$lsc_pos\nIRb:$irb_pos\nSSC:$ssc_pos\nIRa:$ira_pos\n";

}


sub get_single_copy_start{

	my $seq = shift;
	my $kmer_len = shift;

	if(!$is_circular){
		return ($seq,1)
	}

	my $double_seq = $seq . $seq . $seq;
	
	my $is_find_single_copy = 0;
	my $start_index = 0;


	#kmer freq count
	my %for_pos_kmer;
	my %for_kmer_count;

	for my $j(0..length($seq) - 1){
		my $kmer = substr($double_seq,length($seq) + $j - $kmer_len + 1,$kmer_len);
		my $rev_kmer = reverse $kmer;
		$rev_kmer =~ tr/ATGC/TACG/;
		
		$for_pos_kmer{$j} = $kmer;

		$for_kmer_count{$kmer}++;
		$for_kmer_count{$rev_kmer}++;

	}
	
	#find single copy start
	while(!$is_find_single_copy and $start_index < length($seq) - $kmer_len){

		my $has_multi_copy = 0;

		for my $j(0..$kmer_len-1){

			my $kmer_nu = $for_kmer_count{$for_pos_kmer{$start_index + $j}};

			if($kmer_nu >1){
				$has_multi_copy = 1;
				$start_index = $start_index + $j + 1;
				last;
			}
		}
		
		if(! $has_multi_copy){
			$is_find_single_copy = 1;
		}
	}
	
	$start_index = $start_index == length($seq) - $kmer_len ? 0 : $start_index;
	
	my $new_seq = substr($seq,$start_index).substr($seq,0,$start_index);

	return ($new_seq,$start_index+1)
}


sub judge_linear_seq_ir_boundary{
	
	#--------------------------------------------------------------------
	#Judging the similarity of the first and last bases of ir, the sequence that is too short should be removed
	#judge_ir_boundary(fasta_file,ir,idy,kmer_len)
	#return new_ir
	#return 0
	#--------------------------------------------------------------------

	my $fasta_file = shift;
	my $ir = shift;
	my $idy = shift;
	my $kmer_len = shift;

	if($idy == 100){
		return $ir;
	}

	my $seq;

	open IN,"$fasta_file" or die "cannot open $fasta_file";
	$/ = "\n";

	while(<IN>){
		chomp;
		next if(/^\s*$|^>/);

		$seq .= "$_";

	}close IN;

	$seq =~ s/\s//g;
	$seq = uc $seq;

	my ($s1,$e1,$s2,$e2) = $ir =~ /(\d+)-(\d+),(\d+)-(\d+)/;

	my $irseq1 = substr($seq,$s1-1,$e1-$s1+1);
	my $irseq2 = substr($seq,$s2-1,$e2-$s2+1);

	my $irseq1_len = length $irseq1;
	my $irseq2_len = length $irseq2;

	my $rev_seq1 = reverse $irseq1;
	   $rev_seq1 =~ tr/ATGCatgc/TACGtacg/;

	my $rev_seq2 = reverse $irseq2;
	   $rev_seq2 =~ tr/ATGCatgc/TACGtacg/;


	#Determine the beginning of seq1 and the end of seq2
	my $seq1_left;
	my $seq2_right;

	for (my $i = 0;$i < $irseq1_len-$kmer_len;$i++) {
		my $kmer = substr($irseq1,$i,$kmer_len);

		my $index = index($rev_seq2,$kmer);
		
		if($index != -1 and abs($index - $i) <= $max_gap_nu){
			$seq1_left = $s1 + $i;
			$seq2_right =$e2 - $index;
			last;
		}
	}

	#Determine the beginning of seq1 and the end of seq2
	my $seq2_left;
	my $seq1_right;

	for(my $i = 0; $i < $irseq2_len-$kmer_len;$i++){
		my $kmer = substr($irseq2,$i,$kmer_len);
		
		my $index = index($rev_seq1,$kmer);

		if($index != -1 and abs($index - $i) <= $max_gap_nu){
			$seq2_left = $s2 + $i;
			$seq1_right =$e1 - $index;
			last;
		}
	}

	if($seq1_left and $seq1_right and $seq2_left and $seq2_right){
		return "$seq1_left-$seq1_right,$seq2_left-$seq2_right";
	}else{
		return 0;
	}
}


sub find_ir_in_linear_seq{
	
	#--------------------------------------------------------------------
	#Call the nucmer program to find the starting point of the linear sequence fasta file,
	#find_ir_in_linear_seq(fasta_file,outdir)
	#return [ir,ir_len,ir_idy]  [83483-109152,126878-152547 25670 100.00]
	#--------------------------------------------------------------------

	my $fasta_file = shift;
	my $outdir = shift;

	mkdir $outdir unless(-d $outdir);

	#my $cmd = "$nucmer $fasta_file $fasta_file -g $max_gap_nu --delta=$outdir/out.delta -b $breaklen &> /dev/null && $show_coords $outdir/out.delta > $outdir/out.coords";
 	#my $cmd = "$nucmer $fasta_file $fasta_file -g $max_gap_nu -b $breaklen &> /dev/null && $show_coords $outdir/out.delta > $outdir/out.coords";
  	my $cmd = "$nucmer $fasta_file $fasta_file -g $max_gap_nu -b $breaklen && $show_coords $outdir/out.delta > $outdir/out.coords";
	system "$cmd";
	
	open IN,"$outdir/out.coords" or die "cannot open $outdir/out.coords file";
	$/ = "\n";

	my $read_flag = 0;
	my %for_ir_length;

	while(<IN>){
		chomp;
		if(/^===/){
			$read_flag = 1;
		}elsif($read_flag){
			my ($start1,$end1,$start2,$end2,$len1,$len2,$idy) = (split)[0,1,3,4,6,7,9];
			
			#Skip forward alignment, skip overlapping regions
			next if($end2 > $start2 or $end1 > $end2);	

			
			#Reverse complementary sequences, ordered from smallest to largest
			($start1,$end1,$start2,$end2) = sort{$a <=> $b} ($start1,$end1,$start2,$end2);


			#record all ir fragments
			my $ir = "$start1-$end1,$start2-$end2";
			$for_ir_length{$ir} = [$len1,$idy];

		}
	}close IN;
	
	unlink "$outdir/out.coords";
	unlink "$outdir/out.delta";

	#get the longest ir
	my @ir = sort {$for_ir_length{$a}->[0] <=> $for_ir_length{$b}->[0]} keys %for_ir_length;
	my $ir = $ir[-1];

	#If it does not exist, or is less than the minimum length
	if(!$ir or $for_ir_length{$ir}->[0] < $min_ir_len){
		return 0;
	}
	
	return ($ir,$for_ir_length{$ir}->[0],$for_ir_length{$ir}->[1]);
}


sub judge_file_type{

	my $file = shift;

	open IN,"$file" or die "cannot open file: $file";
	$/ = "\n";

	my $first_line;

	while(<IN>){
		chomp;
		next if(/^\s*$/);
		$first_line = $_;
		last;
	}close IN;

	if($first_line =~ /^>/){
		return "fasta";
	}elsif($first_line =~ /^LOCUS/){
		return "gb";
	}else{
		return "0";
	}
}


sub get_genbank_seq{

	my $gb_file = shift;

	open IN,"$gb_file" or die "cannot open gb file: $gb_file";
	$/ = "\n";

	my $seq;
	my $read_flag = 0;

	while(<IN>){
		chomp;
		
		if(/^ORIGIN/){
			$read_flag = 1;
		}elsif($read_flag == 1 and /^\s*\d/){
			$seq .= $_;
		}

	}

	$seq =~ s/\s|\d|\///g;
	$seq = uc $seq;

	return $seq;
}


sub get_fasta_seq{
	my $fasta_file = shift;

	open IN, "$fasta_file" or die "cannot open fasta file: $fasta_file";
	$/ = "\n";

	my $seq = 0;

	while(<IN>){
		chomp;
		next if(/^\s*$|>/);

		$seq .= $_;
	}

	$seq =~ s/\s|\d|\///g;
	$seq = uc $seq;

	return $seq;
}


sub USAGE {         
	my $usage=<<"USAGE";				
Program: $0
Version: $version
Contact: xul<xul\@genepioneer.cn> <1275875706\@qq.com>
Description:

	find inverted repeats and single-copy regions of chloroplasts

Usage:
		perl $0 -i infile.fasta/infile.gb [-c 0/1]

  Options:
	-i	<string>		input fasta file or genbank file, only contains one sequence

	-c	<int>		Whether the sequence is circular
					
					1 is circular [default]
					0 is not circular

	-m	<int>		The shortest length of the inverted repeat region(bp),default: 100

	-h				Help

USAGE
	print $usage;
	exit;
}


