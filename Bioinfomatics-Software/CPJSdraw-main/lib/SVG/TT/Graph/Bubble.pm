package SVG::TT::Graph::Bubble;

use strict;
use Carp;
use SVG::TT::Graph;
use base qw(SVG::TT::Graph);

our $VERSION     = $SVG::TT::Graph::VERSION;
our $TEMPLATE_FH = \*DATA;


=head1 NAME

SVG::TT::Graph::Bubble - Create presentation quality SVG Bubble plot

=head1 SYNOPSIS

use SVG::TT::Graph::Bubble;

my @data = ( 2, 15, 18.10, 6, 19, 0.10, 12, 17, 12.92, 17, 10, 17.97 );

my $graph = SVG::TT::Graph::Bubble->new( { 'height' => '500',
                                           'width'  => '300',
                                         } );

$graph->add_data( { 'data'  => \@data_cpu,
                    'title' => 'CPU',
                  } );


print "Content-type: image/svg+xml\n\n";
print $graph->burn();

=head1 DESCRIPTION

This object aims to allow you to easily create high quality
SVG Bubble plot graphs using xyz data. You can either use the default style sheet
or supply your own. Either way there are many options which can
be configured to give you control over how the graph is
generated - with or without a key, data elements at each point,
title, subtitle etc.

=head1 METHODS

=head2 new()

  use SVG::TT::Graph::Bubble;

  my $graph = SVG::TT::Graph::Bubble->new({

    # Optional - defaults shown
    'height'              => 500,
    'width'               => 300,

    'show_y_labels'       => 1,
    'yscale_divisions'    => '',
    'min_yscale_value'    => 0,
    'max_yscale_value'    => '',

    'show_x_labels'       => 1,
    'xscale_divisions'    => '',
    'min_xscale_value'    => '',
    'max_xscale_value'    => '',
    'stagger_x_labels'    => 0,
    'rotate_x_labels'     => 0,
    'y_label_formatter'   => sub { return @_ },
    'x_label_formatter'   => sub { return @_ },

    'show_data_values'    => 1,
    'rollover_values'     => 0,

    'area_fill'           => 0,

    'show_x_title'        => 0,
    'x_title'             => 'X Field names',

    'show_y_title'        => 0,
    'y_title'             => 'Y Scale',

    'show_graph_title'    => 0,
    'graph_title'         => 'Graph Title',
    'show_graph_subtitle' => 0,
    'graph_subtitle'      => 'Graph Sub Title',
    'key'                 => 0,
    'key_position'        => 'right',

    # Stylesheet defaults
    'style_sheet'         => '/includes/graph.css', # internal stylesheet
    'random_colors'       => 0,
    'bubble_fill'   => 0.4,
    'bubble_border_stroke'   => 0,
  });

The constructor takes a hash reference with values defaulted to those
shown above - with the exception of style_sheet which defaults
to using the internal style sheet.

=head2 add_data()

  my @data = ( 2,  15, 18.10, 
               6,  19, 0.10, 
               12, 17, 12.92, 
               17, 10, 17.97 );
  or
  my @data = ( [2, 15, 18.10] , [6, 19, 0.10], 
               [12, 17, 12.92], [17, 10, 17.97], );
  or
  my @data = ( { x => 2,  y => 15, z => 18.10 },
               { x => 6,  y => 19, z => 0.10 },
               { x => 12, y => 17, z => 12.92 },
               { x => 17, y => 10, z => 17.97 },
             )


  $graph->add_data({
    'data' => \@data_cpu,
    'title' => 'CPU',
  });

This method allows you to add data to the graph object.  The
data are expected to be either a list of scalars (in which
case pairs of elements are taken to be X,Y pairs) or a list
of array references.  In the latter case, the first two
elements in each referenced array are taken to be X and Y,
and the optional third element (if present) is used as the
text to display for that point for show_data_values and
rollover_values; otherwise the Y value itself is displayed.
It can be called several times to add more data sets in.

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

=item height()

Set the height of the graph box, this is the total height
of the SVG box created - not the graph it self which auto
scales to fix the space.

=item width()

Set the width of the graph box, this is the total width
of the SVG box created - not the graph it self which auto
scales to fix the space.

