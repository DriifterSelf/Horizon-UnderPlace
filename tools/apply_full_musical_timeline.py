import os, sys, struct
import xml.etree.ElementTree as ET

MOD_DIR = r"C:\Users\uwu\Downloads\radiounder"
GAME_DIR = r"F:\SteamLibrary\steamapps\common\ForzaHorizon4"

if MOD_DIR not in sys.path:
    sys.path.append(MOD_DIR)

import fsb5

# ====================================================================
# COMPREHENSIVE MUSICAL TIMELINE FOR ALL 20 TRACKS (IN SECONDS)
# Analyzed by musical phrasing, BPM, arrangement structure, and game triggers:
# - TrackStart: 0.0s
# - DJDrop: Point where intro radio DJ ducks/cuts before the beat drop
# - TrackDrop: Primary beat/kick drop (countdown 3-2-1-GO lands here!)
# - TrackLoopStart: Starting point of race loop (driving groove, not intro silence)
# - DJSegment: Mid-track dynamic valley/bridge (free roam DJ & Skill Song)
# - TrackBreakDown: Late-track bridge/buildup before the final drop
# - PostRaceLoopStart: Start of peak victory chorus/hook for podium screen
# - PostRaceLoopEnd: End of podium loop (energetic 32-44s loop)
# - TrackLoopEnd: End of race loop (loops back to TrackLoopStart if race is long)
# - StingerStart: Finish line trigger / outro transition (~3.0s before end)
# - DJStart: Free roam DJ begins talking over outro fade (~3.0s before end)
# - End: Final audio sample (SampleLength - 1)
# ====================================================================

