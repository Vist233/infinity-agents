#!/usr/bin/perl
use strict;
use Getopt::Long;

my $program=`basename $0`; chomp $program;
my $usage=<<USAGE; #******* Instruction of this program *********#

Program: multi fasta cds 2222 aa.seq, then, multi alignments ######charge

Usage: $program  <cds.fas>                                 ######charge
        -s1     comput slidwindow  "n" or "y" ,n(defaut)
        -k1     width of seq window, 34aa (defaut)
        -k2     remove signal peptide, 0 aa (defaut)
    -k3     slid seq, 17aa (defaut)
    -help   output help information

USAGE

my %opts;
GetOptions(\%opts, "k1:i","k2:i","k3:i","s1:s","s2:s","so:s","help!");
die $usage if ( @ARGV==0 || defined($opts{"help"}));

#****************************************************************#
#--------------------Main-----Function-----Start-----------------#
#****************************************************************#


$opts{k1} = (defined $opts{k1}) ? $opts{k1} : 34;
$opts{k2} = (defined $opts{k2}) ? $opts{k2} : 0;
$opts{k3} = (defined $opts{k3}) ? $opts{k3} : 17;
$opts{s1} = (defined $opts{s1}) ? $opts{s1} : "n";
$opts{s2} = (defined $opts{s2}) ? $opts{s2} : "\t";
$opts{so} = (defined $opts{so}) ? $opts{so} : "\t";


open (F1, "<", $ARGV[0]) || die "can't open inseq1";
my @name1;
my @seq1;
my $n=0;
while (<F1>) {
        chomp;
        $_=~s/\s+//g;
        if (/^>/) {
                $name1[$n]=$_;
        $n++;
        }
    else {
                $seq1[$n-1].=$_;
        }
}
close F1;

my $seqLen = (length $seq1[1])/3;
if ((length $seq1[0])%3 != 0) {
        print "$seqLen\n$name1[0]\n$seq1[0]\n";
    die "seq is not divided by 3";
}
my $m=0;
my $x=0;
my @seq3=@seq1;
my $nn;
my $mm;

open (F4, ">", "$ARGV[0]_kaks_seq");
for $n(0..$#name1) {
        for $m(0..$#name1) {
                if ($n>$m) {
                        $nn=substr($seq3[$n],$opts{k2}*3);
                        $mm=substr($seq3[$m],$opts{k2}*3);
                        print F4 "$name1[$n]_vs_$name1[$m]\n$nn\n$mm\n\n";
                }
        }
}
close F4;
`./KaKs_Calculator2-1.0/bin/Linux/./KaKs_Calculator -i "$ARGV[0]_kaks_seq" -o "kaks_$ARGV[0]_kaks_seq" -m YN `;

if ($opts{s1} eq "y") {

open (F5, ">", "$ARGV[0]_kaks_seq_$opts{k1}");
for $n(0..$#name1) {
        for $m(0..$#name1) {
          for $x(0..($seqLen-$opts{k1})/$opts{k3}) {
                if ($n>$m) {
                        my $kaks1=substr($seq3[$n],$x*$opts{k3}*3,$opts{k1}*3);
                        my $kaks2=substr($seq3[$m],$x*$opts{k3}*3,$opts{k1}*3);
                        if ($kaks1=~/A|T|G|C/i && $kaks2=~/A|T|G|C/i) {
                        print F5 "$name1[$n]_vs_$name1[$m]**$x*$opts{k1}\n$kaks1\n$kaks2\n\n";
print "$x\t$seqLen\t$opts{k3}\t$opts{k1}\n";
                        }
                }
          }
        }
}
close F5;
`./KaKs_Calculator2-1.0/bin/Linux/./KaKs_Calculator  -i "$ARGV[0]_kaks_seq_$opts{k1}" -o "kaks_$ARGV[0]_kaks_seq_$opts{k1}" -m YN `;
}