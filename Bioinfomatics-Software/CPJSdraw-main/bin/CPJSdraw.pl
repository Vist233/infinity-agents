#!/usr/bin/env perl
use warnings;
use strict;

use Getopt::Long;
use File::Basename qw/dirname basename/;
use Cwd;
use FindBin qw/$Bin/;
use lib "$Bin/../lib/";
use SVG;

my $version = "0.0.1";
my $BEGIN_TIME=time();

my $infile;
my $outfile;
my @gb_files;
my $skip_pseudo_gene;
my $skip_orf_gene;
my $skip_NA_gene;
my $back_ground_color;

GetOptions(
				"help|?" =>\&USAGE,
				"i:s"=>\$infile,
				"b:s"=>\$back_ground_color,
				"o:s"=>\$outfile,
				"p!"=>\$skip_pseudo_gene,
				"orf!"=>\$skip_orf_gene,
				"n!"=>\$skip_NA_gene,
				"g:s{1,}"=>\@gb_files,
				) or &USAGE;
&USAGE unless ($infile or @gb_files);

######################################################################################################
#load config
$outfile //= "CPJSDRAW.svg";
$back_ground_color //= "white";

$outfile .= ".svg" unless($outfile =~ /\.svg$/);
my $pwd = getcwd();
my $outfile_basename = basename $outfile;
my $outfile_dirname = dirname $outfile;
my $ppi = 300;

use constant pi => 3.141592653;

my %color=(	"LSC" => "#D1EEEE",
			"IRb" => "#EEAD0E",
			"SSC" => "#B4EEB4",
			"IRa" => "#EEAD0E",

			"rps19" => "#228B22",
			"ycf1"  => "#1E90FF",
			"ndhF"  => "#8B4500",
			"trnH"  => "#8B8B83",
			"trnN"  => "#d57b2a",
			"NA"    => "red",
);

my %for_color_set = (
			"#D02090" => 1,
			"#CD3333" => 1,
			"#9370DB" => 1,
			"#836FFF" => 1,
			"#FF4500" => 1,
			"#9A32CD" => 1,
			"#FF6EB4" => 1,
			"#4F94CD" => 1,
			"#2E8B57" => 1, 
			"#DAA520" => 1, 
			"#20d9d9" => 1,
			"#42e087" => 1,
			"#EE6363" => 1,
			"#D2691E" => 1,
			"#08c1c9" => 1,
			"#8B8682" => 1,
			"#5ba45b" => 1,
			"#7283ee" => 1,
			"#6c922a" => 1,
);


my %charwidths = 
(
	'a' => 6.627, 'b' => 6.627, 'c' => 6.025, 'd' => 6.627, 'e' => 6.627, 'f' => 3.313, 'g' => 6.627, 'h' => 6.627,
	'i' => 2.711, 'j' => 2.711, 'k' => 6.025, 'l' => 2.711, 'm' => 9.941, 'n' => 6.627, 'o' => 6.627, 'p' => 6.627,
	'q' => 6.627, 'r' => 3.916, 's' => 6.025, 't' => 3.313, 'u' => 6.627, 'v' => 6.025, 'w' => 8.736, 'x' => 6.025,
	'y' => 6.025, 'z' => 6.025, 'A' => 8.133,'B' => 8.133, 'C' => 8.736, 'D' => 8.736, 'E' => 8.133, 'F' => 7.23,
	'G' => 9.338, 'H' => 8.736, 'I' => 3.313, 'J' => 6.025, 'K' => 8.133, 'L' => 6.627, 'M' => 9.941, 'N' => 8.736,
	'O' => 9.338, 'P' => 8.133, 'Q' => 9.338, 'R' => 8.736, 'S' => 8.133, 'T' => 7.23, 'U' => 8.736, 'V' => 8.133,
	'W' => 11.447, 'X' => 8.133, 'Y' => 8.133, 'Z' => 7.23, ' ' => 3.313, '.' => 3.313, ',' => 3.313, '-' => 3.916,
	'_' => 6.627, '(' => 3.916, ')' => 3.916, '1' => 6.627, '2' => 6.627, '3' => 6.627, '4' => 6.627, '5' => 6.627,
	'6' => 6.627, '7' => 6.627, '8' => 6.627, '9' => 6.627, '0' => 6.627, '!' => 3.313, '\'' => 3.313, '/' => 3.916,
	'\\' => 3.916, '&' => 6.627
);

######################################################################################################
#read cfg file, get junction site info
warn "-" x 60 ,"\n";
warn"##step1: read cfg file or gb file, get junction site info\n";

my @gb_file_info;

if($infile){
	open IN,"$infile";
	$/ = "\n";
	while(<IN>){
		chomp;
		next if(/^\s*$/);
		push @gb_file_info,$_;
	}
}

if(@gb_files){
	push @gb_file_info,@gb_files;
}


my @input;

for(@gb_file_info){

	my ($gb_file,$js_info) = split/\t/;

	if(-f $gb_file){

		my $gb_info = parse_genbank_file($gb_file);
		my $gene_info = $gb_info->{'gene'};

		if(! defined $gene_info){
			warn "# WRONG: $gb_file has no gene info(no primary gene tag)\n";
			exit;
		}

		if($js_info and $js_info =~ /LSC:(\d+)-(\d+),IRb:(\d+)-(\d+),SSC:(\d+)-(\d+),IRa:(\d+)-(\d+)/i){
			1;
		}elsif($js_info){
			warn "# ERROR: $gb_file: $js_info\n";
			warn "# The junction location has been defined, but the format is incorrect\n";
			warn "# CORRECT: LSC:(\\d+)-(\\d+),IRb:(\\d+)-(\\d+),SSC:(\\d+)-(\\d+),IRa:(\\d+)-(\\d+)\n";
			warn "# (\\d+) stands for position\n";
			exit;
		}else{
			$js_info = get_js_pos($gb_file);

			unless($js_info){
				warn "$gb_file no IR";
				exit;
			}
		}
		
		push @input,[$gb_file,$js_info];

	}else{
		warn "WRONG: $gb_file is not file\n";
		exit;
	}

}
close IN;


######################################################################################################
#read gb file, get gene information
warn "-" x 60 ,"\n";
warn"##step2: read gb file, get gene information\n";

my $longest_name_len = 0;
my $sample_nu = @input;
my @draw_input;

for my $i(0..$#input){
	my $gb_file = $input[$i]->[0];
	my $js_info = $input[$i]->[1];
	print "$gb_file\t$js_info\n";
	my $gb_info = parse_genbank_file($gb_file);

	#get organism	
	$longest_name_len = get_string_len($gb_info->{'organism'}) > $longest_name_len ? get_string_len($gb_info->{'organism'}) : $longest_name_len;

	#format js site
	my $region_info = format_js_info($js_info,$gb_info->{'length'});
	
	#get region gene info
	my $gene_info = get_gene_info($region_info,$gb_info->{'gene'});
	
	push @draw_input,[$gb_info,$region_info,$gene_info];
}


######################################################################################################
#draw
warn "-" x 60 ,"\n";
warn"##step3: draw...\n";

my $font_family = "times new roman";
#my $font_family = "Arial";

my $top = 100;
my $left = 50;
my $right = 100;
my $bottom = 0;

my $acr_r = 25;

my $size_of_sample_name = 20;
my $size_of_junction_name = 15;
my $junction_name_y = 25;

my $size_of_gene_name = 13;
my $size_of_gene_len = 13;

my $size_of_region_name = 16;
my $size_of_region_len = 16;

my $len_of_ir = 250;
my $len_of_lsc = 150;
my $len_of_ssc	= 300;
my $len_of_sample = $longest_name_len * $size_of_sample_name/10;

my $region_rec_height = 25;
my $gene_rec_height = 15;

my $interval_of_sample_name_and_rect = 20;
my $interval_of_rect = 140;
my $interval_of_sample_name_and_seq_length = 5;
my $interval_of_region_name_and_junction = 5;

my $svg_width = $left + $len_of_sample + $interval_of_sample_name_and_rect + $len_of_lsc * 2 + $len_of_ssc + $len_of_ir * 2 + $right;
my $svg_height = $top + $interval_of_rect * $sample_nu + $bottom;

open OUT,"> $outfile" or die "cannot create file : $outfile";

