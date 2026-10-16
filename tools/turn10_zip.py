import struct, zlib, io, zipfile, os

def create_turn10_zip(source_zip_path, target_zip_path, replacements=None):
    """
    Repacks or updates a Turn 10 asset ZIP archive, ensuring every single file
    in the Central Directory has the exact Turn 10 0x1123 direct streaming offset tag.
    
    replacements: dict of { internal_path: bytes_data }
    """
    if replacements is None:
        replacements = {}

    with open(source_zip_path, 'rb') as f:
        src_bytes = f.read()

    src_z = zipfile.ZipFile(io.BytesIO(src_bytes))
    
    out_bio = io.BytesIO()
    cd_entries = []

    for info in src_z.infolist():
        fn = info.filename
        if fn in replacements:
            uncompressed_data = replacements[fn]
        else:
            uncompressed_data = src_z.read(fn)

        fn_bytes = fn.encode('utf-8')
        fn_len = len(fn_bytes)

        # Deflate data
        compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15, memLevel=8, strategy=zlib.Z_DEFAULT_STRATEGY)
        compressed_data = compressor.compress(uncompressed_data) + compressor.flush()

        crc = zlib.crc32(uncompressed_data)
        uncompressed_size = len(uncompressed_data)
        compressed_size = len(compressed_data)

        local_header_offset = out_bio.tell()

        # Local File Header: exlen = 0
        local_hdr = struct.pack(
            '<4sHHHHHIIIHH',
            b'PK\x03\x04',
            20, # version needed
            0,  # flags
            8,  # compression method (Deflate)
            info.date_time[3] << 11 | info.date_time[4] << 5 | (info.date_time[5] // 2), # time
            (info.date_time[0] - 1980) << 9 | info.date_time[1] << 5 | info.date_time[2], # date
            crc,
            compressed_size,
            uncompressed_size,
            fn_len,
            0 # exlen = 0
        )
        out_bio.write(local_hdr)
        out_bio.write(fn_bytes)

        payload_offset = out_bio.tell()
        out_bio.write(compressed_data)

        # Build Central Directory Extra field with 0x1123 tag pointing to payload_offset
        extra_1123 = struct.pack('<HHI', 0x1123, 4, payload_offset)

        cd_hdr = struct.pack(
            '<4sHHHHHHIIIHHHHHII',
            b'PK\x01\x02',
            20, # version made by
            20, # version needed
            0,  # flags
            8,  # method
            info.date_time[3] << 11 | info.date_time[4] << 5 | (info.date_time[5] // 2),
            (info.date_time[0] - 1980) << 9 | info.date_time[1] << 5 | info.date_time[2],
            crc,
            compressed_size,
            uncompressed_size,
            fn_len,
            len(extra_1123),
            0, # comment len
            0, # disk start
            0, # internal attrs
            0, # external attrs
            local_header_offset
        )
        cd_entries.append((cd_hdr, fn_bytes, extra_1123))

    cd_start_offset = out_bio.tell()
    for cd_hdr, fn_bytes, extra in cd_entries:
        out_bio.write(cd_hdr)
        out_bio.write(fn_bytes)
        out_bio.write(extra)

    cd_size = out_bio.tell() - cd_start_offset

    # End of Central Directory Record
    eocd = struct.pack(
        '<4sHHHHIIH',
        b'PK\x05\x06',
        0, # disk num
        0, # cd disk
        len(cd_entries), # disk entries
        len(cd_entries), # total entries
        cd_size,
        cd_start_offset,
        0 # comment len
    )
    out_bio.write(eocd)

    with open(target_zip_path, 'wb') as f:
        f.write(out_bio.getvalue())

    print(f"Created Turn 10 ZIP: {target_zip_path} ({os.path.getsize(target_zip_path)} bytes, {len(cd_entries)} entries)")

if __name__ == '__main__':
    # Test on RadioStations.zip.bak
    test_target = r'C:\Users\uwu\Downloads\radiounder\test_t10.zip'
    create_turn10_zip('media/ui/textures/hires/data_bound/RadioStations.zip.bak', test_target)
    
    # Verify with zipfile
    with open(test_target, 'rb') as f:
        test_bytes = f.read()
    test_z = zipfile.ZipFile(io.BytesIO(test_bytes))
    print("Verification:")
    for info in test_z.infolist():
        tag, length, off = struct.unpack('<HHI', info.extra)
        print(f"  {info.filename}: tag={hex(tag)}, payload_off={off}")