=item compress()

Whether or not to compress the content of the SVG file (Compress::Zlib required).

=item tidy()

Whether or not to tidy the content of the SVG file (XML::Tidy required).

=item style_sheet()

Set the path to an external stylesheet, set to '' if
you want to revert back to using the default internal version.

Set to "inline:<style>...</style>" with your CSS in between the tags.
You can thus override the default style without requireing an external URL.

The default stylesheet handles up to 12 data sets. All data series over
the 12th will have no style and be in black. If you have over 12 data
sets you can assign them all random colors (see the random_color()
method) or create your own stylesheet and add the additional settings
for the extra data sets.

To create an external stylesheet create a graph using the
default internal version and copy the stylesheet section to
an external file and edit from there.

=item random_colors()

Use random colors in the internal stylesheet.

=item show_data_values()

Show the value of each element of data on the graph (or
optionally a user-defined label; see add_data).

=item rollover_values()

Shows data values and data points when the mouse is over the point.
Used in combination with show_data_values.

=item data_value_format()

Format specifier to for data values (as per printf).

=item max_x_span()

Maximum span for a line between data points on the X-axis. If this span is
exceeded, the points are not connected. This is useful for skipping missing data
sections. If you set this value to something smaller than 0 (e.g. -1), you will
get an XY scatter plot with no line joining the data points.

=item stacked()

Accumulates each data set. (i.e. Each point increased by
sum of all previous series at same point). Default is 0,
set to '1' to show.

=item min_yscale_value()

The point at which the Y axis starts, defaults to '0',
if set to '' it will default to the minimum data value.

=item max_yscale_value()

The point at which the Y axis ends,
if set to '' it will default to the maximum data value.

=item yscale_divisions()

This defines the gap between markers on the Y axis,
default is a 10th of the range, e.g. you will have
10 markers on the Y axis. NOTE: do not set this too
low - you are limited to 999 markers, after that the
graph won't generate.

=item show_x_labels()

Whether to show labels on the X axis or not, defaults
to 1, set to '0' if you want to turn them off.

=item show_y_labels()

Whether to show labels on the Y axis or not, defaults
to 1, set to '0' if you want to turn them off.

=item y_label_format()

Format string for presenting the Y axis labels (as per printf).

=item xscale_divisions()

This defines the gap between markers on the X axis.
Default is the entire range (only start and end axis
labels).

=item stagger_x_labels()

This puts the labels at alternative levels so if they
are long field names they will not overlap so easily.
Default it '0', to turn on set to '1'.

=item rotate_x_labels()

This turns the X axis labels by 90 degrees.
Default it '0', to turn on set to '1'.

=item min_xscale_value()

This sets the minimum X value. Any data points before this value will not be
shown.

=item max_xscale_value()

This sets the maximum X value. Any data points after this value will not be
shown.

=item show_x_title()

Whether to show the title under the X axis labels,
default is 0, set to '1' to show.

=item x_title()

What the title under X axis should be, e.g. 'Parameter X'.

=item show_y_title()

Whether to show the title under the Y axis labels,
default is 0, set to '1' to show.

=item y_title()

What the title under Y axis should be, e.g. 'Sales in thousands'.

=item show_graph_title()

Whether to show a title on the graph,
default is 0, set to '1' to show.

=item graph_title()

What the title on the graph should be.

=item show_graph_subtitle()

Whether to show a subtitle on the graph,
default is 0, set to '1' to show.

=item graph_subtitle()

What the subtitle on the graph should be.

=item key()

Whether to show a key, defaults to 0, set to
'1' if you want to show it.

=item key_position()

Where the key should be positioned, defaults to
'right', set to 'bottom' if you want to move it.

=item x_label_formatter ()

A callback subroutine which will format a label on the x axis.  For example:

    $graph->x_label_formatter( sub { return '$' . $_[0] } );

=item y_label_formatter()

A callback subroutine which will format a label on the y axis.  For example:

    $graph->y_label_formatter( sub { return '$' . $_[0] } );

=item bubble_fill()
    
This is a floating number from 0 to 1 and determins how opaque the bubbles are.
Default: 0.4

