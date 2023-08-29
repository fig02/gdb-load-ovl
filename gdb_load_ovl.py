#!/usr/bin/env python3

# Author: Fig
# Work based off of HailToDodongo's original tool: 
# https://github.com/HailToDodongo/oot/blob/daea8bacb27425a7dd8923dea6e0467ba68d1047/gdb_script.py
# License: CC0 (https://creativecommons.org/publicdomain/zero/1.0/)

import gdb
import re

TYPE_U32 = gdb.lookup_type('u32')

def GetAllocAddress(table, index):
    return int(table[index]["loadedRamAddr"].cast(TYPE_U32))

def AddOverlaySymbols(alloc_address):
    if alloc_address == 0:
        print("ERROR: Requested overlay is not currently loaded")
        return
    
    print("Loading symbols for actor at ", alloc_address)
    # get first symbol-name starting from vramStart (usually the first function in the overlay)
    target_func_name = gdb.execute("info symbol vramStart", False, True).partition(' ')[0].rstrip()

    # get section in main ELF (returns: "EnKusa_SetupAction in section ..ovl_En_Kusa of zelda_ocarina_mq_dbg.elf")
    ovl_sec_name = gdb.execute("info sym " + target_func_name, False, True)
    # extract section name (@TODO: check if there is a direct API for this)
    ovl_sec_name = ovl_sec_name.partition('section ..')[2].partition(" ")[0].rstrip()

    ovl_address_text   = get_section_address(ovl_sec_name, "Text")
    ovl_address_data   = get_section_address(ovl_sec_name, "Data")
    ovl_address_rodata = get_section_address(ovl_sec_name, "RoData")
    ovl_address_bss    = get_section_address(ovl_sec_name, "Bss")

    ovl_offset_text   = alloc_address
    ovl_offset_data   = alloc_address + (ovl_address_data   - ovl_address_text)
    ovl_offset_rodata = alloc_address + (ovl_address_rodata - ovl_address_text)
    ovl_offset_bss    = alloc_address + (ovl_address_bss    - ovl_address_text)

    # get full object-file path that contains the first symbol
    target_filename = gdb.lookup_symbol(target_func_name)[0].symtab.filename
    obj_name = "build/" + target_filename[:-1] + "o"

    obj_address_map[hex(alloc_address)] = obj_name
    print("Loading overlay: ", obj_name, "(text:", hex(ovl_offset_text), " data:", hex(ovl_offset_data), " rodata:", hex(ovl_offset_rodata), " bss:", hex(ovl_offset_bss), ")")

    gdb.execute("add-symbol-file -readnow " + obj_name +
      " -o 0xFF000000" +
      " -s .text "   + hex(ovl_offset_text)   +
      " -s .data "   + hex(ovl_offset_data)   +
      " -s .rodata " + hex(ovl_offset_rodata) +
      " -s .bss "    + hex(ovl_offset_bss),
      False, True)

class LoadOvlCmd(gdb.Command):
    def __init__(self):
        super().__init__("ovl", gdb.COMMAND_DATA, gdb.COMPLETE_EXPRESSION)

    def invoke(self, arg, from_tty):
        arg = arg.upper()

        if arg == "PAUSE" or arg == "KALEIDO" or arg == "KALEIDO_SCOPE":
            # Pause menu does not have an enum, special case it. Index is 0 in `gKaleidoMgrOverlayTable`
            table = gdb.lookup_global_symbol("gKaleidoMgrOverlayTable").value()
            AddOverlaySymbols(GetAllocAddress(table, 0))
        elif arg == "ACTOR_PLAYER":
            # Player's index does not correspond to his actor ID, Special case it. Index is 1 in `gKaleidoMgrOverlayTable`
            table = gdb.lookup_global_symbol("gKaleidoMgrOverlayTable").value()
            AddOverlaySymbols(GetAllocAddress(table, 1))
        else:
            # try to get the index from the elf via gdb
            try:
                index = gdb.lookup_symbol(arg)[0].value().cast(TYPE_U32)
            except:
                print("ERROR: Provided enum value could not be found in the elf")
                return

            pattern = r'^([^_]+)'
            matches = re.findall(pattern, arg)
            ovl_type = matches[0]

            if ovl_type == "GAMESTATE":
                table = gdb.lookup_global_symbol("gGameStateOverlayTable").value()
            elif ovl_type == "ACTOR":
                table = gdb.lookup_global_symbol("gActorOverlayTable").value()
            elif ovl_type == "EFFECT":
                table = gdb.lookup_global_symbol("gEffectSsOverlayTable").value()
            else:
                raise Exception("Type of enum provided is not supported")

            AddOverlaySymbols(GetAllocAddress(table, index))

LoadOvlCmd()
