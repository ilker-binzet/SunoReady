#!/usr/bin/env python3
"""
SunoReady CLI - Command Line Interface
Audio processing tool with pitch control and copyright bypass capabilities
"""

import argparse
import sys
import json
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def create_parser():
    """Create the command line argument parser with comprehensive help text"""
    parser = argparse.ArgumentParser(
        prog='SunoReady',
        description='Audio processing tool for Suno AI with advanced pitch control and copyright bypass features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --gui                              # Launch GUI interface
  %(prog)s process input.mp3                 # Process with default settings
  %(prog)s process input.mp3 --pitch 3       # Apply +3 semitones pitch shift
  %(prog)s process *.mp3 --pitch -2 --tempo 105  # Batch process with custom settings
  %(prog)s process song.wav --pitch 7 --normalize --clean-metadata
  
Pitch Control:
  The pitch control feature allows precise adjustment of audio pitch while maintaining tempo.
  
  Range: −12 to +12 semitones (2 full octaves)
  • 1 semitone = smallest musical interval (piano keys)
  • +12 semitones = 1 octave higher (double frequency)
  • −12 semitones = 1 octave lower (half frequency)
  
  Common Usage:
  • ±1-3 semitones: Subtle changes for copyright bypass
  • ±4-7 semitones: Noticeable pitch changes for creative purposes
  • ±8-12 semitones: Dramatic pitch shifts (may reduce quality)
  
  Mathematical Formula: frequency_out = frequency_in × 2^(semitones/12)
  
Audio Quality Tips:
  • Smaller pitch changes (±1-6 semitones) maintain better quality
  • Combine with other effects for maximum copyright bypass effectiveness
  • Use Lightning processor (default) for best speed vs quality balance

Copyright Notice:
  This tool is for educational and research purposes only.
  Users are responsible for complying with copyright laws.
        """
    )
    
    # Main command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch graphical user interface')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process audio files with specified settings')
    process_parser.add_argument('files', nargs='+', help='Input audio files to process')
    
    # Audio processing options
    audio_group = process_parser.add_argument_group('Audio Processing Options')
    
    audio_group.add_argument(
        '--pitch', 
        type=float, 
        default=0, 
        metavar='SEMITONES',
        help='Pitch shift in semitones (range: −12 to +12). '
             'Positive values raise pitch, negative values lower it. '
             'Examples: --pitch 3 (raise by 3 semitones), --pitch -2 (lower by 2 semitones)'
    )
    
    audio_group.add_argument(
        '--tempo', 
        type=float, 
        default=100, 
        metavar='PERCENT',
        help='Tempo change as percentage (50-200). '
             'Examples: --tempo 105 (5%% faster), --tempo 95 (5%% slower). Default: 100'
    )
    
    audio_group.add_argument(
        '--normalize', 
        action='store_true',
        help='Normalize volume levels for consistent output'
    )
    
    audio_group.add_argument(
        '--add-noise', 
        action='store_true',
        help='Add imperceptible white noise to alter audio signature'
    )
    
    audio_group.add_argument(
        '--highpass', 
        action='store_true',
        help='Apply highpass filter for frequency modification'
    )
    
    audio_group.add_argument(
        '--clean-metadata', 
        action='store_true',
        help='Remove metadata and copyright information from output files'
    )
    
    # Output options
    output_group = process_parser.add_argument_group('Output Options')
    
    output_group.add_argument(
        '--format', 
        choices=['mp3', 'wav', 'flac'], 
        default='mp3',
        help='Output audio format. Default: mp3'
    )
    
    output_group.add_argument(
        '--output-dir', 
        default='output/processed',
        help='Output directory for processed files. Default: output/processed'
    )
    
    output_group.add_argument(
        '--quality', 
        default='320k',
        help='Output quality for MP3 format (e.g., 128k, 192k, 320k). Default: 320k'
    )
    
    # YouTube download command
    download_parser = subparsers.add_parser('download', help='Download audio from YouTube')
    download_parser.add_argument('url', help='YouTube URL to download')
    download_parser.add_argument(
        '--quality', 
        choices=['64', '128', '192', '256', '320'], 
        default='192',
        help='Audio quality in kbps. Default: 192'
    )
    
    # Configuration command
    config_parser = subparsers.add_parser('config', help='Show or modify configuration')
    config_parser.add_argument(
        '--show', 
        action='store_true',
        help='Show current configuration'
    )
    config_parser.add_argument(
        '--reset', 
        action='store_true',
        help='Reset configuration to defaults'
    )
    
    # Version and info
    parser.add_argument(
        '--version', 
        action='version', 
        version='SunoReady v1.0.0 - Audio Processing Tool'
    )
    
    return parser

def validate_pitch_range(pitch_value):
    """Validate pitch value is within acceptable range"""
    if not -12 <= pitch_value <= 12:
        raise ValueError(f"Pitch value {pitch_value} is outside valid range (−12 to +12 semitones)")
    return pitch_value

def validate_tempo_range(tempo_value):
    """Validate tempo value is within acceptable range"""
    if not 50 <= tempo_value <= 200:
        raise ValueError(f"Tempo value {tempo_value}% is outside valid range (50-200%)")
    return tempo_value

def main():
    """Main CLI entry point"""
    parser = create_parser()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.command == 'gui' or args.command is None:
        # Launch GUI
        print("🚀 Launching SunoReady GUI...")
        from app import SunoReadyApp
        app = SunoReadyApp()
        app.run()
        
    elif args.command == 'process':
        # Validate arguments
        try:
            pitch = validate_pitch_range(args.pitch)
            tempo = validate_tempo_range(args.tempo)
        except ValueError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        
        # Process files
        print(f"🎵 Processing {len(args.files)} file(s)...")
        print(f"⚙️ Settings:")
        print(f"   • Pitch: {pitch:+.0f} semitones")
        print(f"   • Tempo: {tempo:.0f}%")
        print(f"   • Format: {args.format}")
        if args.normalize:
            print(f"   • Volume normalization: enabled")
        if args.add_noise:
            print(f"   • Noise injection: enabled") 
        if args.highpass:
            print(f"   • Highpass filter: enabled")
        if args.clean_metadata:
            print(f"   • Metadata cleaning: enabled")
        print()
        
        # TODO: Implement actual processing logic
        print("🚧 CLI processing not yet implemented. Please use the GUI interface.")
        print("💡 Run 'python sunoready_cli.py gui' to launch the graphical interface.")
        
    elif args.command == 'download':
        print(f"⬇️ Downloading from: {args.url}")
        print(f"🎵 Quality: {args.quality} kbps")
        # TODO: Implement download logic
        print("🚧 CLI download not yet implemented. Please use the GUI interface.")
        
    elif args.command == 'config':
        if args.show:
            # Show current configuration
            try:
                with open('config/config.json', 'r') as f:
                    config = json.load(f)
                print("📋 Current Configuration:")
                print(f"   • Pitch: {config.get('pitch_semitones', 0)} semitones")
                print(f"   • Tempo: {config.get('tempo_change', 100)}%")
                print(f"   • Normalize: {config.get('normalize_volume', True)}")
                print(f"   • Add noise: {config.get('add_noise', False)}")
                print(f"   • Highpass: {config.get('apply_highpass', False)}")
                print(f"   • Clean metadata: {config.get('clean_metadata', False)}")
                print(f"   • Output format: {config.get('output_format', 'mp3')}")
            except FileNotFoundError:
                print("⚠️ Configuration file not found. Using defaults.")
        elif args.reset:
            print("🔄 Resetting configuration to defaults...")
            # TODO: Implement config reset
            print("🚧 Config reset not yet implemented.")

if __name__ == '__main__':
    main()
