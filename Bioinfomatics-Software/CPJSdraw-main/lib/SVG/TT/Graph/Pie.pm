package SVG::TT::Graph::Pie;

use strict;
use Carp;
use SVG::TT::Graph;
use base qw(SVG::TT::Graph);

our $VERSION = $SVG::TT::Graph::VERSION;
our $TEMPLATE_FH = \*DATA;

=head1 NAME

SVG::TT::Graph::Pie - Create presentation quality SVG pie graphs easily

=head1 SYNOPSIS

  use SVG::TT::Graph::Pie;

  my @fields = qw(Jan Feb Mar);
  my @data_sales_02 = qw(12 45 21);

  my $graph = SVG::TT::Graph::Pie->new({
    'height' => '500',
    'width'  => '300',
    'fields' => \@fields,
  });

  $graph->add_data({
    'data'  => \@data_sales_02,
    'title' => 'Sales 2002',
  });

  print "Content-type: image/svg+xml\n\n";
  print $graph->burn();

=head1 DESCRIPTION

This object aims to allow you to easily create high quality
SVG pie graphs. You can either use the default style sheet
or supply your own. Either way there are many options which can
be configured to give you control over how the graph is
generated - with or without a key, display percent on pie chart,
title, subtitle etc.

=head1 METHODS

=head2 new()

  use SVG::TT::Graph::Pie;

  # Field names along the X axis
  my @fields = qw(Jan Feb Mar);

  my $graph = SVG::TT::Graph::Pie->new({
    # Required
    'fields'                  => \@fields,

    # Optional - defaults shown
    'height'                  => '500',
    'width'                   => '300',

    'show_graph_title'        => 0,
    'graph_title'             => 'Graph Title',
    'show_graph_subtitle'     => 0,
    'graph_subtitle'          => 'Graph Sub Title',

    'show_shadow'             => 1,
    'shadow_size'             => 1,
    'shadow_offset'           => 15,

    'key_placement'           => 'R',

    # data by pie chart wedges:
    'show_data_labels'        => 0,
    'show_actual_values'      => 0,
    'show_percent'            => 1,
    'rollover_values'         => 0,
    'show_path_title'	      => 0,
    'show_title_fields'	      => 0,

    # data on key:
    'show_key_data_labels'    => 1,
    'show_key_actual_values'  => 1,
    'show_key_percent'        => 0,

    'expanded'                => 0,
    'expand_greatest'         => 0,

    # Stylesheet defaults
    'style_sheet'             => '/includes/graph.css', # internal stylesheet
    'style_sheet_field_names' => 0,
    'random_colors'           => 0,

  });

The constructor takes a hash reference, fields (the name for each
slice on the pie) MUST be set, all other values are defaulted to those
shown above - with the exception of style_sheet which defaults
to using the internal style sheet.

=head2 add_data()

  my @data_sales_02 = qw(12 45 21);

  $graph->add_data({
    'data' => \@data_sales_02,
    'title' => 'Sales 2002',
  });

This method allows you to add data to the graph object, only
the first data set added will be used!

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

=item style_sheet_field_names()

If you use the style_sheet_field_names() option then you can
use the field names within your stylesheet. This allows
consistent use of styles. The names should be:

=over 4

=item <field>_dataPoint

=item <field>_key

=back

=item show_graph_title()

Whether to show a title on the graph, default is '0'.

=item graph_title()

What the title on the graph should be.

=item show_graph_subtitle()

Whether to show a subtitle on the graph, default is '0'.

=item graph_subtitle()

What the subtitle on the graph should be.

=item show_shadow()

Turn the shadow on and off, default to '1', set
to '0' if you don't want it. It is automatically
turned off if you extract one section of the pie.

=item shadow_size()

Size of the shadow if shown, measured as
percentage of pie chart radius, default of 1
being the same size as the pie.

=item shadow_offset()

Offset (in pixels) of shadow to bottom-right
in relation to the center of the pie chart.

=item key()

Whether to show a key, defaults to 0, set to
'1' if you want to show it.

=item key_placement()

Defaults to 'R' - right, can be
'R', 'L', 'T' or 'B'.

=item show_data_labels()

Show label on pie chart, defaults
to '0', can be set to '1'.

=item show_actual_values()

Show values on pie chart, defaults
to '0', can be set to '1'.

=item show_percent()

