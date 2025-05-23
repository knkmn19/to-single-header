# simple inline .h files tool
import sys
import os

g_input_path = sys.argv[1]
g_output_path = sys.argv[2]
g_flags = 0
flags_dict = {
    "KEEP_INCLUDES" : (1 << 0),
    "KEEP_GUARDS"   : (1 << 1),
    "EXTRA_INFO"    : (1 << 2),
}

if len(sys.argv) > 3:
    for i in range(3, len(sys.argv)):
        g_flags |= flags_dict[sys.argv[i]] if sys.argv[i] in flags_dict else 0x00

def enabled(flag):
    global g_flags
    return (flag in flags_dict) and (g_flags & flags_dict[flag])

g_stdafx_input = ""
g_stdafx_notes = ""
g_stdafx_output = ""

g_input_dir = os.path.dirname(g_input_path)
g_output_dir = os.path.dirname(g_output_path)

with open(g_input_path, "r", encoding="utf-8") as file:
    g_stdafx_input = file.read().strip().split('\n')

def add_inline_note(note):
    global g_stdafx_notes
    g_stdafx_notes += "// " + note + '\n'

def is_include_directive(s):
    return string_begins_with(s, '#include "')

def string_begins_with(s, target):
    s = s.strip()
    return (len(s) >= len(target)) and (s[:len(target)] == target)

def parse_include_directive(s):
    header_incl_dir = s.split('"')[1].split('/')
    path_fragments = [g_input_dir] + header_incl_dir
    header_path = os.path.join(*path_fragments)
    return header_path

def get_header_code(filename):
    contents = ""
    with open(filename, "r", encoding="utf-8") as file:
        contents = file.read().strip().split('\n')
    
    output_list = []
    if (enabled("EXTRA_INFO")):
        output_list.append("// {0}".format(filename))
    
    # discard header guards
    guard_macro = ""
    header_guard_removed = False
    endif_indices = []
    print(filename, "begin")
    for i in range(len(contents)):
        if not (enabled("KEEP_GUARDS")):
            # case for the #define GUARD
            if (guard_macro != "" and not header_guard_removed):
                header_guard_removed = True
                print(guard_macro)
                continue
            
            # case for the #ifndef GUARD
            elif (
                not header_guard_removed                       and
                i + 1 < len(contents)                          and
                string_begins_with(contents[i], "#ifndef")     and
                string_begins_with(contents[i + 1], "#define")
            ):
                if (
                    contents[i].split()[1] == contents[i + 1].split()[1]
                ):
                    guard_macro = contents[i].split()[1]
                    continue
            
            # pragma once case
            elif string_begins_with(contents[i], "#pragma once"):
                header_guard_removed = True
                continue
            
            elif string_begins_with(contents[i], "#endif"):
                endif_indices.append(len(output_list))
        
        if (
            (not enabled("KEEP_INCLUDES")) and
            (string_begins_with(contents[i], "#include"))
        ):
            add_inline_note("include directive found at l{0} in {1}".format(i, filename))
            add_inline_note(contents[i])
            add_inline_note("")
            continue
        
        output_list.append(contents[i])
    
    if guard_macro != "" and header_guard_removed:
        # last endif must be related to header guard
        print(filename, endif_indices)
        print(filename, output_list)
        print(filename, len(output_list))
        print(output_list[endif_indices[-1]])
        output_list.pop(endif_indices[-1])
    elif not ((header_guard_removed) or (enabled("KEEP_GUARDS"))):
        add_inline_note("no header guard was found for {0}".format(filename))
        add_inline_note("")
        
    # add_inline_note(len(endif_indices))
    out = '\n'.join(output_list)
    return out.strip() + '\n'

def get_inlined_header_data(s):
    inlined_data = s
    if not is_include_directive(s):
        return s
    
    include_directive_full_path = parse_include_directive(s)
    inlined_data = get_header_code(include_directive_full_path)
    return inlined_data

add_inline_note("parser notes will be put here if any:")

for line in g_stdafx_input:
    g_stdafx_output += get_inlined_header_data(line) + "\n"

add_inline_note("")

g_stdafx_output = g_stdafx_notes + '\n' + g_stdafx_output

print(g_stdafx_output)
with open(g_output_path, "w", encoding="utf-8") as file:
    file.write(g_stdafx_output)
