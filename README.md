# gdb-load-ovl
Utility for loading individual overlays while debugging OoT using GDB

Usage:  
In a gdb console with the script loaded, enter:  
```
ovl ENUM_NAME
```
where `ENUM_NAME` corresponds to some overlay in the source code of the game.  

This tool currently supports:
- Actors
- Gamestates
- Effects
- The pause menu

A note for the pause menu: There is no enum currently in OoT that corresponds to the pause menu. Because of this the following hardcoded enum names will work:
- `PAUSE`
- `KALEIDO`
- `KALEIDO_SCOPE`

The script can also automatically load overlays into gdb as the game uses them. To do so, run `ovl auto on`. Disable with `ovl auto off`. The default is `off` (see `AUTOLOAD_ENABLED_BY_DEFAULT` in the script to change the default).

Note: This tool does not currently support overlays made up of multiple object files, but hopefully it will soon :)

***

To have gdb auto-load the script, you need the following:

In the oot directory, create a `.gdbinit` file with the following contents:
```
define target hookpost-remote
    source gdb_load_z64overlay.py
end
```
And in your home directory, create `~/.config/gdb/gdbinit` with the following contents:
```
add-auto-load-safe-path path/to/oot/.gdbinit
```
where `path/to/oot/` is your own path to the oot directory.