my $svg = SVG->new(width=>$svg_width,height=>$svg_height);
$svg->rect(x=>0,y=>0,width=>$svg_width,height=>$svg_height,"stroke-opacity"=>"1","stroke"=>"$back_ground_color",fill=>$back_ground_color);

my $region_x;
$region_x->{'LSC1'}{'start'} = $left + $len_of_sample + $interval_of_sample_name_and_rect;

#region vertical line
{
	my $region_vertical_line_top = 40;
	my $region_vertical_line_bottom = $svg_height - 50;
	
	my $line_width = 0.5;

	#LSC1-IRb
	$region_x->{'IRb'}{'start'} = $left+$len_of_sample+$interval_of_sample_name_and_rect+$len_of_lsc;
	$svg->path("d"=>"M $region_x->{'IRb'}{'start'}  $region_vertical_line_top L $region_x->{'IRb'}{'start'}  $region_vertical_line_bottom",style=>"stroke","stroke"=>"#9D9D9D","stroke-width"=>$line_width,fill=>"none");
	
	#IRb-SSC
	$region_x->{'SSC'}{'start'} = $region_x->{'IRb'}{'start'} + $len_of_ir;
	$svg->path("d"=>"M $region_x->{'SSC'}{'start'} $region_vertical_line_top L $region_x->{'SSC'}{'start'} $region_vertical_line_bottom",style=>"stroke","stroke"=>"#9D9D9D","stroke-width"=>$line_width,fill=>"none");
	
	#SSC-IRa
	$region_x->{'IRa'}{'start'} = $region_x->{'SSC'}{'start'} + $len_of_ssc;
	$svg->path("d"=>"M $region_x->{'IRa'}{'start'} $region_vertical_line_top L $region_x->{'IRa'}{'start'} $region_vertical_line_bottom",style=>"stroke","stroke"=>"#9D9D9D","stroke-width"=>$line_width,fill=>"none");
	
	#IRa-LSC2
	$region_x->{'LSC2'}{'start'} = $region_x->{'IRa'}{'start'} + $len_of_ir;
	$svg->path("d"=>"M $region_x->{'LSC2'}{'start'} $region_vertical_line_top L $region_x->{'LSC2'}{'start'} $region_vertical_line_bottom",style=>"stroke","stroke"=>"#9D9D9D","stroke-width"=>$line_width,fill=>"none");
}

$region_x->{'LSC1'}{'end'} = $region_x->{'IRb'}{'start'};
$region_x->{'IRb'}{'end'} = $region_x->{'SSC'}{'start'};
$region_x->{'SSC'}{'end'} = $region_x->{'IRa'}{'start'};
$region_x->{'IRa'}{'end'} = $region_x->{'LSC2'}{'start'};
$region_x->{'LSC2'}{'end'} = $region_x->{'LSC2'}{'start'} + $len_of_lsc;



my $x;
my $y;

