#!/usr/bin/env perl
use warnings;
use strict;

use FindBin qw/$Bin/;
use Cwd 'abs_path';

if(@ARGV and -f $ARGV[0]){
	for my $file(@ARGV){
		if(-f $file){
			
			my $realpath = abs_path $file;
			my ($lsc,$irb,$ssc,$ira);

			for(`perl $Bin/cp_Find_IR.pl -i $file`){
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
				print "$realpath\t$lsc,$irb,$ssc,$ira\n";
			}else{
				warn "$realpath not have IR\n";
			}

		}else{
			warn "$file is not file\n";
		}
	}
	
}else{
	warn "\n\tusage: perl $0 file1.gb file2.gb ... > input.cfg\n";
}
