# gdb-load-ovl
Utility for loading individual overlays while debugging OoT using GDB

Usage:  
In a gdb console with the script loaded, enter:  
```
ovl ENUM_NAME
```
where `ENUM_NAME` corresponds to some overlay in the source code of the game.  

(note: `ovl` is a base command in gdb. Using this script will override its functionality. If you still want access to it, change the command name)

This tool currently supports:
- Actors
- Gamestates
- Effects
- The pause menu
  

A note for the pause menu: There is no enum currently in OoT that corresponds to the pause menu. Because of this the following hardcoded enum names will work:
- `PAUSE`
- `KALEIDO`
- `KALEIDO_SCOPE`
  
Note: This tool does not currently support overlays made up of multiple object files, but hopefully it will soon :)

***

To change versions of the game, enter the following command:
```
ver version-string
```
Where `version-string` corresponds to one of the following:
- gc-eu-mq-dbg
- gc-eu-mq
- gc-eu
- gc-us

The default version is gc-eu-mq-dbg.

***

To have gdb auto-load the script, you need the following:

In the oot directory, create a `.gdbinit` file with the following contents:
```
define target hookpost-remote
    source gdb_load_ovl.py
end
```
And in your home directory, create `~/.config/gdb/gdbinit` with the following contents:
```
add-auto-load-safe-path path/to/oot/.gdbinit
```
where `path/to/oot/` is your own path to the oot directory.