for my $i(0..$#draw_input){
	$y = $top + $i * $interval_of_rect;
	
#	warn "\n";
#	warn "-" x 80,"\n";
#	warn "$draw_input[$i]->[0]->{'file'}\n";
#	warn "$draw_input[$i]->[1]->{'region'}\n";

	#sample name
	my $sample_name_x = $left + $len_of_sample;
	my $sample_name_y = $y;
	my $sample_name = $draw_input[$i]->[0]->{'organism'};

	$svg->text(x=>$sample_name_x,y=>$sample_name_y,'font-size'=>$size_of_sample_name,'font-family'=>$font_family,'font-style'=>'italic','-cdata'=>$sample_name,"text-anchor"=>"end");

	#junction gene
	{
	#SC
		for my $sc(qw/LSC1 SSC LSC2/){
			unless(defined $draw_input[$i]->[2]->{$sc}){
				warn "warn: No gene in $sc\n";
			}else{
				my @sc_gene_info = @{$draw_input[$i]->[2]->{$sc}};
				my $sc_start = $draw_input[$i]->[1]->{$sc}->{'start'};
				my $sc_end = $draw_input[$i]->[1]->{$sc}->{'end'};
				my $sc_len = $draw_input[$i]->[1]->{$sc}->{'length'};

				if(@sc_gene_info == 1 and $sc eq "SSC"){
					my $gene_for_draw = $sc_gene_info[0];
					my ($gene_name,$gene_start,$gene_end,$chain) = @{$gene_for_draw};
					my $js_start_x = $region_x->{$sc}->{'start'};
					my $js_end_x = $region_x->{$sc}->{'end'};
					
					if($gene_start < $sc_start and $gene_end < $sc_end){	#gene over start
						my $js_x = $region_x->{$sc}->{'start'};
						my $gene_seq_len = $gene_end - $gene_start + 1;
						my $gene_rect_y = $y - $size_of_sample_name/2 + $region_rec_height/2;
						my $right_dist_len = get_gap_len($sc_end - $gene_end);

						my $left_seq_len = $sc_start - $gene_start;
						my $right_seq_len = $gene_end - $sc_start + 1;

						my $left_rect_len = get_gap_len($left_seq_len);
						
						my $gene_rect_len = $len_of_ssc - $right_dist_len + $left_rect_len;

						my $right_rect_len = $gene_rect_len - $left_rect_len;

						my $gene_rect_x = $js_x - $left_rect_len;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

						#span line
						my $span_line_y = $gene_rect_y+$gene_rec_height + 10;
						draw_span_line($gene_rect_x,$span_line_y,$js_x - 2,$span_line_y);
						draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len - 1,$span_line_y);
						draw_span_line($js_x+$len_of_ssc,$span_line_y,$js_x + $right_rect_len + 1,$span_line_y);

						draw_len($left_seq_len,$js_x - 10,$span_line_y + $size_of_gene_len + 7,"end");
						draw_len($right_seq_len,$js_x + $right_rect_len/2,$span_line_y + $size_of_gene_len + 7,"middle");
						draw_len($sc_end - $gene_end,$region_x->{$sc}->{'end'}-$right_dist_len/2,$span_line_y + $size_of_gene_len + 7,"middle");

					}elsif($gene_end > $sc_end and $gene_start > $sc_start){	#gene over end
						my $js_x = $region_x->{$sc}->{'end'};
						my $gene_seq_len = $gene_end - $gene_start + 1;
						my $gene_rect_y = $y - $size_of_sample_name/2 + $region_rec_height/2;
						my $left_dist_len = get_gap_len($gene_start - $sc_start);

						my $left_seq_len = $sc_end - $gene_start + 1;
						my $right_seq_len = $gene_end - $sc_end;
						
						my $right_rect_len = get_gap_len($right_seq_len);

						my $gene_rect_len = $len_of_ssc - $left_dist_len + $right_rect_len;

						my $left_rect_len = $gene_rect_len - $right_rect_len;

						my $gene_rect_x = $js_x - $left_rect_len;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

						#span line

						my $span_line_y = $gene_rect_y+$gene_rec_height+10;
						draw_span_line($region_x->{$sc}->{'start'},$span_line_y,$gene_rect_x-1,$span_line_y);
						draw_span_line($gene_rect_x+1,$span_line_y,$js_x - 2,$span_line_y);
						draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len,$span_line_y);
						
						draw_len($gene_start - $sc_start,$region_x->{$sc}->{'start'} + $left_dist_len/2,$span_line_y + $size_of_gene_len + 7,"middle");
						draw_len($left_seq_len,$gene_rect_x + $left_rect_len/2,$span_line_y + $size_of_gene_len + 7,"middle");
						draw_len($right_seq_len,$js_x + 7,$span_line_y + $size_of_gene_len + 7,"middle");
						

					}else{ #over ssc
						my $gene_seq_len = $gene_end - $gene_start + 1;

						my $left_dist_len = $len_of_ssc * ($gene_start - $sc_start)/$draw_input[$i]->[1]->{$sc}->{'length'};
						my $right_dist_len = $len_of_ssc * ($sc_end - $gene_end)/$draw_input[$i]->[1]->{$sc}->{'length'};
							
						if(45 + $left_dist_len + $right_dist_len > $len_of_ssc){
							$left_dist_len = $left_dist_len - (45 + $left_dist_len + $right_dist_len - $len_of_ssc)/2;
							$right_dist_len = $right_dist_len - (45 + $left_dist_len + $right_dist_len - $len_of_ssc)/2;
						}

						my $gene_rect_len = $len_of_ssc - $left_dist_len - $right_dist_len;
						my $gene_rect_x = $region_x->{$sc}->{'start'} + $left_dist_len;
						my $gene_rect_y = $y - $size_of_sample_name/2 + $region_rec_height/2;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);
						draw_len($gene_seq_len,$gene_rect_x + $gene_rect_len/2,$gene_rect_y + $region_rec_height + 2,"middle");
						
						#span line
						my $span_line_y = $gene_rect_y+$gene_rec_height+10;
						draw_span_line($gene_rect_x,$span_line_y,$region_x->{$sc}->{'start'},$span_line_y);
						draw_span_line($gene_rect_x + $gene_rect_len,$span_line_y,$region_x->{$sc}->{'end'},$span_line_y);

						draw_len(abs($gene_start - $sc_start),$region_x->{$sc}->{'start'} + $left_dist_len/2, $span_line_y + $size_of_gene_len + 7,"middle");
						draw_len(abs($sc_end - $gene_end),$region_x->{$sc}->{'end'} - $right_dist_len/2, $span_line_y + $size_of_gene_len + 7,"middle");

					}
				}else{
					#start
					if($sc eq "SSC" or $sc eq "LSC2"){
						my $left_gene_for_draw = (sort{$a->[1] <=> $b->[1]} @sc_gene_info)[0];
						my ($gene_name,$gene_start,$gene_end,$chain) = @{$left_gene_for_draw};
						my $js_x = $region_x->{$sc}->{'start'};

						my $gene_seq_len = $gene_end - $gene_start + 1;
						my $gene_rect_len = get_gene_len($gene_seq_len);
						my $gene_rect_y = $y - $size_of_sample_name/2 + $region_rec_height/2;

						if($gene_start >= $sc_start){	#in SC
							my $gene_to_js_dist = get_gap_len($gene_start - $sc_start);
							my $gene_rect_x = $js_x + $gene_to_js_dist;
							draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);
							draw_len($gene_seq_len,$gene_rect_x + $gene_rect_len/2,$gene_rect_y + $region_rec_height + 2,"middle");

							#acr 4
							my $acr_x1 = $gene_rect_x - $gene_to_js_dist/2;
							my $acr_y1 = $gene_rect_y + $gene_rec_height;
							my $acr_x2 = $acr_x1 + $acr_r;
							my $acr_y2 = $acr_y1 + $acr_r;
							draw_acr($acr_x1,$acr_y1,$acr_x2,$acr_y2,$acr_r,4);
							
							#dist len
							my $dist_len = $gene_start - $sc_start;
							draw_len($dist_len,$acr_x2 + 2,$acr_y2 + $size_of_gene_len/2 - 2,"start");

						}else{	##over JS
							my $left_seq_len = $sc_start - $gene_start;
							my $right_seq_len = $gene_end - $sc_start + 1;
							
							my $left_rect_len = get_gap_len($left_seq_len);

							my $right_rect_len = $gene_rect_len - $left_rect_len;

							my $gene_rect_x = $js_x - $left_rect_len;
							draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

							#span line
							my $span_line_y = $gene_rect_y+$gene_rec_height+10;
							draw_span_line($gene_rect_x,$span_line_y,$js_x - 2,$span_line_y);
							draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len,$span_line_y);

							draw_len($left_seq_len,$js_x - 10,$span_line_y + $size_of_gene_len + 7,"end");
							draw_len($right_seq_len,$js_x + 7,$span_line_y + $size_of_gene_len + 7,"start");
						}
					}

					#end
					if($sc eq "SSC" or $sc eq "LSC1"){
						my $right_gene_for_draw = (sort{$a->[2] <=> $b->[2]} @sc_gene_info)[-1];
						my ($gene_name,$gene_start,$gene_end,$chain) = @{$right_gene_for_draw};
						my $js_x = $region_x->{$sc}->{'end'};

						my $gene_seq_len = $gene_end - $gene_start + 1;
						my $gene_rect_len = get_gene_len($gene_seq_len);
						my $gene_rect_y =  $y - $size_of_sample_name/2 + $region_rec_height/2;

						if($gene_end <= $sc_end){	#in sc
							my $gene_to_js_dist = get_gap_len($sc_end - $gene_end);
							my $gene_rect_x = $js_x - $gene_rect_len - $gene_to_js_dist;
							draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);
							draw_len($gene_seq_len,$gene_rect_x + $gene_rect_len/2,$gene_rect_y + $region_rec_height + 2,"middle");

							#acr 3
							my $acr_x1 =$gene_rect_x + $gene_rect_len + $gene_to_js_dist/2;
							my $acr_y1 = $gene_rect_y + $gene_rec_height;
							my $acr_x2 = $acr_x1 - $acr_r;
							my $acr_y2 = $acr_y1 + $acr_r;
							draw_acr($acr_x1,$acr_y1,$acr_x2,$acr_y2,$acr_r,3);
							
							#dist len
							my $dist_len = $sc_end - $gene_end;
							draw_len($dist_len,$acr_x2 - 2,$acr_y2 + $size_of_gene_len/2 - 2,"end");
						}else{	#over JLB
							my $left_seq_len = $sc_end - $gene_start + 1;
							my $right_seq_len = $gene_end - $sc_end;
							
							my $right_rect_len = get_gap_len($right_seq_len);

							my $left_rect_len = $gene_rect_len - $right_rect_len;

							my $gene_rect_x = $js_x - $left_rect_len;
							draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

							#span line
							my $span_line_y = $gene_rect_y+$gene_rec_height+10;
							draw_span_line($gene_rect_x,$span_line_y,$js_x - 2,$span_line_y);
							draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len,$span_line_y);

							draw_len($left_seq_len,$js_x - 10,$span_line_y + $size_of_gene_len + 7,"end");
							draw_len($right_seq_len,$js_x + 7,$span_line_y + $size_of_gene_len + 7,"start");
						}
					}
				}
			}
		}
	#IR
		for my $ir(qw/IRb IRa/){
			unless(defined $draw_input[$i]->[2]->{$ir}){
				warn "warn: No gene in $ir\n";
			}else{
				my @ir_gene_info = @{$draw_input[$i]->[2]->{$ir}};
				my $ir_start = $draw_input[$i]->[1]->{$ir}->{'start'};
				my $ir_end = $draw_input[$i]->[1]->{$ir}->{'end'};

				if(@ir_gene_info == 1){	#only have one gene
					my $gene_for_draw = $ir_gene_info[0];
					my ($gene_name,$gene_start,$gene_end,$chain) = @{$gene_for_draw};
					my $js_start_x = $region_x->{$ir}->{'start'};
					my $js_end_x = $region_x->{$ir}->{'end'};
					
					if($gene_start < $ir_start and $gene_end < $ir_end){	#gene over start
						my $js_x = $region_x->{$ir}->{'start'};
						my $gene_seq_len = $gene_end - $gene_start + 1;

						my $gene_rect_y = $y - $size_of_sample_name/2 - $region_rec_height/2 - $gene_rec_height;
						my $right_dist_len = get_gap_len($ir_end - $gene_end);

						my $left_seq_len = $ir_start - $gene_start;
						my $right_seq_len = $gene_end - $ir_start + 1;
						
						my $left_rect_len = get_gap_len($left_seq_len);

						my $gene_rect_len = $left_rect_len + $len_of_ir - $right_dist_len;

						my $right_rect_len = $gene_rect_len - $left_rect_len;

						my $gene_rect_x = $js_x - $left_rect_len;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

						#span line
						my $span_line_y = $gene_rect_y - 10;
						draw_span_line($region_x->{$ir}->{'end'},$span_line_y,$js_x + $right_rect_len + 1,$span_line_y);
						draw_span_line($gene_rect_x,$span_line_y,$js_x - 2,$span_line_y);
						draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len - 1,$span_line_y);
						
						draw_len($ir_end - $gene_end,$region_x->{$ir}->{'end'} - $right_dist_len/2,$span_line_y - 7,"middle");
						draw_len($left_seq_len,$js_x - 10,$span_line_y - 7,"end");
						draw_len($right_seq_len,$js_x + $right_rect_len/2,$span_line_y - 7,"middle");

					}elsif($gene_end > $ir_end and $gene_start > $ir_start){	#gene over end
						my $js_x = $region_x->{$ir}->{'end'};
						my $gene_seq_len = $gene_end - $gene_start + 1;
						my $gene_rect_y = $y - $size_of_sample_name/2 - $region_rec_height/2 - $gene_rec_height;
						my $left_dist_len = get_gap_len($gene_start - $ir_start);

						my $left_seq_len = $ir_end - $gene_start + 1;
						my $right_seq_len = $gene_end - $ir_end;
						
						my $right_rect_len = get_gap_len($right_seq_len);
						
						my $gene_rect_len = $right_rect_len + $len_of_ir - $left_dist_len;

						my $left_rect_len = $gene_rect_len - $right_rect_len;

						my $gene_rect_x = $js_x - $left_rect_len;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

						#span line
						my $span_line_y = $gene_rect_y - 10;
						draw_span_line($gene_rect_x - 1,$span_line_y,$region_x->{$ir}->{'start'},$span_line_y);
						draw_span_line($gene_rect_x + 1,$span_line_y,$js_x - 2,$span_line_y);
						draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len,$span_line_y);
						
						draw_len($gene_start - $ir_start,$region_x->{$ir}->{'start'} + $left_dist_len/2 ,$span_line_y - 7,"middle");
						draw_len($left_seq_len,$gene_rect_x + $left_rect_len/2,$span_line_y - 7,"middle");
						draw_len($right_seq_len,$js_x + 7,$span_line_y - 7,"start");
						
					}else{ #over IR
						my $gene_seq_len = $gene_end - $gene_start + 1;
						my $left_dist_len = $len_of_ir * ($gene_start - $ir_start)/$draw_input[$i]->[1]->{$ir}->{'length'};
						my $right_dist_len = $len_of_ir * ($ir_end - $gene_end)/$draw_input[$i]->[1]->{$ir}->{'length'};
							
						if(45 + $left_dist_len + $right_dist_len > $len_of_ir){
							$left_dist_len = $left_dist_len - (45 + $left_dist_len + $right_dist_len - $len_of_ir)/2;
							$right_dist_len = $right_dist_len - (45 + $left_dist_len + $right_dist_len - $len_of_ir)/2;
						}

						my $gene_rect_len = $len_of_ir - $left_dist_len - $right_dist_len;
						my $gene_rect_x = $region_x->{$ir}->{'start'} + $left_dist_len;
						my $gene_rect_y = $y - $size_of_sample_name/2 - $region_rec_height/2 - $gene_rec_height;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);
						draw_len($gene_seq_len,$gene_rect_x + $gene_rect_len/2,$gene_rect_y - 2,"middle");
						
						#span line
						my $span_line_y = $gene_rect_y - 10;
						draw_span_line($gene_rect_x,$span_line_y,$region_x->{$ir}->{'start'},$span_line_y);
						draw_span_line($gene_rect_x + $gene_rect_len,$span_line_y,$region_x->{$ir}->{'end'},$span_line_y);

						draw_len(abs($gene_start - $ir_start),$region_x->{$ir}->{'start'} + $left_dist_len/2,$span_line_y - 7,"middle");
						draw_len(abs($ir_end - $gene_end),$region_x->{$ir}->{'end'} - $right_dist_len/2,$span_line_y - 7,"middle");

					}
			
				}else{
					#start
					my $left_gene_for_draw = (sort{$a->[1] <=> $b->[1]} @ir_gene_info)[0];
					my ($gene_name,$gene_start,$gene_end,$chain) = @{$left_gene_for_draw};
					my $js_x = $region_x->{$ir}->{'start'};

					my $gene_seq_len = $gene_end - $gene_start + 1;
					my $gene_rect_len = get_gene_len($gene_seq_len);
					my $gene_rect_y = $y - $size_of_sample_name/2 - $region_rec_height/2 - $gene_rec_height;

					if($gene_start >= $ir_start){	#in IR
						my $gene_to_js_dist = get_gap_len($gene_start - $ir_start);
						my $gene_rect_x = $js_x + $gene_to_js_dist;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);
						draw_len($gene_seq_len,$gene_rect_x + $gene_rect_len/2,$gene_rect_y - 2,"middle");

						#acr 1
						my $acr_x1 = $gene_rect_x - $gene_to_js_dist/2;
						my $acr_y1 = $gene_rect_y ;
						my $acr_x2 = $acr_x1 + $acr_r;
						my $acr_y2 = $acr_y1 - $acr_r;
						draw_acr($acr_x1,$acr_y1,$acr_x2,$acr_y2,$acr_r,1);
						
						#dist len
						my $dist_len = $gene_start - $ir_start;
						draw_len($dist_len,$acr_x2 + 2,$acr_y2 + $size_of_gene_len/2 - 2,"start");

					}else{	##over JLB
						my $left_seq_len = $ir_start - $gene_start;
						my $right_seq_len = $gene_end - $ir_start + 1;
						
						my $left_rect_len = get_gap_len($left_seq_len);

						my $right_rect_len = $gene_rect_len - $left_rect_len;

						my $gene_rect_x = $js_x - $left_rect_len;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

						#span line
						my $span_line_y = $gene_rect_y - 10;
						draw_span_line($gene_rect_x,$span_line_y,$js_x - 2,$span_line_y);
						draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len,$span_line_y);

						draw_len($left_seq_len,$js_x - 10,$span_line_y - 7,"end");
						draw_len($right_seq_len,$js_x + 7,$span_line_y - 7,"start");
					}

					#end
					my $right_gene_for_draw = (sort{$a->[2] <=> $b->[2]} @ir_gene_info)[-1];
					($gene_name,$gene_start,$gene_end,$chain) = @{$right_gene_for_draw};
					$js_x = $region_x->{$ir}->{'end'};

					$gene_seq_len = $gene_end - $gene_start + 1;
					$gene_rect_len = get_gene_len($gene_seq_len);
					$gene_rect_y = $y - $size_of_sample_name/2 - $region_rec_height/2 - $gene_rec_height;

					if($gene_end <= $ir_end){	#in IR
						my $gene_to_js_dist = get_gap_len($ir_end - $gene_end);
						my $gene_rect_x = $js_x - $gene_rect_len - $gene_to_js_dist;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);
						draw_len($gene_seq_len,$gene_rect_x + $gene_rect_len/2,$gene_rect_y - 2,"middle");

						#acr 2
						my $acr_x1 =$gene_rect_x + $gene_rect_len + $gene_to_js_dist/2;
						my $acr_y1 = $gene_rect_y ;
						my $acr_x2 = $acr_x1 - $acr_r;
						my $acr_y2 = $acr_y1 - $acr_r;
						draw_acr($acr_x1,$acr_y1,$acr_x2,$acr_y2,$acr_r,2);
						
						#dist len
						my $dist_len = $ir_end - $gene_end;
						draw_len($dist_len,$acr_x2 - 2,$acr_y2 + $size_of_gene_len/2 - 2,"end");
					}else{	#over JLB
						my $left_seq_len = $ir_end - $gene_start + 1;
						my $right_seq_len = $gene_end - $ir_end;
						
						my $right_rect_len = get_gap_len($right_seq_len);

						my $left_rect_len = $gene_rect_len - $right_rect_len;

						my $gene_rect_x = $js_x - $left_rect_len;
						draw_gene_rect_and_name($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain);

						#span line
						my $span_line_y = $gene_rect_y - 10;
						draw_span_line($gene_rect_x,$span_line_y,$js_x - 2,$span_line_y);
						draw_span_line($js_x+2,$span_line_y,$js_x + $right_rect_len,$span_line_y);

						draw_len($left_seq_len,$js_x - 10,$span_line_y - 7,"end");
						draw_len($right_seq_len,$js_x + 7,$span_line_y - 7,"start");
					}
				}
			}
		}
	}

	#genome length
	my $seq_len = $draw_input[$i]->[0]->{'length'};
	my $seq_len_x = $left + $len_of_sample;
	my $seq_len_y = $y + $interval_of_sample_name_and_seq_length + $size_of_gene_len;
	$svg->text(x=>$seq_len_x,y=>$seq_len_y,'font-size'=>15,'font-family'=>$font_family,'-cdata'=>format_nu($seq_len)." bp","text-anchor"=>"end");

	#region rect
	my ($x_line1,$x_line2,$x_line3,$x_line4,$y_line1,$y_line2,$line_interval);
	$line_interval = 10;
	my $region_rect_y = $y - $size_of_sample_name/2 - $region_rec_height/2;

	$svg->rect(x=>$region_x->{'LSC1'}->{'start'},y=>$region_rect_y,width=>$len_of_lsc,height=>$region_rec_height,"stroke-opacity"=>"1","stroke"=>"black",fill=>$color{'LSC'});	#LSC
	$x_line1 = $region_x->{'LSC1'}->{'start'} + $len_of_lsc/2 - 25;
	$x_line2 = $x_line1 + $line_interval;
	$x_line3 = $x_line1;
	$x_line4 = $x_line3 - $line_interval;
	$y_line1 = $region_rect_y;
	$y_line2 = $region_rect_y + $region_rec_height;
	$svg->path("d"=>"M $x_line1 $y_line1 L $x_line2 $y_line1 L $x_line3 $y_line2 L $x_line4 $y_line2 L $x_line1 $y_line1",style=>"stroke","stroke"=>"black","stroke-width"=>1,fill=>"white");

	$svg->rect(x=>$region_x->{'LSC1'}->{'end'},y=>$region_rect_y,width=>$len_of_ir,height=>$region_rec_height,"stroke-opacity"=>"1","stroke"=>"black",fill=>$color{'IRb'});	#IRb
	$x_line1 = $region_x->{'LSC1'}->{'end'} + $len_of_ir/2;
	$x_line2 = $x_line1 + $line_interval;
	$x_line3 = $x_line1;
	$x_line4 = $x_line3 - $line_interval;
	$y_line1 = $region_rect_y;
	$y_line2 = $region_rect_y + $region_rec_height;
	$svg->path("d"=>"M $x_line1 $y_line1 L $x_line2 $y_line1 L $x_line3 $y_line2 L $x_line4 $y_line2 L $x_line1 $y_line1",style=>"stroke","stroke"=>"black","stroke-width"=>1,fill=>"white");

	$svg->rect(x=>$region_x->{'SSC'}->{'start'},y=>$region_rect_y,width=>$len_of_ssc,height=>$region_rec_height,"stroke-opacity"=>"1","stroke"=>"black",fill=>$color{'SSC'});	#SSC
	$x_line1 = $region_x->{'SSC'}->{'start'} + $len_of_ssc/2;
	$x_line2 = $x_line1 + $line_interval;
	$x_line3 = $x_line1;
	$x_line4 = $x_line3 - $line_interval;
	$y_line1 = $region_rect_y;
	$y_line2 = $region_rect_y + $region_rec_height;
	$svg->path("d"=>"M $x_line1 $y_line1 L $x_line2 $y_line1 L $x_line3 $y_line2 L $x_line4 $y_line2 L $x_line1 $y_line1",style=>"stroke","stroke"=>"black","stroke-width"=>1,fill=>"white");

	$svg->rect(x=>$region_x->{'SSC'}->{'end'},y=>$region_rect_y,width=>$len_of_ir,height=>$region_rec_height,"stroke-opacity"=>"1","stroke"=>"black",fill=>$color{'IRa'});	#IRa
	$x_line1 = $region_x->{'SSC'}->{'end'} + $len_of_ir/2;
	$x_line2 = $x_line1 + $line_interval;
	$x_line3 = $x_line1;
	$x_line4 = $x_line3 - $line_interval;
	$y_line1 = $region_rect_y;
	$y_line2 = $region_rect_y + $region_rec_height;
	$svg->path("d"=>"M $x_line1 $y_line1 L $x_line2 $y_line1 L $x_line3 $y_line2 L $x_line4 $y_line2 L $x_line1 $y_line1",style=>"stroke","stroke"=>"black","stroke-width"=>1,fill=>"white");

	$svg->rect(x=>$region_x->{'IRa'}->{'end'},y=>$region_rect_y,width=>$len_of_lsc,height=>$region_rec_height,"stroke-opacity"=>"1","stroke"=>"black",fill=>$color{'LSC'});	#LSC
	$x_line1 = $region_x->{'IRa'}->{'end'} + $len_of_lsc/2;
	$x_line2 = $x_line1 + $line_interval;
	$x_line3 = $x_line1;
	$x_line4 = $x_line3 - $line_interval;
	$y_line1 = $region_rect_y;
	$y_line2 = $region_rect_y + $region_rec_height;
	$svg->path("d"=>"M $x_line1 $y_line1 L $x_line2 $y_line1 L $x_line3 $y_line2 L $x_line4 $y_line2 L $x_line1 $y_line1",style=>"stroke","stroke"=>"black","stroke-width"=>1,fill=>"white");

	#region name
	my $region_name_y = $y - $size_of_sample_name/2 + $size_of_region_name/2;
	$svg->text(x=>$region_x->{'LSC1'}->{'start'}+$interval_of_region_name_and_junction,y=>$region_name_y,'font-size'=>$size_of_region_name,'font-family'=>$font_family,'-cdata'=>'LSC',"text-anchor"=>"start");
	$svg->text(x=>$region_x->{'LSC1'}->{'end'}+$interval_of_region_name_and_junction,y=>$region_name_y,'font-size'=>$size_of_region_name,'font-family'=>$font_family,'-cdata'=>'IRb',"text-anchor"=>"start");
	$svg->text(x=>$region_x->{'SSC'}->{'start'}+$interval_of_region_name_and_junction,y=>$region_name_y,'font-size'=>$size_of_region_name,'font-family'=>$font_family,'-cdata'=>'SSC',"text-anchor"=>"start");
	$svg->text(x=>$region_x->{'SSC'}->{'end'}+$interval_of_region_name_and_junction,y=>$region_name_y,'font-size'=>$size_of_region_name,'font-family'=>$font_family,'-cdata'=>'IRa',"text-anchor"=>"start");
	$svg->text(x=>$region_x->{'IRa'}->{'end'}+$interval_of_region_name_and_junction,y=>$region_name_y,'font-size'=>$size_of_region_name,'font-family'=>$font_family,'-cdata'=>'LSC',"text-anchor"=>"start");

	#region length
	my $lsc_len = $draw_input[$i]->[1]->{'LSC'}->{'length'};
	my $irb_len = $draw_input[$i]->[1]->{'IRb'}->{'length'};
	my $ssc_len = $draw_input[$i]->[1]->{'SSC'}->{'length'};
	my $ira_len = $draw_input[$i]->[1]->{'IRa'}->{'length'};
	my $region_len_y = $y - $size_of_sample_name/2 + $size_of_region_name/2;

	$svg->text(x=>$region_x->{'LSC1'}->{'end'}-$interval_of_region_name_and_junction,y=>$region_len_y,'font-size'=>$size_of_region_len,'font-family'=>$font_family,'-cdata'=>format_nu($lsc_len)." bp","text-anchor"=>"end");
	$svg->text(x=>$region_x->{'SSC'}->{'start'}-$interval_of_region_name_and_junction,y=>$region_len_y,'font-size'=>$size_of_region_len,'font-family'=>$font_family,'-cdata'=>format_nu($irb_len)." bp","text-anchor"=>"end");
	$svg->text(x=>$region_x->{'SSC'}->{'end'}-$interval_of_region_name_and_junction,y=>$region_len_y,'font-size'=>$size_of_region_len,'font-family'=>$font_family,'-cdata'=>format_nu($ssc_len)." bp","text-anchor"=>"end");
	$svg->text(x=>$region_x->{'IRa'}->{'end'}-$interval_of_region_name_and_junction,y=>$region_len_y,'font-size'=>$size_of_region_len,'font-family'=>$font_family,'-cdata'=>format_nu($ira_len)." bp","text-anchor"=>"end");

	#junction name
	$svg->text(x=>$region_x->{'LSC1'}->{'end'},y=>$junction_name_y ,'font-size'=>$size_of_junction_name,'font-family'=>$font_family,'-cdata'=>"JLB","text-anchor"=>"middle");
	$svg->text(x=>$region_x->{'SSC'}->{'start'},y=>$junction_name_y ,'font-size'=>$size_of_junction_name,'font-family'=>$font_family,'-cdata'=>"JSB","text-anchor"=>"middle");
	$svg->text(x=>$region_x->{'SSC'}->{'end'},y=>$junction_name_y ,'font-size'=>$size_of_junction_name,'font-family'=>$font_family,'-cdata'=>"JSA","text-anchor"=>"middle");
	$svg->text(x=>$region_x->{'IRa'}->{'end'},y=>$junction_name_y ,'font-size'=>$size_of_junction_name,'font-family'=>$font_family,'-cdata'=>"JLA","text-anchor"=>"middle");
}

