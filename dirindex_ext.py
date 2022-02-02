import struct
from collections import namedtuple

# v2 spec
'''
DIRINDEXv2.0
# header
[u64: number of entries]
[u64: path table offset]
[u64: path table size]
[u64: meta table offset]

# path table
for entry in range(number of entries):
    [u64: path byte count]
    [u64: symlink byte count]
    [path] [symlink]

# meta table (byte count = 36 * number of entries) 
for entry in range(number of entries):
    [u64: path offset]
    [u32: mode]
    [u32: uid]
    [u32: gid]
    [i64: size]
    [u64: mtime]
'''

class AutoStruct(object):
    def __init__(self, struct_format, name, fields):
        self.struct = struct.Struct(struct_format)
        self.named_tuple = namedtuple(name, fields)
        self.size = self.struct.size
    
    def unpack(self, raw):
        return self.named_tuple(*self.struct.unpack(raw))
    def read(self, fob):
        return self.unpack(fob.read(self.size))
    def read_iter(self, raw):
        # continuously read `struct` from raw until all data is consumed
        entries = []
        i = 0
        while i < len(raw) // self.size:
            entries.append(self.unpack(raw[i*self.size:(i+1)*self.size]))
        return entries
    def pack(self, data):
        return self.struct.pack(*data)

# num_of_entries, path_table_offset, meta_table_offset
DI_V2_HEADER = AutoStruct('<QQQQ', 'Header', 
    'entry_count path_table_offset path_table_size meta_table_offset')
DI_V2_PATH_ENTRY_HEAD = AutoStruct('<QQ', 'PathEntryHead', 'path_size symlink_size' )
DI_V2_META_ENTRY = AutoStruct('<QIIIqQ', 'MetaEntry', 
    'path_offset mode uid gid size mtime')

def read_dirindex_v2(fob, di_class):
    di = di_class()
    # read header
    header = DI_V2_HEADER.read(fob)

    # read raw path table
    fob.seek(header.path_table_offset + DI_V2_HEADER.size)
    raw_path_table = fob.read(header.path_table_size)

    # read meta table
    fob.seek(header.meta_table_offset + DI_V2_HEADER.size)
    raw_meta_table = fob.read(DI_V2_META_ENTRY.size * header.size)
    meta = DI_V2_META_ENTRY.read_iter(raw_meta_table)

    for entry in meta:
        # read path
        offset = entry.path_offset
        path_header = DI_V2_PATH_ENTRY_HEAD.unpack(
                raw_path_table[offset:offset + DI_V2_PATH_ENTRY_HEAD.size])

        offset += DI_V2_PATH_ENTRY_HEAD.size
        path = raw_path_table[offset:offset+path_header.path_size]
        # ... and symlink
        offset += path_header.path_size
        symlink = raw_path_table[offset:offset+path_header.symlink_size]

        # add it to dirindex object
        di[path] = di_class.Record(
            path = path,
            mod = entry.mode,
            uid = entry.uid,
            gid = entry.gid,
            size = entry.size,
            mtime = entry.mtime,
            symlink = symlink if symlink else None
        )

def write_dirindex_v2(path, di):
    raw_path_table = ''
    raw_meta_table = ''
    path_offset = 0
    for record in di:
        # write a meta entry to the meta table
        raw_meta_table += DI_V2_META_ENTRY.pack((
            path_offset, record.mod, record.uid,
            record.uid, record.gid, record.size,
            record.mtime
        ))
        # write path data to path table
        path_data = DI_V2_PATH_ENTRY_HEAD.pack((
            len(record.path),
            len(record.symlink) if record.symlink is not None else 0
        )) + record.path
        if record.symlink is not None:
            path_data += record.symlink

        raw_path_table += path_data
        # inc path_offset, by the size of the last path added
        path_offset += len(path_data)

    with open(path, 'wb') as fob:
        # write the header, the path table and the meta table
        fob.write(
            'DIRINDEXv2.0\n' +
            DI_V2_HEADER.pack((
                len(di), 0, len(raw_path_table), len(raw_path_table)
            )) + raw_path_table + raw_meta_table
        )

def read_dirindex(path, di_class):
    with open(path, 'rb') as fob:
        magic = fob.readline().rstrip()
        if magic in DI_MAGICS:
            return DI_MAGICS[magic][0](fob, di_class)
        else:
            return di_class(path, check_version=False)

def write_dirindex(path, di, version):
    with open(path, 'wb') as fob:
        rw = VERSION_MAP.get(version, None)
        if rw is None:
            di.save(path)
        else:
            rw[1](path, di)

DI_MAGICS = {
        'DIRINDEXv2.0': (read_dirindex_v2, write_dirindex_v2)
}
VERSION_MAP = {
        '1': None,
        '2': (read_dirindex_v2, write_dirindex_v2)
}