Show percent (rounded) on the pie chart, defaults
to '1', can be set to '0'.

=item rollover_values()

Shows data field and value when the mouse is over a piechart wedge.

=item show_path_title()

Whether to add the title attribute to the data path tags,
which will show "tooltips" when hovering over the bar area.

=item show_title_fields()

Whether to show field values as title elements in path tag,
defaults to 0, set to '1' to turn on. Suggest on single
add_data graphs, for overlapping graphs leave off to see
the title value used in the add_data call.

=item show_key_data_labels()

Show label on the key, defaults
to '1', can be set to '0'.

=item show_key_actual_values()

Show value on the key, defaults
to '1', can be set to '0'.

=item show_key_percent()

Show percent (rounded) on the key, defaults
to '0', can be set to '1'.

=item expanded()

All slices of pie are exploded out, defaults
to '0'. Do not set to '1' if you are going to
use expanded_greatest().

=item expand_greatest()

The largest slice of pie is exploded out
from the pie, defaults to '0'. Useful if you are
only showing the percentages (which are rounded) but
still want to visually show which slice was largest.

Do not set to '1' if you are going to
use expanded().

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
    'width'                   => '500',
    'height'                  => '300',

    'style_sheet'             => '',
    'style_sheet_field_names' => 0,
    'random_colors'       => 0,

    'show_graph_title'        => 0,
    'graph_title'             => 'Graph Title',
    'show_graph_subtitle'     => 0,
    'graph_subtitle'          => 'Graph Sub Title',

    'show_shadow'             => 1,
    'shadow_size'             => 1,
    'shadow_offset'           => 15,

    'key_placement'           => 'R',

    'show_data_labels'        => 0,
    'show_actual_values'      => 0,
    'show_percent'            => 1,
    'rollover_values'         => 0,
    'show_path_title'	      => 0,
    'show_title_fields'	      => 0,

    'key'                     => 0,
    'show_key_data_labels'    => 1,
    'show_key_actual_values'  => 1,
    'show_key_percent'        => 0,

    'expanded'                => 0,
    'expand_greatest'         => 0,
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
<defs>
  <radialGradient id="shadow">
    <stop offset="85%" style="stop-color: #ccc;"/>
    <stop offset="100%" style="stop-color: #ccc;stop-opacity: 0"/>
  </radialGradient>

