"""
Metadata utilities for SunoReady
Handles cleaning and removing ID3/EXIF metadata from audio files
"""

import os
from mutagen import File
from mutagen.id3 import ID3NoHeaderError
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
import subprocess
from pathlib import Path

class MetadataUtils:
    def __init__(self):
        self.supported_formats = ['.mp3', '.flac', '.m4a', '.ogg', '.wav']
    
    def clean_metadata(self, file_path):
        """
        Remove all metadata from audio file
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext not in self.supported_formats:
                print(f"Unsupported format: {file_ext}")
                return False
            
            # Use mutagen for metadata removal
            success = self._clean_with_mutagen(file_path)
            
            # If mutagen fails or for extra safety, use FFmpeg
            if not success or file_ext == '.mp3':
                success = self._clean_with_ffmpeg(file_path)
            
            return success
            
        except Exception as e:
            print(f"Error cleaning metadata for {file_path}: {str(e)}")
            return False
    
    def _clean_with_mutagen(self, file_path):
        """Clean metadata using mutagen library"""
        try:
            # Load the file
            audio_file = File(file_path)
            
            if audio_file is None:
                return False
            
            # Remove all tags
            if hasattr(audio_file, 'tags') and audio_file.tags:
                audio_file.delete()
                audio_file.save()
            
            return True
            
        except ID3NoHeaderError:
            # File has no ID3 header, which is fine
            return True
        except Exception as e:
            print(f"Mutagen cleaning failed: {str(e)}")
            return False
    
    def _clean_with_ffmpeg(self, file_path):
        """Clean metadata using FFmpeg (more thorough)"""
        try:
            # Create temporary file
            temp_path = file_path + "_temp"
            
            # FFmpeg command to remove metadata
            cmd = [
                'ffmpeg', '-y',
                '-i', file_path,
                '-map_metadata', '-1',  # Remove all metadata
                '-c:a', 'copy',  # Copy audio without re-encoding
                temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Replace original file with cleaned version
                os.replace(temp_path, file_path)
                return True
            else:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False
                
        except FileNotFoundError:
            print("FFmpeg not found for metadata cleaning")
            return False
        except Exception as e:
            print(f"FFmpeg cleaning failed: {str(e)}")
            return False
    
    def get_metadata(self, file_path):
        """
        Get metadata from audio file
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            dict: Dictionary containing metadata
        """
        try:
            audio_file = File(file_path)
            
            if audio_file is None or not audio_file.tags:
                return {}
            
            metadata = {}
            
            # Common tags
            tag_mapping = {
                'title': ['TIT2', 'TITLE', '\xa9nam'],
                'artist': ['TPE1', 'ARTIST', '\xa9ART'],
                'album': ['TALB', 'ALBUM', '\xa9alb'],
                'date': ['TDRC', 'DATE', '\xa9day'],
                'genre': ['TCON', 'GENRE', '\xa9gen'],
                'track': ['TRCK', 'TRACKNUMBER', 'trkn'],
            }
            
            for key, tags in tag_mapping.items():
                for tag in tags:
                    if tag in audio_file.tags:
                        metadata[key] = str(audio_file.tags[tag][0])
                        break
            
            return metadata
            
        except Exception as e:
            print(f"Error reading metadata: {str(e)}")
            return {}
    
    def set_metadata(self, file_path, metadata):
        """
        Set metadata for audio file
        
        Args:
            file_path (str): Path to audio file
            metadata (dict): Dictionary containing metadata to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.mp3':
                return self._set_mp3_metadata(file_path, metadata)
            elif file_ext == '.flac':
                return self._set_flac_metadata(file_path, metadata)
            elif file_ext in ['.m4a', '.mp4']:
                return self._set_mp4_metadata(file_path, metadata)
            elif file_ext == '.ogg':
                return self._set_ogg_metadata(file_path, metadata)
            else:
                return False
                
        except Exception as e:
            print(f"Error setting metadata: {str(e)}")
            return False
    
    def _set_mp3_metadata(self, file_path, metadata):
        """Set metadata for MP3 file"""
        try:
            audio_file = MP3(file_path)
            
            # Add ID3 tag if it doesn't exist
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Set metadata
            if 'title' in metadata:
                audio_file.tags['TIT2'] = metadata['title']
            if 'artist' in metadata:
                audio_file.tags['TPE1'] = metadata['artist']
            if 'album' in metadata:
                audio_file.tags['TALB'] = metadata['album']
            if 'date' in metadata:
                audio_file.tags['TDRC'] = metadata['date']
            if 'genre' in metadata:
                audio_file.tags['TCON'] = metadata['genre']
            if 'track' in metadata:
                audio_file.tags['TRCK'] = metadata['track']
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error setting MP3 metadata: {str(e)}")
            return False
    
    def _set_flac_metadata(self, file_path, metadata):
        """Set metadata for FLAC file"""
        try:
            audio_file = FLAC(file_path)
            
            # Clear existing metadata
            if audio_file.tags:
                audio_file.delete()
            
            # Set metadata
            for key, value in metadata.items():
                audio_file[key.upper()] = value
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error setting FLAC metadata: {str(e)}")
            return False
    
    def _set_mp4_metadata(self, file_path, metadata):
        """Set metadata for MP4/M4A file"""
        try:
            audio_file = MP4(file_path)
            
            # Tag mapping for MP4
            tag_mapping = {
                'title': '\xa9nam',
                'artist': '\xa9ART',
                'album': '\xa9alb',
                'date': '\xa9day',
                'genre': '\xa9gen',
            }
            
            # Set metadata
            for key, value in metadata.items():
                if key in tag_mapping:
                    audio_file.tags[tag_mapping[key]] = [value]
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error setting MP4 metadata: {str(e)}")
            return False
    
    def _set_ogg_metadata(self, file_path, metadata):
        """Set metadata for OGG file"""
        try:
            audio_file = OggVorbis(file_path)
            
            # Set metadata
            for key, value in metadata.items():
                audio_file[key.upper()] = value
            
            audio_file.save()
            return True
            
        except Exception as e:
            print(f"Error setting OGG metadata: {str(e)}")
            return False
    
    def batch_clean_metadata(self, file_paths):
        """
        Clean metadata from multiple files
        
        Args:
            file_paths (list): List of file paths
            
        Returns:
            dict: Results with success/failure for each file
        """
        results = {}
        
        for file_path in file_paths:
            try:
                success = self.clean_metadata(file_path)
                results[file_path] = {
                    'success': success,
                    'error': None if success else 'Failed to clean metadata'
                }
            except Exception as e:
                results[file_path] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def verify_clean(self, file_path):
        """
        Verify that file has no metadata
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            bool: True if file has no metadata, False otherwise
        """
        try:
            metadata = self.get_metadata(file_path)
            return len(metadata) == 0
        except Exception as e:
            print(f"Error verifying clean metadata: {str(e)}")
            return False
