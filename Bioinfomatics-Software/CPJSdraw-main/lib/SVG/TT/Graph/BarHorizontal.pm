package SVG::TT::Graph::BarHorizontal;

use strict;
use Carp;
use SVG::TT::Graph;
use base qw(SVG::TT::Graph);

our $VERSION = $SVG::TT::Graph::VERSION;
our $TEMPLATE_FH = \*DATA;

=head1 NAME

SVG::TT::Graph::BarHorizontal - Create presentation quality SVG horizontal bar graphs easily

=head1 SYNOPSIS

  use SVG::TT::Graph::BarHorizontal;

  my @fields = qw(Jan Feb Mar);
  my @data_sales_02 = qw(12 45 21);
  
  my $graph = SVG::TT::Graph::BarHorizontal->new({
    'height' => '500',
    'width' => '300',
    'fields' => \@fields,
  });
  
  $graph->add_data({
    'data' => \@data_sales_02,
    'title' => 'Sales 2002',
  });
  
  print "Content-type: image/svg+xml\n\n";
  print $graph->burn();

=head1 DESCRIPTION

This object aims to allow you to easily create high quality
SVG horitonzal bar graphs. You can either use the default style sheet
or supply your own. Either way there are many options which can
be configured to give you control over how the graph is
generated - with or without a key, data elements at each point,
title, subtitle etc.

=head1 METHODS

=head2 new()

  use SVG::TT::Graph::BarHorizontal;
  
  # Field names along the X axis
  my @fields = qw(Jan Feb Mar);
  
  my $graph = SVG::TT::Graph::BarHorizontal->new({
    # Required
    'fields'                 => \@fields,
  
    # Optional - defaults shown
    'height'                 => '500',
    'width'                  => '300',

    'show_data_values'       => 1,

    'scale_divisions'        => '',
    'min_scale_value'        => '0',
    'bar_gap'                => 1,

    'show_x_labels'          => 1,
    'stagger_x_labels'       => 0,
    'show_y_labels'          => 1,
    'scale_integers'         => 0,
    'y_label_formatter'      => sub { return @_ },
    'x_label_formatter'      => sub { return @_ },

    'show_path_title'	     => 0,
    'show_title_fields'	     => 0,

    'show_x_title'           => 0,
    'x_title'                => 'X Field names',

    'show_y_title'           => 0,
    'y_title_text_direction' => 'bt',
    'y_title'                => 'Y Scale',

    'show_graph_title'       => 0,
    'graph_title'            => 'Graph Title',
    'show_graph_subtitle'    => 0,
    'graph_subtitle'         => 'Graph Sub Title',
    'key'                    => 0,
    'key_position'           => 'right',

    # Stylesheet defaults
    'style_sheet'             => '/includes/graph.css', # internal stylesheet
    'random_colors'           => 0,
  });

The constructor takes a hash reference, only fields (the names for each
field on the X axis) MUST be set, all other values are defaulted to those
shown above - with the exception of style_sheet which defaults
to using the internal style sheet.

=head2 add_data()

  my @data_sales_02 = qw(12 45 21);

  $graph->add_data({
    'data'  => \@data_sales_02,
    'title' => 'Sales 2002',
  });

This method allows you to add data to the graph object.
It can be called several times to add more data sets in,
but the likelihood is you should be using SVG::TT::Graph::Line
as it won't look great!

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
you want to revert back to using the defaut internal version.

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

Use random colors in the internal stylesheet

=item show_data_values()

Show the value of each element of data on the graph

=item bar_gap()

Whether to have a gap between the bars or not, default
is '1', set to '0' if you don't want gaps.

=item min_scale_value()

The point at which the Y axis starts, defaults to '0',
if set to '' it will default to the minimum data value.

=item show_x_labels()

Whether to show labels on the X axis or not, defaults
to 1, set to '0' if you want to turn them off.

=item stagger_x_labels()

This puts the labels at alternative levels so if they
are long field names they will not overlap so easily.
Default it '0', to turn on set to '1'.

=item show_y_labels()

Whether to show labels on the Y axis or not, defaults
to 1, set to '0' if you want to turn them off.

=item scale_integers()

Ensures only whole numbers are used as the scale divisions.
Default it '0', to turn on set to '1'. This has no effect if 
scale divisions are less than 1.

