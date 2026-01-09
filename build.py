import PyInstaller.__main__
import os
import customtkinter
import sys

# Get the path to customtkinter library to include its theme files
ctk_path = os.path.dirname(customtkinter.__file__)

# Determine separator based on OS
sep = ';' if sys.platform.startswith('win') else ':'

print(f"Building for {sys.platform}...")
print(f"Including CustomTkinter from: {ctk_path}")

try:
    PyInstaller.__main__.run([
        'geinei_uploader.py',
        '--onefile',
        '--noconsole',
        '--name=GeineiUploader',
        f'--add-data={ctk_path}{sep}customtkinter',
        '--clean',  # Clean cache
    ])
    print("\n✅ Build complete! Look in the 'dist' folder.")
except Exception as e:
    print(f"\n❌ Build failed: {e}")