TRACK_CUES = {
    0:  {
        "title": "KINK!", "artist": "White-oh, S-DEY!, Noisebro",
        "drop": 7.8, "dj_drop": 5.2, "loop_start": 7.8, "dj_mid": 92.0,
        "breakdown": 145.0, "pr_start": 149.0, "pr_end": 185.0, "loop_end": 185.0,
        "stinger_offset": 3.18
    },
    1:  {
        "title": "So what we get drunk? (Extended Version)", "artist": "Flvckka",
        "drop": 28.0, "dj_drop": 24.0, "loop_start": 28.0, "dj_mid": 174.0,
        "breakdown": 272.0, "pr_start": 324.0, "pr_end": 368.0, "loop_end": 400.0,
        "stinger_offset": 3.13
    },
    2:  {
        "title": "Pigmentos (feat. Amorpho)", "artist": "Cxsinensis",
        "drop": 16.2, "dj_drop": 13.0, "loop_start": 16.2, "dj_mid": 116.0,
        "breakdown": 150.0, "pr_start": 162.0, "pr_end": 198.0, "loop_end": 220.0,
        "stinger_offset": 2.91
    },
    3:  {
        "title": "Vainilla", "artist": "Cxsinensis",
        "drop": 30.0, "dj_drop": 26.0, "loop_start": 30.0, "dj_mid": 112.0,
        "breakdown": 165.0, "pr_start": 175.0, "pr_end": 208.0, "loop_end": 218.0,
        "stinger_offset": 3.23
    },
    4:  {
        "title": "CHROMEHEARTS", "artist": "KATSUU ENERGY, yakashi",
        "drop": 13.8, "dj_drop": 11.0, "loop_start": 13.8, "dj_mid": 92.0,
        "breakdown": 120.0, "pr_start": 128.0, "pr_end": 164.0, "loop_end": 180.0,
        "stinger_offset": 3.07
    },
    5:  {
        "title": "Nada Es Igual", "artist": "White OH, Noisebro",
        "drop": 15.0, "dj_drop": 12.0, "loop_start": 15.0, "dj_mid": 76.0,
        "breakdown": 112.0, "pr_start": 118.0, "pr_end": 150.0, "loop_end": 152.0,
        "stinger_offset": 2.82
    },
    6:  {
        "title": "UN MOMENTO", "artist": "i killed a leopard, yakashi & SMOK3",
        "drop": 14.5, "dj_drop": 11.5, "loop_start": 14.5, "dj_mid": 72.0,
        "breakdown": 135.0, "pr_start": 142.0, "pr_end": 174.0, "loop_end": 175.0,
        "stinger_offset": 2.98
    },
    7:  {
        "title": "Sola", "artist": "Saramalacara",
        "drop": 14.0, "dj_drop": 11.2, "loop_start": 14.0, "dj_mid": 96.0,
        "breakdown": 146.0, "pr_start": 154.0, "pr_end": 188.0, "loop_end": 195.0,
        "stinger_offset": 3.15
    },
    8:  {
        "title": "dormiré sin ti", "artist": "IZATKM",
        "drop": 17.0, "dj_drop": 13.5, "loop_start": 17.0, "dj_mid": 96.0,
        "breakdown": 142.0, "pr_start": 148.0, "pr_end": 180.0, "loop_end": 182.0,
        "stinger_offset": 3.10
    },
    9:  {
        "title": "portal 88", "artist": "3delincuentes, Noisebro",
        "drop": 15.0, "dj_drop": 12.0, "loop_start": 15.0, "dj_mid": 94.0,
        "breakdown": 142.0, "pr_start": 150.0, "pr_end": 182.0, "loop_end": 185.0,
        "stinger_offset": 2.99
    },
    10: {
        "title": "estupefacientes", "artist": "Depresión Sonora",
        "drop": 14.0, "dj_drop": 11.0, "loop_start": 14.0, "dj_mid": 102.0,
        "breakdown": 138.0, "pr_start": 148.0, "pr_end": 188.0, "loop_end": 198.0,
        "stinger_offset": 3.07
    },
    11: {
        "title": "50 Varos", "artist": "MICRO, Flakko La Tentacion",
        "drop": 15.0, "dj_drop": 12.0, "loop_start": 15.0, "dj_mid": 98.0,
        "breakdown": 142.0, "pr_start": 150.0, "pr_end": 186.0, "loop_end": 195.0,
        "stinger_offset": 3.35
    },
    12: {
        "title": "Cacti (feat. Amorpho)", "artist": "Cxsinensis",
        "drop": 31.5, "dj_drop": 27.0, "loop_start": 31.5, "dj_mid": 160.0,
        "breakdown": 240.0, "pr_start": 255.0, "pr_end": 295.0, "loop_end": 315.0,
        "stinger_offset": 3.39
    },
    13: {
        "title": "Buscándome", "artist": "Pato Shoucair & xHEIDIx",
        "drop": 30.5, "dj_drop": 26.0, "loop_start": 30.5, "dj_mid": 124.0,
        "breakdown": 175.0, "pr_start": 186.0, "pr_end": 226.0, "loop_end": 236.0,
        "stinger_offset": 3.10
    },
    14: {
        "title": "2000nunca", "artist": "Kirnbauer",
        "drop": 16.5, "dj_drop": 13.0, "loop_start": 16.5, "dj_mid": 78.0,
        "breakdown": 122.0, "pr_start": 130.0, "pr_end": 162.0, "loop_end": 166.0,
        "stinger_offset": 3.24
    },
    15: {
        "title": "teoría del tiempo", "artist": "AKRIILA & Gianluca",
        "drop": 14.0, "dj_drop": 11.0, "loop_start": 14.0, "dj_mid": 88.0,
        "breakdown": 138.0, "pr_start": 146.0, "pr_end": 178.0, "loop_end": 184.0,
        "stinger_offset": 3.16
    },
    16: {
        "title": "suerteceleste", "artist": "Noisebro, dreamly.",
        "drop": 11.5, "dj_drop": 9.0,  "loop_start": 11.5, "dj_mid": 86.0,
        "breakdown": 122.0, "pr_start": 130.0, "pr_end": 162.0, "loop_end": 170.0,
        "stinger_offset": 3.14
    },
    17: {
        "title": "Sola (House Alone Remix)", "artist": "Hillkidd & Mi Compa el Chino",
        "drop": 15.5, "dj_drop": 12.5, "loop_start": 15.5, "dj_mid": 108.0,
        "breakdown": 152.0, "pr_start": 164.0, "pr_end": 200.0, "loop_end": 210.0,
        "stinger_offset": 3.21
    },
    18: {
        "title": "p4ris", "artist": "3delincuentes & Kozta",
        "drop": 14.0, "dj_drop": 11.0, "loop_start": 14.0, "dj_mid": 98.0,
        "breakdown": 136.0, "pr_start": 144.0, "pr_end": 178.0, "loop_end": 195.0,
        "stinger_offset": 3.23
    },
    19: {
        "title": "SLOW", "artist": "Mi Compa el Chino",
        "drop": 15.5, "dj_drop": 12.0, "loop_start": 15.5, "dj_mid": 96.0,
        "breakdown": 138.0, "pr_start": 150.0, "pr_end": 186.0, "loop_end": 195.0,
        "stinger_offset": 3.24
    },
}

