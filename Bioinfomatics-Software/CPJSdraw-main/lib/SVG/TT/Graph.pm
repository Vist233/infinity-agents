package SVG::TT::Graph;

use strict;
use Carp;
use Template;
use POSIX;
require 5.6.1;

our $VERSION = '0.26';
our $AUTOLOAD;
our $TEMPLATE_FH;

=head1 NAME

SVG::TT::Graph - Base module for generating SVG graphics

=head1 SYNOPSIS

  package SVG::TT::Graph::GRAPH_TYPE;
  use SVG::TT::Graph;
  use base qw(SVG::TT::Graph);
  our $VERSION = $SVG::TT::Graph::VERSION;
  our $TEMPLATE_FH = \*DATA;

  sub _set_defaults {
    my $self = shift;

    my %default = (
        'keys'  => 'value',
    );
    while( my ($key,$value) = each %default ) {
      $self->{config}->{$key} = $value;
    }
  }


  # optional - called when object is created
  sub _init {
    my $self = shift;
  # any testing you want to do.

  }

  ...

  1;
  __DATA__
  <!-- SVG Template goes here  -->


  In your script:

  use SVG::TT::Graph::GRAPH_TYPE;

  my $width = '500',
  my $heigh = '300',
  my @fields = qw(field_1 field_2 field_3);

  my $graph = SVG::TT::Graph::GRAPH_TYPE->new({
    # Required for some graph types
    'fields'           => \@fields,
    # .. other config options
    'height' => '500',
  });

  my @data = qw(23 56 32);
  $graph->add_data({
    'data' => \@data,
    'title' => 'Sales 2002',
  });

  # find a config options value
  my $config_value = $graph->config_option();
  # set a config option value
  $graph->config_option($config_value);

  # All graphs support SVGZ (compressed SVG) if
  # Compress::Zlib is available. Use either the
  # 'compress' => 1 config option, or:
  $graph->compress(1);

  # All graph SVGs can be tidied if XML::Tidy
  # is installed. Use either the 'tidy' => 1
  # config option, or:
  $graph->tidy(1);

  print "Content-type: image/svg+xml\n\n";
  print $graph->burn();

=head1 DESCRIPTION

This package is a base module for creating graphs in Scalable Vector Format
(SVG). Do not use this module directly. Instead, use one of the following
modules to create the plot of your choice:

=over

=item L<SVG::TT::Graph::Line>

=item L<SVG::TT::Graph::Bar>

=item L<SVG::TT::Graph::BarHorizontal>

=item L<SVG::TT::Graph::BarLine>

=item L<SVG::TT::Graph::Pie>

=item L<SVG::TT::Graph::TimeSeries>

=item L<SVG::TT::Graph::XY>

=back

If XML::Tidy is installed, the SVG files generated can be tidied. If
Compress::Zlib is available, the SVG files can also be compressed to SVGZ.

=cut

sub new {
  my ($proto,$conf) = @_;
  my $class = ref($proto) || $proto;
  my $self = {};

  bless($self, $class);

  if($self->can('_set_defaults')) {
    # Populate with local defaults
    $self->_set_defaults();
  } else {
    croak "$class should have a _set_defaults method";
  }

  # overwrite defaults with user options
  while( my ($key,$value) = each %{$conf} ) {
    $self->{config}->{$key} = $value;
  }

  # Allow the inheriting modules to do checks
  if($self->can('_init')) {
    $self->_init();
  }

  return $self;
}

=head1 METHODS

=head2 add_data()

  my @data_sales_02 = qw(12 45 21);

  $graph->add_data({
    'data' => \@data_sales_02,
    'title' => 'Sales 2002',
  });

This method allows you do add data to the graph object.
It can be called several times to add more data sets in.

=cut

sub add_data {
  my ($self, $conf) = @_;
  # create an array
  unless(defined $self->{'data'}) {
    my @data;
    $self->{'data'} = \@data;
  }

  croak 'no fields array ref'
  unless defined $self->{'config'}->{'fields'}
    && ref($self->{'config'}->{'fields'}) eq 'ARRAY';

  if(defined $conf->{'data'} && ref($conf->{'data'}) eq 'ARRAY') {
    my %new_data;
    @new_data{ map { s/&/&amp;/; $_ } @{$self->{'config'}->{'fields'}}} = @{$conf->{'data'}};
    my %store = (
      'data' => \%new_data,
    );
    $store{'title'} = $conf->{'title'} if defined $conf->{'title'};
    push (@{$self->{'data'}},\%store);
    return 1;
  }
  return undef;
}

=head2 clear_data()

  my $graph->clear_data();

This method removes all data from the object so that you can
reuse it to create a new graph but with the same config options.

=cut

sub clear_data {
  my $self = shift;
  my @data;
  $self->{'data'} = \@data;
}