[% IF stylesheet == 'inline' %]
[% style_inline %]
[% ELSIF stylesheet == 'excluded' %]
<!-- include default stylesheet if none specified -->
<style type="text/css">
<![CDATA[
/* Copy from here for external style sheet */
.svgBackground{
  fill:none;
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

.dataPointLabel{
  fill: #000000;
  text-anchor:middle;
  font-size: 10px;
  font-family: "Arial", sans-serif;
  font-weight: normal;
}

[% FOREACH field = config.fields %]
  [% color = '' %]
  [% IF config.random_colors %]
    [% color = random_color() %]
  [% ELSE %]
    [% color = predefined_color(loop.count) %]
  [% END %]

  .key[% loop.count %],.dataPoint[% loop.count %]{
    fill: [% color %];
    fill-opacity: 0.5;
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
[% END %]
</defs>

[% IF config.rollover_values %]
  <!-- Script to toggle paths when their key is clicked on -->
  <script language="JavaScript"><![CDATA[
  function togglePath( series ) {
    var text = document.getElementById('n' + series);
    if ( text.getAttribute('opacity') == 0 ) {
      text.setAttribute('opacity',1);
    } else {
      text.setAttribute('opacity',0);
    }
  }
  ]]></script>
[% END %]

<!-- svg bg -->
<rect x="0" y="0" width="[% config.width %]" height="[% config.height %]" class="svgBackground"/>

<!-- ///////////////// CALCULATE GRAPH AREA AND BOUNDARIES //////////////// -->
<!-- get dimensions of actual graph area (NOT SVG area) -->
[% w = config.width %]
[% h = config.height %]
[% Pi = 3.14159 %]

<!-- calc min and max values -->
[% total = 0 %]
[% count = 0 %]
[% min_value = 99999999999 %]
[% max_value = 0 %]
[% FOREACH field = config.fields %]
  [% total = total + data.0.data.$field %]
  [% count = count + 1 %]
  [% IF min_value > data.0.data.$field && data.0.data.$field != '' %]
    [% min_value = data.0.data.$field %]
  [% END %]
  [% IF max_value < data.0.data.$field && data.0.data.$field != '' %]
    [% max_value = data.0.data.$field %]
  [% END %]
[% END %]

<!-- reduce height if graph has title or subtitle -->
[% IF config.show_graph_title %][% h = h - 25 %][% END %]
[% IF config.show_graph_subtitle %][% y = y + 10 %][% END %]
[% IF config.show_graph_subtitle %][% y = y + 10 %][% END %]

<!-- set start/default coords of graph -->
[% x = w / 2 %]
[% y = h / 2 %]

<!-- move centre of pie chart if title present -->
[% IF config.show_graph_title %][% y = y + 15 %][% END %]
[% IF config.show_graph_subtitle %][% y = y + 10 %][% END %]

[% padding = 30 %]

<!-- calc radius and check whether KEY will affect this -->
[% IF w >= h %]
  [% r = (h / 2) - padding %]

  [% IF config.key %]
    [% key_position = 'h' %]
    [% x_key_start = 30 %]
    [% IF config.key_placement == 'R' %]
      <!-- if there is a key, move the pie chart -->
      [% x = x - r / 3 %]
      <!-- if the radius is too big, shrink it -->
      [% IF x < r %]
        [% r = r - (w / 8) %]
      [% END %]
    [% ELSE %]
      <!-- if there is a key, move the pie chart -->
      [% x = x + r / 3 %]
      <!-- if the radius is too big, shrink it -->
      [% IF r > (w - x) && x > (w / 2) %]
        [% r = r - (w / 8) %]
      [% END %]
    [% END %]
  [% END %]

[% ELSE %]
  [% r = (w / 2) - padding %]

  [% IF config.key %]
    [% key_position = 'v' %]
    [% y_key_start = 40 %]
    [% IF config.key_placement == 'B' %]
      <!-- if there is a key, move the pie chart -->
      [% y = y - (r / 2) %]
      <!-- if the radius is too big, shrink it -->
      [% IF y < r %]
        [% r = r - (h / 8) %]
      [% END %]
    [% ELSE %]
      <!-- if there is a key, move the pie chart -->
      [% y = y + (r / 2) %]
      <!-- if the radius is too big, shrink it -->
      [% IF r > (h - y) && y > (h / 2) %]
        [% r = r - (h / 8) %]
      [% END %]
    [% END %]
  [% END %]
[% END %]

<!-- if chart expanded -->
[% IF config.expanded OR config.expand_greatest %]
  [% e = 10 %]
[% ELSE %]
  [% e = 0 %]
[% END %]


[% IF config.show_shadow %]
  <!-- check if a shadow size has been entered -->
  [% IF config.shadow_size && config.shadow_size != '' %]
    [% shadow_size = r + ((r / 100) * config.shadow_size) %]
  [% ELSE %]
    [% shadow_size = r %]
  [% END %]

  [% IF !config.expanded && !config.expand_greatest %]
    <!-- only show shadow if not expanded -->
    <circle cx="[% x + config.shadow_offset %]" cy="[% y + config.shadow_offset %]" r="[% shadow_size + e %]" style="fill: url(#shadow); stroke: none;"/>
  [% END %]

[% END %]

<circle cx="[% x %]" cy="[% y %]" r="[% r + e %]" fill="#ffffff"/>

[% px_start = x + r %]
[% pmin_scale_value = y %]

[% values = 0 %]
<!-- half values used to show values next to wedges -->
[% values_half = 0 %]
[% last_value_half = 0 %]

[% IF config.show_percent && config.show_data_labels %]
  [% wedge_text_pad = 20 %]
[% ELSE %]
  [% wedge_text_pad = 5 %]
[% END %]

[% count = 1 %]
[% FOREACH field = config.fields %]
  [% FOREACH dataset = data %]
    [% value = data.0.data.$field %]
    [% value_half = data.0.data.$field / 2 %]

    <!-- calc percentage -->
    [% IF total == 0 %]
      [% percent = 0 %]
    [% ELSE %]
      [% percent = (100 / total) * value FILTER format('%2.0f')%]
    [% END %]

    [% values = values + value %]

    [% IF count == 1 %]
      <!-- offset values at start to get mid point -->
      [% values_half = values_half + value_half %]
    [% ELSE %]
      [% values_half = values_half + last_value_half + value_half %]
    [% END %]

    [% IF total == 0 %]
      [% degrees = 0 %]
      [% degrees_half = 0 %]
    [% ELSE %]
      [% degrees = (values / total) * 360 %]
      [% degrees_half = (values_half / total) * 360 %]
    [% END %]

    [% radians = degrees * (Pi / 180) %]
    [% radians_half = degrees_half * (Pi / 180) %]

    [% px_end = r * cos(radians) FILTER format('%02.10f') %]
    [% py_end = r * sin(radians) FILTER format('%02.10f') %]

    [% px_mid = r * cos(radians_half) FILTER format('%02.10f') %]
    [% py_mid = r * sin(radians_half) FILTER format('%02.10f') %]


    <!-- segments displayed clockwise from ' 3 o'clock ' -->
    [% IF config.expanded && !config.expand_greatest %]
      [% re = r / e %]
      [% xe = re * cos(radians_half) FILTER format('%02.10f') %]
      [% ye = re * sin(radians_half) FILTER format('%02.10f') %]

      <path id="w[% count %]" d="M[% px_start + xe %] [% pmin_scale_value + ye %] A[% r %] [% r %] 0
      [% IF percent >= 50 %]1[% ELSE %]0[% END %] 1 [% x + px_end + xe %] [% y + py_end + ye %] L[% x + xe %] [% y + ye %] Z" class="[% IF config.style_sheet_field_names %][% field %]_dataPoint[% ELSE %]dataPoint[% count %][% END %]" [% IF config.rollover_values %]onmouseover="togglePath([% count %]);" onmouseout="togglePath([% count %]);"[% END %]

    [% ELSIF !config.expanded && config.expand_greatest %]
      [% IF data.0.data.$field == max_value %]
        [% re = r / e %]
        [% xe = re * cos(radians_half) FILTER format('%02.10f') %]
        [% ye = re * sin(radians_half) FILTER format('%02.10f') %]
        <path id="w[% count %]" d="M[% px_start + xe %] [% pmin_scale_value + ye %] A[% r %] [% r %] 0
        [% IF percent >= 50 %]1[% ELSE %]0[% END %] 1 [% x + px_end + xe %] [% y + py_end + ye %] L[% x + xe %] [% y + ye %] Z" class="[% IF config.style_sheet_field_names %][% field %]_dataPoint[% ELSE %]dataPoint[% count %][% END %]" [% IF config.rollover_values %]onmouseover="togglePath([% count %]);" onmouseout="togglePath([% count %]);"[% END %]
      [% ELSE %]
        <path id="w[% count %]" d="M[% px_start %] [% pmin_scale_value %] A[% r %] [% r %] 0
        [% IF percent >= 50 %]1[% ELSE %]0[% END %] 1 [% x + px_end %] [% y + py_end %] L[% x %] [% y %] Z" class="[% IF config.style_sheet_field_names %][% field %]_dataPoint[% ELSE %]dataPoint[% count %][% END %]" [% IF config.rollover_values %]onmouseover="togglePath([% count %]);" onmouseout="togglePath([% count %]);"[% END %]
      [% END %]

    [% ELSE %]
      <path id="w[% count %]" d="M[% px_start %] [% pmin_scale_value %] A[% r %] [% r %] 0
      [% IF percent >= 50 %]1[% ELSE %]0[% END %] 1 [% x + px_end %] [% y + py_end %] L[% x %] [% y %] Z" class="[% IF config.style_sheet_field_names %][% field %]_dataPoint[% ELSE %]dataPoint[% count %][% END %]" [% IF config.rollover_values %]onmouseover="togglePath([% count %]);" onmouseout="togglePath([% count %]);"[% END %]
    [% END %]

    [% IF config.show_path_title %]
      [% IF config.show_title_fields %]
	><title>[% data.0.data.$field %] - [% field %]</title></path>
      [% ELSE %]
	><title>[% data.0.data.$field %] - [% data.0.title %]</title></path>
      [% END %]
    [% ELSE %]
      />
    [% END %]

    <!-- show values next to wedges -->
    [% text_x_offset = 0 %]
    [% text_y_offset = 0 %]
    [% IF px_mid >= x && px_mid <= y %]
      [% text_x_offset =  wedge_text_pad %]
      [% text_y_offset =  wedge_text_pad %]
    [% ELSIF px_mid <= x && py_mid <= y %]
      [% text_x_offset = 0-wedge_text_pad %]
      [% text_y_offset =  wedge_text_pad %]
    [% ELSIF px_mid <= x && py_mid >= y %]
      [% text_x_offset =  wedge_text_pad %]
      [% text_y_offset = 0-wedge_text_pad %]
    [% ELSE %]
      [% text_x_offset = 0-wedge_text_pad %]
      [% text_y_offset = 0-wedge_text_pad %]
    [% END %]
    <text id="d[% count %]" x="[% x + px_mid + text_x_offset %]" y="[% y + py_mid + text_y_offset %]" class="dataPointLabel">[% IF config.show_data_labels %][% field %][% END %][% IF config.show_actual_values %][[% data.0.data.$field %]][% END %][% IF config.show_percent %][% percent %]%[% END %]</text>

    <!-- show rollover field names next to wedge values -->
    [% IF config.rollover_values %]
        <text id="n[% count %]" x="[% x %]" y="[% y + r + e + padding %]" class="subTitle" opacity="0">[% field %]</text>
    [% END %]

    [% px_start = x + px_end %]
    [% pmin_scale_value = y + py_end %]
    [% last_value_half = value_half %]
    [% count = count + 1 %]

  [% END %]
[% END %]


<!-- //////////////////////////////// KEY ////////////////////////////////// -->

[% IF config.key %]

  [% key_box_size = 12 %]
  [% key_count = 1 %]
  [% key_padding = 5 %]
  [% x_off = 0 %]
  [% y_off = 0 %]

  [% IF key_position == 'h' %]
    <!-- position key left or right -->
    [% IF config.key_placement == 'R' %]
      [% x_off = x + r + x_key_start %]
      [% y_off = (y - r) %]
    [% ELSE %]
      [% x_off = x_key_start %]
      [% y_off = (y - r) %]
    [% END %]
  [% ELSIF key_position == 'v' %]
    <!-- only allow key under or over chart if the height dimensions are greatest -->
    [% IF w < h && config.key_placement == 'R' OR config.key_placement == 'L' %]
      [% config.key_placement = 'T' %]
    [% END %]
    <!-- calc y position of start of key -->
    [% y_key = padding %]
    [% x_key = padding %]
    [% IF key_count == 7 || key_count == 13 %]
      <!-- wrap key every 3 entries -->
      [% x_key = x_key + (w / 3) %]
      [% y_key = y_key - (key_box_size * 8) - 6 %]
    [% END %]
    [% IF config.key_placement == 'T' %]
      [% x_off = x_key %]
      [% y_off = y_key %]
    [% ELSE %]
      [% x_off = x_key %]
      [% y_off = (r * 2) + (padding * 2) + y_key %]
    [% END %]
  [% END %]

  [% FOREACH field = config.fields %]
    [% IF total == 0 %]
      [% percent = 0 %]
    [% ELSE %]
      [% percent = (100 / total) * data.0.data.$field FILTER format('%2.0f')%]
    [% END %]
    <rect x="[% x_off %]" y="[% y_off + (key_box_size * key_count) + (key_count * key_padding) %]" width="[% key_box_size %]" height="[% key_box_size %]" class="[% IF config.style_sheet_field_names %][% field %]_key[% ELSE %]key[% key_count %][% END %]"/>
    <text x="[% x_off + key_box_size + key_padding %]" y="[% y_off + (key_box_size * key_count) + (key_count * key_padding) + key_box_size %]" class="keyText">[% IF config.show_key_data_labels %][% field %][% END %] [% IF config.show_key_actual_values %][[% data.0.data.$field %]][% END %] [% IF config.show_key_percent %][% percent %]%[% END %]</text>
    [% key_count = key_count + 1 %]
  [% END %]

[% END %]


<!-- //////////////////////////////// MAIN TITLES ////////////////////////// -->

<!-- main graph title -->
[% IF config.show_graph_title %]
  <text x="[% x %]" y="15" class="mainTitle">[% config.graph_title %]</text>
[% END %]

<!-- graph sub title -->
[% IF config.show_graph_subtitle %]
  [% IF config.show_graph_title %]
    [% y_subtitle = 30 %]
  [% ELSE %]
    [% y_subtitle = 15 %]
  [% END %]
  <text x="[% x %]" y="[% y_subtitle %]" class="subTitle">[% config.graph_subtitle %]</text>
[% END %]

</svg>