=item bubble_border_stroke()

Whether to show a 1px border stroke around the bubble.
   
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

        'width'  => '500',
        'height' => '300',

        'style_sheet'   => '',
        'random_colors' => 0,

        'show_data_values'     => 1,
        'rollover_values'      => 0,
        'bubble_fill'          => 0.4,
        'bubble_border_stroke' => 0,


        'max_x_span' => '',

        'area_fill' => 0,

        'show_y_labels'    => 1,
        'yscale_divisions' => '',
        'min_yscale_value' => '0',
        'pad_top_y_axis'   => 1,
        'stacked'          => 0,

        'show_x_labels'     => 1,
        'stagger_x_labels'  => 0,
        'rotate_x_labels'   => 0,
        'xscale_divisions'  => '',
        'x_label_formatter' => sub {return @_},
        'y_label_formatter' => sub {return @_},

        'show_x_title' => 0,
        'x_title'      => 'X Field names',

        'show_y_title' => 0,
        'y_title'      => 'Y Scale',

        'show_graph_title'    => 0,
        'graph_title'         => 'Graph Title',
        'show_graph_subtitle' => 0,
        'graph_subtitle'      => 'Graph Sub Title',

        'key'           => 0,
        'key_position'  => 'right',    # bottom or right
        'diagonal_path' => 0,
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

    # convert to sorted (by ascending numeric value) array of [ x, y ]
    my @new_data = ();
    my ( $i, $x, @pair );

    $i = 0;
    while ( $i < @{ $conf->{ 'data' } } )
    {
        @pair = ();
        if ( ref( $conf->{ 'data' }->[$i] ) eq 'ARRAY' )
        {
            push @pair, @{ $conf->{ 'data' }->[$i] };
            $i++;
        }
        elsif ( ref( $conf->{ 'data' }->[$i] ) eq 'HASH' )
        {
            $pair[0] = $conf->{ 'data' }->[$i]->{ x };
            $pair[1] = $conf->{ 'data' }->[$i]->{ y };
            $pair[2] = $conf->{ 'data' }->[$i]->{ z };
            $i++;
        }
        else
        {
            $pair[0] = $conf->{ 'data' }->[$i++];
            $pair[1] = $conf->{ 'data' }->[$i++];
            $pair[2] = $conf->{ 'data' }->[$i++];
        }
        push @new_data, [@pair];
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
    my ( $max_key_size, $max_x, $min_x, $max_y, $min_y, $max_z,
         $max_x_label_length, $x_label );


    foreach my $dataset ( @{ $self->{ data } } )
    {
        $max_key_size = length( $dataset->{ title } )
          if ( ( !defined $max_key_size ) ||
               ( $max_key_size < length( $dataset->{ title } ) ) );

        foreach my $pair ( @{ $dataset->{ pairs } } )
        {
            $max_x = $pair->[0]
              if ( ( !defined $max_x ) || ( $max_x < $pair->[0] ) );
            $min_x = $pair->[0]
              if ( ( !defined $min_x ) || ( $min_x > $pair->[0] ) );
            $max_y = $pair->[1]
              if ( ( $pair->[1] ne '' ) &&
                   ( ( !defined $max_y ) || ( $max_y < $pair->[1] ) ) );
            $min_y = $pair->[1]
              if ( ( $pair->[1] ne '' ) &&
                   ( ( !defined $min_y ) || ( $min_y > $pair->[1] ) ) );
            $max_z = $pair->[2]
              if ( ( $pair->[2] ne '' ) &&
                   ( ( !defined $max_z ) || ( $max_z < $pair->[2] ) ) );

            $x_label            = $pair->[0];
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
    $self->{ calc }->{ max_z }              = $max_z;
    $self->{ calc }->{ max_x_label_length } = $max_x_label_length;

    # Calc the x axis scale values
    $self->{ calc }->{ min_xscale_value } =
      ( $self->_is_valid_config('min_xscale_value') ) ?
      $self->{ config }->{ min_xscale_value } :
      $min_x;
    $self->{ calc }->{ max_xscale_value } =
      ( $self->_is_valid_config('max_xscale_value') ) ?
      $self->{ config }->{ max_xscale_value } :
      $max_x;
    $self->{ calc }->{ xscale_range } =
      $self->{ calc }->{ max_xscale_value } -
      $self->{ calc }->{ min_xscale_value };

    # Calc the y axis scale values
    $self->{ calc }->{ min_yscale_value } =
      ( $self->_is_valid_config('min_yscale_value') ) ?
      $self->{ config }->{ min_yscale_value } :
      $min_y;
    $self->{ calc }->{ max_yscale_value } =
      ( $self->_is_valid_config('max_yscale_value') ) ?
      $self->{ config }->{ max_yscale_value } :
      $max_y;
    $self->{ calc }->{ yscale_range } =
      $self->{ calc }->{ max_yscale_value } -
      $self->{ calc }->{ min_yscale_value };

    my ( $range, $division, $precision );

    if ( $self->_is_valid_config('yscale_divisions') )
    {
        $division = $self->{ config }->{ yscale_divisions };

        if ( $division >= 1 )
        {
            $precision = 0;
        }
        else
        {
            $precision = length($division) - 2;
        }
    }
    else
    {
        # Find divisions, format and range
        ( $range, $division, $precision ) =
          $self->_range_calc( $self->{ calc }->{ yscale_range } );

        # If a max value hasn't been set we can set a revised range and max value
        if ( !$self->_is_valid_config('max_yscale_value') )
        {
            $self->{ calc }->{ max_yscale_value } =
              $self->{ calc }->{ min_yscale_value } + $range;
            $self->{ calc }->{ yscale_range } =
              $self->{ calc }->{ max_yscale_value } -
              $self->{ calc }->{ min_yscale_value };
        }
    }
    $self->{ calc }->{ yscale_division } = $division;

    $self->{ calc }->{ y_label_format } =
      ( $self->_is_valid_config('y_label_format') ) ?
      $self->{ config }->{ y_label_format } :
      "%.${precision}f";
    $self->{ calc }->{ data_value_format } =
      ( $self->_is_valid_config('data_value_format') ) ?
      $self->{ config }->{ data_value_format } :
      "%.${precision}f";

    # This is some sanity incase someone activates the diganonal path, and the axis
    # are not the same size
    if ( $self->{ config }->{ diagonal_path } &&
         ( $self->{ calc }->{ max_xscale_value } !=
            $self->{ calc }->{ max_yscale_value } ||
            $self->{ calc }->{ min_xscale_value } !=
            $self->{ calc }->{ min_yscale_value } ) )
    {
        warn
          "Using the diagonal_path in the configs assumes the axis\n will be the same size. If you want to use this.\nYou might want to set the min and max x and y sizes.";
    }

}

1;
__DATA__
<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"
  "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">

[% stylesheet = 'included' %]

[% IF config.style_sheet && config.style_sheet != '' && config.style_sheet.substr(0,7) != 'inline:' %]
  <?xml-stylesheet href="[% config.style_sheet %]" type="text/css"?>
[% ELSIF config.style_sheet && config.style_sheet.substr(0,7) == 'inline:'%]
  [% stylesheet = 'inline'
     style_inline = config.style_sheet.substr(7) %]
[% ELSE %]
  [% stylesheet = 'excluded' %]
[% END %]

<svg width="[% config.width %]" height="[% config.height %]" viewBox="0 0 [% config.width %] [% config.height %]" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">

<!-- \\\\\\\\\\\\\\\\\\\\\\\\\\\\  -->
<!-- Created with SVG::TT::Graph   -->
<!-- Dave Meibusch                 -->
<!-- ////////////////////////////  -->

[% IF stylesheet == 'inline' %]
[% style_inline %]
[% ELSIF stylesheet == 'excluded' %]
[%# include default stylesheet if none specified %]
<defs>
<style type="text/css">
<![CDATA[
/* Copy from here for external style sheet */
.svgBackground{
  fill:#ffffff;
}
.graphBackground{
  fill:#f0f0f0;
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
  font-family: "Arial", sans-serif;
  font-weight: normal;
}

.xAxisTitle{
  text-anchor: middle;
  fill: #ff0000;
  font-size: 14px;
  font-family: "Arial", sans-serif;
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
    fill-opacity: [% config.bubble_fill %];
    [% IF config.bubble_border_stroke %]
    stroke: [% color %];
    stroke-width: 1px;
  [% ELSE %]
    stroke: none;
    stroke-width: 1px;
  [% END %]
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
<rect x="0" y="0" width="[% config.width %]" height="[% config.height %]" stroke="rgba(0,0,0,1)" class="svgBackground"/>

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

<!-- CALC HEIGHT AND Y COORD DIMENSIONS -->
[%# reduce height of graph area if there is labelling on x axis %]
[% IF config.show_x_labels %][% h = h - 20 %][% END %]

[%# reduce height if x labels are rotated %]
[% x_label_allowance = 0 %]
[% IF config.rotate_x_labels %]
  [% x_label_allowance = (calc.max_x_label_length * char_width) - 20 %]
  [% h = h - x_label_allowance %]
[% END %]

[%# stagger x labels if overlapping occurs %]
[% stagger = 0 %]
[% IF config.show_x_labels && config.stagger_x_labels %]
  [% stagger = 17 %]
  [% h = h - stagger %]
[% END %]

[% IF config.show_x_title %][% h = h - 25 - stagger %][% END %]

[%# pad top of graph if y axis has data labels so labels do not get chopped off %]
[% IF config.show_y_labels %][% h = h - 10 %][% y = y + 10 %][% END %]

[%# reduce height if graph has title or subtitle %]
[% IF config.show_graph_title %][% h = h - 25 %][% y = y + 25 %][% END %]
[% IF config.show_graph_subtitle %][% h = h - 10 %][% y = y + 10 %][% END %]

[%# reduce graph dimensions if there is a KEY %]
[% key_box_size = 12 %]
[% key_padding = 5 %]

[% IF config.key && config.key_position == 'right' %]
  [% w = w - (calc.max_key_size * (char_width - 1)) - (key_box_size * 3 ) %]
[% ELSIF config.key && config.key_position == 'bottom' %]
  [% IF data.size < 4 %]
    [% h = h - ((data.size + 1) * (key_box_size + key_padding))%]
  [% ELSE %]
    [% h = h - (4 * (key_box_size + key_padding))%]
  [% END %]
[% END %]

<!-- min_yscale_value [% calc.min_yscale_value %] max_yscale_value [% calc.max_yscale_value %] -->

[%# base line %]
[% base_line = h + y %]

[%# find the string length of max value %]
[% max_y_length = calc.max_yscale_value.length %]

[%# label width in pixels %]
[% max_y_length_px = max_y_length * char_width %]
[%# If the y labels are shown but the size of the x labels are small, pad for y labels %]

<!-- CALC WIDTH AND X COORD DIMENSIONS -->
[%# reduce width of graph area if there is large labelling on x axis %]
[% space_b4_y_axis = (calc.min_xscale_value.length / 2) * char_width  %]

[% IF config.show_x_labels %]
  [% IF config.key && config.key_position == 'right' %]
    [% w = w - space_b4_y_axis %]
  [% ELSE %]
    <!-- pad both sides -->
    [% w = w - (space_b4_y_axis * 2) %]
  [% END %]
  [% x = x + space_b4_y_axis %]
[% ELSIF config.show_data_values %]
  [% w = w - (max_y_length_px * 2) %]
  [% x = x + max_y_length_px %]
[% END %]

[% IF config.show_y_labels && space_b4_y_axis < max_y_length_px %]
  <!-- allow slightly more padding if small labels -->
  [% IF max_y_length < 2 %]
    [% w = w - (max_y_length * (char_width * 2)) %]
    [% x = x + (max_y_length * (char_width * 2)) %]
  [% ELSE %]
    [% w = w - max_y_length_px %]
    [% x = x + max_y_length_px %]
  [% END %]
[% ELSIF config.show_y_labels && !config.show_x_labels %]
  [% w = w - max_y_length_px %]
  [% x = x + max_y_length_px %]
[% END %]

[% IF config.show_y_title %]
  [% w = w - 25 %]
  [% x = x + 25 %]
[% END %]

<!-- min_xscale_value [% calc.min_xscale_value %] max_xscale_value [% calc.max_xscale_value %] -->

[%# Missing data spans %]
[% max_x_span = 0 %]
[% IF config.max_x_span %]
  [% max_x_span = config.max_x_span %]
  <!-- max_x_span [% max_x_span %] -->
[% END %]
  
  [%# scaling for bubbles %]
  [% wpad = w / 10  %]
  [% w = w - wpad * 2  %]
  [% h = h - wpad %]
  [% x = x + wpad %]
  [% y = y + wpad %]
 

<!-- //////////////////////////////  BUILD GRAPH AREA ////////////////////////////// -->
[%# graph bg and clipping regions for lines/fill and clip extended to included data labels %]
<rect x="[% x %]" y="[% y %]" width="[% w %]" height="[% h %]" stroke="rgba(0,0,0,1)" class="graphBackground"/>
<clipPath id="clipGraphArea">
  <rect x="[% x %]" y="[% y %]" width="[% w %]" height="[% h %]"/>
</clipPath>

<!-- axis -->
<path d="M[% x %] [% base_line %] h[% w %]" class="axis" id="xAxis"/>
<path d="M[% x %] [% y %] v[% h %]" class="axis" id="yAxis"/>
[% IF config.diagonal_path %]
<path d="M[% x %] [% base_line %] [% x+w %] [% y %]" class="axis" id="zAxis"/>
[% END %]

<!-- //////////////////////////////  AXIS DISTRIBUTIONS //////////////////////////// -->
<!-- x axis scaling -->
[% dx = calc.xscale_range %]
[% IF dx == 0 %]
  [% dx = 1 %]
[% END %]
[% dw = w / dx %]
<!-- dx [% dx %] dw [% dw %] -->

<!-- x axis labels -->
[% IF config.show_x_labels %]
  [% x_value_txt = config.x_label_formatter(calc.min_xscale_value) %]
  <text x="[% x %]" y="[% base_line + 15 %]" [% IF config.rotate_x_labels %] transform="rotate(90 [% x  - half_char_height %] [% base_line + 15 %]) translate(-10,0)" style="text-anchor: start" [% END %] class="xAxisLabels">[% x_value_txt %]</text>
  [% last_label = calc.min_xscale_value %]

  [% IF config.xscale_divisions %]

    [% xscale_division = config.xscale_divisions %]
    [% x_value = calc.min_xscale_value + xscale_division %]

    [% count = 0 %]
    [% WHILE ((x_value > calc.min_xscale_value) && ((x_value < calc.max_xscale_value))) %]
      [% x_value_txt = config.x_label_formatter(x_value) %]
      [% xpos = (dw * (x_value - calc.min_xscale_value)) + x %]
      [% IF (config.stagger_x_labels && ((count % 2) == 0)) %]
        <path d="M[% xpos %] [% base_line %] v[% stagger %]" class="staggerGuideLine" />
        <text x="[% xpos %]" y="[% base_line + 15 + stagger %]" [% IF config.rotate_x_labels %] transform="rotate(90 [% xpos  - half_char_height %] [% base_line + 15 + stagger %]) translate(-10,0)" style="text-anchor: start" [% END %] class="xAxisLabels">[% x_value_txt %]</text>
      [% ELSE %]
        <text x="[% xpos %]" y="[% base_line + 15 %]" [% IF config.rotate_x_labels %] transform="rotate(90 [% xpos  - half_char_height %] [% base_line + 15 %]) translate(-10,0)" style="text-anchor: start" [% END %] class="xAxisLabels">[% x_value_txt %]</text>
      [% END %]
      [% last_label = x_value %]
      [% x_value = x_value + xscale_division %]
      [% count = count + 1 %]
      [% LAST IF (count >= 999) %]
    [% END %]

  [% END %]

  [% IF calc.max_xscale_value != last_label %]
    [% x_value_txt = config.x_label_formatter(calc.max_xscale_value) %]
    [% IF (config.stagger_x_labels && ((count % 2) == 0)) %]
    <path d="M[% x + w %] [% base_line %] v[% stagger %]" class="staggerGuideLine" />
    <text x="[% x + w %]" y="[% base_line + 15 + stagger %]" [% IF config.rotate_x_labels %] transform="rotate(90 [% x + w - half_char_height %] [% base_line + 15 + stagger %]) translate(-10,0)" style="text-anchor: start" [% END %] class="xAxisLabels">[% x_value_txt %]</text>
    [% ELSE %]
    <text x="[% x + w %]" y="[% base_line + 15 %]" [% IF config.rotate_x_labels %] transform="rotate(90 [% x + w - half_char_height %] [% base_line + 15 %]) translate(-10,0)" style="text-anchor: start" [% END %] class="xAxisLabels">[% x_value_txt %]</text>
    [% END %]
  [% END %]
[% END %]

<!-- y axis scaling -->
[%# how much padding between largest bar and top of graph %]
[% top_pad = config.pad_top_y_axis ?  h / 40 : 0 %]

[% dy = calc.yscale_range %]
[% IF dy == 0 %]
  [% dy = 1 %]
[% END %]
[% dh = (h - top_pad) / dy %]
<!-- dy [% dy %] dh [% dh %] yscale_division [% calc.yscale_division %] max_yscale_value [% calc.max_yscale_value %]-->

[% count = 0 %]
[% last_label = '' %]
[% IF (calc.min_yscale_value > calc.max_yscale_value) %]
    <!-- Reversed y range -->
    [% y_value = calc.max_yscale_value %]
    [% reversed = 1 %]
[% ELSE %]
    [% y_value = calc.min_yscale_value %]
    [% reversed = 0 %]
[% END %]
[% IF config.show_y_labels %]
  [% WHILE ((y_value == calc.min_yscale_value) || (y_value == calc.max_yscale_value) || ((y_value > calc.min_yscale_value) && (y_value < calc.max_yscale_value)) || ((y_value > calc.max_yscale_value) && (y_value < calc.min_yscale_value) && reversed )) %]
    [%- next_label = y_value FILTER format(calc.y_label_format) -%]
    [%- next_label = config.y_label_formatter(next_label) -%]
    [%- IF ((count == 0) && (reversed == 0)) -%]
      [%# no stroke for first line unless reversed %]
      <text x="[% x - 5 %]" y="[% base_line - (dh * (y_value - calc.min_yscale_value)) %]" class="yAxisLabels">[% next_label %]</text>
    [%- ELSE -%]
      [% IF next_label != last_label %]
        <text x="[% x - 5 %]" y="[% base_line - (dh * (y_value - calc.min_yscale_value)) %]" class="yAxisLabels">[% next_label %]</text>
        <path d="M[% x %] [% base_line - (dh * (y_value - calc.min_yscale_value)) %] h[% w %]" class="guideLines"/>
      [% END %]
    [%- END -%]
    [%- y_value = y_value + calc.yscale_division -%]
    [%- last_label = next_label -%]
    [%- count = count + 1 -%]
    [%- LAST IF (count >= 999) -%]
  [% END %]
[% END %]

<!-- //////////////////////////////  AXIS TITLES ////////////////////////////// -->
<!-- x axis title -->
  [% IF config.show_x_title %]
    [% IF !config.show_x_labels %]
      [% y_xtitle = 15 %]
    [% ELSE %]
      [% y_xtitle = 35 %]
    [% END %]
    <text x="[% (w / 2) + x %]" y="[% h + y + y_xtitle + stagger + x_label_allowance %]" class="xAxisTitle">[% config.x_title %]</text>
  [% END %]

<!-- y axis title -->
  [% IF config.show_y_title %]
      <text x="10" y="[% (h / 2) + y %]" transform="rotate(270,10,[% (h / 2) + y %])" class="yAxisTitle">[% config.y_title %]</text>
  [% END %]

<!-- //////////////////////////////  SHOW DATA ////////////////////////////// -->
[% line = data.size %]
<g id="groupData" class="data">
[% FOREACH dataset = data.reverse %]
  <g id="groupDataLabels[% line %]" class="dataLabels[% line %]">
    [% FOREACH pair = dataset.pairs %]
      [% IF ((pair.0 >= calc.min_xscale_value) && (pair.0 <= calc.max_xscale_value)) %]
        <g class="dataLabel[% line %]" [% IF config.rollover_values %] opacity="0" [% END %]>    
          <circle
          cx="[% (dw * (pair.0 - calc.min_xscale_value)) + x %]"
          cy="[% base_line - (dh * (pair.1 - calc.min_yscale_value)) %]"
          r="[% wpad * (pair.2 / calc.max_z) %]"
          class="fill[% line %]"></circle>
        [% IF config.show_data_values %]
          [%# datavalue shown %]
          [% IF (pair.2.defined) && (pair.2 != '') %][% point_label = pair.2 %][% ELSE %][% point_label = pair.1 FILTER format(calc.data_value_format) %][% END %]
          <text x="[% (dw * (pair.0 - calc.min_xscale_value)) + x %]" y="[% base_line - (dh * (pair.1 - calc.min_yscale_value)) - 6 %]" class="dataPointLabel[% line %]"
          [% IF config.rollover_values %]
            onmouseover="evt.target.parentNode.setAttribute('opacity',1);"
            onmouseout="evt.target.parentNode.setAttribute('opacity',0);"
          [% END %]
          >[% point_label %]</text>
        [% END %]
        </g>
      [% END %]
    [% END %]
  </g>
  [% line = line - 1 %]
[% END %]
</g>

<!-- //////////////////////////////////// KEY ////////////////////////////// -->
[% key_count = 1 %]
[% IF config.key && config.key_position == 'right' %]
  [% FOREACH dataset = data %]
    <rect x="[% x + w + 20 %]" y="[% y + (key_box_size * key_count) + (key_count * key_padding) %]" width="[% key_box_size %]" height="[% key_box_size %]" class="key[% key_count %]" onclick="togglePath([% key_count %]);"/>
    <text x="[% x + w + 20 + key_box_size + key_padding %]" y="[% y + (key_box_size * key_count) + (key_count * key_padding) + key_box_size %]" class="keyText">[% dataset.title %]</text>
    [% key_count = key_count + 1 %]
  [% END %]
[% ELSIF config.key && config.key_position == 'bottom' %]
  [%# calc y position of start of key %]
  [% y_key = base_line %]
  [%# consider x title %]
  [% IF config.show_x_title %][% y_key = base_line + 25 %][% END %]
  [%# consider x label rotation and stagger %]
  [% IF config.rotate_x_labels && config.show_x_labels %]
    [% y_key = y_key + x_label_allowance %]
  [% ELSIF config.show_x_labels && stagger < 1 %]
    [% y_key = y_key + 20 %]
  [% END %]

  [% y_key_start = y_key %]
  [% x_key = x %]
  [% FOREACH dataset = data %]
    [% IF key_count == 4 || key_count == 7 || key_count == 10 %]
      [%# wrap key every 3 entries %]
      [% x_key = x_key + 200 %]
      [% y_key = y_key - (key_box_size * 4) - 2 %]
    [% END %]
    <rect x="[% x_key %]" y="[% y_key + (key_box_size * key_count) + (key_count * key_padding) + stagger %]" width="[% key_box_size %]" height="[% key_box_size %]" class="key[% key_count %]" onclick="togglePath([% key_count %]);"/>
    <text x="[% x_key + key_box_size + key_padding %]" y="[% y_key + (key_box_size * key_count) + (key_count * key_padding) + key_box_size + stagger %]" class="keyText">[% dataset.title %]</text>
    [% key_count = key_count + 1 %]
  [% END %]

[% END %]

<!-- //////////////////////////////// MAIN TITLES ////////////////////////// -->
<!-- main graph title -->
[% IF config.show_graph_title %]
  <text x="[% config.width / 2 %]" y="15" class="mainTitle">[% config.graph_title %]</text>
[% END %]

<!-- graph sub title -->
[% IF config.show_graph_subtitle %]
  [% IF config.show_graph_title %]
    [% y_subtitle = 30 %]
  [% ELSE %]
    [% y_subtitle = 15 %]
  [% END %]
  <text x="[% config.width / 2 %]" y="[% y_subtitle %]" class="subTitle">[% config.graph_subtitle %]</text>
[% END %]
</svg>
