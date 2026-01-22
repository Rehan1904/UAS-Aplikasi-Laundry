# build.py
import os
import shutil
import PyInstaller.__main__

def clean_build():
    """Bersihkan folder build sebelumnya"""
    folders = ['build', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    print("Folder build dibersihkan")

def build_app():
    """Build aplikasi menjadi executable"""
    
    # Data files yang diperlukan
    data_files = [
        ('ui/*.png', 'ui'),
        ('ui/*.ui', 'ui'),
        ('laundry.db', '.')  # Database kosong
    ]
    
    # Format data untuk pyinstaller
    add_data = []
    for src, dst in data_files:
        if os.path.exists(src if '*' not in src else src.replace('*', '')):
            add_data.append(f'--add-data={src};{dst}')
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=LaundryApp',
        '--onefile',
        '--windowed',
        '--noconsole',
        '--icon=ui/icon.ico' if os.path.exists('ui/icon.ico') else '',
        '--clean',
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.pdfgen',
        '--hidden-import=reportlab.lib',
        '--hidden-import=sqlite3',
    ]
    
    # Tambahkan data files
    args.extend(add_data)
    
    # Filter argumen kosong
    args = [arg for arg in args if arg]
    
    print("Building aplikasi...")
    print("Args:", args)
    
    # Jalankan PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n✅ Build selesai!")
    print("📁 Executable ada di folder: dist/LaundryApp.exe")

if __name__ == "__main__":
    clean_build()
    build_app()