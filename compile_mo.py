import struct


def unescape(s):
    return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\').replace('\\"', '"')


def compile_mo(po_path, mo_path):
    catalog = {}
    msgid = None
    msgstr_lines = []
    in_msgid = False
    in_msgstr = False

    with open(po_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('msgid "') and not line.startswith('msgid_plural'):
                if msgid is not None and msgstr_lines:
                    msgstr = unescape(''.join(msgstr_lines))
                    mid = unescape(msgid)
                    if msgstr:
                        catalog[mid] = msgstr
                msgid = line[7:-1]
                msgstr_lines = []
                in_msgid = True
                in_msgstr = False
            elif line.startswith('msgstr "'):
                in_msgstr = True
                in_msgid = False
                msgstr_lines = [line[8:-1]]
            elif line.startswith('"') and line.endswith('"'):
                if in_msgid:
                    msgid += line[1:-1]
                elif in_msgstr:
                    msgstr_lines.append(line[1:-1])
            elif not line.strip():
                if msgid is not None and msgstr_lines:
                    msgstr = unescape(''.join(msgstr_lines))
                    mid = unescape(msgid)
                    if msgstr:
                        catalog[mid] = msgstr
                msgid = None
                msgstr_lines = []
                in_msgid = False
                in_msgstr = False

    if msgid is not None and msgstr_lines:
        msgstr = unescape(''.join(msgstr_lines))
        mid = unescape(msgid)
        if msgstr:
            catalog[mid] = msgstr

    keys = sorted(catalog.keys())
    N = len(keys)
    orig = [k.encode('utf-8') for k in keys]
    trans = [catalog[k].encode('utf-8') for k in keys]

    orig_table_offset = 28
    trans_table_offset = 28 + N * 8
    strings_offset = 28 + N * 16

    orig_strings = b''
    orig_offsets = []
    for s in orig:
        orig_offsets.append((len(s), strings_offset + len(orig_strings)))
        orig_strings += s + b'\x00'

    trans_strings_offset = strings_offset + len(orig_strings)
    trans_strings = b''
    trans_offsets = []
    for s in trans:
        trans_offsets.append((len(s), trans_strings_offset + len(trans_strings)))
        trans_strings += s + b'\x00'

    output = struct.pack('<I', 0x950412de)
    output += struct.pack('<I', 0)
    output += struct.pack('<I', N)
    output += struct.pack('<I', orig_table_offset)
    output += struct.pack('<I', trans_table_offset)
    output += struct.pack('<I', 0)
    output += struct.pack('<I', 0)
    for length, offset in orig_offsets:
        output += struct.pack('<II', length, offset)
    for length, offset in trans_offsets:
        output += struct.pack('<II', length, offset)
    output += orig_strings
    output += trans_strings

    with open(mo_path, 'wb') as f:
        f.write(output)
    print(f'Compiled {N} translations -> {mo_path}')


compile_mo(
    r'locale\ar\LC_MESSAGES\django.po',
    r'locale\ar\LC_MESSAGES\django.mo',
)