=item scale_divisions()

This defines the gap between markers on the X axis,
default is a 10th of the max_value, e.g. you will have
10 markers on the X axis. NOTE: do not set this too
low - you are limited to 999 markers, after that the
graph won't generate.

=item show_x_title()

Whether to show the title under the X axis labels,
default is 0, set to '1' to show.

=item x_title()

What the title under X axis should be, e.g. 'Months'.

=item show_y_title()

Whether to show the title under the Y axis labels,
default is 0, set to '1' to show.

=item y_title_text_direction()

Aligns writing mode for Y axis label. Defaults to 'bt' (Bottom to Top).
Change to 'tb' (Top to Bottom) to reverse.

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

=item show_path_title()

Whether to add the title attribute to the data path tags,
which will show "tooltips" when hovering over the bar area.

=item show_title_fields()

Whether to show field values as title elements in path tag,
defaults to 0, set to '1' to turn on. Suggest on single
add_data graphs, for overlapping graphs leave off to see
the title value used in the add_data call.

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
L<SVG::TT::Graph::BarLine>,
L<SVG::TT::Graph::Pie>,
L<SVG::TT::Graph::TimeSeries>,
L<SVG::TT::Graph::XY>,
L<Compress::Zlib>,
L<XML::Tidy>

=cut

sub _init {
  my $self = shift;
  croak "fields was not supplied or is empty" 
  unless defined $self->{'config'}->{fields} 
    && ref($self->{'config'}->{fields}) eq 'ARRAY'
    && scalar(@{$self->{'config'}->{fields}}) > 0;
}

