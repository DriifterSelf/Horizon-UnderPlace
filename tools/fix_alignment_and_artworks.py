import os, sys, struct, subprocess, shutil, zipfile, io
from PIL import Image
import xml.etree.ElementTree as ET

MOD_DIR = r"C:\Users\uwu\Downloads\radiounder"
GAME_DIR = r"F:\SteamLibrary\steamapps\common\ForzaHorizon4"

if MOD_DIR not in sys.path:
    sys.path.append(MOD_DIR)

import fsb5
from turn10_zip import create_turn10_zip

# ====================================================================
# 1. EXACT MAPPING ARCHITECTURE BETWEEN XML SLOTS & FMOD BANK SAMPLES
# ====================================================================
# XML Slot -> Bank Sample Index (alphabetical order by Turn 10 event name)
XML_TO_BANK = {
    0: 3,   # HZ4_R4_BlackRebelMotorcycleClub_LittleThingGoneWild
    1: 13,  # HZ4_R4_QueensOfTheStoneAge_TheEvilHasLanded
    2: 7,   # HZ4_R4_FooFighters_LaDeeDa
    3: 8,   # HZ4_R4_GretaVanFleet_SafariSong
    4: 5,   # HZ4_R4_Dommengang_PastelCity
    5: 6,   # HZ4_R4_Dorothy_DowntotheBottom
    6: 2,   # HZ4_R4_BatFangs_TurnItUp
    7: 9,   # HZ4_R4_HotSnakes_SixWaveHoldDown
    8: 1,   # HZ4_R4_BassDrumOfDeath_IDontWannaKnow
    9: 10,  # HZ4_R4_IPrevail_Rise
    10: 11, # HZ4_R4_JackWhite_OverandOverandOver
    11: 12, # HZ4_R4_Pennywise_CantBeIgnored
    12: 14, # HZ4_R4_RedSunRising_Deathwish
    13: 15, # HZ4_R4_Starset_Satellite
    14: 17, # HZ4_R4_TheWonderYears_SisterCities
    15: 0,  # HZ4_R4_AtTheDriveIn_NoWolfLikeThePresent
    16: 19, # HZ4_R4_WalkTheMoon_Headphones
    17: 16, # HZ4_R4_TheKillers_RunForCover
    18: 18, # HZ4_R4_Underoath_Rapture
    19: 4,  # HZ4_R4_BlackRebelMotorcycleClub_LittleThingGoneWild_TG
}

BANK_TO_XML = {bank_idx: xml_idx for xml_idx, bank_idx in XML_TO_BANK.items()}

# Exact internal swatchbin filenames used by Turn 10 in AlbumArt.zip
XML_TO_SWATCHBIN = {
    0:  "XS/XS_BRMC.swatchbin",
    1:  "XS/XS_Villains.swatchbin",
    2:  "XS/XS_Foo_Fighters.swatchbin",
    3:  "XS/XS_RSZ_Gretava.swatchbin",
    4:  "XS/XS_Dommengang.swatchbin",
    5:  "XS/XS_Dorothy_Down_To_The_Bottom.swatchbin",
    6:  "XS/XS_DG.swatchbin",
    7:  "XS/XS_Hot_Snakes.swatchbin",
    8:  "XS/XS_BDOD.swatchbin",
    9:  "XS/XS_I_Prevail.swatchbin",
    10: "XS/XS_Jack_White.swatchbin",
    11: "XS/XS_Pennywise.swatchbin",
    12: "XS/XS_Red_Sun_Rising.swatchbin",
    13: "XS/XS_Starset_Vessels.swatchbin",
    14: "XS/XS_Sister_Cities.swatchbin",
    15: "XS/XS_At_The_Drive_In.swatchbin",
    16: "XS/XS_Walk_The_Moon.swatchbin",
    17: "XS/XS_The_Killers.swatchbin",
    18: "XS/XS_Underoath.swatchbin",
    19: "XS/XS_Eyes_Set_To_Kill.swatchbin", # cut track swatchbin for Slot 19
}