print  OUT $svg->xmlify;

warn "-" x 60 ,"\n";
warn"##step4: convert svg to png and pdf...\n";
chdir $outfile_dirname;
`perl $Bin/../script/svg_kit/svg2xxx -t pdf $outfile_basename`;
`perl $Bin/../script/svg_kit/svg2xxx -t png -dpi $ppi $outfile_basename`;
chdir $pwd;

warn "done.\n";
#====================================================================================================
sub draw_span_line{
	my ($x1,$y1,$x2,$y2) = @_;

	$svg->path("d"=>"M $x1 $y1 L $x2 $y2",style=>"stroke","stroke"=>"black","stroke-width"=>0.7,fill=>"none");

	my $x3 = $x1;
	my $y3 = $y1 - 5;
	my $x4 = $x1;
	my $y4 = $y1 + 5;

	$svg->path("d"=>"M $x3 $y3 L $x4 $y4",style=>"stroke","stroke"=>"black","stroke-width"=>0.7,fill=>"none");

	my $x5 = $x2;
	my $y5 = $y2 - 5;
	my $x6 = $x2;
	my $y6 = $y2 + 5;

	$svg->path("d"=>"M $x5 $y5 L $x6 $y6",style=>"stroke","stroke"=>"black","stroke-width"=>0.7,fill=>"none");

}