sub _set_defaults {
  my $self = shift;
  
  my %default = (
    'width'                  => '500',
    'height'                 => '300',

    'random_colors'          => 0,
    'style_sheet'            => '',

    'show_data_values'       => 1,
  
    'min_scale_value'        => '0',
    'scale_divisions'        => '',
    
    'bar_gap'                => 1,
    
    'show_x_labels'          => 1,
    'stagger_x_labels'       => 0,
    'show_y_labels'          => 1,
    'scale_integers'         => 0,
    'x_label_formatter'      => sub { return @_ },
    'y_label_formatter'      => sub { return @_ },

    'show_path_title'	     => 0,
    'show_title_fields'	     => 0,
  
    'show_x_title'           => 0,
    'x_title'                => 'X Field names',
  
    'show_y_title'           => 0,
    'y_title_text_direction' => 'bt',
    'y_title'                => 'Y Scale',
  
    'show_graph_title'       => 0,
    'graph_title'            => 'Graph Title',
    'show_graph_subtitle'    => 0,
    'graph_subtitle'         => 'Graph Sub Title',
    'key'                    => 0, 
    'key_position'           => 'right', # bottom or right
  );
  
  while( my ($key,$value) = each %default ) {
    $self->{config}->{$key} = $value;
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
<!-- Stephen Morgan / Leo Lapworth -->
<!-- ////////////////////////////  -->
[% IF stylesheet == 'inline' %]
[% style_inline %]
[% ELSIF stylesheet == 'excluded' %]
<!-- include default stylesheet if none specified -->
<defs>
<style type="text/css">
<![CDATA[
/* Copy from here for external style sheet */
.svgBackground{
  fill:#ffffff;
  /* set 'fill: none;' and then include 'wmode="transparent"'
   in the HTML embed tag if you need the SVG transparent */
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
  font-weight: bold;
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

  .key[% loop.count %],.fill[% loop.count %]{
    fill: [% color %];
    fill-opacity: 0.5;
    stroke: none;
    stroke-width: 0.5px;
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
<!-- svg bg -->
<rect x="0" y="0" width="[% config.width %]" height="[% config.height %]" class="svgBackground"/>
  
<!-- ///////////////// CALCULATE GRAPH AREA AND BOUNDARIES //////////////// -->
<!-- get dimensions of actual graph area (NOT SVG area) -->
[% w = config.width %]
[% h = config.height %]

<!-- set start/default coords of graph --> 
[% x = 0 %]
[% y = 0 %]

[% char_width = 7 %]

<!-- CALC WIDTH AND X COORD DIMENSIONS -->
<!-- reduce width of graph area if there is labelling on y axis -->
[% IF config.show_y_title %][% w = w - 20 %][% x = x + 20 %][% END %]
[% IF config.show_y_labels %]
  [% max_ylabel_length = 0 %]
  <!-- calculate largest label width and add margin accordingly -->
  [% FOREACH y_label = config.fields %]
    [% IF max_ylabel_length < y_label.length %]
      [% max_ylabel_length = y_label.length %]
    [% END %]
  [% END %]

  [% space_b4_axis = char_width * max_ylabel_length %]

  [% w = w - space_b4_axis %]
  [% x = x + space_b4_axis %]
[% END %]

<!-- corrects space around graph when very small y labels are used -->
[% IF max_ylabel_length == 1 %]
  [% w = w - 5 %]
  [% x = x + 5 %]
[% END %]

<!-- pad ends of graph if there are x labels -->
[% IF config.show_x_labels %]
  [% w = w - 20 %]
  <!-- if there are no y labels or titles BUT there are x labels, then pad left -->
  [% IF !config.show_y_labels && !config.show_y_title %]
    [% w = w - 10 %]
    [% x = x + 10 %]
  [% END %]
  <!-- adjust axis start position using the  first x label char lengths -->
  [% IF config.min_scale_value.length > 1 %]
    [% padding_for_labels = char_width * config.min_scale_value.length %]
    [% w = w - (padding_for_labels / 2) %]
    [% x = x + (padding_for_labels / 2) %]
  [% END %]
[% END %]


<!-- CALC HEIGHT AND Y COORD DIMENSIONS -->
<!-- reduce height of graph area if there is labelling on x axis -->
[% IF config.show_x_labels %][% h = h - 20 %][% END %]

<!-- stagger x labels if overlapping occurs -->
[% stagger = 0 %]
[% IF config.stagger_x_labels %]
  [% stagger = 17 %]
  [% h = h - stagger %]
[% END %]

[% IF config.show_x_title %][% h = h - 25 - stagger %][% END %]

<!-- pad top of graph if y axis has data labels so labels do not get chopped off -->
[% IF config.show_y_labels %][% h = h - 10 %][% y = y + 10 %][% END %]

<!-- reduce height if graph has title or subtitle -->
[% IF config.show_graph_title %][% h = h - 25 %][% y = y + 25 %][% END %]
[% IF config.show_graph_subtitle %][% h = h - 10 %][% y = y + 10 %][% END %]

[% max_key_size = 0 %]  
[% FOREACH y_label = config.fields %]
  <!-- find largest dataset title for Key size -->
  [% IF max_key_size < data.0.title.length %]
    [% max_key_size = data.0.title.length %]
  [% END %]
[% END %]

<!-- reduce graph dimensions if there is a KEY -->
[% key_box_size = 12 %]
[% IF config.key && config.key_position == 'right' %]
  [% w = w - (max_key_size * (char_width - 1)) - (key_box_size * 3 ) %]
[% ELSIF config.key && config.key_position == 'bottom' %]
  [% IF data.size < 4 %]
    [% h = h - ((data.size + 1) * (key_box_size + key_padding))%]
  [% ELSE %]
    [% h = h - (4 * (key_box_size + key_padding))%]
  [% END %]        
[% END %]


<!-- calc min and max values -->
[% min_value = 99999999999 %]
[% max_value = 0 %]
[% FOREACH field = config.fields %]
  [% FOREACH dataset = data %]
    [% IF min_value > dataset.data.$field && dataset.data.$field != '' %]
      [% min_value = dataset.data.$field %]
    [% END %]
    [% IF max_value < dataset.data.$field && dataset.data.$field != '' %]
      [% max_value = dataset.data.$field %]
    [% END %]
  [% END %]
[% END %]

[% IF config.min_scale_value || config.min_scale_value == '0' %]
  [% min_scale_value = config.min_scale_value %]
[% ELSE %]
  <!-- setting lowest value to be min_value as no min_scale_value defined -->
  [% min_scale_value = min_value %]
[% END %]

<!-- base line -->
[% base_line = h + y %]

<!-- how much padding above max point on graph -->
[% IF (max_value - min_scale_value) == 0 %]
  [% top_pad = 10 %]
[% ELSE %]
  [% top_pad = (max_value - min_scale_value) / 20 %]
[% END %]

[% scale_range = (max_value + top_pad) - min_scale_value %]

<!-- default to 10 scale_divisions if none have been set -->
[% IF config.scale_divisions %]
  [% scale_division = config.scale_divisions %]
[% ELSE %]
  [% scale_division = scale_range / 10 %]
[% END %]

[% IF config.scale_integers %]
  [% IF scale_division < 1 %]
    [% scale_division = 1 %]
  [% ELSIF scale_division.match('.') %]
    [% scale_division = scale_division FILTER format('%2.0f') %]
  [% END %]
[% END %]

<!-- //////////////////////////////  BUILD GRAPH AREA ////////////////////////////// -->
<!-- graph bg -->
<rect x="[% x %]" y="[% y %]" width="[% w %]" height="[% h %]" class="graphBackground"/>

<!-- axis -->
<path d="M[% x %] [% base_line %] h[% w %]" class="axis" id="xAxis"/>
<path d="M[% x %] [% y %] v[% h %]" class="axis" id="yAxis"/>

<!-- //////////////////////////////  AXIS DISTRIBUTIONS //////////////////////////// -->
<!-- get number of data points on y scale -->
[% dy = config.fields.size %]
[% IF dy == 0 %]
  [% dy = 1 %]
[% END %]

<!-- get distribution heights on y axis -->
[% data_widths_y = h / dy %]
[% dh = data_widths_y.match('(\d+[\.\d\d])').0 %]

[% i = dh %]
[% count = 0 %]

<!-- y axis labels -->
[% IF config.show_y_labels %]
  [% FOREACH field = config.fields %]
    [% field_txt = config.y_label_formatter(field) %]
    [% IF count == 0 %]
      <text x="[% x - 10 %]" y="[% base_line - (dh / 2) %]" class="yAxisLabels">[% field_txt %]</text>
      [% i = i - dh %]
    [% ELSE %]
      <text x="[% x - 10 %]" y="[% base_line - i - (dh / 2) %]" class="yAxisLabels">[% field_txt %]</text>
    [% END %]
    [% i = i + dh %]
    [% count = count + 1 %]
  [% END %]
[% END %]


<!-- distribute x scale -->
[% dx = scale_range / scale_division %]
[% IF dx == 0 %]
  [% dx = 1 %]
[% END %]
<!-- ensure x_data_points butt up to edge of graph -->
[% scale_division_height = w / dx %]
[% dx = scale_division_height.match('(\d+[\.\d\d])').0 %]
[% count = 0 %]
[% y_value = min_scale_value %]
[% stagger_count = 0 %]
[% IF config.show_x_labels %]
  [% WHILE (dx * count) < w %]
    [% IF count == 0 %]
      <!-- no stroke for first line -->
      [% y_value_txt = y_value FILTER format('%2.0f') %]
      [% y_value_txt = config.y_label_formatter(y_value_txt) %]
      <text x="[% x + (dx * count) %]" y="[% base_line + 15 %]" class="xAxisLabels">[% y_value_txt %]</text>
    [% ELSE %]
      [% IF stagger_count == 2 %]
        [% y_value_txt = y_value FILTER format('%2.01f') %]
        [% y_value_txt = config.y_label_formatter(y_value_txt) %]
        <text x="[% x + (dx * count) %]" y="[% base_line + 15 %]" class="xAxisLabels" style="text-anchor: middle;">[% y_value_txt %]</text>
        <path d="M[% x + (dx * count) %] [% base_line %] V[% y %]" class="guideLines"/>
        [% stagger_count = 0 %]
      [% ELSE %]
        [% y_value_txt = y_value FILTER format('%2.01f') %]
        [% y_value_txt = config.y_label_formatter(y_value_txt) %]
        <text x="[% x + (dx * count) %]" y="[% base_line + 15 + stagger %]" class="xAxisLabels" style="text-anchor: middle;">[% y_value_txt %]</text>
        <path d="M[% x + (dx * count) %] [% base_line %] V[% y %]" class="guideLines"/>
        <path d="M[% x + (dx * count) %] [% base_line %] v[% stagger %]" class="staggerGuideLine" />
      [% END %]
    [% END %]
    [% y_value = y_value + scale_division %]
    [% count = count + 1 %]
    [% stagger_count = stagger_count + 1 %]
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
  <text x="[% (w / 2) + x %]" y="[% h + y + y_xtitle + stagger %]" class="xAxisTitle">[% config.x_title %]</text>
[% END %]  

<!-- y axis title -->
[% IF config.show_y_title %]
  [% IF config.y_title_text_direction == 'tb' %]
    <text x="11" y="[% (h / 2) + y %]" class="yAxisTitle" style="writing-mode:tb;">[% config.y_title %]</text>
  [% ELSE %]
    <text class="yAxisTitle" transform="translate(15,[% (h / 2) + y %]) rotate(270)">[% config.y_title %]</text>
  [% END %]
[% END %]


<!-- //////////////////////////////  SHOW DATA ////////////////////////////// -->
[% IF config.bar_gap %]
  [% bar_gap = 10 %]
[% ELSE %]
  [% bar_gap = 0 %]
[% END %]
 
[% bar_width = dh - bar_gap %]

[% divider = dx / scale_division %]

[% xcount = 0 %]

[% FOREACH field = config.fields %]
  [% dcount = 1 %]

  [% FOREACH dataset = data %]
    [% IF config.show_path_title %]
      [% IF config.show_title_fields %]
	<path d="M[% x %] [% base_line - (dh * xcount) - dh %] H[% x + (dataset.data.$field * divider) %] v[% bar_width %] H[% x %] Z" class="fill[% dcount %]"><title>[% dataset.data.$field %] - [% field %]</title></path>
      [% ELSE %]
	<path d="M[% x %] [% base_line - (dh * xcount) - dh %] H[% x + (dataset.data.$field * divider) %] v[% bar_width %] H[% x %] Z" class="fill[% dcount %]"><title>[% dataset.data.$field %] - [% dataset.title %]</title></path>
      [% END %]
    [% ELSE %]
      <path d="M[% x %] [% base_line - (dh * xcount) - dh %] H[% x + (dataset.data.$field * divider) %] v[% bar_width %] H[% x %] Z" class="fill[% dcount %]"/>
    [% END %]

    [% IF config.show_data_values %]
      <text x="[% x + (dataset.data.$field * divider) + 5 %]" y="[% base_line - (dh * xcount) - dh + (dh / 2) %]" class="dataPointLabel" style="text-anchor: start;">[% dataset.data.$field %]</text>
    [% END %]
    [% dcount = dcount + 1 %]
  [% END %]
  [% xcount = xcount + 1 %]
[% END %]



<!-- //////////////////////////////// KEY /////// ////////////////////////// -->
[% key_box_size = 12 %]
[% key_count = 1 %]
[% key_padding = 5 %]
[% IF config.key && config.key_position == 'right' %]
  [% FOREACH dataset = data %]
    <rect x="[% x + w + 20 %]" y="[% y + (key_box_size * key_count) + (key_count * key_padding) %]" width="[% key_box_size %]" height="[% key_box_size %]" class="key[% key_count %]"/>
    <text x="[% x + w + 20 + key_box_size + key_padding %]" y="[% y + (key_box_size * key_count) + (key_count * key_padding) + key_box_size %]" class="keyText">[% dataset.title %]</text>
    [% key_count = key_count + 1 %]
  [% END %]
[% ELSIF config.key && config.key_position == 'bottom' %]
  <!-- calc y position of start of key -->
  [% y_key = base_line %]
  [% IF config.show_x_labels %][% y_key = base_line + 20 %][% END %]
  [% IF config.show_x_title %][% y_key = base_line + 25 %][% END %]
  [% y_key_start = y_key %]
  [% x_key = x %]
  [% FOREACH dataset = data %]
    [% IF key_count == 4 || key_count == 7 || key_count == 10 %]
      <!-- wrap key every 3 entries -->
      [% x_key = x_key + 200 %]
      [% y_key = y_key - (key_box_size * 4) - 2 %]
    [% END %]
    <rect x="[% x_key %]" y="[% y_key + (key_box_size * key_count) + (key_count * key_padding) + stagger %]" width="[% key_box_size %]" height="[% key_box_size %]" class="key[% key_count %]"/>
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
