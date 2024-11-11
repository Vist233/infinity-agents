package SVG::TT::Graph::HeatMap;

use Modern::Perl;
use Carp;
use Data::Dumper;
use SVG::TT::Graph;
use base qw(SVG::TT::Graph);

our $VERSION     = $SVG::TT::Graph::VERSION;
our $TEMPLATE_FH = \*DATA;


=head1 NAME

SVG::TT::Graph::HeatMap - Create presentation quality SVG HeatMap graph of XYZ data points easily

=head1 SYNOPSIS

  use SVG::TT::Graph::HeatMap;

  my @data_cpu = (
                   {  x        => x_point1,
                      y_point1 => 10,
                      y_point2 => 200,
                      y_point3 => 1000,
                   },
                   {  x        => x_point2,
                      y_point1 => 100,
                      y_point2 => 400,
                      y_point3 => 500,
                   },
                   {  x        => x_point3,
                      y_point1 => 1000,
                      y_point2 => 600,
                      y_point3 => 0,
                   },
                 );

  my $graph = SVG::TT::Graph::HeatMap->new(
                                            { block_height => 24,
                                              block_width  => 24,
                                              gutter_width => 1,
                                            } );

  $graph->add_data(
                    { 'data'  => \@data_cpu,
                      'title' => 'CPU',
                    } );

  print "Content-type: image/svg+xml\n\n";
  print $graph->burn();

=head1 DESCRIPTION

This object aims to allow you to easily create high quality
SVG HeatMap graphs of XYZ data. You can either use the default style sheet
or supply your own. 

Please note, the height and width of the final image is computed from the 
size of the labels, block_height/block_with and gutter_size.

=head1 METHODS

=head2 new()

  use SVG::TT::Graph::HeatMap;

  my $graph = SVG::TT::Graph::HeatMap->new({

    # Optional - defaults shown
    block_height => 24,
    block_width  => 24,
    gutter_width => 1,

    'y_axis_order' => [],
  });

The constructor takes a hash reference with values defaulted to those
shown above - with the exception of style_sheet which defaults
to using the internal style sheet.

=head2 add_data()

  my @data_cpu = (
                   {  x        => x_point1,
                      y_point1 => 10,
                      y_point2 => 200,
                      y_point3 => 1000,
                   },
                   {  x        => x_point2,
                      y_point1 => 100,
                      y_point2 => 400,
                      y_point3 => 500,
                   },
                   {  x        => x_point3,
                      y_point1 => 1000,
                      y_point2 => 600,
                      y_point3 => 0,
                   },
                 );
  or

   my @data_cpu = ( ['x',        'y_point1', 'y_point2', 'y_point3'],
                 ['x_point1', 10,         200,        5],
                 ['x_point2', 100,        400,        1000],
                 ['x_point3', 1000,       600,        0],
               );

  $graph->add_data({
    'data' => \@data_cpu,
    'title' => 'CPU',
  });

This method allows you to add data to the graph object.  The
data are expected to be either a array of hashes or as a 2D 
matrix (array of arrays), with the Y-axis as the first arrayref, 
and the X-axis values in the first element of subsequent arrayrefs.

=head2 clear_data()

  my $graph->clear_data();

This method removes all data from the object so that you can
reuse it to create a new graph but with the same config options.

=head2 burn()

  print $graph->burn();

This method processes the template with the data and
config which has been set and returns the resulting SVG.

This method will croak unless at least one data set has
been added to the graph object.

=head2 config methods

  my $value = $graph->method();
  my $confirmed_new_value = $graph->method($value);

The following is a list of the methods which are available
to change the config of the graph object after it has been
created.

=over 4


=item compress()

Whether or not to compress the content of the SVG file (Compress::Zlib required).

=item tidy()

Whether or not to tidy the content of the SVG file (XML::Tidy required).

=item block_width()

The width of the blocks in px.

=item block_height()

The height of the blocks in px.

=item gutter()

The space between the blocks in px.

=item y_axis_order()

 This is order the columns are presented on the y-axis, if the data is in a Array of hashes,
 this has to be set, however is the data is in an 2D matrix (array of arrays), it will use
 the order presented in the header array. 

 If the data is given in a 2D matrix, and the y_axis_order is set, the y_axis_order will take 
 prescience.

