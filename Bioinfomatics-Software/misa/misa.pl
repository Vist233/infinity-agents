#!/usr/bin/perl -w

###_______________________________________________________________________________
###
###Program name: misa.pl
###Authors:       Thomas Thiel, Sebastian Beier
###Release date: 25/08/20 (version 2.1)
###
###_______________________________________________________________________________
###
## _______________________________________________________________________________
##
## DESCRIPTION: Tool for the identification and localization of
##              (I)  perfect microsatellites as well as
##              (II) compound microsatellites (two individual microsatellites,
##                   disrupted by a certain number of bases)
##
## SYNTAX:   misa.pl <FASTA file>
##
##    <FASTAfile>    Single file in FASTA format containing the sequence(s).
##
##    In order to specify the search criteria, an additional file containing
##    the microsatellite search parameters is required named "misa.ini", which
##    has the following structure:
##      (a) Following a text string beginning with 'def', pairs of numbers are
##          expected, whereas the first number defines the unit size and the
##          second number the lower threshold of repeats for that specific unit.
##      (b) Following a text string beginning with 'int' a single number defines
##          the maximal number of bases between two adjacent microsatellites in
##          order to specify the compound microsatellite type.
##      (c) Following a text string beginning with 'GFF' a single string is expected
##          either 'true' or 'false' to indicate with optional GFF(v3) output
##          should be provided.
##    Example:
##      definition(unit_size,min_repeats):          1-10 2-6 3-5 4-5 5-5 6-5
##      interruptions(max_difference_for_2_SSRs):   100
##	    GFF:                                        true
##
## EXAMPLE: misa.pl seqs.fasta
##
## _______________________________________________________________________________
##

use POSIX;
my $version = "2.1";

my $loctime = localtime;
$loctime = strftime('%Y-%m-%d',localtime); ## outputs 2012-08-17

#§§§§§ DECLARATION §§§§§#

# Check for arguments. If none display syntax #

