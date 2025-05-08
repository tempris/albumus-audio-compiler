import os
import sys
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import Picture, FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, TDRC, COMM, TCON, TRCK, TPE2, TCOP, TCOM
import base64
import subprocess
from PIL import Image
import json

SCRIPT_TITLE = "Albumus Audio Compiler"
LOG_TAG_COMPILE = "[🎵 Compile Audio]"

print(f'{LOG_TAG_COMPILE} [Init] {SCRIPT_TITLE} Importing...')

# Path to this Python file
LOCATION_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.join(LOCATION_SCRIPT, '../../')

from cure_log import CureLog

logger = CureLog(os.path.join(DIR_ROOT, '_log/compile_audio.log'))

logger.log("debug", LOG_TAG_COMPILE, "sys.path:", sys.path)
logger.log("init", LOG_TAG_COMPILE, "Import complete.")

# Load config/settings.json
settings_path = os.path.join(DIR_ROOT, 'config', 'settings.json')
config_dir = ""

try:
    with open(settings_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config_dir = os.path.abspath(config.get('dir'))
except Exception as e:
    logger.log("error", LOG_TAG_COMPILE, "Failed to load settings.json:", e)
    sys.exit(0)

from load_project_config import load_project_config

# Load default and project-specific config
default_config_path = os.path.join(DIR_ROOT, 'config', 'default', 'project', 'config.json')
project_config_path = os.path.join(config_dir, 'config.json')

project_config = load_project_config(default_config_path, project_config_path)

log_relative = project_config.get("logging", {}).get("log_relative_paths", True)
ffmpeg_strategy = project_config.get("ffmpeg", {}).get("bitrate_strategy", {})
mp3_strategy = ffmpeg_strategy.get("mp3", {})
ogg_strategy = ffmpeg_strategy.get("ogg", {})

def read_metadata(metadata_artist_file, metadata_album_file, metadata_track_file, song_file, total_tracks):
    try:
        with open(metadata_artist_file, 'r', encoding='utf-8') as f:
            artist_data = json.load(f)
        with open(metadata_album_file, 'r', encoding='utf-8') as f:
            album_data = json.load(f)
        with open(metadata_track_file, 'r', encoding='utf-8') as f:
            track_data_all = json.load(f)

        track_data = track_data_all.get(song_file, {})
        if 'tracknumber' in track_data:
            track_num = int(track_data['tracknumber'])
            pad_length = len(str(total_tracks))
            track_data['tracknumber'] = str(track_num).zfill(pad_length)

        metadata = {**artist_data, **album_data, **track_data}
        track_number = track_data.get('tracknumber')

        return metadata, track_number
    except Exception as e:
        logger.log("error", LOG_TAG_COMPILE, "Error loading metadata JSON:", e)
        return {}, None

def add_cover_art(audio_file, cover_art_path, audio_format):
    with open(cover_art_path, 'rb') as img_file:
        cover_data = img_file.read()

    if audio_format == 'ogg':
        audio = OggVorbis(audio_file)
        picture = Picture()
        picture.type = 3  # Cover (front)
        picture.desc = 'Cover Art'
        picture.data = cover_data
        audio['metadata_block_picture'] = [base64.b64encode(picture.write()).decode('ascii')]
        audio.save()
    elif audio_format == 'mp3':
        audio = MP3(audio_file, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/png',  # MIME type of the cover art image
                type=3,  # Front cover
                desc='Cover Art',
                data=cover_data
            )
        )
        audio.save()
    elif audio_format == 'flac':
        audio = FLAC(audio_file)
        picture = Picture()
        picture.type = 3  # Cover (front)
        picture.desc = 'Cover Art'
        picture.data = cover_data
        audio.add_picture(picture)
        audio.save()

