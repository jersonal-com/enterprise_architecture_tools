# Generate capability maps for Enterprise Architecture

This is a tool that I have quickly put together to create capability
maps for an enterprise architecture discussion. 

To learn more about the usage of these maps have a look at my 
website at https://enterprise-architecture-book.com

The tool is licensed under the [GPL version 3](https://www.gnu.org/licenses/gpl-3.0.html) or later. 

In order to use the tool you have to create a capability file that 
follows the following structure:

```
Toplevel
    Sublevel
        SubSublevel
        [identifier]Another Sublevel
---
SubSublevel,complexity,1
identifier,complexity,5
SubSublevel,cost,3
identifier,cost,4
```

The map itself is defined in the top part by changing the order and the indentation 
of the individual lines. To make renaming capabilities easier an identifier can be
put at the beginning of the line. 

After the `---` comes a CSV-file that has the identifier or the capability name in the
first column, then the identifier of the parameter and finally the number representing
this parameter. 


## Calling the program

The application is called on the command line with the following parameters:

```
generate_capability_map.py [-h] [-o OUTPUT] [-t TITLE] [-c CRITERIA] [-r RESTRICT] [-m MAX] [-x MAP] [-b BUBBLE] [-n BUBBLEMAX] [-y BUBBLEMAP] [-l HEIGHT] [-w WIDTH] input
```

Obviously the input filename is mandatory. 

It is also mandatory to set a criteria or parameter with `-c`. In the example above the
two options would be `-c cost` or `-c complexity`. 

Using the `-o` parameter the SVG output filename can be changed from the standard output.svg. 

With the `-r` parameter the granularity of the capabilty map is limited to only a particular level. 

For coloring the boxes there are currently 2 options: `-x heatmap` uses a red-yellow-green 
heatmap and `-x blues` uses a gradient of lighter to darker blue tones. 

The maximum value is set with `-m 5` -- in this case any number above 5
would be colorcoded according to the last value of the gradient. 

### Bubbles

Besides the color of the boxes one can add small "bubbles" on each capability box
to indicate a second parameter. These follow the same logic as the coloring of the
boxes:

```
  -b BUBBLE, --bubble BUBBLE
                        Criteria used for bubble (default: )
  -n BUBBLEMAX, --bubblemax BUBBLEMAX
                        Maximum value for bubbles (default: 10)
  -y BUBBLEMAP, --bubblemap BUBBLEMAP
                        Color mapping for bubbles (default: heatmap)
```

With the `-l HEIGHT` and `-w WIDTH` you chan change the height and width of these bubbles. 


## Contributions

The code is only a quick hack at the moment - all kind of contributions are welcome. 


