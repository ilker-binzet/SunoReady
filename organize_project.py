#!/usr/bin/env python3
"""
SunoReady Proje Organizasyon Scripti
Dağınık dosyaları düzenli klasörlere taşır
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """Proje dosyalarını organize et"""
    
    base_path = Path.cwd()
    print(f"🗂️ Organizing project at: {base_path}")
    
    # Dosya kategorileri ve hedef klasörleri
    file_moves = {
        # Ana kaynak kodlar -> src/
        'src': [
            'app.py', 'audio_utils.py', 'yt_downloader.py', 'metadata_utils.py',
            'fast_processor.py', 'lightning_processor.py', 'audio_processor_dll.py'
        ],
        
        # Test dosyaları -> tests/
        'tests': [
            'test_audio_devices.py', 'test_audio_processing.py', 'test_compact_design.py',
            'test_demo_startstop.py', 'test_duration_fix.py', 'test_exact_pipeline.py',
            'test_fade_optimization.py', 'test_force_compact.py', 'test_gui_processing.py',
            'test_microphone.py', 'test_microphone_advanced.py', 'test_problematic_file.py',
            'test_progress_callback.py', 'test_responsive_design.py', 'test_smart_controls.py',
            'test_audio.wav', 'simple_test.wav'
        ],
        
        # Script dosyaları -> scripts/
        'scripts': [
            'compile_dll.bat', 'setup_dll.bat', 'launch.bat', 'fix_dll.bat',
            'organize_output_files.py', 'basit_hiz_testi.py', 'exact_integration_steps.py',
            'final_performance_test.py', 'final_test.py', 'integration_guide.py',
            'quick_performance_test.py'
        ],
        
        # Dokümantasyon -> docs/
        'docs': [
            'BUILD_INFO.md', 'COMPACT_DESIGN_COMPLETE.md', 'DURATION_BUG_FIX.md',
            'FIXED_SMALL_MONITOR_ISSUE.md', 'LIVE_PREVIEW_REMOVED.md', 'NEW_FEATURES.md',
            'RESPONSIVE_DESIGN_UPDATE.md', 'SMART_CONTROLS_FEATURE.md', 'THEME_UPDATE.md',
            'README.md', 'PROJECT_ORGANIZATION_PLAN.md'
        ],
        
        # Konfigürasyon -> config/
        'config': [
            'config.json', 'theme_config.json', '.env', 'pyproject.toml', 'pyrightconfig.json'
        ],
        
        # Varlıklar -> assets/
        'assets': [
            'generated-icon.png'
        ],
        
        # Build dosyaları -> build/
        'build': [
            'sunoready_audio.dll', 'sunoready_audio.cpp', 'SunoReady.spec'
        ],
        
        # Debug dosyaları -> debug/
        'debug': [
            'debug_auto_restart.py', 'debug_current_bug.py', 'debug_duration.py',
            'debug_duration_bug.py', 'debug_extreme_duration.py', 'performance_analysis.py',
            'performance_benchmark.py', 'performance_comparison.py', 'performance_test.py'
        ]
    }
    
    moved_count = 0
    errors = []
    
    # Dosyaları taşı
    for target_dir, files in file_moves.items():
        target_path = base_path / target_dir
        target_path.mkdir(exist_ok=True)
        
        for filename in files:
            source_file = base_path / filename
            target_file = target_path / filename
            
            if source_file.exists():
                try:
                    shutil.move(str(source_file), str(target_file))
                    print(f"✅ {filename} -> {target_dir}/")
                    moved_count += 1
                except Exception as e:
                    error_msg = f"❌ Error moving {filename}: {e}"
                    print(error_msg)
                    errors.append(error_msg)
            else:
                print(f"⚠️ File not found: {filename}")
    
    # Özel durumlar
    
    # fonts klasörünü assets altına taşı
    if (base_path / 'fonts').exists():
        try:
            shutil.move(str(base_path / 'fonts'), str(base_path / 'assets' / 'fonts'))
            print("✅ fonts/ -> assets/fonts/")
            moved_count += 1
        except Exception as e:
            errors.append(f"❌ Error moving fonts/: {e}")
    
    # requirements.txt'i root'ta bırak (çünkü pip install için gerekli)
    print("ℹ️ requirements.txt stays in root (needed for pip install)")
    
    # Özet
    print(f"\n🎉 Organization complete!")
    print(f"📦 {moved_count} files moved")
    print(f"❌ {len(errors)} errors")
    
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"  {error}")
    
    print(f"\n📁 New structure:")
    for target_dir in file_moves.keys():
        count = len([f for f in file_moves[target_dir] if (base_path / target_dir / f).exists()])
        print(f"  {target_dir}/: {count} files")

if __name__ == "__main__":
    organize_project()