def add_metadata_to_file(audio_file, metadata, audio_format):
    if audio_format == 'ogg':
        audio = OggVorbis(audio_file)
        for key, value in metadata.items():
            audio[key] = value
        audio.save()
    elif audio_format == 'mp3':
        audio = MP3(audio_file, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        id3_map = {
            'title': TIT2,
            'album': TALB,
            'artist': TPE1,
            'album_artist': TPE2,
            'date': TDRC,
            'comment': COMM,
            'genre': TCON,
            'tracknumber': TRCK,
            'composer': TCOM,
            'copyright': TCOP
        }
        for key, value in metadata.items():
            tag_class = id3_map.get(key)
            if tag_class:
                if key == 'comment':
                    audio.tags.add(tag_class(encoding=3, desc='', text=value))
                else:
                    audio.tags.add(tag_class(encoding=3, text=value))
        audio.save()
    elif audio_format == 'flac':
        audio = FLAC(audio_file)
        for key, value in metadata.items():
            audio[key] = value
        audio.save()

LOG_TAG_FFMPEG = LOG_TAG_COMPILE + " [🔊 FFmpeg]"

def run_ffmpeg(command_args):
    logger.log("debug", LOG_TAG_FFMPEG, "Running command:", command_args)

    try:
        process = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            logger.log("debug", LOG_TAG_FFMPEG, "Output:", line.rstrip())
        process.wait()
        if process.returncode != 0:
            logger.log("error", LOG_TAG_FFMPEG, "ffmpeg exited with code", process.returncode)
        return process.returncode
    except KeyboardInterrupt:
        logger.log("notice", LOG_TAG_FFMPEG, "FFmpeg process interrupted by user.")
        return 130  # Standard code for Ctrl+C
    except Exception as e:
        logger.log("error", LOG_TAG_FFMPEG, "Failed to run ffmpeg:", e)
        return 1

def get_bitrate(input_file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return int(result.stdout.strip()) if result.stdout.strip().isdigit() else None

def get_path_formatted(path):
    return os.path.relpath(path, config_dir) if log_relative else path

def convert_formats(input_file, base_name, output_dir, metadata, cover_art_path, formats):
    source_bitrate = get_bitrate(input_file)
    for fmt in formats:
        output_format_dir = os.path.join(output_dir, fmt)
        os.makedirs(output_format_dir, exist_ok=True)
        output_file = os.path.join(output_format_dir, f"{base_name}.{fmt}")

        logger.log("info", LOG_TAG_FFMPEG, "Processing:", {"Input": get_path_formatted(input_file)})
        result = 0

        if fmt == 'mp3':
            if source_bitrate:
                result = run_ffmpeg(['ffmpeg', '-y', '-i', input_file, '-codec:a', 'libmp3lame', '-b:a', f'{source_bitrate}k', output_file])
            else:
                fallback_q = str(mp3_strategy.get("fallback_qscale", 2))
                result = run_ffmpeg(['ffmpeg', '-y', '-i', input_file, '-codec:a', 'libmp3lame', '-qscale:a', fallback_q, output_file])
        elif fmt == 'flac':
            result = run_ffmpeg(['ffmpeg', '-y', '-i', input_file, '-c:a', 'flac', '-compression_level', '8', output_file])
        elif fmt == 'wav':
            result = run_ffmpeg(['ffmpeg', '-y', '-i', input_file, output_file])
        elif fmt == 'ogg':
            if source_bitrate:
                min_q = ogg_strategy.get("min_quality", 0)
                max_q = ogg_strategy.get("max_quality", 10)
                base = ogg_strategy.get("base_bitrate", 64000)
                step = ogg_strategy.get("step", 16000)

                quality = min(max((source_bitrate - base) // step, min_q), max_q)
                result = run_ffmpeg(['ffmpeg', '-y', '-i', input_file, '-codec:a', 'libvorbis', '-qscale:a', str(quality), output_file])
            else:
                fallback_q = str(ogg_strategy.get("fallback_qscale", 10))
                result = run_ffmpeg(['ffmpeg', '-y', '-i', input_file, '-codec:a', 'libvorbis', '-qscale:a', fallback_q, output_file])

        if result != 0:
            logger.log("error", LOG_TAG_FFMPEG, "Processing Exited Early, see above...")
        else:
            logger.log("success", LOG_TAG_FFMPEG, "Complete:", {"Output": get_path_formatted(output_file)})

        if fmt != 'wav':
            add_metadata_to_file(output_file, metadata, fmt)
            add_cover_art(output_file, cover_art_path, fmt)

def create_album_art_images(cover_art_path, output_folder, base_name):
    sizes = {
        k: tuple(v) for k, v in project_config.get("output", {}).get("art_sizes", {}).items()
    }

    with Image.open(cover_art_path) as img:
        original_width, original_height = img.size

        for size_name, dimensions in sizes.items():
            target_width, target_height = dimensions
            if target_width <= original_width and target_height <= original_height:
                img_resized = img.resize(dimensions, Image.LANCZOS)
                if img_resized.mode in ("RGBA", "P"):
                    img_resized = img_resized.convert("RGB")
                output_path = os.path.join(output_folder, f"{size_name}.jpg")
                img_resized.save(
                    output_path,
                    project_config.get("output", {}).get("image_output_format", "JPEG"),
                    quality=project_config.get("output", {}).get("image_quality", 95)
                )
                logger.log("info", LOG_TAG_COMPILE, "Created album art", {"name": size_name, "path": output_path})

def process_album(artist_dir, album_dir, output_base_dir, formats):
    cover_art_path = os.path.join(album_dir, 'folder.png')
    metadata_artist_file = os.path.join(artist_dir, 'metadata_artist.json')
    metadata_album_file = os.path.join(album_dir, 'metadata_album.json')
    metadata_track_file = os.path.join(album_dir, 'metadata_track.json')

    files = [os.path.join(album_dir, f) for f in os.listdir(album_dir) if f.endswith(('.wav', '.flac', '.mp3', '.ogg'))]
    total_tracks = len(files)
    output_album_dir = os.path.join(output_base_dir, os.path.basename(artist_dir), os.path.basename(album_dir))

    os.makedirs(output_album_dir, exist_ok=True)
    create_album_art_images(cover_art_path, output_album_dir, os.path.basename(album_dir))

    for file_path in files:
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        metadata, track_number = read_metadata(metadata_artist_file, metadata_album_file, metadata_track_file, file_name, total_tracks)
        if track_number:
            title = metadata.get("title", base_name).replace(" ", "_")
            base_name_output = f"{track_number}_{title}"
            convert_formats(file_path, base_name_output, output_album_dir, metadata, cover_art_path, formats)
        else:
            logger.log("warn", LOG_TAG_COMPILE, 'Track number not found for file:', {"file": file_name})

def process_all(input_base_dir, output_base_dir, formats):
    for artist in os.listdir(input_base_dir):
        artist_dir = os.path.join(input_base_dir, artist)
        if os.path.isdir(artist_dir):
            for album in os.listdir(artist_dir):
                album_dir = os.path.join(artist_dir, album)
                if os.path.isdir(album_dir):
                    process_album(artist_dir, album_dir, output_base_dir, formats)

if __name__ == '__main__':
    input_base_dir = os.path.join(config_dir, 'in')
    output_base_dir = os.path.join(config_dir, 'out')
    formats = project_config.get('formats', ['flac', 'mp3', 'ogg', 'wav'])

    PATHS_PROJECT = {
        "Project Path": config_dir,
        "Input": input_base_dir,
        "Output": output_base_dir
    }
    logger.log("begin", LOG_TAG_COMPILE, 'Running:', PATHS_PROJECT)
    process_all(input_base_dir, output_base_dir, formats)
    logger.log("end", LOG_TAG_COMPILE, 'Complete:', PATHS_PROJECT)