# ====================================================================
# 2. DEFINITIONS OF ALL 20 TRACKS (Audio WAV, Cover Art, Cues)
# ====================================================================
WAV_20_DIR = os.path.join(MOD_DIR, "wav_20")
COVERS_DIR = os.path.join(MOD_DIR, "covers_20")
SETLIST_DIR = os.path.join(MOD_DIR, "setlist")

def get_file_by_kw(kw, ext=None):
    for f in os.listdir(SETLIST_DIR):
        if kw.lower() in f.lower():
            if ext and not f.lower().endswith(ext.lower()):
                continue
            return os.path.join(SETLIST_DIR, f)
    raise FileNotFoundError(f"File with kw '{kw}' not found in {SETLIST_DIR}")

TRACKS = {
    0:  {
        "title": "KINK!", "artist": "White-oh, S-DEY!, Noisebro",
        "wav": os.path.join(WAV_20_DIR, "0000.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_07_hires.png"),
        "drop": 7.8, "dj_drop": 5.2, "loop_start": 7.8, "dj_mid": 92.0,
        "breakdown": 145.0, "pr_start": 149.0, "pr_end": 185.0, "loop_end": 185.0,
        "stinger_offset": 3.18
    },
    1:  {
        "title": "So what we get drunk? (Extended Version)", "artist": "Flvckka",
        "wav": os.path.join(WAV_20_DIR, "0001.wav"),
        "cover": get_file_by_kw("flvckka.jpg"),
        "drop": 28.0, "dj_drop": 24.0, "loop_start": 28.0, "dj_mid": 174.0,
        "breakdown": 272.0, "pr_start": 324.0, "pr_end": 368.0, "loop_end": 400.0,
        "stinger_offset": 3.13
    },
    2:  {
        "title": "Pigmentos (feat. Amorpho)", "artist": "Cxsinensis",
        "wav": os.path.join(WAV_20_DIR, "0002.wav"),
        "cover": get_file_by_kw("elimaginario.jpg"),
        "drop": 16.2, "dj_drop": 13.0, "loop_start": 16.2, "dj_mid": 116.0,
        "breakdown": 150.0, "pr_start": 162.0, "pr_end": 198.0, "loop_end": 220.0,
        "stinger_offset": 2.91
    },
    3:  {
        "title": "Vainilla", "artist": "Cxsinensis",
        "wav": os.path.join(WAV_20_DIR, "0003.wav"),
        "cover": get_file_by_kw("vainilla.jpg"),
        "drop": 30.0, "dj_drop": 26.0, "loop_start": 30.0, "dj_mid": 112.0,
        "breakdown": 165.0, "pr_start": 175.0, "pr_end": 208.0, "loop_end": 218.0,
        "stinger_offset": 3.23
    },
    4:  {
        "title": "CHROMEHEARTS", "artist": "KATSUU ENERGY, yakashi",
        "wav": os.path.join(WAV_20_DIR, "0004.wav"),
        "cover": get_file_by_kw("aun asi son mis sentimientos.jpg"),
        "drop": 13.8, "dj_drop": 11.0, "loop_start": 13.8, "dj_mid": 92.0,
        "breakdown": 120.0, "pr_start": 128.0, "pr_end": 164.0, "loop_end": 180.0,
        "stinger_offset": 3.07
    },
    5:  {
        "title": "Nada Es Igual", "artist": "White OH, Noisebro",
        "wav": os.path.join(WAV_20_DIR, "0005.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_09_hires.png"),
        "drop": 15.0, "dj_drop": 12.0, "loop_start": 15.0, "dj_mid": 76.0,
        "breakdown": 112.0, "pr_start": 118.0, "pr_end": 150.0, "loop_end": 152.0,
        "stinger_offset": 2.82
    },
    6:  {
        "title": "UN MOMENTO", "artist": "i killed a leopard, yakashi & SMOK3",
        "wav": os.path.join(WAV_20_DIR, "0006.wav"),
        "cover": get_file_by_kw("aun asi son mis sentimientos.jpg"),
        "drop": 14.5, "dj_drop": 11.5, "loop_start": 14.5, "dj_mid": 72.0,
        "breakdown": 135.0, "pr_start": 142.0, "pr_end": 174.0, "loop_end": 175.0,
        "stinger_offset": 2.98
    },
    7:  {
        "title": "Sola", "artist": "Saramalacara",
        "wav": os.path.join(WAV_20_DIR, "0007.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_11_hires.png"),
        "drop": 14.0, "dj_drop": 11.2, "loop_start": 14.0, "dj_mid": 96.0,
        "breakdown": 146.0, "pr_start": 154.0, "pr_end": 188.0, "loop_end": 195.0,
        "stinger_offset": 3.15
    },
    8:  {
        "title": "dormiré sin ti", "artist": "IZATKM",
        "wav": os.path.join(WAV_20_DIR, "0008.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_15_hires.png"),
        "drop": 17.0, "dj_drop": 13.5, "loop_start": 17.0, "dj_mid": 96.0,
        "breakdown": 142.0, "pr_start": 148.0, "pr_end": 180.0, "loop_end": 182.0,
        "stinger_offset": 3.10
    },
    9:  {
        "title": "portal 88", "artist": "3delincuentes, Noisebro",
        "wav": os.path.join(WAV_20_DIR, "0009.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_16_hires.png"),
        "drop": 15.0, "dj_drop": 12.0, "loop_start": 15.0, "dj_mid": 94.0,
        "breakdown": 142.0, "pr_start": 150.0, "pr_end": 182.0, "loop_end": 185.0,
        "stinger_offset": 2.99
    },
    10: {
        "title": "estupefacientes", "artist": "Depresión Sonora",
        "wav": os.path.join(WAV_20_DIR, "0010.wav"),
        "cover": get_file_by_kw("estupefacientes.jpg"),
        "drop": 14.0, "dj_drop": 11.0, "loop_start": 14.0, "dj_mid": 102.0,
        "breakdown": 138.0, "pr_start": 148.0, "pr_end": 188.0, "loop_end": 198.0,
        "stinger_offset": 3.07
    },
    11: {
        "title": "50 Varos", "artist": "MICRO, Flakko La Tentacion",
        "wav": os.path.join(WAV_20_DIR, "0011.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_02_hires.png"),
        "drop": 15.0, "dj_drop": 12.0, "loop_start": 15.0, "dj_mid": 98.0,
        "breakdown": 142.0, "pr_start": 150.0, "pr_end": 186.0, "loop_end": 195.0,
        "stinger_offset": 3.35
    },
    12: {
        "title": "Cacti (feat. Amorpho)", "artist": "Cxsinensis",
        "wav": os.path.join(WAV_20_DIR, "0012.wav"),
        "cover": get_file_by_kw("cacti.jpg"),
        "drop": 31.5, "dj_drop": 27.0, "loop_start": 31.5, "dj_mid": 160.0,
        "breakdown": 240.0, "pr_start": 255.0, "pr_end": 295.0, "loop_end": 315.0,
        "stinger_offset": 3.39
    },
    13: {
        "title": "Buscándome", "artist": "Pato Shoucair & xHEIDIx",
        "wav": os.path.join(WAV_20_DIR, "0013.wav"),
        "cover": get_file_by_kw("buscandome.jpg"),
        "drop": 30.5, "dj_drop": 26.0, "loop_start": 30.5, "dj_mid": 124.0,
        "breakdown": 175.0, "pr_start": 186.0, "pr_end": 226.0, "loop_end": 236.0,
        "stinger_offset": 3.10
    },
    14: {
        "title": "2000nunca", "artist": "Kirnbauer",
        "wav": os.path.join(WAV_20_DIR, "0014.wav"),
        "cover": get_file_by_kw("2000nunca.jpg"),
        "drop": 16.5, "dj_drop": 13.0, "loop_start": 16.5, "dj_mid": 78.0,
        "breakdown": 122.0, "pr_start": 130.0, "pr_end": 162.0, "loop_end": 166.0,
        "stinger_offset": 3.24
    },
    15: {
        "title": "teoría del tiempo", "artist": "AKRIILA & Gianluca",
        "wav": os.path.join(WAV_20_DIR, "0015.wav"),
        "cover": get_file_by_kw("epistolares.jpg"),
        "drop": 14.0, "dj_drop": 11.0, "loop_start": 14.0, "dj_mid": 88.0,
        "breakdown": 138.0, "pr_start": 146.0, "pr_end": 178.0, "loop_end": 184.0,
        "stinger_offset": 3.16
    },
    16: {
        "title": "suerteceleste", "artist": "Noisebro, dreamly.",
        "wav": os.path.join(WAV_20_DIR, "0016.wav"),
        "cover": os.path.join(COVERS_DIR, "cov_18_hires.png"),
        "drop": 11.5, "dj_drop": 9.0,  "loop_start": 11.5, "dj_mid": 86.0,
        "breakdown": 122.0, "pr_start": 130.0, "pr_end": 162.0, "loop_end": 170.0,
        "stinger_offset": 3.14
    },
    17: {
        "title": "Sola (House Alone Remix)", "artist": "Hillkidd & Mi Compa el Chino",
        "wav": os.path.join(WAV_20_DIR, "0017.wav"),
        "cover": get_file_by_kw("sola artwork.jpg"),
        "drop": 15.5, "dj_drop": 12.5, "loop_start": 15.5, "dj_mid": 108.0,
        "breakdown": 152.0, "pr_start": 164.0, "pr_end": 200.0, "loop_end": 210.0,
        "stinger_offset": 3.21
    },
    18: {
        "title": "p4ris", "artist": "3delincuentes & Kozta",
        "wav": os.path.join(WAV_20_DIR, "0018.wav"),
        "cover": get_file_by_kw("days before wakeup.jpg"),
        "drop": 14.0, "dj_drop": 11.0, "loop_start": 14.0, "dj_mid": 98.0,
        "breakdown": 136.0, "pr_start": 144.0, "pr_end": 178.0, "loop_end": 195.0,
        "stinger_offset": 3.23
    },
    19: {
        "title": "SLOW", "artist": "Mi Compa el Chino",
        "wav": os.path.join(WAV_20_DIR, "0019.wav"),
        "cover": get_file_by_kw("slow artwork.jpg"),
        "drop": 15.5, "dj_drop": 12.0, "loop_start": 15.5, "dj_mid": 96.0,
        "breakdown": 138.0, "pr_start": 150.0, "pr_end": 186.0, "loop_end": 195.0,
        "stinger_offset": 3.24
    },
}