sub draw_acr{
	my ($acr_x1,$acr_y1,$acr_x2,$acr_y2,$acr_r,$relative_position) = @_;
	
	if($relative_position == 1){
		#arc
		$svg->path("d"=>"M $acr_x1  $acr_y1 A $acr_r $acr_r 0 0 1 $acr_x2  $acr_y2 ",style=>"stroke", "stroke"=>"black","stroke-width"=>0.5, fill=>"none");

		#arc_arrow
		my ($arc_arrow_x1,$arc_arrow_y1) = ($acr_x2-3,$acr_y2-3);
		my ($arc_arrow_x2,$arc_arrow_y2) = ($acr_x2-3,$acr_y2+3);

		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x1 $arc_arrow_y1",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");
		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x2 $arc_arrow_y2",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");

	}elsif($relative_position == 2){
		#arc
		$svg->path("d"=>"M $acr_x1  $acr_y1 A $acr_r $acr_r 0 0 0 $acr_x2  $acr_y2 ",style=>"stroke", "stroke"=>"black","stroke-width"=>0.5, fill=>"none");

		#arc_arrow
		my ($arc_arrow_x1,$arc_arrow_y1) = ($acr_x2+3,$acr_y2-3);
		my ($arc_arrow_x2,$arc_arrow_y2) = ($acr_x2+3,$acr_y2+3);

		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x1 $arc_arrow_y1",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");
		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x2 $arc_arrow_y2",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");

	}elsif($relative_position == 3){

		#arc
		$svg->path("d"=>"M $acr_x1  $acr_y1 A $acr_r $acr_r 0 0 1 $acr_x2  $acr_y2 ",style=>"stroke", "stroke"=>"black","stroke-width"=>0.5, fill=>"none");

		#arc_arrow
		my ($arc_arrow_x1,$arc_arrow_y1) = ($acr_x2+3,$acr_y2-3);
		my ($arc_arrow_x2,$arc_arrow_y2) = ($acr_x2+3,$acr_y2+3);

		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x1 $arc_arrow_y1",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");
		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x2 $arc_arrow_y2",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");


	}elsif($relative_position == 4){
		#arc
		$svg->path("d"=>"M $acr_x1  $acr_y1 A $acr_r $acr_r 0 0 0 $acr_x2  $acr_y2 ",style=>"stroke", "stroke"=>"black","stroke-width"=>0.5, fill=>"none");

		#arc_arrow
		my ($arc_arrow_x1,$arc_arrow_y1) = ($acr_x2-3,$acr_y2-3);
		my ($arc_arrow_x2,$arc_arrow_y2) = ($acr_x2-3,$acr_y2+3);

		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x1 $arc_arrow_y1",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");
		$svg->path("d"=>"M $acr_x2  $acr_y2 L $arc_arrow_x2 $arc_arrow_y2",style=>"stroke","stroke"=>"black","stroke-width"=>0.5,fill=>"none");
	}
}


