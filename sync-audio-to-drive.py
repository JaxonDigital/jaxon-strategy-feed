#!/usr/bin/env python3
"""
Sync strategy audio files to Google Drive and create drive-urls.json mapping.

Usage:
    python3 sync-audio-to-drive.py
"""

import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Configuration
AUDIO_DIR = Path("/Users/bgerby/Documents/dev/pivot/sprint-0/audio")
MP3_FOLDER_ID = "1lYbPNf6nJIvJCCCbD2weO_VEuLj5Hb1i"  # Strategy Audio folder
TOKEN_PATH = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'
DRIVE_URLS_FILE = Path(__file__).parent / "drive-urls.json"

def get_drive_service():
    """Get Google Drive API service."""
    if not os.path.exists(TOKEN_PATH):
        raise Exception(f"Google Drive token not found at {TOKEN_PATH}")

    with open(TOKEN_PATH, 'r') as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)

def list_drive_files(service, folder_id):
    """List all MP3 files in Drive folder."""
    files = {}
    page_token = None

    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType='audio/mpeg'",
            fields='nextPageToken, files(id, name, webViewLink, webContentLink)',
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        for file in response.get('files', []):
            # Convert webViewLink to direct download link
            file_id = file['id']
            download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            files[file['name']] = download_link

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return files

def upload_file_to_drive(service, file_path, parent_folder_id):
    """Upload file to Google Drive and return download link."""
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id]
    }

    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id',
        supportsAllDrives=True
    ).execute()

    file_id = file['id']

    # Make publicly accessible
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(
        fileId=file_id,
        body=permission,
        supportsAllDrives=True
    ).execute()

    # Return direct download link
    download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    return download_link

def main():
    print("Syncing Strategy Audio Files to Google Drive")
    print("=" * 50)
    print(f"Audio Directory: {AUDIO_DIR}")
    print(f"Drive Folder ID: {MP3_FOLDER_ID}")
    print()

    # Get Drive service
    drive_service = get_drive_service()

    # List existing files on Drive
    print("Checking existing files on Drive...")
    existing_files = list_drive_files(drive_service, MP3_FOLDER_ID)
    print(f"Found {len(existing_files)} files already on Drive\n")

    # Load existing mapping if it exists
    if DRIVE_URLS_FILE.exists():
        with open(DRIVE_URLS_FILE, 'r') as f:
            drive_urls = json.load(f)
    else:
        drive_urls = {}

    # Find all local MP3 files (exclude temp/chunk files)
    local_mp3s = [
        f for f in AUDIO_DIR.glob('*.mp3')
        if '.temp.' not in f.name and '.chunk' not in f.name
    ]

    print(f"Found {len(local_mp3s)} local MP3 files\n")

    # Sync files
    uploaded_count = 0
    for mp3_path in local_mp3s:
        filename = mp3_path.name

        if filename in existing_files:
            print(f"✓ {filename} - already on Drive")
            drive_urls[filename] = existing_files[filename]
        elif filename in drive_urls:
            print(f"✓ {filename} - already mapped")
        else:
            print(f"↑ Uploading {filename}...")
            try:
                download_link = upload_file_to_drive(drive_service, str(mp3_path), MP3_FOLDER_ID)
                drive_urls[filename] = download_link
                uploaded_count += 1
                print(f"  ✓ Uploaded: {download_link}")
            except Exception as e:
                print(f"  ✗ Error: {e}")

    # Save mapping
    with open(DRIVE_URLS_FILE, 'w') as f:
        json.dump(drive_urls, f, indent=2)

    print(f"\n{'=' * 50}")
    print(f"Uploaded: {uploaded_count} new files")
    print(f"Total mapped: {len(drive_urls)} files")
    print(f"Mapping saved to: {DRIVE_URLS_FILE}")
    print(f"\nNext step: Regenerate RSS feed with:")
    print(f"  cd {Path(__file__).parent} && python3 generate-feed.py")

if __name__ == '__main__':
    main()
