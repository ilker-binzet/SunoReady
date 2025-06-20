"""
YouTube downloader utilities for SunoReady
Handles YouTube search and audio downloading using yt-dlp
"""

import yt_dlp
import os
from youtubesearchpython import VideosSearch
import re
from pathlib import Path

class YouTubeDownloader:
    def __init__(self, log_callback=None, config=None):
        # Load config for output directory
        if config and 'downloaded_output_folder' in config:
            self.output_dir = config['downloaded_output_folder']
        else:
            self.output_dir = "output/downloads"
        os.makedirs(self.output_dir, exist_ok=True)
        self.log_callback = log_callback
    
    def log(self, message, msg_type="normal"):
        """Log message to callback if available"""
        if self.log_callback:
            self.log_callback(message, msg_type)
        else:
            print(f"[{msg_type.upper()}] {message}")
    
    def progress_hook(self, d):
        """Progress callback for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.log(f"Downloading... {percent:.1f}% ({d['downloaded_bytes']}/{d['total_bytes']} bytes)", "download")
            elif 'total_bytes_estimate' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                self.log(f"Downloading... ~{percent:.1f}% ({d['downloaded_bytes']}/?? bytes)", "download")
            else:
                self.log(f"Downloading... {d['downloaded_bytes']} bytes", "download")
        elif d['status'] == 'finished':
            self.log(f"Download completed: {d['filename']}", "success")
        elif d['status'] == 'error':
            self.log(f"Download error: {d.get('error', 'Unknown error')}", "error")
    
    def search_youtube(self, query, limit=10):
        """
        Search YouTube for videos
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            list: List of video dictionaries with title, url, duration, views
        """
        try:
            # If query is already a URL, return it as single result
            if self._is_youtube_url(query):
                return [{"title": "Direct URL", "url": query, "duration": "Unknown", "views": "Unknown"}]
            
            # Search YouTube with error handling for compatibility
            try:
                videos_search = VideosSearch(query, limit=limit)
                results = videos_search.result()
            except TypeError:
                # Fallback for compatibility issues
                import requests
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                return [{"title": f"Search: {query}", "url": search_url, "duration": "Unknown", "views": "Unknown"}]
            
            formatted_results = []
            for video in results['result']:
                formatted_results.append({
                    'title': video['title'],
                    'url': video['link'],
                    'duration': video['duration'],
                    'views': video['viewCount']['text'] if 'viewCount' in video else 'Unknown',
                    'channel': video['channel']['name'] if 'channel' in video else 'Unknown'
                })
            
            return formatted_results
            
        except Exception as e:
            # Return a fallback result instead of failing completely
            return [{"title": f"Search: {query}", "url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}", "duration": "Unknown", "views": "Unknown"}]
    
    def _is_youtube_url(self, url):
        """Check if string is a valid YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
    
    def download_audio(self, url, output_format='mp3', quality='192'):
        """
        Download audio from YouTube URL
        
        Args:
            url (str): YouTube URL
            output_format (str): Output format (mp3, wav, etc.)
            quality (str): Audio quality in kbps ('64', '128', '192', '256', '320')
            
        Returns:
            str: Path to downloaded file or None if failed
        """
        try:
            self.log("Starting download process...", "info")
            self.log(f"URL: {url}", "youtube")
            self.log(f"Audio quality: {quality} kbps", "info")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'extractaudio': True,
                'audioformat': output_format,
                'audioquality': f'{quality}K',  # Use selected quality
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': output_format,
                    'preferredquality': quality,  # Use selected quality
                }],
                'postprocessor_args': [
                    '-ar', '44100',  # Sample rate
                ],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'no_warnings': False,
                'quiet': False,
                'progress_hooks': [self.progress_hook],
            }
            
            # Download the audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.log("Extracting video information...", "youtube")
                
                # Extract info first to get the title
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                
                self.log(f"Title: {title}", "info")
                self.log(f"Duration: {duration//60}:{duration%60:02d}", "info")
                self.log(f"Uploader: {uploader}", "info")
                
                # Clean title for filename
                clean_title = self._clean_filename(title)
                
                # Update output template with clean title
                ydl_opts['outtmpl'] = os.path.join(self.output_dir, f'{clean_title}.%(ext)s')
                
                self.log("Starting download...", "download")
                
                # Create new YoutubeDL instance with updated options
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    ydl_download.download([url])
                
                # Find the downloaded file
                expected_filename = os.path.join(self.output_dir, f'{clean_title}.{output_format}')
                
                if os.path.exists(expected_filename):
                    self.log(f"Successfully downloaded: {expected_filename}", "success")
                    return expected_filename
                else:
                    # Try to find any new file in output directory
                    for file in os.listdir(self.output_dir):
                        if file.endswith(f'.{output_format}') and clean_title in file:
                            full_path = os.path.join(self.output_dir, file)
                            self.log(f"Successfully downloaded: {full_path}", "success")
                            return full_path
                    
                    self.log("Download completed but file not found!", "error")
                    return None
                    
        except Exception as e:
            self.log(f"Download failed: {str(e)}", "error")
            raise Exception(f"Failed to download audio from YouTube: {str(e)}")
    
    def _clean_filename(self, filename):
        """Clean filename to remove invalid characters"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        # Remove extra spaces and dots
        filename = re.sub(r'\s+', ' ', filename).strip()
        filename = filename.rstrip('.')
        
        return filename
    
    def get_video_info(self, url):
        """
        Get video information without downloading
        
        Args:
            url (str): YouTube URL
            
        Returns:
            dict: Video information
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date', 'Unknown'),
                }
                
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
    
    def download_playlist(self, playlist_url, output_format='mp3', max_downloads=None):
        """
        Download audio from YouTube playlist
        
        Args:
            playlist_url (str): YouTube playlist URL
            output_format (str): Output format
            max_downloads (int): Maximum number of videos to download
            
        Returns:
            list: List of downloaded file paths
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(playlist_index)s - %(title)s.%(ext)s'),
                'extractaudio': True,
                'audioformat': output_format,
                'audioquality': '320K',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': output_format,
                    'preferredquality': '320',
                }],
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'no_warnings': False,
            }
            
            if max_downloads:
                ydl_opts['playlistend'] = max_downloads
            
            downloaded_files = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get playlist info
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                # Download each video
                for entry in playlist_info['entries'][:max_downloads] if max_downloads else playlist_info['entries']:
                    if entry:
                        try:
                            ydl.download([entry['webpage_url']])
                            
                            # Try to find the downloaded file
                            clean_title = self._clean_filename(entry['title'])
                            expected_file = os.path.join(self.output_dir, f"{entry.get('playlist_index', 1)} - {clean_title}.{output_format}")
                            
                            if os.path.exists(expected_file):
                                downloaded_files.append(expected_file)
                                
                        except Exception as e:
                            print(f"Failed to download {entry.get('title', 'Unknown')}: {str(e)}")
                            continue
            
            return downloaded_files
            
        except Exception as e:
            raise Exception(f"Failed to download playlist: {str(e)}")