if (@ARGV == 0)
{
	open (IN,"<$0");
	while (<IN>) {if (/^\#\# (.*)/) {$message .= "$1\n"}};
	close (IN);
	die $message;
};

# Check if help is required #

if ($ARGV[0] =~ /-help/i)
{
	open (IN,"<$0");
	while (<IN>) {if (/^\#\#\#(.*)/) {$message .= "$1\n"}};
	close (IN);
	die $message;
};

# Open FASTA file #

open (IN,"<$ARGV[0]") || die ("\nError: FASTA file doesn't exist !\n\n");
#open (OUT,">$ARGV[0].misa");
#print OUT "ID\tSSR nr.\tSSR type\tSSR\tsize\tstart\tend\n";

# Reading arguments #

open (SPECS,"misa.ini") || die ("\nError: Specifications file doesn't exist !\n\n");
my %typrep;
my $amb = 0;
my $gff = 0;
while (<SPECS>)
{
	%typrep = $1 =~ /(\d+)/gi if (/^def\S*\s+(.*)/i);
	if (/^int\S*\s+(\d+)/i) {$amb = $1};
	if (/^GFF\S*\s+true/i) {$gff = 1};
};
my @typ = sort { $a <=> $b } keys %typrep;

if($gff){

}else{
	open (OUT,">$ARGV[0].misa");
	print OUT "ID\tSSR nr.\tSSR type\tSSR\tsize\tstart\tend\n";
}

#§§§§§ CORE §§§§§#

$/ = ">";
my $max_repeats = 1; #count repeats
my $min_repeats = 1000; #count repeats
my (%count_motif,%count_class); #count
my ($number_sequences,$size_sequences,%ssr_containing_seqs); #stores number and size of all sequences examined
my $ssr_in_compound = 0;
my ($id,$seq);
while (<IN>)
{
	next unless (($id,$seq) = /(.*?)\n(.*)/s);
	my ($nr,%start,@order,%end,%motif,%repeats,%len); # store info of all SSRs from each sequence
	$seq =~ s/[\d\s>]//g; #remove digits, spaces, line breaks,...
	if($gff){
		$id = (split(/\s/,$id))[0];
	}else{
		$id =~ s/^\s*//g; $id =~ s/\s*$//g;$id =~ s/\s/_/g; #replace whitespace with "_"
	}
	$number_sequences++;
	$size_sequences += length $seq;
	for ($i=0; $i < scalar(@typ); $i++) #check each motif class
	{
		my $motiflen = $typ[$i];
		my $minreps = $typrep{$typ[$i]} - 1;
		if ($min_repeats > $typrep{$typ[$i]}) {$min_repeats = $typrep{$typ[$i]}}; #count repeats
		my $search = "(([acgt]{$motiflen})\\2{$minreps,})";
		while ( $seq =~ /$search/ig ) #scan whole sequence for that class
		{
			my $motif = uc $2;
			my $redundant; #reject false type motifs [e.g. (TT)6 or (ACAC)5]
			for ($j = $motiflen - 1; $j > 0; $j--)
			{
				my $redmotif = "([ACGT]{$j})\\1{".($motiflen/$j-1)."}";
				$redundant = 1 if ( $motif =~ /$redmotif/ )
			};
			next if $redundant;
			$motif{++$nr} = $motif;
			my $ssr = uc $1;
			$repeats{$nr} = length($ssr) / $motiflen;
			$end{$nr} = pos($seq);
			$start{$nr} = $end{$nr} - length($ssr) + 1;
			$len{$nr} = length $seq;
			# count repeats
			$count_motifs{$motif{$nr}}++; #counts occurrence of individual motifs
			$motif{$nr}->{$repeats{$nr}}++; #counts occurrence of specific SSR in its appearing repeat
			$count_class{$typ[$i]}++; #counts occurrence in each motif class
			if ($max_repeats < $repeats{$nr}) {$max_repeats = $repeats{$nr}};
		};
	};
	next if (!$nr); #no SSRs
	$ssr_containing_seqs{$nr}++;
	@order = sort { $start{$a} <=> $start{$b} } keys %start; #put SSRs in right order
	$i = 0;
	my $count_seq; #counts
	my ($start,$end,$ssrseq,$ssrtype,$size,$len,$note);
	while ($i < $nr)
	{
		my $space = $amb + 1;
		if (!$order[$i+1]) #last or only SSR
		{
			$count_seq++;
			my $motiflen = length ($motif{$order[$i]});
			if($gff){
				if($motiflen == 1){
					$ssrtype = "monomeric_repeat";
					$note = "monomeric_repeat,";
				}else{
					$ssrtype = "microsatellite";
					if($motiflen == 2){
						$note="dinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 3){
						$note="trinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 4){
						$note="tetranucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen > 4){
						$note="microsatellite,";
					}
				}
			}else{
				$ssrtype = "p".$motiflen;
			}
			$ssrseq = "($motif{$order[$i]})$repeats{$order[$i]}";
			if($gff){
				$note.=$ssrseq;
			}
			$len = $len{$order[$i]};
			$start = $start{$order[$i]}; $end = $end{$order[$i++]};
			next
		};
		if (($start{$order[$i+1]} - $end{$order[$i]}) > $space)
		{
			$count_seq++;
			my $motiflen = length ($motif{$order[$i]});
			if($gff){
				if($motiflen == 1){
					$ssrtype = "monomeric_repeat";
					$note = "monomeric_repeat,";
				}else{
					$ssrtype = "microsatellite";
					if($motiflen == 2){
						$note="dinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 3){
						$note="trinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 4){
						$note="tetranucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen > 4){
						$note="microsatellite,";
					}
				}
			}else{
				$ssrtype = "p".$motiflen;
			}
			$ssrseq = "($motif{$order[$i]})$repeats{$order[$i]}";
			if($gff){
				$note.=$ssrseq;
			}
			$len = $len{$order[$i]};
			$start = $start{$order[$i]}; $end = $end{$order[$i++]};
			next
		};
		my ($interssr);
		if (($start{$order[$i+1]} - $end{$order[$i]}) < 1)
		{
			$count_seq++; $ssr_in_compound++;
			if($gff){
				$ssrtype = "repeat_region";
				$note = "repeat_region,";
				$len = $len{$order[$i]};
				my $motiflen = length ($motif{$order[$i]}); #motif1
				if($motiflen == 1){
					$note.="repeat_region,monomeric_repeat,";
				}elsif($motiflen == 2){
					$note="repeat_region,dinucleotide_repeat_microsatellite_feature,";
				}elsif($motiflen == 3){
					$note="repeat_region,trinucleotide_repeat_microsatellite_feature,";
				}elsif($motiflen == 4){
					$note="repeat_region,tetranucleotide_repeat_microsatellite_feature,";
				}elsif($motiflen > 4){
					$note="repeat_region,microsatellite,";
				}
				$ssrseq = "($motif{$order[$i]})$repeats{$order[$i]}";
				$note.="$ssrseq,";

				$motiflen = length ($motif{$order[$i+1]}); #motif2
				if($motiflen == 1){
					$note.="monomeric_repeat,";
				}elsif($motiflen == 2){
					$note.="dinucleotide_repeat_microsatellite_feature,";
				}elsif($motiflen == 3){
					$note.="trinucleotide_repeat_microsatellite_feature,";
				}elsif($motiflen == 4){
					$note.="tetranucleotide_repeat_microsatellite_feature,";
				}elsif($motiflen > 4){
					$note.="microsatellite,";
				}
				$ssrseq = "($motif{$order[$i+1]})$repeats{$order[$i+1]}";
				$note.=$ssrseq;
				$start = $start{$order[$i]}; $end = $end{$order[$i+1]}
			}else{
				$ssrtype = 'c*';
				$len = $len{$order[$i]};
				$part1 = substr($seq,$end{$order[$i]}-length($motif{$order[$i]}),length($motif{$order[$i]})-($end{$order[$i]}-$start{$order[$i+1]}+1));
				$rep1=$repeats{$order[$i]}-1;
				$overlap = substr($seq,$end{$order[$i]}-($end{$order[$i]}-$start{$order[$i+1]}+1),$end{$order[$i]}-$start{$order[$i+1]}+1);
				$part2 = substr($seq,$start{$order[$i+1]}+($end{$order[$i]}-$start{$order[$i+1]}),length($motif{$order[$i+1]})-($end{$order[$i]}-$start{$order[$i+1]}+1));
				$rep2=$repeats{$order[$i+1]}-1;
				$ssrseq = "($motif{$order[$i]})$rep1($part1<$overlap>$part2)($motif{$order[$i+1]})$rep2";
				#$ssrseq = "($motif{$order[$i]})$repeats{$order[$i]}($motif{$order[$i+1]})$repeats{$order[$i+1]}*";
				$start = $start{$order[$i]}; $end = $end{$order[$i+1]}
			}
		}
		else
		{
			$count_seq++; $ssr_in_compound++;
			if($gff){
				my $motiflen = length ($motif{$order[$i]}); #motif1
				$len = $len{$order[$i]};
				if($motiflen == 1){
					$ssrtype = "monomeric_repeat";
					$note = "compound_repeat,monomeric_repeat,";
				}else{
					$ssrtype = "microsatellite";
					if($motiflen == 2){
						$note="compound_repeat,dinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 3){
						$note="compound_repeat,trinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 4){
						$note="compound_repeat,tetranucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen > 4){
						$note="compound_repeat,microsatellite,";
					}
				}
				$ssrseq = "($motif{$order[$i]})$repeats{$order[$i]}";
				$note.="$ssrseq";
				$start = $start{$order[$i]};  $end = $end{$order[$i]};

				if($count_seq == 1){
					no warnings;
					if(tell(OUT) != -1){
						close(OUT);
					}
					use warnings;
					open (OUT,">$id.gff");
					print OUT "##gff-version 3\n";
					print OUT "##sequence-region $id 1 $len\n";
					print OUT "#!Date $loctime\n";
					print OUT "#!Type DNA\n";
					print OUT "#!Source-version MISA $version\n";
					print OUT "$id\tMISA\tregion\t1\t$len\t.\t.\t.\tID=$id",".1","\n";
				}
				print OUT "$id\tMISA\t$ssrtype\t$start\t$end\t.\t.\t.\tNote=$note;ID=$id",".",($count_seq+1),"\n";
				$count_seq++;
				$motiflen = length ($motif{$order[$i+1]}); #motif2
				if($motiflen == 1){
					$ssrtype = "monomeric_repeat";
					$note = "compound_repeat,monomeric_repeat,";
				}else{
					$ssrtype = "microsatellite";
					if($motiflen == 2){
						$note="compound_repeat,dinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 3){
						$note="compound_repeat,trinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 4){
						$note="compound_repeat,tetranucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen > 4){
						$note="compound_repeat,microsatellite,";
					}
				}
				$ssrseq = "($motif{$order[$i+1]})$repeats{$order[$i+1]}";
				$note.=$ssrseq;
				$start = $start{$order[$i+1]}; $end = $end{$order[$i+1]};

				if( ($start{$order[$i+1]} - $end{$order[$i]}) > 0){
					$interssr = lc substr($seq,$end{$order[$i]},($start{$order[$i+1]} - $end{$order[$i]}) - 1);
				}
				else
				{
					$interssr = lc substr($seq,$end{$order[$i]},0)
				}
				#$space -= length $interssr
			}else{	
				$interssr = lc substr($seq,$end{$order[$i]},($start{$order[$i+1]} - $end{$order[$i]}) - 1);
				$ssrseq = "($motif{$order[$i]})$repeats{$order[$i]}$interssr($motif{$order[$i+1]})$repeats{$order[$i+1]}";
				$ssrtype = 'c';
				$len = $len{$order[$i]};
				$start = $start{$order[$i]};  $end = $end{$order[$i+1]};
				#$space -= length $interssr
			}
		};
		while ($order[++$i + 1] and (($start{$order[$i+1]} - $end{$order[$i]}) <= $space))
		{
			if (($start{$order[$i+1]} - $end{$order[$i]})< 1)
			{
				$ssr_in_compound++;
				if($gff){
					$ssrtype="repeat_region";
					$note =~ s/compound_repeat/repeat_region/;
					$ssrseq ="($motif{$order[$i+1]})$repeats{$order[$i+1]}";
					$note .=",";
					$motiflen = length ($motif{$order[$i+1]}); #motif x
					if($motiflen == 1){
						$note.="monomeric_repeat,";
					}elsif($motiflen == 2){
						$note.="dinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 3){
						$note.="trinucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen == 4){
						$note.="tetranucleotide_repeat_microsatellite_feature,";
					}elsif($motiflen > 4){
						$note.="microsatellite,";
					}
					$note .= $ssrseq;
					$end = $end{$order[$i+1]}
				}else{
					$len = $len{$order[$i]};
					$ssrseq .= "($motif{$order[$i+1]})$repeats{$order[$i+1]}*";
					$ssrtype = 'c*';
					$end = $end{$order[$i+1]}
				}
			}
			else
			{
				$ssr_in_compound++;
				if($gff)
				{
					$len = $len{$order[$i]};
					if($count_seq == 1){
						if(tell(OUT) != -1){
							close(OUT);
						}
						use warnings;
						open (OUT,">$id.gff");
						print OUT "##gff-version 3\n";
						print OUT "##sequence-region $id 1 $len\n";
						print OUT "#!Date $loctime\n";
						print OUT "#!Type DNA\n";
						print OUT "#!Source-version MISA $version\n";
						print OUT "$id\tMISA\tregion\t1\t$len\t.\t.\t.\tID=$id",".1","\n";
					}
					print OUT "$id\tMISA\t$ssrtype\t$start\t$end\t.\t.\t.\tNote=$note;ID=$id",".",($count_seq+1),"\n";
					$count_seq++;

					$motiflen = length ($motif{$order[$i+1]}); #motif x
					if($motiflen == 1){
						$ssrtype = "monomeric_repeat";
						$note = "compound_repeat,monomeric_repeat,";
					}else{
						$ssrtype = "microsatellite";
						if($motiflen == 2){
							$note="compound_repeat,dinucleotide_repeat_microsatellite_feature,";
						}elsif($motiflen == 3){
							$note="compound_repeat,trinucleotide_repeat_microsatellite_feature,";
						}elsif($motiflen == 4){
							$note="compound_repeat,tetranucleotide_repeat_microsatellite_feature,";
						}elsif($motiflen > 4){
							$note="compound_repeat,microsatellite,";
						}
					}
					$ssrseq = "($motif{$order[$i+1]})$repeats{$order[$i+1]}";
					$note.=$ssrseq;
					$start = $start{$order[$i+1]}; $end = $end{$order[$i+1]};
					$interssr = lc substr($seq,$end{$order[$i]},($start{$order[$i+1]} - $end{$order[$i]}) - 1);
					
					
					#$space -= length $interssr
				}else{
					$len = $len{$order[$i]};
					$interssr = lc substr($seq,$end{$order[$i]},($start{$order[$i+1]} - $end{$order[$i]}) - 1);
					$ssrseq .= "$interssr($motif{$order[$i+1]})$repeats{$order[$i+1]}";
					$end = $end{$order[$i+1]};
					#$space -= length $interssr
				}
			}
		};
		$i++;
	}
	continue
	{
		if($gff){
			if($count_seq == 1){
				no warnings;
				if(tell(OUT) != -1){
					close(OUT);
				}
				use warnings;
				open (OUT,">$id.gff");
				print OUT "##gff-version 3\n";
				print OUT "##sequence-region $id 1 $len\n";
				print OUT "#!Date $loctime\n";
				print OUT "#!Type DNA\n";
				print OUT "#!Source-version MISA $version\n";
				print OUT "$id\tMISA\tregion\t1\t$len\t.\t.\t.\tID=$id",".1","\n";
				print OUT "$id\tMISA\t$ssrtype\t$start\t$end\t.\t.\t.\tNote=$note;ID=$id",".",($count_seq+1),"\n";
			}else{
				print OUT "$id\tMISA\t$ssrtype\t$start\t$end\t.\t.\t.\tNote=$note;ID=$id",".",($count_seq+1),"\n";
			}
		}else{
			print OUT "$id\t$count_seq\t$ssrtype\t$ssrseq\t",($end - $start + 1),"\t$start\t$end\n"
		}
	};
};

close (OUT);
open (OUT,">$ARGV[0].statistics");

#§§§§§ INFO §§§§§#

#§§§ Specifications §§§#
print OUT "Specifications\n==============\n\nSequence source file: \"$ARGV[0]\"\n\nDefinement of microsatellites (unit size / minimum number of repeats):\n";
for ($i = 0; $i < scalar (@typ); $i++) {print OUT "($typ[$i]/$typrep{$typ[$i]}) "};print OUT "\n";
if ($amb > 0) {print OUT "\nMaximal number of bases interrupting 2 SSRs in a compound microsatellite:  $amb\n"};
print OUT "\n\n\n";

#§§§ OCCURRENCE OF SSRs §§§#

#small calculations
my @ssr_containing_seqs = values %ssr_containing_seqs;
my $ssr_containing_seqs = 0;
for ($i = 0; $i < scalar (@ssr_containing_seqs); $i++) {$ssr_containing_seqs += $ssr_containing_seqs[$i]};
my @count_motifs = sort {length ($a) <=> length ($b) || $a cmp $b } keys %count_motifs;
my @count_class = sort { $a <=> $b } keys %count_class;
for ($i = 0; $i < scalar (@count_class); $i++) {$total += $count_class{$count_class[$i]}};

#§§§ Overview §§§#
print OUT "RESULTS OF MICROSATELLITE SEARCH\n================================\n\n";
print OUT "Total number of sequences examined:              $number_sequences\n";
print OUT "Total size of examined sequences (bp):           $size_sequences\n";
print OUT "Total number of identified SSRs:                 $total\n";
print OUT "Number of SSR containing sequences:              $ssr_containing_seqs\n";
print OUT "Number of sequences containing more than 1 SSR:  ",$ssr_containing_seqs - ($ssr_containing_seqs{1} || 0),"\n";
print OUT "Number of SSRs present in compound formation:    $ssr_in_compound\n\n\n";

#§§§ Frequency of SSR classes §§§#
print OUT "Distribution to different repeat type classes\n---------------------------------------------\n\n";
print OUT "Unit size\tNumber of SSRs\n";
my $total = undef;
for ($i = 0; $i < scalar (@count_class); $i++) {print OUT "$count_class[$i]\t$count_class{$count_class[$i]}\n"};
print OUT "\n";

#§§§ Frequency of SSRs: per motif and number of repeats §§§#
print OUT "Frequency of identified SSR motifs\n----------------------------------\n\nRepeats";
for ($i = $min_repeats;$i <= $max_repeats; $i++) {print OUT "\t$i"};
print OUT "\ttotal\n";
for ($i = 0; $i < scalar (@count_motifs); $i++)
{
	my $typ = length ($count_motifs[$i]);
	print OUT $count_motifs[$i];
	for ($j = $min_repeats; $j <= $max_repeats; $j++)
	{
		if ($j < $typrep{$typ}) {print OUT "\t-";next};
		if ($count_motifs[$i]->{$j}) {print OUT "\t$count_motifs[$i]->{$j}"} else {print OUT "\t"};
	};
	print OUT "\t$count_motifs{$count_motifs[$i]}\n";
};
print OUT "\n";

#§§§ Frequency of SSRs: summarizing redundant and reverse motifs §§§#
# Eliminates %count_motifs !
print OUT "Frequency of classified repeat types (considering sequence complementary)\n-------------------------------------------------------------------------\n\nRepeats";
my (%red_rev,@red_rev); # groups
for ($i = 0; $i < scalar (@count_motifs); $i++)
{
	next if ($count_motifs{$count_motifs[$i]} eq 'X');
	my (%group,@group,$red_rev); # store redundant/reverse motifs
	my $reverse_motif = $actual_motif = $actual_motif_a = $count_motifs[$i];
	$reverse_motif =~ tr/ACGT/TGCA/;
	$reverse_motif = reverse $reverse_motif;
	my $reverse_motif_a = $reverse_motif;
	for ($j = 0; $j < length ($count_motifs[$i]); $j++)
	{
		if ($count_motifs{$actual_motif}) {$group{$actual_motif} = "1"; $count_motifs{$actual_motif}='X'};
		if ($count_motifs{$reverse_motif}) {$group{$reverse_motif} = "1"; $count_motifs{$reverse_motif}='X'};
		$actual_motif =~ s/(.)(.*)/$2$1/;
		$reverse_motif =~ s/(.)(.*)/$2$1/;
		$actual_motif_a = $actual_motif if ($actual_motif lt $actual_motif_a);
		$reverse_motif_a = $reverse_motif if ($reverse_motif lt $reverse_motif_a)
	};
	if ($actual_motif_a lt $reverse_motif_a) {$red_rev = "$actual_motif_a/$reverse_motif_a"}
	else {$red_rev = "$reverse_motif_a/$actual_motif_a"}; # group name
	$red_rev{$red_rev}++;
	@group = keys %group;
	for ($j = 0; $j < scalar (@group); $j++)
	{
		for ($k = $min_repeats; $k <= $max_repeats; $k++)
		{
			if ($group[$j]->{$k}) {$red_rev->{"total"} += $group[$j]->{$k};$red_rev->{$k} += $group[$j]->{$k}}
		}
	}
};
for ($i = $min_repeats; $i <= $max_repeats; $i++) {print OUT "\t$i"};
print OUT "\ttotal\n";
@red_rev = sort {length ($a) <=> length ($b) || $a cmp $b } keys %red_rev;
for ($i = 0; $i < scalar (@red_rev); $i++)
{
	my $typ = (length ($red_rev[$i])-1)/2;
	print OUT $red_rev[$i];
	for ($j = $min_repeats; $j <= $max_repeats; $j++)
	{
		if ($j < $typrep{$typ}) {print OUT "\t-";next};
		if ($red_rev[$i]->{$j}) {print OUT "\t",$red_rev[$i]->{$j}}
		else {print OUT "\t"}
	};
	print OUT "\t",$red_rev[$i]->{"total"},"\n";
};