# ====================================================================
# STEP 1: UPDATE RadioInfo_MX.xml AND RadioInfo_EN.xml
# ====================================================================
for lang in ['MX', 'EN']:
    target_xml = os.path.join(GAME_DIR, f'media/audio/RadioInfo_{lang}.xml')
    tree = ET.parse(target_xml)
    root = tree.getroot()
    xs = root.find(".//RadioStation[@Name='Horizon XS']")
    sample_list = xs.find('SampleList')

    for slot_idx in range(20):
        elem = sample_list[slot_idx]
        tot = int(elem.attrib['SampleLength'])
        c = TRACK_CUES[slot_idx]
        
        drop_samp = int(c['drop'] * 48000)
        dj_drop_samp = int(c['dj_drop'] * 48000)
        loop_start_samp = int(c['loop_start'] * 48000)
        dj_mid_samp = int(c['dj_mid'] * 48000)
        brk_samp = int(c['breakdown'] * 48000)
        pr_start_samp = int(c['pr_start'] * 48000)
        pr_end_samp = int(c['pr_end'] * 48000)
        loop_end_samp = int(c['loop_end'] * 48000)
        stinger_samp = tot - int(c['stinger_offset'] * 48000)
        dj_start_samp = stinger_samp + 1000

        elem.set('TrackStart', '0')
        elem.set('DJDrop', str(dj_drop_samp))
        elem.set('TrackDrop', str(drop_samp))
        elem.set('TrackLoopStart', str(loop_start_samp))
        elem.set('DJSegment', str(dj_mid_samp))
        elem.set('PostRaceLoopStart', str(pr_start_samp))
        elem.set('TrackBreakDown', str(brk_samp))
        elem.set('PostRaceLoopEnd', str(pr_end_samp))
        elem.set('TrackLoopEnd', str(loop_end_samp))
        elem.set('StingerStart', str(stinger_samp))
        elem.set('DJStart', str(dj_start_samp))
        elem.set('End', str(tot - 1))

    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    xml_str = xml_str.replace('\n', '\r\n')
    with open(target_xml, 'wb') as f:
        f.write(b'\xef\xbb\xbf')
        f.write(xml_str.encode('utf-8'))
    print(f"Updated {target_xml} successfully!")

# ====================================================================
# STEP 2: REBUILD R4_Tracks.bank CHUNK 4 (11 NATIVE SYNCPOINTS)
# ====================================================================
current_bank_path = os.path.join(GAME_DIR, r'media\audio\fmodopus\x64\R4_Tracks.bank')
with open(current_bank_path, 'rb') as f:
    hdr_704 = bytearray(f.read(704))
    fsb_data = f.read()

fsb = fsb5.load(fsb_data)

orig_bank_path = os.path.join(GAME_DIR, r'media\audio\fmodopus\x64\R4_Tracks.bank.bak')
with open(orig_bank_path, 'rb') as f:
    f.seek(704)
    orig_fsb = fsb5.load(f.read())

repacked_samples = []
current_data_offset = 0