sub draw_gene_rect_and_name{
	my ($gene_name,$gene_rect_x,$gene_rect_y,$gene_rect_len,$chain) = @_;
	
	if((!$color{$gene_name}) and keys %for_color_set > 0){
		$color{$gene_name} = (sort keys %for_color_set)[0];
		delete $for_color_set{$color{$gene_name}};
	}

	$color{$gene_name} //= 'red';

	#rect
	if($chain){	#complement <=
		my $x0 = $gene_rect_x;
		my $y0 = $gene_rect_y + $gene_rec_height/2;
		my $x1 = $x0 + 6;
		my $y1 = $gene_rect_y + $gene_rec_height;
		my $x2 = $x0 + $gene_rect_len;
		my $y2 = $y1;
		my $x3 = $x2;
		my $y3 = $gene_rect_y;
		my $x4 = $x1;
		my $y4 = $gene_rect_y;

		$svg->path("d"=>"M $x0 $y0 L $x1 $y1 L $x2 $y2 L $x3 $y3 L $x4 $y4 ",style=>"stroke","stroke"=>$color{$gene_name},"stroke-width"=>0.5,fill=>$color{$gene_name});

	}else{
		my $x0 = $gene_rect_x + $gene_rect_len;
		my $y0 = $gene_rect_y + $gene_rec_height/2;
		my $x1 = $x0 - 6;
		my $y1 = $gene_rect_y;
		my $x2 = $x0 - $gene_rect_len;
		my $y2 = $y1;
		my $x3 = $x2;
		my $y3 = $gene_rect_y + $gene_rec_height;
		my $x4 = $x1;
		my $y4 = $gene_rect_y + $gene_rec_height;

		$svg->path("d"=>"M $x0 $y0 L $x1 $y1 L $x2 $y2 L $x3 $y3 L $x4 $y4 ",style=>"stroke","stroke"=>$color{$gene_name},"stroke-width"=>0.5,fill=>$color{$gene_name});
	}
	
	#name
	my $name_x = $gene_rect_x + $gene_rect_len/2;
	my $name_y = $gene_rect_y + $gene_rec_height - 2;

	$svg->text(x=>$name_x,y=>$name_y,'font-size'=>$size_of_gene_name,'font-family'=>$font_family,'-cdata'=>$gene_name,"text-anchor"=>"middle",fill=>"white",'font-style'=>'italic');

}


sub draw_len{
	my ($gene_len,$gene_len_x,$gene_len_y,$align) = @_;

	$svg->text(x=>$gene_len_x,y=>$gene_len_y,'font-size'=>$size_of_gene_len,'font-family'=>$font_family,'-cdata'=>"$gene_len bp","text-anchor"=>$align,fill=>"black");
}

sub get_gene_len{
	my $len = shift;

	my $raw_len = $len;
	$len = abs $len;
	my $L;

	if($len == 0){
		$L = 0
	}elsif($len<100){
		$L = 45
	}elsif($len<200){
		$L = 50
	}elsif($len<300){
		$L = 60
	}elsif($len<400){
		$L = 61
	}elsif($len<500){
		$L = 62
	}elsif($len<600){
		$L = 64
	}elsif($len<700){
		$L = 66
	}elsif($len<800){
		$L = 68
	}elsif($len<900){
		$L = 70
	}elsif($len<1000){
		$L = 72
	}elsif($len<2000){
		$L = 76
	}elsif($len<3000){
		$L = 80
	}elsif($len<4000){
		$L = 85
	}elsif($len<5000){
		$L = 90
	}else{
		$L = 100
	}

	if($raw_len < 0){
		"-$L";
	}else{
		$L;
	}
}


