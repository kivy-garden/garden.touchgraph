![screenshot](https://raw.githubusercontent.com/wackazong/garden.touchgraph/master/screenshot_big.png)

# Touchgraph

TouchGraph is a Kivy widget for displaying a 2D graph based composed of
a number of interconnectedstraight lines. The user can adjust the form 
of the graph in order to define a function. Is is based on the ```bezier.py```
example from the Kivy examples.

A use case for this widget is the situation where a functional relationship
between two variables (e.g. a sensor reading like temperature and a desired 
reaction like fan speed) needs to be defined by the user.

# Features

* user-defined tickmarks and labels
* static function provided for using the defined graph (```y_for_x()```)
* input validation for points provided

# Install

Install the touchgraph garden module using the `garden` tool:

```
garden install touchgraph
```

# Usage

The following parameters are available:

## points

Pass a list of points as ```[x1, y1, x2, y2, ...]``` to define the default
function. Points do not have to start at (0,0) although it makes sense to 
start x with 0. x values must be in ascending order.

## x_ticks, y_ticks (optional)

Defines where tickmarks should be placed. If x_labels or y_labels is not
defined, the ticks are labeled with the value of x or y.

## x_labels, y_labels (optional)

Text labels for the tickmarks.

## max_y

Maximum value for the y-axis, if the default function does not reach the maximum value

## line_width (optional)

Line width of the displayed graph

## font_size (optional)

Font size for the labels

## pointColor, lineColor, backColor (optional)

Color values for the different parks of the graph