=head2 get_template()

  print $graph->get_template();

This method returns the TT template used for making the graph.

=cut

sub get_template {
  my $self = shift;

  # Template filehandle
  my $template_fh_sr = $self->_get_template_fh_sr();
  croak ref($self) . ' must have a template' if not $template_fh_sr;

  my $template_fh = $$template_fh_sr;

  # Read in TT template
  my $start = tell $template_fh;
  my $template = '';
  while(<$template_fh>) {
    chomp;
    $template .= $_ . "\n";
  }

  # This method may be used again, so return to start of filehandle
  seek $template_fh, $start, 0;

  return $template;
}

sub _get_template_fh_sr {
    my ($self) = @_;

    my $ns_ref = \%main::;
    for my $node ( split m<::>, ref $self ) {
        $ns_ref = $ns_ref->{"${node}::"};
    }

    return *{$ns_ref->{'TEMPLATE_FH'}}{'SCALAR'};
}

=head2 burn()

  print $graph->burn();

This method processes the template with the data and
config which has been set and returns the resulting SVG.

This method will croak unless at least one data set has
been added to the graph object.

=cut

sub burn {
  my $self = shift;

  # Check we have at least one data value
  croak "No data available"
    unless scalar(@{$self->{'data'}}) > 0;

  # perform any calculations prior to burn
  $self->calculations() if $self->can('calculations');

  my $template = $self->get_template();
  my %vals = (
    'data'             => $self->{'data'},     # the data
    'config'           => $self->{'config'},   # the configuration
    'calc'             => $self->{'calc'},     # the calculated values
    'sin'              => \&_sin_it,
    'cos'              => \&_cos_it,
    'predefined_color' => \&_predefined_color,
    'random_color'     => \&_random_color,
  );

  # euu - hack!! - maybe should just be a method
  $self->{sin} = \&_sin_it;
  $self->{cos} = \&_cos_it;

  # set up TT object
  my %config = (
    POST_CHOMP   => 1,
    INCLUDE_PATH => '/',
    #STRICT      => 1, # we should probably enable this for strict checking
    #DEBUG       => 'undef', # TT warnings on, useful for debugging, finding undef values
  );
  my $tt = Template->new( \%config );
  my $file;

  my $template_response = $tt->process( \$template, \%vals, \$file );
  if($tt->error()) {
    croak "Template error: " . $tt->error . "\n" if $tt->error;
  }

  # tidy SVG if required
  if ($self->tidy()) {
    if (eval "require XML::Tidy") {
      # remove the doctype tag temporarily because it seems to cause trouble
      $file =~ s/(<!doctype svg .+?>)//si;
      my $doctype = $1;
      # tidy
      my $tidy_obj = XML::Tidy->new( 'xml' => $file );
      $tidy_obj->tidy();
      $file = $tidy_obj->toString();
      # re-add the doctype
      if (defined $doctype) {
        $file =~ s/(<\?xml.+?\?>)/$1\n$doctype/si;
      }
      # even more tidy
      $file = $self->_tidy_more($file);
    } else {
      croak "Error tidying the SVG file: XML::Tidy does not seem to be installed properly";
    }
  }

  # compress SVG if required
  if ($self->compress()) {
    if (eval "require Compress::Zlib") {
      $file = Compress::Zlib::memGzip($file);
    } else {
      croak "Error compressing the SVG file: Compress::Zlib does not seem to be installed properly";
    }
  }

  return $file;
}



sub _sin_it {
  return sin(shift);
}


sub _cos_it {
  return cos(shift);
}


=head2 compress()

  $graph->compress(1);

If Compress::Zlib is installed, the content of the SVG file can be compressed.
This get/set method controls whether or not to compress. The default is 0 (off).

=cut

sub compress {
  my ($self, $val) = @_;
  # set the default compress value
  if (not defined $self->{config}->{compress}) {
    $self->{config}->{compress} = 0;
  }
  # set the user-defined compress value
  if (defined $val) {
    $self->{config}->{compress} = $val;
  }
  # get the compress value
  return $self->{config}->{compress};
}


=head2 tidy()

  $graph->tidy(1);

If XML::Tidy is installed, the content of the SVG file can be formatted in a
prettier way. This get/set method controls whether or not to tidy. The default
is 0 (off). The limitations of tidy are described at this URL:
L<http://search.cpan.org/~pip/XML-Tidy-1.12.B55J2qn/Tidy.pm#tidy%28%29>

=cut

sub tidy {
  my ($self, $val) = @_;
  # set the default tidy value
  if (not defined $self->{config}->{tidy}) {
    $self->{config}->{tidy} = 0;
  }
  # set the user-defined tidy value
  if (defined $val) {
    $self->{config}->{tidy} = $val;
  }
  # get the tidy value
  return $self->{config}->{tidy};
}


