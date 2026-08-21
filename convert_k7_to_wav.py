import os
import struct
import sys
import array
from pathlib import Path

def make_wav_header(num_samples, sample_rate=44100):
    bits_per_sample = 16
    num_channels = 1
    byte_rate = sample_rate * num_channels * (bits_per_sample // 8)
    block_align = num_channels * (bits_per_sample // 8)
    subchunk2_size = num_samples * block_align
    chunk_size = 36 + subchunk2_size
    
    return struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        chunk_size,
        b'WAVE',
        b'fmt ',
        16,
        1,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b'data',
        subchunk2_size
    )

def generate_vg5k_wav(casdata, baud_rate=1200, sample_rate=44100):
    if baud_rate == 1200:
        len_short = 10
        len_long = 20
    else:
        len_short = 5
        len_long = 10

    cycle_short = [32767] * len_short + [-32768] * len_short
    cycle_long = [32767] * len_long + [-32768] * len_long

    eob_samples = cycle_short * 4 + cycle_long

    # Pre-generate bit-level samples for all byte values
    byte_bit_samples = {}
    for b in range(256):
        samples = []
        temp_b = b
        for _ in range(8):
            if temp_b & 0x01:
                samples.extend(cycle_short * 2)
            else:
                samples.extend(cycle_long)
            temp_b >>= 1
        byte_bit_samples[b] = samples

    out_samples = []
    k7_size = len(casdata)
    data_pos = 0

    if k7_size < 3 or casdata[0] != 0xd3 or casdata[1] != 0xd3 or casdata[2] != 0xd3:
        raise ValueError("Invalid K7 file: must start with 0xD3 0xD3 0xD3")

    while data_pos < k7_size:
        block_size = 0
        block_type = casdata[data_pos]

        if block_type == 0xd3:
            block_size = 0x20
            out_samples.extend([0] * sample_rate)
            out_samples.extend(cycle_short * 30000)
            out_samples.extend(eob_samples)
        elif block_type == 0xd6:
            if data_pos >= 4:
                val = casdata[data_pos - 4] | (casdata[data_pos - 3] << 8)
                block_size = val + 20
            else:
                block_size = 20
            
            silence_len = 10000 if baud_rate == 2400 else 20000
            out_samples.extend([0] * silence_len)
            out_samples.extend(cycle_short * 7200)
            out_samples.extend(eob_samples)
        else:
            while data_pos < k7_size and casdata[data_pos] not in (0xd3, 0xd6):
                data_pos += 1
            continue

        for _ in range(block_size):
            if data_pos >= k7_size:
                break
            val = casdata[data_pos]
            out_samples.extend(byte_bit_samples[val])
            out_samples.extend(eob_samples)
            data_pos += 1

    out_samples.extend([0] * 10000)
    
    pcm_data = array.array('h', out_samples).tobytes()
    header = make_wav_header(len(out_samples), sample_rate)
    return header + pcm_data

def main():
    # Setup paths
    workspace_dir = Path(r"f:\Spiele\retro\vg5000\roms").resolve()
    
    # Speed selection: 1200 or 2400
    baud_rate = 1200
    if len(sys.argv) > 1:
        try:
            val = int(sys.argv[1])
            if val in (1200, 2400):
                baud_rate = val
        except ValueError:
            pass
            
    target_dir_name = "wavs_1200" if baud_rate == 1200 else "wavs"
    target_dir = workspace_dir / target_dir_name
    
    print(f"Scanning for .k7 files in: {workspace_dir}")
    print(f"Baud rate: {baud_rate} baud")
    print(f"Target directory: {target_dir}")
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all .k7 files recursively
    k7_files = []
    for path in workspace_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".k7":
            # Skip files that are inside the target folder
            if target_dir in path.parents:
                continue
            k7_files.append(path)
            
    total_files = len(k7_files)
    print(f"Found {total_files} .k7 files to convert.")
    
    success_count = 0
    fail_count = 0
    
    for idx, k7_path in enumerate(k7_files, 1):
        print(f"[{idx}/{total_files}] Converting: {k7_path.relative_to(workspace_dir)}")
        
        # Determine the target filename
        base_name = k7_path.stem
        wav_filename = f"{base_name}.wav"
        wav_path = target_dir / wav_filename
        
        # Handle filename collisions
        counter = 1
        while wav_path.exists():
            wav_filename = f"{base_name}_{counter}.wav"
            wav_path = target_dir / wav_filename
            counter += 1
            
        try:
            # Read K7 file
            with open(k7_path, 'rb') as f:
                casdata = f.read()
            
            # Generate WAV data
            wav_data = generate_vg5k_wav(casdata, baud_rate=baud_rate)
            
            # Write WAV file (Python handles long path names automatically)
            with open(wav_path, 'wb') as f:
                f.write(wav_data)
                
            print(f"   -> Converted to: {wav_path.name}")
            success_count += 1
        except Exception as e:
            print(f"   -> ERROR processing file: {e}")
            fail_count += 1
            if wav_path.exists():
                try:
                    wav_path.unlink()
                except Exception:
                    pass
                    
    print("\n--- Summary ---")
    print(f"Total found: {total_files}")
    print(f"Successfully converted: {success_count}")
    print(f"Failed conversions: {fail_count}")
    print(f"Target directory size: {len(list(target_dir.glob('*.wav')))} wav files")

if __name__ == "__main__":
    main()
