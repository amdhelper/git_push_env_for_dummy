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
        '--clean',
    ])
    
    # If on Linux, also try to package as DEB if version is provided
    if sys.platform.startswith('linux') and os.environ.get('VERSION'):
        version = os.environ.get('VERSION')
        print(f"Packaging for Linux DEB (Version: {version})...")
        pkg_dir = f"deb_dist/geinei-uploader"
        os.makedirs(f"{pkg_dir}/usr/local/bin", exist_ok=True)
        os.makedirs(f"{pkg_dir}/DEBIAN", exist_ok=True)
        
        shutil.copy2("dist/GeineiUploader", f"{pkg_dir}/usr/local/bin/geinei-uploader")
        os.chmod(f"{pkg_dir}/usr/local/bin/geinei-uploader", 0o755)
        
        with open(f"{pkg_dir}/DEBIAN/control", "w") as f:
            f.write(f"Package: geinei-uploader\n")
            f.write(f"Version: {version}\n")
            f.write(f"Architecture: amd64\n")
            f.write(f"Maintainer: AMDHelper <admin@example.com>\n")
            f.write(f"Description: Auto Git Uploader for Geinei Site\n")
            
        subprocess.run(["dpkg-deb", "--build", pkg_dir], check=True)
        shutil.move("deb_dist/geinei-uploader.deb", f"dist/GeineiUploader_v{version}_amd64.deb")

    print("\n[SUCCESS] Build complete! Look in the 'dist' folder.")
except Exception as e:
    print(f"\n[ERROR] Build failed: {e}")