sub get_gap_len{
	my $len = shift;

	my $raw_len = $len;
	$len = abs $len;
	my $L;

	if($len == 0 ){
		$L = 0
	}elsif($len<10){
		$L = 5
	}elsif($len<30){
		$L = 9	
	}elsif($len<40){
		$L = 11	
	}elsif($len<50){
		$L = 13	
	}elsif($len<100){
		$L = 15
	}elsif($len<200){
		$L = 17
	}elsif($len<300){
		$L = 19
	}elsif($len<400){
		$L = 21
	}elsif($len<500){
		$L = 21
	}elsif($len<600){
		$L = 22
	}elsif($len<700){
		$L = 23
	}elsif($len<800){
		$L = 24
	}elsif($len<900){
		$L = 25
	}elsif($len<1000){
		$L = 30
	}elsif($len<2000){
		$L = 32
	}elsif($len<3000){
		$L = 34
	}elsif($len<4000){
		$L = 36
	}elsif($len<5000){
		$L = 38
	}else{
		$L = 40
	}

	if($raw_len < 0){
		"-$L";
	}else{
		$L;
	}
}


sub get_gene_info{
	my $region_info = shift;
	my $gene = shift;

	my $gene_info;
	
	for my $i(0..@$gene-1){

		my ($gene_name,$gene_start,$gene_end,$chain) = @{$gene->[$i]};
		
		#LSC1
		if( ($gene_start >= $region_info->{'LSC1'}->{'start'} and $gene_end <= $region_info->{'LSC1'}->{'end'}   ) or 
			($gene_start <  $region_info->{'LSC1'}->{'start'} and $gene_end >= $region_info->{'LSC1'}->{'start'} and $gene_end - $region_info->{'LSC1'}->{'start'} + 1 > $region_info->{'LSC1'}->{'start'} - $gene_start) or
			($gene_start <= $region_info->{'LSC1'}->{'end'}   and $gene_end >  $region_info->{'LSC1'}->{'end'} and $gene_end < $region_info->{'IRb'}->{'end'} and $gene_end - $region_info->{'LSC1'}->{'end'} < $region_info->{'LSC1'}->{'end'} - $gene_start + 1) )
		{
			push @{$gene_info->{'LSC1'}},$gene->[$i];
		}
		#IRb gene maybe only one or spanning this region
		elsif( ($gene_start >= $region_info->{'IRb'}{'start'} and $gene_end <= $region_info->{'IRb'}{'end'}   ) or
			   ($gene_start <  $region_info->{'IRb'}{'start'} and $gene_end >= $region_info->{'IRb'}{'start'} and  $gene_end - $region_info->{'IRb'}{'start'} + 1 >=  $region_info->{'IRb'}{'start'} - $gene_start and $gene_end < $region_info->{'SSC'}{'end'}) or 
			   ($gene_start <= $region_info->{'IRb'}{'end'}   and $gene_end > $region_info->{'IRb'}{'end'} and $gene_end - $region_info->{'IRb'}{'end'} <=  $region_info->{'IRb'}{'end'} - $gene_start + 1 and $gene_end < $region_info->{'SSC'}{'end'}) )
		{
			push @{$gene_info->{'IRb'}},$gene->[$i];
		}
		#SSC gene maybe only one or spanning this region
		elsif(($gene_start >= $region_info->{'SSC'}{'start'} and $gene_end <= $region_info->{'SSC'}{'end'}    ) or
			   ($gene_start <  $region_info->{'SSC'}{'start'} and $gene_end >= $region_info->{'SSC'}{'start'} and $gene_end - $region_info->{'SSC'}{'start'} + 1 > $region_info->{'SSC'}{'start'} - $gene_start and $gene_start >  $region_info->{'IRb'}{'start'} and $gene_end < $region_info->{'IRa'}{'end'}) or 
			   ($gene_start <= $region_info->{'SSC'}{'end'}   and $gene_end > $region_info->{'SSC'}{'end'} and $gene_end - $region_info->{'SSC'}{'end'} < $region_info->{'SSC'}{'end'} - $gene_start + 1 and $gene_start >  $region_info->{'IRb'}{'start'} and $gene_end < $region_info->{'IRa'}{'end'}) )
		{
			push @{$gene_info->{'SSC'}},$gene->[$i];
		}
		#IRa gene maybe only one or spanning this region
		elsif(($gene_start >= $region_info->{'IRa'}{'start'} and $gene_end <= $region_info->{'IRa'}{'end'}   ) or
			   ($gene_start <  $region_info->{'IRa'}{'start'} and $gene_end >= $region_info->{'IRa'}{'start'} and $gene_end - $region_info->{'IRa'}{'start'} + 1 >= $region_info->{'IRa'}{'start'} - $gene_start and $gene_start > $region_info->{'SSC'}{'start'} and $gene_end < $region_info->{'LSC2'}{'end'}) or 
			   ($gene_start <= $region_info->{'IRa'}{'end'}   and $gene_end > $region_info->{'IRa'}{'end'} and $gene_end - $region_info->{'IRa'}{'end'} <= $region_info->{'IRa'}{'end'} - $gene_start + 1 and $gene_start > $region_info->{'SSC'}{'start'} and $gene_end < $region_info->{'LSC2'}{'end'}) )
		{
			push @{$gene_info->{'IRa'}},$gene->[$i];
		}
		#LSC2
		elsif(($gene_start >= $region_info->{'LSC2'}{'start'} and $gene_end <= $region_info->{'LSC2'}{'end'}   ) or
			   ($gene_start <  $region_info->{'LSC2'}{'start'} and $gene_end >= $region_info->{'LSC2'}{'start'} and $gene_start > $region_info->{'IRa'}{'start'} and $gene_end - $region_info->{'LSC2'}{'start'} + 1 > $region_info->{'LSC2'}{'start'} - $gene_start) or 
			   ($gene_start <= $region_info->{'LSC2'}{'end'}   and $gene_end > $region_info->{'LSC2'}{'end'}    ) )
		{
			push @{$gene_info->{'LSC2'}},$gene->[$i];
		}
	}

	return $gene_info;
}


sub format_nu{
	my $nu = shift;
	my $re_nu = reverse $nu;
	my @re_nu = $re_nu =~ /(\d{1,3})/g;
	my $format_nu = reverse(join",",@re_nu);

	return $format_nu;

}


sub format_js_info{
	my $js_info = shift;
	my $genome_len = shift;

	my $region_info;
	my @pos = $js_info =~ /LSC:(\d+)-(\d+),IRb:(\d+)-(\d+),SSC:(\d+)-(\d+),IRa:(\d+)-(\d+)/;

#	my ($lsc_start,$lsc_end,$irb_start,$irb_end,$ssc_start,$ssc_end,$ira_start,$ira_end) = $js_info =~ /LSC:(\d+)-(\d+),IRb:(\d+)-(\d+),SSC:(\d+)-(\d+),IRa:(\d+)-(\d+)/;

	for my $i(1..$#pos){
		if($pos[$i] < $pos[$i-1]){
			$pos[$i] += $genome_len;
		}
	}

	$region_info->{'LSC1'}{'start'} = $pos[0];
	$region_info->{'LSC1'}{'end'} = $pos[1];
	$region_info->{'LSC'}{'length'} = $pos[1] - $pos[0] + 1;

	$region_info->{'LSC2'}{'start'} = $pos[0] + $genome_len;
	$region_info->{'LSC2'}{'end'} = $pos[1] + $genome_len;

	$region_info->{'IRb'}{'start'} = $pos[2];
	$region_info->{'IRb'}{'end'} = $pos[3];
	$region_info->{'IRb'}{'length'} = $pos[3] - $pos[2] + 1;

	$region_info->{'SSC'}{'start'} = $pos[4];
	$region_info->{'SSC'}{'end'} = $pos[5];
	$region_info->{'SSC'}{'length'} = $pos[5] - $pos[4] + 1;

	$region_info->{'IRa'}{'start'} = $pos[6];
	$region_info->{'IRa'}{'end'} = $pos[7];
	$region_info->{'IRa'}{'length'} = $pos[7] - $pos[6] + 1;
	
	$region_info->{'region'} = join",",@pos;;

	return $region_info;
}