sub _tidy_more {
  # Remove extra spaces in the SVG <path> tag
  my ($self, $svg_string) = @_;
  while ($svg_string =~ s/(<path .*? )\s+(.*?"\s*?\/>)/$1$2/mgi) {};
  return $svg_string;
}


sub _random_color {
  # Generate the rgb code for a randomly selected color
  my $rgb = 'rgb('.int(rand(256)).','.int(rand(256)).','.int(rand(256)).')';
  return $rgb;
}


sub _predefined_color {
  # Get the hexadecimal code for one of 12 predefined colors
  my ($num) = shift;
  my @colors = ("#ff0000", "#0000ff", "#00ff00", "#ffcc00", "#00ccff",
    "#ff00ff", "#00ffff", "#ffff00", "#cc6666", "#663399", "#339900", "#9966FF");
  my $hex;
  if ($num-1 < scalar @colors) {
    $hex = $colors[$num-1];
  }
  return $hex;
}

# Calculate a scaling range and divisions to be aesthetically pleasing
# Parameters:
#   value range
# Returns
#   (revised range, division size, division precision)
sub _range_calc () {
  my ($self, $range) = @_;

  my ($max,$division);
  my $count = 0;
  my $value = $range;

  if ($value == 0) {
    # Can't do much really
    $division = 0.2;
    $max = 1;
    return ($max,$division,1);
  }

  if (($value < 1) and ($value > 0)) {
    while ($value < 1) {
      $value *= 10;
      $count++;
    }
    $division = 1;
    while ($count--) {
      $division /= 10;
    }
    $max = ceil($range / $division) * $division;
  }
  else {
    while ($value > 10) {
      $value /= 10;
      $count++;
    }
    $division = 1;
    while ($count--) {
      $division *= 10;
    }
    $max = ceil($range / $division) * $division;
  }

  if (int($max / $division) <= 2) {
    $division /= 5;
    $max = ceil($range / $division) * $division;
  }
  elsif (int($max / $division) <= 5) {
    $division /= 2;
    $max = ceil($range / $division) * $division;
  }

  if ($division >= 1) {
    $count = 0;
  }
  else {
    $count = length($division) - 2;
  }

  return ($max,$division,$count);
}


# Returns true if config value exists, is defined and not ''
sub _is_valid_config() {
  my ($self,$name) = @_;
  return ((exists $self->{config}->{$name}) && (defined $self->{config}->{$name}) && ($self->{config}->{$name} ne ''));
}


=head2 config methods

  my $value = $graph->method();
  $graph->method($value);

This object provides autoload methods for all config
options defined in the _set_default method within the
inheriting object.

See the SVG::TT::Graph::GRAPH_TYPE documentation for a list.

=cut

## AUTOLOAD FOR CONFIG editing

sub AUTOLOAD {
  my $name = $AUTOLOAD;
  $name =~ s/.*://;

  croak "No object supplied" unless $_[0];
  if(defined $_[0]->{'config'}->{$name}) {
    if(defined $_[1]) {
      # set the value
      $_[0]->{'config'}->{$name} = $_[1];
    }
    return $_[0]->{'config'}->{$name} if defined $_[0]->{'config'}->{$name};
    return undef;
  } else {
    croak "Method: $name can not be used with " . ref($_[0]);
  }
}


# As we have AUTOLOAD we need this
sub DESTROY {
}


1;
__END__

=head1 EXAMPLES

For examples look at the project home page http://leo.cuckoo.org/projects/SVG-TT-Graph/

=head1 EXPORT

None by default.

=head1 ACKNOWLEDGEMENTS

Thanks to Foxtons for letting us put this on CPAN, Todd Caine for heads up on
reparsing the template (but not using atm), David Meibusch for TimeSeries and a
load of other ideas, Stephen Morgan for creating the TT template and SVG, and
thanks for all the patches by Andrew Ruthven and others.

=head1 AUTHOR

Leo Lapworth <LLAP@cuckoo.org>

=head1 MAINTAINER

Florent Angly <florent.angly@gmail.com>

=head1 COPYRIGHT AND LICENSE

Copyright (C) 2003, Leo Lapworth

This module is free software; you can redistribute it or
modify it under the same terms as Perl itself.

=head1 SEE ALSO

L<SVG::TT::Graph::Line>,
L<SVG::TT::Graph::Bar>,
L<SVG::TT::Graph::BarHorizontal>,
L<SVG::TT::Graph::BarLine>,
L<SVG::TT::Graph::Pie>,
L<SVG::TT::Graph::TimeSeries>,
L<SVG::TT::Graph::XY>,
L<Compress::Zlib>,
L<XML::Tidy>

=cut
