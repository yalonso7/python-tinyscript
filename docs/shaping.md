## Metadata

Metadata can be defined using *dunders* (double underscore variables) at the very beginning of the script/tool and is used by Tinyscript to format the help message.

```python
from tinyscript import *

__script__    = "MyScript"
__author__    = "John Doe"
__copyright__ = "John Doe Inc."
__email__     = "john.doe@example.com"
__license__   = "agpl-3.0"
__version__   = "1.0"
__reference__ = "..."
__source__    = "..."
__training__  = "..."
__examples__  = ["..."]
__doc__       = "This tool ..."

initialize()
```

This gives the following help message:

```sh hl_lines="2 3 4 5 6 7 8 12 19"
$ python tool.py -h
MyScript v1.0
Author   : John Doe (john.doe@example.com)
Copyright: © 2020 John Doe Inc.
License  : GNU Affero General Public License v3.0
Reference: ...
Source   : ...
Training : ...

usage: tool [-h] [-v]

This tool ...

extra arguments:
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  python tool.py ...
```

If not using `__script__`, the name of the script will be used taking a format into account. This format is defined by the `SCRIPTNAME_FORMAT` constant and defaults to "`slugified`". The possible values are:

- `acronym`: split the name on whitespaces, hyphens and underscores then make an acronym from the collected tokens (e.g. "`my-super-script`" becomes "`MSS`")
- `as_is`: do not modify the name
- `none`: equivalent to "`as_is`"
- `slugified`: split the name on whitespaces, hyphens and underscores then capitalize and gather the collected tokens (e.g. "`my-script`" becomes "`MyScript`")

[See example here](examples/metadata.md)

For more detailed information about metadata fields, see [this section](usage.html#customization).

-----

## Help message styling

Help can be formatted using multiple markup languages for making the help text more user-friendly with colors and styling. This is configured by using the `__docformat__` dunder (which can also be `None`, meaning no formatting). This feature is supported by [`mdv`](https://github.com/axiros/terminal_markdown_viewer) and the theme can be tuned by using the constant `DOCFORMAT_THEME`.

Currently, the following markup languages are supported: HTML, Markdown, RestructuredText and Textile.

```python hl_lines="2 4"
...
__docformat__ = "html"  # None|"md"|"rst"|"textile"
...
DOCFORMAT_THEME = "Star"
...
```

!!! warning "Various formats support"
    
    The support for HTML, RestructuredText and Textile is based on document conversion with ['pypandoc'](https://pypi.org/project/pypandoc/) to get Markdown before using [`mdv`](https://github.com/axiros/terminal_markdown_viewer). In some cases with complex formate text, Pandoc can cause issues with indentation or break the layout. It is then advised to only use Markdown directly to avoid any conversion.

!!! note "List of themes"
    
    Unfortunately, the documentation of [`mdv`](https://github.com/axiros/terminal_markdown_viewer) is a bit poor. However, one can find the names of the available themes in [this JSON](https://github.com/axiros/terminal_markdown_viewer/blob/master/mdv/ansi_tables.json).

-----

## Script banner

Displaying a banner can be achieved in two ways:

- by passing a keyword argument `add_banner=True` ; in this case, a random font is used

```python hl_lines="3"
    ...
    initialize(...
               add_banner=True,
               ...)
    ...
```

- by defining the `BANNER_FONT` constant

The `BANNER_STYLE` constant also allows to style the banner with the following properties:

- `adjust`: can be `left` | `center` | `right` ; by default, the banner is centered
- `bgcolor`: determines the background color
- `fgcolor`: determines the foreground color

```python hl_lines="2 3"
...
BANNER_FONT = "roman"
BANNER_STYLE = {'adjust': "right", 'fgcolor': "blue"}
...
```

-----

## Multi-level debugging

This is achieved by passing a keyword argument `multi_level_debug=[boolean]` to `initialize(...)`.

```python hl_lines="3"
    ...
    initalize(...
              multi_level_debug=True,
              ...)
    ...
```

This modifies the classical `-v`/`--verbose` option to `-v`/`-vv`/`-vvv`.

!!! note "Debug levels"

    - '': `logging.ERROR`
    - `-v`: `logging.WARNING`
    - `-vv`: `logging.INFO`
    - `-vvv`: `logging.DEBUG`

[See example here](examples/multi-level-debug.md)

-----

## Extended logging options

This is achieved by passing a keyword argument `ext_logging=[boolean]` to `initialize(...)`.

```python hl_lines="3"
    ...
    initalize(...
              ext_logging=True,
              ...)
    ...
```

This adds multiple options:

- `-f`, `--logfile`: This sets the log filename for saving logging messages.
- `-r`, `--relative`: This sets the log timestamps to the time relative to the start of the execution.
- `-s`, `--syslog`: This allows to save the log messages to `/var/log/syslog` (Linux only).

-----

## Multi-level help

This is achieved by setting the `__details__` metadata at the beginning of the script.

```python hl_lines="2 3 4 5"
    ...
    __details__ = [
    """Extra documentation, displayed when using -hh. """,
    """Other extra documentation, displayed when using -hhh. """
    ]
    ...
    initalize(...)
    ...
```

This modifies the classical `-h`/`--help` option to `-h`/`-hh`/`-hhh`.

!!! note "Help levels"

    - `-h`: classical help message
    - `-hh`: classical help message + first string in __details__ list
    - `-hhh`: classical help message + first and second strings in __details__ list
    
    Note: Strings beyond the two first elements of `__details__` are not handled by purpose.

[See example here](examples/multi-level-help.md)

-----

## Short/Long help

This is enabled by the `short_long_help` parameter of `initialize(...)` and is set to `True` by default.

```python hl_lines="3"
...
initalize(...
          short_long_help=False,
          ...)
...
```

When set to `True`, `-h` only displays usage information and `--help` shows the full help message. If `False`, `-h` and `--help` both displays the full help message.