# ====================================================================
# STEP 1: COMPILE FSB5 WITH BANK ORDER (0..19)
# ====================================================================
print("=== STEP 1: Compiling FSB5 with exact Bank Sample Ordering ===")
fsb_lst_path = os.path.join(WAV_20_DIR, "tracks_bank_order.lst")
with open(fsb_lst_path, "w", encoding="utf-8") as f:
    for bank_idx in range(20):
        xml_idx = BANK_TO_XML[bank_idx]
        wav_path = TRACKS[xml_idx]["wav"]
        f.write(wav_path + "\n")
        print(f"  Bank Sample {bank_idx:02d} <- XML Slot {xml_idx:02d}: '{TRACKS[xml_idx]['title']}'")

fsbankcl = os.path.join(MOD_DIR, r"fmod_tools\Tools\FmodBankTools\Fmod\fsbankcl.exe")
out_fsb = os.path.join(WAV_20_DIR, "R4_Tracks_ordered.fsb")
if os.path.exists(out_fsb):
    os.remove(out_fsb)

cmd = [fsbankcl, "-format", "vorbis", "-quality", "75", "-o", out_fsb, fsb_lst_path]
print("Running fsbankcl...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("fsbankcl error:", res.stderr)
    sys.exit(1)
print(f"Compiled {out_fsb} ({os.path.getsize(out_fsb)} bytes)!")

# ====================================================================
# STEP 2: REBUILD R4_Tracks.bank WITH 11 NATIVE SYNCPOINTS PER BANK SAMPLE
# ====================================================================
print("\n=== STEP 2: Rebuilding R4_Tracks.bank with Chunk 4 Syncpoints ===")
with open(out_fsb, "rb") as f:
    fsb_data = f.read()
fsb = fsb5.load(fsb_data)

orig_bank_path = os.path.join(GAME_DIR, r'media\audio\fmodopus\x64\R4_Tracks.bank.bak')
with open(orig_bank_path, 'rb') as f:
    orig_hdr_704 = bytearray(f.read(704))
    orig_fsb = fsb5.load(f.read())

repacked_samples = []
current_data_offset = 0

for bank_idx in range(20):
    s_curr = fsb.samples[bank_idx]
    s_orig = orig_fsb.samples[bank_idx]
    tot = s_curr.samples
    
    xml_idx = BANK_TO_XML[bank_idx]
    c = TRACKS[xml_idx]
    
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
struct.pack_into('<I', orig_hdr_704, 0x04, total_bank_size - 8)
struct.pack_into('<I', orig_hdr_704, 0x198, new_fsb_size)
struct.pack_into('<I', orig_hdr_704, 0x2ba, new_fsb_size + 2)

target_bank_path = os.path.join(GAME_DIR, r'media\audio\fmodopus\x64\R4_Tracks.bank')
with open(target_bank_path, 'wb') as f:
    f.write(orig_hdr_704)
    f.write(new_fsb_bytes)

print(f"Bank updated at {target_bank_path} ({os.path.getsize(target_bank_path)} bytes)!")

# ====================================================================
# STEP 3: UPDATE RadioInfo_MX.xml AND RadioInfo_EN.xml
# ====================================================================
print("\n=== STEP 3: Updating RadioInfo XMLs ===")
for lang in ['MX', 'EN']:
    target_xml = os.path.join(GAME_DIR, f'media/audio/RadioInfo_{lang}.xml')
    tree = ET.parse(target_xml)
    root = tree.getroot()
    xs = root.find(".//RadioStation[@Name='Horizon XS']")
    sample_list = xs.find('SampleList')

    for xml_idx in range(20):
        elem = sample_list[xml_idx]
        bank_idx = XML_TO_BANK[xml_idx]
        tot = repacked_samples[bank_idx]['samples']
        c = TRACKS[xml_idx]

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

        elem.set('DisplayName', c['title'])
        elem.set('Artist', c['artist'])
        elem.set('SampleLength', str(tot))
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
# STEP 4: CONVERT ALL 20 ARTWORKS AND INJECT INTO AlbumArt.zip
# ====================================================================
print("\n=== STEP 4: Converting Artworks and Injecting into AlbumArt.zip ===")
texconv = os.path.join(MOD_DIR, 'texconv.exe')

sample_hires = os.path.join(MOD_DIR, 'Radio_Logo_Horizon_XS_hires.swatchbin')
sample_norm = os.path.join(MOD_DIR, 'Radio_Logo_Horizon_XS_normal.swatchbin')

with open(sample_hires, 'rb') as f:
    hdr_hires_140 = bytearray(f.read(140))
with open(sample_norm, 'rb') as f:
    hdr_norm_140 = bytearray(f.read(140))

struct.pack_into('<HH', hdr_hires_140, 16, 276, 276)
struct.pack_into('<I', hdr_hires_140, 28, 76176)
struct.pack_into('<HH', hdr_norm_140, 16, 138, 138)
struct.pack_into('<I', hdr_norm_140, 28, 19600)

temp_png_hires = os.path.join(MOD_DIR, 'temp_fix_hires.png')
temp_png_norm = os.path.join(MOD_DIR, 'temp_fix_norm.png')

hires_replacements = {}
norm_replacements = {}

for xml_idx in range(20):
    src_cover = TRACKS[xml_idx]['cover']
    swatch_name = XML_TO_SWATCHBIN[xml_idx]
    
    img = Image.open(src_cover).convert('RGBA')

    # 1. Hires 276x276
    img_hires = img.resize((276, 276), Image.Resampling.LANCZOS)
    img_hires.save(temp_png_hires)
    subprocess.run([texconv, "-f", "BC7_UNORM", "-m", "1", "-y", "-o", MOD_DIR, temp_png_hires],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_dds_hires = os.path.join(MOD_DIR, 'temp_fix_hires.dds')
    with open(temp_dds_hires, 'rb') as f:
        f.seek(148)
        bc7_hires = f.read()
    assert len(bc7_hires) == 76176
    swatch_hires = bytes(hdr_hires_140) + bc7_hires
    hires_replacements[swatch_name] = swatch_hires

    # 2. Normal 138x138
    img_norm = img.resize((138, 138), Image.Resampling.LANCZOS)
    img_norm.save(temp_png_norm)
    subprocess.run([texconv, "-f", "BC7_UNORM", "-m", "1", "-y", "-o", MOD_DIR, temp_png_norm],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_dds_norm = os.path.join(MOD_DIR, 'temp_fix_norm.dds')
    with open(temp_dds_norm, 'rb') as f:
        f.seek(148)
        bc7_norm = f.read()
    assert len(bc7_norm) == 19600
    swatch_norm = bytes(hdr_norm_140) + bc7_norm
    norm_replacements[swatch_name] = swatch_norm

    print(f"  Slot {xml_idx:02d} -> {swatch_name}: '{TRACKS[xml_idx]['title']}'")

# Also overwrite remaining cut track swatchbins so no original rock cover can ever appear
cut_swatches = [
    "XS/XS_Parquet_Courts_Wide_Awake.swatchbin",
    "XS/XS_Regrettes.swatchbin",
    "XS/XS_The_Decemberists.swatchbin",
]
for cs in cut_swatches:
    hires_replacements[cs] = hires_replacements["XS/XS_Eyes_Set_To_Kill.swatchbin"]
    norm_replacements[cs] = norm_replacements["XS/XS_Eyes_Set_To_Kill.swatchbin"]

# Clean temp files
for p in [temp_png_hires, temp_png_norm, temp_dds_hires, temp_dds_norm]:
    if os.path.exists(p):
        os.remove(p)

# Pack hires AlbumArt.zip
hires_zip = os.path.join(GAME_DIR, r'media\ui\textures\hires\data_bound\AlbumArt.zip')
bak_hires_zip = os.path.join(GAME_DIR, r'media\ui\textures\hires\data_bound\AlbumArt.zip.bak')
create_turn10_zip(bak_hires_zip, hires_zip, hires_replacements)
print(f"Updated {hires_zip} ({os.path.getsize(hires_zip)} bytes)!")

# Pack normal AlbumArt.zip
norm_zip = os.path.join(GAME_DIR, r'media\ui\textures\data_bound\AlbumArt.zip')
bak_norm_zip = os.path.join(GAME_DIR, r'media\ui\textures\data_bound\AlbumArt.zip.bak')
create_turn10_zip(bak_norm_zip, norm_zip, norm_replacements)
print(f"Updated {norm_zip} ({os.path.getsize(norm_zip)} bytes)!")

print("\n=======================================================")
print(" ALL 20 TRACKS AND ARTWORKS ARE 100% PERFECTLY ALIGNED! ")
print("=======================================================")
