"""
Phase 0: Auto-extraction of DeepMIMO zip files
Extracts NY and LA datasets to working directory
"""
import zipfile
import os
from pathlib import Path

def extract_datasets(working_dir=None):
    """
    Automatically extract zipped DeepMIMO datasets
    
    Args:
        working_dir: Root working directory
        
    Returns:
        dict: Paths to extracted datasets
    """
    if working_dir is None:
        project_root = Path(__file__).resolve().parent.parent
        working_dir = str(project_root)
    else:
        project_root = Path(working_dir)
        working_dir = str(working_dir)
        
    # Create working directory if not exists
    os.makedirs(working_dir, exist_ok=True)
    
    # Define zip paths
    _downloads = Path(os.environ.get("DOWNLOADS_DIR", Path.home() / "Downloads"))
    
    zips = {
        'NewYork': str(project_root / 'city_0_newyork_3p5.zip') if (project_root / 'city_0_newyork_3p5.zip').exists() else str(_downloads / 'city_0_newyork_3p5.zip'),
        'LosAngeles': str(project_root / 'city_1_losangeles_3p5.zip') if (project_root / 'city_1_losangeles_3p5.zip').exists() else str(_downloads / 'city_1_losangeles_3p5.zip')
    }
    
    extracted_paths = {}
    
    for city, zip_path in zips.items():
        extract_dir = os.path.join(working_dir, 'data', city)
        
        # Skip if already extracted
        if os.path.exists(extract_dir) and len(os.listdir(extract_dir)) > 0:
            print(f'[OK] {city} dataset already extracted at {extract_dir}')
            extracted_paths[city] = extract_dir
            continue
        
        # Check if zip exists
        if not os.path.exists(zip_path):
            print(f'[ERR] {city} zip not found at {zip_path}')
            continue
        
        # Extract
        os.makedirs(extract_dir, exist_ok=True)
        print(f'Extracting {city} ({os.path.getsize(zip_path) / 1e9:.2f} GB)...')
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f'[OK] {city} extraction complete')
            extracted_paths[city] = extract_dir
        except Exception as e:
            print(f'[ERR] Error extracting {city}: {e}')
    
    return extracted_paths


if __name__ == '__main__':
    print('Phase 0: Auto-Extraction')
    print('-' * 50)
    paths = extract_datasets()
    print(f'\nExtracted paths: {paths}')
