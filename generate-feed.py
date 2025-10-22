#!/usr/bin/env python3
"""
Generate podcast RSS feed for Jaxon Strategy documents.

Usage:
    python3 generate-feed.py

Reads MP3 files from /Users/bgerby/Documents/dev/pivot/sprint-0/audio/
and generates feed.rss
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

AUDIO_DIR = Path("/Users/bgerby/Documents/dev/pivot/sprint-0/audio")
DRIVE_URLS_FILE = Path(__file__).parent / "drive-urls.json"
GITHUB_BASE_URL = "https://jaxondigital.github.io/jaxon-strategy-feed/audio"

def get_mp3_metadata(mp3_path):
    """Extract metadata from MP3 file using ffprobe."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            str(mp3_path)
        ], capture_output=True, text=True, check=True)

        data = json.loads(result.stdout)
        format_info = data.get('format', {})
        tags = format_info.get('tags', {})

        return {
            'title': tags.get('title', mp3_path.stem),
            'artist': tags.get('artist', 'Jaxon Digital'),
            'album': tags.get('album', 'Project Pivot Strategy'),
            'comment': tags.get('comment', ''),
            'duration': int(float(format_info.get('duration', 0))),
            'size': int(format_info.get('size', 0))
        }
    except Exception as e:
        print(f"Error reading metadata from {mp3_path}: {e}")
        return None

def load_drive_urls():
    """Load Google Drive URLs mapping from JSON file."""
    if DRIVE_URLS_FILE.exists():
        with open(DRIVE_URLS_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_audio_url(filename, drive_urls):
    """Get audio file URL (Google Drive if available, else GitHub Pages)."""
    if filename in drive_urls:
        return drive_urls[filename]
    else:
        # Fallback to GitHub Pages URL (will need to upload audio files there)
        return f"{GITHUB_BASE_URL}/{filename}"

def generate_rss(output_path):
    """Generate podcast RSS feed."""

    # Load Drive URLs
    drive_urls = load_drive_urls()

    # Create RSS structure
    rss = Element('rss', version='2.0')
    rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

    channel = SubElement(rss, 'channel')

    # Channel metadata
    SubElement(channel, 'title').text = 'Jaxon Strategy Feed'
    SubElement(channel, 'description').text = (
        'Strategy documents for Jaxon Digital\'s transformation from Optimizely '
        'services company to AI Operations Platform SaaS. Includes platform vision, '
        'agent catalog, roadmaps, and partnership materials.'
    )
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'link').text = 'https://github.com/JaxonDigital/jaxon-strategy-feed'

    # iTunes-specific metadata
    SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = 'Jaxon Digital'
    SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category', text='Business')
    SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'no'

    # Self-reference link
    atom_link = SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', 'https://jaxondigital.github.io/jaxon-strategy-feed/feed.rss')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    # Find all MP3 files
    mp3_files = sorted(AUDIO_DIR.glob('*.mp3'))

    print(f"Found {len(mp3_files)} audio files")

    episodes = []

    for mp3_path in mp3_files:
        # Skip temp/chunk files
        if '.temp.' in mp3_path.name or '.chunk' in mp3_path.name:
            continue

        print(f"Processing: {mp3_path.name}")

        metadata = get_mp3_metadata(mp3_path)
        if not metadata:
            continue

        audio_url = get_audio_url(mp3_path.name, drive_urls)

        # Get file modification time as pub date
        mtime = mp3_path.stat().st_mtime
        pub_date = datetime.fromtimestamp(mtime).strftime('%a, %d %b %Y %H:%M:%S %z')
        if not pub_date.endswith(' +0000'):
            pub_date += ' +0000'

        episodes.append({
            'filename': mp3_path.name,
            'title': metadata['title'],
            'artist': metadata['artist'],
            'description': metadata['comment'] or f"Strategy document - {metadata['title']}",
            'audio_url': audio_url,
            'pub_date': pub_date,
            'duration': metadata['duration'],
            'size': metadata['size']
        })

    # Sort episodes by modification time (most recent first)
    episodes.sort(key=lambda e: e['pub_date'], reverse=True)

    # Add episodes to RSS
    for ep in episodes:
        item = SubElement(channel, 'item')

        SubElement(item, 'title').text = ep['title']
        SubElement(item, 'description').text = ep['description']
        SubElement(item, 'pubDate').text = ep['pub_date']
        SubElement(item, 'guid').text = ep['audio_url']

        enclosure = SubElement(item, 'enclosure')
        enclosure.set('url', ep['audio_url'])
        enclosure.set('type', 'audio/mpeg')
        enclosure.set('length', str(ep['size']))

        if ep['duration'] > 0:
            hours = ep['duration'] // 3600
            minutes = (ep['duration'] % 3600) // 60
            seconds = ep['duration'] % 60
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text = duration_str

        SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = ep['artist']

    # Pretty print XML
    xml_string = tostring(rss, encoding='unicode')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent='  ')

    # Remove extra blank lines
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print(f"\n✓ Generated RSS feed: {output_path}")
    print(f"  Episodes: {len(episodes)}")

def main():
    output_path = Path(__file__).parent / 'feed.rss'
    generate_rss(output_path)

    print(f"\nSubscribe URL:")
    print(f"https://jaxondigital.github.io/jaxon-strategy-feed/feed.rss")

if __name__ == '__main__':
    main()