sub get_js_pos{

	my $file = shift;
	
	my ($lsc,$irb,$ssc,$ira);

	for(`perl $Bin/../script/cp_Find_IR.pl -i $file`){
		chomp;

		if(/LSC/){
			$lsc = $_;
		}elsif(/IRb/){
			$irb = $_;
		}elsif(/IRa/){
			$ira = $_;
		}elsif(/SSC/){
			$ssc = $_;
		}
	}

	if($lsc and $irb and $ssc and $ira){
		return "$lsc,$irb,$ssc,$ira\n";
	}else{
		return 0;
	}
}


# &parse_genbank_file 
#	my $info = parse_genbank_file($gb_file);
#	return $for_info
#	$for_info->{'locus'}
#	$for_info->{'length'}
#	$for_info->{'organism'}
#	@{$for_info->{'gene'}} = ([$gene_name,$start,$end,$chain])
#	$for_info->{'seq'}
sub parse_genbank_file{

	my $file = shift;

	$/ = undef;
	
	open my $parse_file,"$file" or die "$file cannot open";

	my $info = <$parse_file>;

	$/ = "\n";

	unless($info =~ /^LOCUS\s+/){
		warn "\nWRONG: The file ($file) you entered is not in the correct genbank format\n";
		exit;
	}

	$info =~ s/,\n {21}/,/mg;
	$info =~ s/\n {21}\// \//mg;
	$info =~ s/\n {21}//mg;
	$info =~ s/\n {12}/ /mg;
	$info =~ s/^\s+//mg;

	$info =~ s/ORIGIN\s*\n\d+ /ORIGIN  /g;
	$info =~ s/\n\d+ //g;

	my @info = split/\n/,$info;

	my $for_info;
	
	$for_info->{'file'} = $file;

	my %has_exists_gene;

	for(@info){

		if(/^LOCUS\s+?(\S+)\s+?(\d+)\s+bp/){
			$for_info->{'locus'} = $1;

			unless($2){
				warn "ERROR: $file ,incorrect format in the first line: $_\n";
				exit;
			}
			$for_info->{'length'} = $2;
			next;
		}

		if(/^source\s+/){
			my ($organism) = /\/organism="(.*?)"/;
			$for_info->{'organism'} = $organism;
			next;
		}

		if(/^gene\s+/){

			next if($skip_pseudo_gene and /\/pseudo/ or /"pseudo/ or /note=.*fragment/);
			next if($skip_orf_gene and /orf/i);

			my ($pos_info) = (split)[1];
			my ($gene_name) = /\/gene="(.*?)"/;

			if(!$gene_name){
				warn "-file: $file : $pos_info has no '/gene=' tag, and has no gene name\n";
				if($skip_NA_gene){
					next;
				}
				$gene_name = "NA";
			}
			
			$gene_name =~ s/ .*//g;
			$gene_name =~ s/-.*//g;
			$gene_name =~ s/\(.*//g;

			$pos_info =~ s/order/join/;
			$pos_info =~ s/>|<//g;

			#geneious format

			if($pos_info =~ /complement/ and $pos_info =~ /join/){

				my @pos_info = split/,/,$pos_info;
				my $complement_nu = $pos_info =~ s/complement/complement/g;

				if(@pos_info == $complement_nu){
					for(@pos_info){
						s/join|complement|\(|\)//g
					}

					@pos_info = reverse @pos_info;
					$pos_info = "complement(join(".join(",",@pos_info).")";
				}
			}

			$pos_info =~ s/\.\.$for_info->{'length'},1\.\./../;	#spanning genes

			my @pos_info = (split/,/,$pos_info);

			if($pos_info =~ /complement\(join/){
				for(@pos_info){
					my ($start,$end) = /(\d+)\.\.(\d+)/;
					my $chain = 1;

					if($start > $end){	#spanning genes
						$end = $end + $for_info->{'length'};
					}

					push @{$for_info->{'gene'}},[$gene_name,$start,$end,$chain] unless($has_exists_gene{"$gene_name,$start,$end,$chain"});
					$has_exists_gene{"$gene_name,$start,$end,$chain"} = 1;
				
					my $new_start = $start+$for_info->{'length'};
					my $new_end = $end+$for_info->{'length'};

					push @{$for_info->{'gene'}},[$gene_name,$new_start,$new_end,$chain] unless($has_exists_gene{"$gene_name,$new_start,$new_end,$chain"});
					$has_exists_gene{"$gene_name,$new_start,$new_end,$chain"} = 1;

					$new_start = $start+$for_info->{'length'}*2;
					$new_end = $end+$for_info->{'length'}*2;

					push @{$for_info->{'gene'}},[$gene_name,$new_start,$new_end,$chain] unless($has_exists_gene{"$gene_name,$new_start,$new_end,$chain"});
					$has_exists_gene{"$gene_name,$new_start,$new_end,$chain"} = 1;
				}
			}else{
				for(@pos_info){
					my ($start,$end) = /(\d+)\.\.(\d+)/;
					my $chain = /complement/ ? 1 : 0;
					
					if($start > $end){	#spanning genes
						$end = $end + $for_info->{'length'};
					}

					push @{$for_info->{'gene'}},[$gene_name,$start,$end,$chain] unless($has_exists_gene{"$gene_name,$start,$end,$chain"});
					$has_exists_gene{"$gene_name,$start,$end,$chain"} = 1;

					my $new_start = $start+$for_info->{'length'};
					my $new_end = $end+$for_info->{'length'};

					push @{$for_info->{'gene'}},[$gene_name,$new_start,$new_end,$chain] unless($has_exists_gene{"$gene_name,$new_start,$new_end,$chain"});
					$has_exists_gene{"$gene_name,$new_start,$new_end,$chain"} = 1;

					$new_start = $start+$for_info->{'length'}*2;
					$new_end = $end+$for_info->{'length'}*2;

					push @{$for_info->{'gene'}},[$gene_name,$new_start,$new_end,$chain] unless($has_exists_gene{"$gene_name,$new_start,$new_end,$chain"});
					$has_exists_gene{"$gene_name,$new_start,$new_end,$chain"} = 1;
				}
			}

			next;
		}

		if(/ORIGIN/){
			my $seq = (split/\s+/,$_,2)[1];
			$seq =~ s/\d|\s//g;
			$seq = uc $seq;
			$for_info->{'seq'} = $seq;
		}
	}

	return $for_info;
}


sub get_string_len{
	my $string = shift;
	my $string_len;

	for(split//,$string){
		$string_len += $charwidths{$_};
	}
	return $string_len;
}

sub USAGE {         
	my $usage=<<"USAGE";				
Program: $0
Version: $version
Contact: xul<xul\@genepioneer.com> <1275875706\@qq.com>
Description: 

	Draw the junctions site of chloroplast genome.
	
Usage:
	1. perl $0 -i input.cfg file
	2. perl $0 -g file1.gb file2.gb file3.gb 

  Options:
	-i	<infile>	Input cfg file with two columns. 
			The first column is the file path and the second column is the region location.
			The region location must be in the following format: LSC:1-85855,IRb:85856-111284,SSC:111285-129051,IRa:129052-154480
			Regional positions can span the beginning and end of the genome.
			The contents of the file are as follows:

		path/MK036045.1.gbk	LSC:152045-85435,IRb:85436-110178,SSC:110179-127301,IRa:127302-152044
		path/MK267301.1.gbk	LSC:156436-84674,IRb:84675-112284,SSC:112285-128825,IRa:128826-156435
		path/MK397858.1.gbk	LSC:154523-85675,IRb:85676-111060,SSC:111061-129137,IRa:129138-154522
		path/MK397875.1.gbk	LSC:1-85855,IRb:85856-111284,SSC:111285-129051,IRa:129052-154480
		path/MK622380.1.gbk	LSC:1-85991,IRb:85992-112399,SSC:112400-131478,IRa:131479-157886
		path/MK817503.1.gbk	LSC:1-91540,IRb:91541-117733,SSC:117734-136982,IRa:136983-163175
		path/AM087200.3.gbk	LSC:5-85878,IRb:85879-111490,SSC:111491-129853,IRa:129854-4
		
	-g	<infiles>	Input genbank files, can be added after '-i'

	-b	back_ground_color, defaut: white
		Use RGB or hexadecimal color codes or simple color description definitions, such as
		"rgb(240,255,255)" or "#F0FFFF" or "white"

	-o	<output>	out.name(.svg)  default CPJSDRAW.svg

	-h				Help
USAGE
	print $usage;
	exit;
}
