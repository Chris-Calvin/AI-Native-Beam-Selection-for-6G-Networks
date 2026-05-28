"""
Installation Validator
Checks if all components are properly installed and configured
"""
import subprocess
import sys
import os
from pathlib import Path

def check_installation():
    """Complete installation check"""
    
    print('\n' + '='*70)
    print('SIONNA-TRANSFER: INSTALLATION VALIDATOR')
    print('='*70 + '\n')
    
    checks = {
        'Python Version': check_python_version,
        'Virtual Environment': check_venv,
        'Required Packages': check_packages,
        'Project Structure': check_project_structure,
        'Directory Permissions': check_permissions,
        'Disk Space': check_disk_space_impl
    }
    
    results = {}
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            results[check_name] = result
            status = '[PASS]' if result else '[FAIL]'
            print(f'{status} - {check_name}')
        except Exception as e:
            results[check_name] = False
            print(f'[FAIL] - {check_name}: {e}')
    
    print()
    return all(results.values())


def check_python_version():
    """Check Python version >= 3.8"""
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print(f'     Python {sys.version.split()[0]}')
        return True
    return False


def check_venv():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f'     Active: {sys.prefix}')
        return True
    else:
        print('     WARNING: Not running in virtual environment')
        print('     Run: venv\\Scripts\\activate')
        return False


def check_packages():
    """Check if all required packages are installed"""
    required = ['torch', 'numpy', 'scipy', 'matplotlib', 'sklearn']
    optional = ['openvino']
    
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f'     Missing: {", ".join(missing)}')
        print(f'     Run: pip install {" ".join(missing)}')
        return False
    else:
        print(f'     All required packages installed')
        
        # Check optional
        for pkg in optional:
            try:
                __import__(pkg)
                print(f'     [OK] {pkg} installed (optional)')
            except ImportError:
                print(f'     [WARN] {pkg} not installed (optional but recommended)')
        
        return True


def check_project_structure():
    """Check if project directories exist"""
    project_root = Path(__file__).resolve().parent.parent
    required_dirs = [
        str(project_root),
        str(project_root / 'src'),
        str(project_root / 'data'),
        str(project_root / 'models'),
        str(project_root / 'outputs')
    ]
    
    required_files = [
        str(project_root / 'main.py'),
        str(project_root / 'requirements.txt'),
        str(project_root / 'src' / 'phase0_extraction.py'),
        str(project_root / 'src' / 'phase1_dataloader.py'),
        str(project_root / 'src' / 'phase3_training.py')
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f'     Missing: {dir_path}')
            all_exist = False
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f'     Missing: {file_path}')
            all_exist = False
    
    if all_exist:
        print('     All directories and files present')
    
    return all_exist


def check_permissions():
    """Check write permissions in output directories"""
    project_root = Path(__file__).resolve().parent.parent
    test_dir = str(project_root / 'outputs')
    test_file = Path(test_dir) / '.test_write'
    
    try:
        test_file.touch()
        test_file.unlink()
        print(f'     Write permissions OK')
        return True
    except PermissionError:
        print(f'     Permission denied: {test_dir}')
        return False


def check_disk_space_impl():
    """Check available disk space"""
    try:
        import shutil
        usage = shutil.disk_usage('C:/')
        available_gb = usage.free / 1e9
        
        if available_gb >= 10:
            print(f'     Available: {available_gb:.1f} GB')
            return True
        else:
            print(f'     WARNING: Only {available_gb:.1f} GB available (need 10+ GB)')
            return False
    except:
        return True


def print_next_steps():
    """Print next steps"""
    print('='*70)
    print('NEXT STEPS')
    print('='*70)
    print()
    project_root = Path(__file__).resolve().parent.parent
    _downloads = Path(os.environ.get("DOWNLOADS_DIR", Path.home() / "Downloads"))
    print('1. Ensure zip files are in Downloads folder or Project Root:')
    print(f'   {project_root / "city_0_newyork_3p5.zip"}')
    print(f'   {project_root / "city_1_losangeles_3p5.zip"}')
    print(f'   (or inside {_downloads})')
    print()
    print('2. Run the pipeline:')
    print(f'   cd {project_root}')
    print('   python main.py')
    print()
    print('3. View results:')
    print(f'   {project_root / "outputs"}')
    print()
    print('='*70)
    print()


if __name__ == '__main__':
    success = check_installation()
    print_next_steps()
    
    if success:
         print('[OK] INSTALLATION VALID - READY TO RUN')
    else:
         print('[ERR] INSTALLATION INCOMPLETE - FIX ISSUES ABOVE')
    
    sys.exit(0 if success else 1)
