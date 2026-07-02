import os
import zipfile

def zip_project():
    # Find Downloads folder dynamically
    home_dir = os.path.expanduser('~')
    downloads_dir = os.path.join(home_dir, 'Downloads')
    
    if not os.path.exists(downloads_dir):
        # Fallback if downloads folder is missing or elsewhere
        downloads_dir = os.path.dirname(os.path.abspath(__file__))
        
    zip_filename = 'student_performance_prediction.zip'
    zip_filepath = os.path.join(downloads_dir, zip_filename)
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Creating project ZIP archive at: {zip_filepath}")
    
    # Excluded directories and file patterns
    exclude_dirs = {'.git', '.github', '.venv', 'venv', '__pycache__', '.ipynb_checkpoints'}
    exclude_files = {zip_filename, 'db.sqlite3'}  # Let's exclude db.sqlite3 so they get a fresh database, or keep it? Keeping it is fine, but django creates a fresh one. Let's include db.sqlite3 if it exists but let migrations handle it. Let's keep it clean.
    
    count = 0
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
            
            for file in files:
                if file in exclude_files or file.endswith('.pyc') or file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                # Compute relative path to preserve directory structure in ZIP
                rel_path = os.path.relpath(file_path, project_root)
                zipf.write(file_path, rel_path)
                count += 1
                
    print(f"Successfully zipped {count} files into {zip_filepath}")
    return zip_filepath

if __name__ == '__main__':
    zip_project()