for slot_idx in range(20):
    s_curr = fsb.samples[slot_idx]
    s_orig = orig_fsb.samples[slot_idx]
    tot = s_curr.samples
    
    c = TRACK_CUES[slot_idx]
    drop_samp = int(c['drop'] * 48000)
    dj_drop_samp = int(c['dj_drop'] * 48000)
    loop_start_samp = int(c['loop_start'] * 48000)
    dj_mid_samp = int(c['dj_mid'] * 48000)
    brk_samp = int(c['breakdown'] * 48000)
    pr_start_samp = int(c['pr_start'] * 48000)
    pr_end_samp = int(c['pr_end'] * 48000)
    loop_end_samp = int(c['loop_end'] * 48000)
    stinger_samp = tot - int(c['stinger_offset'] * 48000)

    # 11 Native FMOD syncpoints strictly sorted by sample position
    markers = [
        (0, b'TrackStart'),
        (dj_drop_samp, b'DJDrop'),
        (drop_samp, b'TrackDrop'),
        (loop_start_samp, b'TrackLoopStart'),
        (dj_mid_samp, b'DJSegment'),
        (brk_samp, b'TrackBreakDown'),
        (pr_start_samp, b'PostRaceLoopStart'),
        (pr_end_samp, b'PostRaceLoopEnd'),
        (loop_end_samp, b'TrackLoopEnd'),
        (stinger_samp, b'StingerStart'),
        (tot - 1, b'End')
    ]
    markers.sort(key=lambda x: x[0])

    new_c4 = bytearray()
    for pos, name_b in markers:
        new_c4.extend(struct.pack('<I', pos))
        new_c4.extend(name_b.ljust(256, b'\x00'))

    assert len(new_c4) == 2860, f"Chunk 4 must be 2860 bytes, got {len(new_c4)}"

    vorbis_obj = s_curr.metadata[fsb5.MetadataChunkType.VORBISDATA]
    new_c11 = bytearray()
    new_c11.extend(struct.pack('<I', vorbis_obj.crc32))
    new_c11.extend(vorbis_obj.unknown)

    new_c13 = s_orig.metadata[13]

    chunks = [
        (4, bytes(new_c4)),
        (11, bytes(new_c11)),
        (13, bytes(new_c13))
    ]

    audio_data = s_curr.data
    pad_len = (16 - (len(audio_data) % 16)) % 16
    padded_audio = audio_data + (b'\x00' * pad_len)

    repacked_samples.append({
        'channels': s_curr.channels,
        'frequency': s_curr.frequency,
        'samples': tot,
        'data_offset': current_data_offset,
        'chunks': chunks,
        'audio_data': padded_audio
    })
    current_data_offset += len(padded_audio)

sample_headers_buf = bytearray()
for s in repacked_samples:
    freq_idx = 9
    channels_bit = s['channels'] - 1
    offset_val = s['data_offset'] // 16
    samples_val = s['samples']

    raw_q = (
        1 |
        (freq_idx << 1) |
        (channels_bit << 5) |
        ((offset_val & 0xFFFFFFF) << 6) |
        ((samples_val & 0x3FFFFFFF) << 34)
    )
    sample_headers_buf.extend(struct.pack('<Q', raw_q))

    chunks = s['chunks']
    for c_idx, (c_type, c_data) in enumerate(chunks):
        has_more = 1 if (c_idx < len(chunks) - 1) else 0
        c_len = len(c_data)
        c_hdr = (
            has_more |
            ((c_len & 0xFFFFFF) << 1) |
            ((c_type & 0x7F) << 25)
        )
        sample_headers_buf.extend(struct.pack('<I', c_hdr))
        sample_headers_buf.extend(c_data)

total_data_size = current_data_offset
sample_headers_size = len(sample_headers_buf)

fsb5_hdr = struct.pack(
    '<4sIIIIII8s16s8s',
    b'FSB5',
    1,
    20,
    sample_headers_size,
    0,
    total_data_size,
    15,
    orig_fsb.header.zero,
    orig_fsb.header.hash,
    orig_fsb.header.dummy
)

fsb_out_bytes = bytearray()
fsb_out_bytes.extend(fsb5_hdr)
fsb_out_bytes.extend(sample_headers_buf)
for s in repacked_samples:
    fsb_out_bytes.extend(s['audio_data'])

new_fsb_bytes = bytes(fsb_out_bytes)
new_fsb_size = len(new_fsb_bytes)

total_bank_size = 704 + new_fsb_size
struct.pack_into('<I', hdr_704, 0x04, total_bank_size - 8)
struct.pack_into('<I', hdr_704, 0x198, new_fsb_size)
struct.pack_into('<I', hdr_704, 0x2ba, new_fsb_size + 2)

with open(current_bank_path, 'wb') as f:
    f.write(hdr_704)
    f.write(new_fsb_bytes)

print(f"Bank successfully updated at {current_bank_path} ({os.path.getsize(current_bank_path)} bytes)!")