=back

=head1 EXAMPLES

For examples look at the project home page
http://leo.cuckoo.org/projects/SVG-TT-Graph/

=head1 EXPORT

None by default.

=head1 SEE ALSO

L<SVG::TT::Graph>,
L<SVG::TT::Graph::Line>,
L<SVG::TT::Graph::Bar>,
L<SVG::TT::Graph::BarHorizontal>,
L<SVG::TT::Graph::BarLine>,
L<SVG::TT::Graph::Pie>,
L<SVG::TT::Graph::Bubble>,
L<Compress::Zlib>,
L<XML::Tidy>

=cut

sub _init
{
    my $self = shift;
}

sub _set_defaults
{
    my $self = shift;

    my @fields = ();

    my %default = (
        'fields' => \@fields,

        'block_width'  => 24,
        'block_height' => 24,
        'gutter'       => 1,

        'y_axis_order' => [],
                  );

    while ( my ( $key, $value ) = each %default )
    {
        $self->{ config }->{ $key } = $value;
    }
}

# override this so we can pre-manipulate the data
sub add_data
{
    my ( $self, $conf ) = @_;

    croak 'no data provided'
      unless ( defined $conf->{ 'data' } &&
               ref( $conf->{ 'data' } ) eq 'ARRAY' );

    # create an array
    unless ( defined $self->{ 'data' } )
    {
        my @data;
        $self->{ 'data' } = \@data;
    }
    else
    {
        croak 'There can only be a single piece of data';
    }

    # If there is an order this takes prescience and all data points should have this
    # however if there are

    my %check;
    if ( 0 == scalar @{ $self->{ config }->{ y_axis_order } } )
    {
        if ( ref( $conf->{ 'data' }->[0] ) eq 'ARRAY' )
        {
            my @header = @{ $conf->{ 'data' }->[0] };
            $self->{ config }->{ y_axis_order } = [@header[1 .. $#header]];
        }
    }
    %check = map {$_, 1} @{ $self->{ config }->{ y_axis_order } };
    croak
      'The Data needs to have either a y_axis_order or a header array in the data'
      if 0 == scalar keys %check;

    # convert to sorted (by ascending numeric value) array of [ x, y ]
    my @new_data = ();
    my ( $i, $x );

    $i = ref( $conf->{ 'data' }->[0] ) eq 'ARRAY' ? 1 : 0;
    my $max = scalar @{ $conf->{ 'data' } };
    while ( $i < $max )
    {
        my %row;
        if ( ref( $conf->{ 'data' }->[$i] ) eq 'ARRAY' )
        {
            $row{ x } = $conf->{ 'data' }->[$i]->[0];
            for my $col ( 1 .. $#{ $conf->{ 'data' }->[$i] } )
            {
                $row{ $conf->{ 'data' }->[0]->[$col] } =
                  $self->colourDecide( $conf->{ 'data' }->[$i]->[$col] )

                  #$conf->{ 'data' }->[$i]->[$col];
            }
        }
        elsif ( ref( $conf->{ 'data' }->[$i] ) eq 'HASH' )
        {
            # check the hash to make sure make sure the data is in it
            croak "row '$i' has no x value"
              unless defined $conf->{ 'data' }->[$i]->{ x };
            $row{ x } = $conf->{ 'data' }->[$i]->{ x };
            while ( my ( $k, $v ) = each %check )
            {
                unless ( defined $conf->{ 'data' }->[$i]->{ $k } )
                {
                    croak "zzz '$row{ x }' does not have a '$k' vaule"
                      unless ( $self->{ config }->{ include_undef_values } );
                }
                $row{ $k } =
                  $self->colourDecide( $conf->{ 'data' }->[$i]->{ $k } );
            }
        }
        else
        {
            croak
              'Data needs to be in an Array of Arrays or an Array of Hashes ';
        }
        push @new_data, \%row;
        $i++;
    }

    my %store = ( 'pairs' => \@new_data, );

    $store{ 'title' } = $conf->{ 'title' } if defined $conf->{ 'title' };
    push( @{ $self->{ 'data' } }, \%store );

    return 1;
}

# override calculations to set a few calculated values, mainly for scaling
sub calculations
{
    my $self = shift;

    # run through the data and calculate maximum and minimum values
    my ( $max_key_size, $max_x, $min_x, $max_y, $min_y, $max_x_label_length,
         $x_label, $max_y_label_length );

    my @y_axis_order = @{ $self->{ config }->{ y_axis_order } };
    for my $y_axis_label (@y_axis_order)
    {
        $max_y_label_length = length $y_axis_label
          if ( ( !defined $max_y_label_length ) ||
               ( $max_y_label_length < length $y_axis_label ) );
    }
    foreach my $dataset ( @{ $self->{ data } } )
    {
        $max_key_size = length( $dataset->{ title } )
          if ( ( !defined $max_key_size ) ||
               ( $max_key_size < length( $dataset->{ title } ) ) );
        $max_x = scalar @{ $dataset->{ pairs } }
          if ( ( !defined $max_x ) ||
               ( $max_x < scalar @{ $dataset->{ pairs } } ) );
        foreach my $pair ( @{ $dataset->{ pairs } } )
        {
            $min_x = 0;

            $max_y = scalar @y_axis_order;

            for my $y_vaules (@y_axis_order)
            {
                $min_y = 0;
            }
            $x_label            = $pair->{ x };
            $max_x_label_length = length($x_label)
              if ( ( !defined $max_x_label_length ) ||
                   ( $max_x_label_length < length($x_label) ) );
        }
    }

    $self->{ calc }->{ max_key_size }       = $max_key_size;
    $self->{ calc }->{ max_x }              = $max_x;
    $self->{ calc }->{ min_x }              = $min_x;
    $self->{ calc }->{ max_y }              = $max_y;
    $self->{ calc }->{ min_y }              = $min_y;
    $self->{ calc }->{ max_x_label_length } = $max_x_label_length;
    $self->{ calc }->{ max_y_label_length } = $max_y_label_length;
    $self->{ config }->{ width } =
      ( 10 * 2 ) + ( $max_y_label_length * 8 ) + 1 + (
                                       $max_x * (
                                           $self->{ config }->{ block_width } +
                                             $self->{ config }->{ gutter_width }
                                       ) );
    $self->{ config }->{ height } =
      ( 10 * 2 ) + ( $max_x_label_length * 8 ) + 1 + (
                                       $max_y * (
                                           $self->{ config }->{ block_width } +
                                             $self->{ config }->{ gutter_width }
                                       ) );

}

sub defaultColours
{
    my ($self) = @_;

    my %default = (
                    '<=' => { 1000 => [0,   0,   255],
                              900  => [4,   150, 252],
                              800  => [4,   218, 252],
                              700  => [4,   200, 100],
                              600  => [36,  225, 36],
                              500  => [132, 255, 14],
                              400  => [244, 254, 4],
                              300  => [252, 190, 4],
                              200  => [252, 125, 4],
                              100  => [252, 2,   4],
                            },
                    '=' => { 0  => [0, 0, 0],
                             -1 => [0, 0, 0],
                             -2 => [0, 0, 0],
                             -3 => [0, 0, 0],
                             -4 => [0, 0, 0],
                           } );


    return %default;
}

sub colourDecide
{
    my ( $self, $score ) = @_;

    my %key = $self->defaultColours;

    # return the default missing colour if the score is undef
    return 'rgb(255,255,255)' unless defined $score;


    my @precidence = qw(< <= > >= = );

    my %tests = ( '<'  => sub {return 1, if $_[0] < $_[1]},
                  '<=' => sub {return 1, if $_[0] <= $_[1]},
                  '>'  => sub {return 1, if $_[0] > $_[1]},
                  '>=' => sub {return 1, if $_[0] >= $_[1]},
                  '='  => sub {return 1, if $_[0] == $_[1]},
                );

    # set this to the default so if there are no rule matches
    # we just use the default
    my $colour = [0, 0, 0];

    for my $symbol (@precidence)
    {
        next unless exists $key{ $symbol };

        my @values = sort {$b <=> $a} keys %{ $key{ $symbol } };

        # if we are looking for the highest we flip the order
        @values = reverse @values if ( $symbol =~ /^>/ );
        for my $value (@values)
        {
            if ( $tests{ $symbol }( $score, $value ) )
            {
                $colour = $key{ $symbol }{ $value };
            }
        }
    }
    return sprintf "rgb(%s,%s,%s)", @$colour;
}

1;
__DATA__
<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"
  "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">

[% stylesheet = 'included' %]

[% IF config.style_sheet && config.style_sheet != '' %]
  <?xml-stylesheet href="[% config.style_sheet %]" type="text/css"?>
[% ELSE %]
  [% stylesheet = 'excluded' %]
[% END %]

<svg width="[% config.width %]" height="[% config.height %]" viewBox="0 0 [% config.width %] [% config.height %]" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">

<!-- \\\\\\\\\\\\\\\\\\\\\\\\\\\\  -->
<!-- Created with SVG::TT::Graph   -->
<!-- Dave Meibusch                 -->
<!-- ////////////////////////////  -->

[% IF stylesheet == 'excluded' %]
[%# include default stylesheet if none specified %]
<defs>
<style type="text/css">
<![CDATA[
/* Copy from here for external style sheet */
.svgBackground{
  fill:#f0f0f0;
}
.graphBackground{
  fill:#fafafa;
}

/* graphs titles */
.mainTitle{
  text-anchor: middle;
  fill: #000000;
  font-size: 14px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}
.subTitle{
  text-anchor: middle;
  fill: #999999;
  font-size: 12px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}

.axis{
  stroke: #000000;
  stroke-width: 1px;
}

.guideLines{
  stroke: #666666;
  stroke-width: 1px;
  stroke-dasharray: 5 5;
}

.xAxisLabels{
  text-anchor: middle;
  fill: #000000;
  font-size: 12px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}

.yAxisLabels{
  text-anchor: end;
  fill: #000000;
  font-size: 12px;
  font-family: "Lucida Console", Monaco, monospace;
  font-weight: normal;
}

.xAxisTitle{
  text-anchor: middle;
  fill: #ff0000;
  font-size: 14px;
  font-family: "Lucida Console", Monaco, monospace;
  font-weight: normal;
}

.yAxisTitle{
  fill: #ff0000;
  text-anchor: middle;
  font-size: 14px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}

.dataPointLabel{
  fill: #000000;
  text-anchor:middle;
  font-size: 10px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}
.staggerGuideLine{
  fill: none;
  stroke: #000000;
  stroke-width: 0.5px;
}

[% FOREACH dataset = data %]
  [% color = '' %]
  [% IF config.random_colors %]
    [% color = random_color() %]
  [% ELSE %]
    [% color = predefined_color(loop.count) %]
  [% END %]

  .fill[% loop.count %]{
    fill: [% color %];
    fill-opacity: 0.2;
    stroke: none;
  }

  .line[% loop.count %]{
    fill: none;
    stroke: [% color %];
    stroke-width: 1px;
  }

  .key[% loop.count %],.fill[% loop.count %]{
    fill: [% color %];
    stroke: none;
    stroke-width: 1px;
  }

  [% LAST IF (config.random_colors == 0 && loop.count == 12) %]
[% END %]

.keyText{
  fill: #000000;
  text-anchor:start;
  font-size: 10px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}
/* End copy for external style sheet */
]]>
</style>
</defs>
[% END %]

[% IF config.key %]
  <!-- Script to toggle paths when their key is clicked on -->
  <script language="JavaScript"><![CDATA[
  function togglePath( series ) {
    var path    = document.getElementById('groupDataSeries' + series);
    var points  = document.getElementById('groupDataLabels' + series);
    var current = path.getAttribute('opacity');
    if ( path.getAttribute('opacity') == 0 ) {
      path.setAttribute('opacity',1);
      points.setAttribute('opacity',1);
    } else {
      path.setAttribute('opacity',0);
      points.setAttribute('opacity',0);
    }
  }
  ]]></script>
[% END %]

<!-- svg bg -->
<rect x="0" y="0" width="[% config.width %]" height="[% config.height %]" class="svgBackground"/>

<!-- ///////////////// CALCULATE GRAPH AREA AND BOUNDARIES //////////////// -->
[%# get dimensions of actual graph area (NOT SVG area) %]
[% w = config.width %]
[% h = config.height %]

[%# set start/default coords of graph %]
[% x = 0 %]
[% y = 0 %]

[% char_width = 8 %]
[% half_char_height = 2.5 %]

<!-- min_y [% calc.min_y %] max_y [% calc.max_y %] min_x [% calc.min_x %] max_x [% calc.max_x %] -->

[%# reduce height and width of graph area for padding %]
[% h = h - 20 %]
[% w = w - 20 %]
[% x = x + 10 %]
[% y = y + 10 %]

[% max_x_label_char =  calc.max_x_label_length * char_width  %]
[% max_y_label_char =  calc.max_y_label_length * char_width  %]

[% w = w - max_y_label_char %]
[% x = x + max_y_label_char %]

[% h = h - max_x_label_char %]
[%# y = y + max_x_label_char %]
<!-- max_x_label_char [% calc.max_x_label_length %] max_y_label_char  [% calc.max_y_label_length %] -->



<!-- //////////////////////////////  BUILD GRAPH AREA ////////////////////////////// -->
[%# graph bg and clipping regions for lines/fill and clip extended to included data labels %]
<rect x="[% x %]" y="[% y %]" width="[% w %]" height="[% h %]" class="graphBackground"/>

[% base_line = h + y %]

<!-- axis -->
<path d="M[% x %] [% y %] v[% h %]" class="axis" id="xAxis"/>
<path d="M[% x %] [% base_line %] h[% w %]" class="axis" id="yAxis"/>

<!-- x axis labels -->

[%# TODO  %]

<!-- y axis labels -->


[%# TODO  %]


<g id="groupData" class="data">
[% FOREACH dataset = data.reverse %]
  <g id="groupDataSeries[% line %]" class="dataSeries[% line %]" clip-path="url(#clipGraphArea)">
    [% xx = 0 %]
    [% yy = 0 %]
    [% FOREACH y_data = config.y_axis_order %]
    <text
    x="[% max_y_label_char %]"
    y="[% (base_line - 1 ) - (yy * (config.block_height + config.gutter_width)) - config.block_height / 3     %]"
    class="yAxisLabels">
    [% y_data %]
    </text>      
        [% yy = yy + 1 %]
    [% END %]
    [% FOREACH pair = dataset.pairs %]
    [% yy = 0 %]
    [% block_start_x = x + 1 + (xx * (config.block_width + config.gutter_width))  %]
        [% IF config.debug %]
        <circle
        cx="[% block_start_x + (config.block_width / 2 )   %]"
        cy="[% (base_line + 5)   %]"
        r="2" fill="red" />
        [% END %]
        [% textx =  block_start_x   %]
        [% texty =  (base_line + 1)     %]
        <text
        x="[% textx   %]"
        y="[% texty   %]"
        transform="rotate(90 [% textx %],[% texty  %]) translate([% (pair.x.length + 1) * 4    %], [% (config.block_height - config.gutter_width) / -3  %])"
        class="xAxisLabels">[% pair.x %]</text>
        
        [% FOREACH y_data = config.y_axis_order %]
        
        <rect
        x="[% block_start_x   %]"
        y="[% (base_line - 1 - config.block_height) - (yy * (config.block_height + config.gutter_width))   %]"
        width="[% config.block_width  %]"
        height="[% config.block_height  %]" style="fill:[% pair.$y_data  %]" />
        <!-- [% y_data %] -z- [% pair.$y_data %] -->
        [% yy = yy + 1 %]
        [% END %]
    [% xx = xx + 1 %]
    [% END %]
  [% END %]
  </g>
</g>

[% IF config.debug %]
<circle cx="[% x %]" cy="[% base_line %]" r="1" stroke="black" stroke-width="1" fill="red" />
[% END %]



</svg>
