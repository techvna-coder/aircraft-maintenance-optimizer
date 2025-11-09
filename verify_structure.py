#!/usr/bin/env python3
"""
Project Structure Verification Script
Kiểm tra tất cả files cần thiết trước khi push lên GitHub
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_check(status, message):
    """Print check result with color"""
    symbol = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
    print(f"{symbol} {message}")

def check_file_exists(filepath, description=""):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    msg = f"{filepath}" + (f" - {description}" if description else "")
    print_check(exists, msg)
    return exists

def check_file_content(filepath, required_strings, description=""):
    """Check if file contains required strings"""
    if not os.path.exists(filepath):
        print_check(False, f"{filepath} - File not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = all(s in content for s in required_strings)
    status = "all patterns found" if all_found else "missing patterns"
    print_check(all_found, f"{filepath} - {description} ({status})")
    return all_found

def main():
    """Main verification function"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔍 AI MAINTENANCE OPTIMIZER - STRUCTURE VERIFICATION{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    all_checks = []
    
    # Root files check
    print(f"{YELLOW}📁 ROOT FILES{RESET}")
    root_files = [
        ('app.py', 'Main Streamlit application'),
        ('requirements.txt', 'Python dependencies'),
        ('README.md', 'Project overview'),
        ('LICENSE', 'MIT License'),
        ('.gitignore', 'Git ignore rules'),
        ('DEPLOYMENT_GUIDE.md', 'Deployment instructions'),
        ('USER_GUIDE.md', 'User manual'),
        ('PROJECT_SUMMARY.md', 'Technical summary'),
        ('QUICK_START.txt', 'Quick reference'),
        ('sample_data.xlsx', 'Sample A350 data'),
        ('GITHUB_CHECKLIST.md', 'GitHub checklist'),
    ]
    
    for filename, desc in root_files:
        all_checks.append(check_file_exists(filename, desc))
    
    print()
    
    # .streamlit directory
    print(f"{YELLOW}⚙️ CONFIGURATION FILES{RESET}")
    config_files = [
        ('.streamlit/config.toml', 'Streamlit configuration'),
    ]
    
    for filename, desc in config_files:
        all_checks.append(check_file_exists(filename, desc))
    
    print()
    
    # utils directory
    print(f"{YELLOW}🧠 UTILS PACKAGE{RESET}")
    utils_files = [
        ('utils/__init__.py', 'Package initialization'),
        ('utils/data_processor.py', 'Data processing module'),
        ('utils/apbc_optimizer.py', 'APBC algorithm'),
        ('utils/visualizer.py', 'Plotly visualizations'),
    ]
    
    for filename, desc in utils_files:
        all_checks.append(check_file_exists(filename, desc))
    
    print()
    
    # Content verification
    print(f"{YELLOW}📝 CONTENT VERIFICATION{RESET}")
    
    # Check .gitignore content
    all_checks.append(check_file_content(
        '.gitignore',
        ['__pycache__', 'venv/', '.streamlit/secrets.toml', '!sample_data.xlsx'],
        'Git ignore patterns'
    ))
    
    # Check LICENSE content
    all_checks.append(check_file_content(
        'LICENSE',
        ['MIT License', '2025', 'AI Maintenance Optimization Team'],
        'MIT License'
    ))
    
    # Check requirements.txt
    all_checks.append(check_file_content(
        'requirements.txt',
        ['streamlit', 'pandas', 'numpy', 'plotly', 'openpyxl'],
        'Dependencies'
    ))
    
    # Check config.toml
    all_checks.append(check_file_content(
        '.streamlit/config.toml',
        ['[theme]', '[server]', 'maxUploadSize'],
        'Streamlit config'
    ))
    
    # Check __init__.py
    all_checks.append(check_file_content(
        'utils/__init__.py',
        ['DataProcessor', 'APBCOptimizer', 'Visualizer', '__all__'],
        'Package imports'
    ))
    
    print()
    
    # File size check
    print(f"{YELLOW}📊 FILE SIZE CHECK{RESET}")
    
    size_checks = [
        ('app.py', 15000, 25000),  # 15-25KB
        ('utils/data_processor.py', 6000, 10000),  # 6-10KB
        ('utils/apbc_optimizer.py', 10000, 16000),  # 10-16KB
        ('utils/visualizer.py', 8000, 14000),  # 8-14KB
    ]
    
    for filepath, min_size, max_size in size_checks:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            in_range = min_size <= size <= max_size
            print_check(in_range, f"{filepath}: {size} bytes (expected {min_size}-{max_size})")
            all_checks.append(in_range)
        else:
            print_check(False, f"{filepath}: File not found")
            all_checks.append(False)
    
    print()
    
    # Security check
    print(f"{YELLOW}🔐 SECURITY CHECK{RESET}")
    
    sensitive_patterns = [
        'password', 'api_key', 'secret_key', 'token', 
        'credential', 'private_key'
    ]
    
    python_files = list(Path('.').rglob('*.py'))
    security_ok = True
    
    for pyfile in python_files:
        with open(pyfile, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            for pattern in sensitive_patterns:
                if pattern in content and 'example' not in content:
                    print_check(False, f"{pyfile}: Contains '{pattern}'")
                    security_ok = False
    
    if security_ok:
        print_check(True, "No sensitive data found in code")
    
    all_checks.append(security_ok)
    
    print()
    
    # Summary
    print(f"{BLUE}{'='*70}{RESET}")
    
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if passed == total:
        print(f"{GREEN}✨ ALL CHECKS PASSED! ({passed}/{total} - 100%)✨{RESET}")
        print(f"{GREEN}🚀 Project is ready for GitHub!{RESET}")
        return_code = 0
    else:
        print(f"{RED}⚠️  SOME CHECKS FAILED ({passed}/{total} - {percentage:.1f}%){RESET}")
        print(f"{RED}❌ Please fix issues before pushing{RESET}")
        return_code = 1
    
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Next steps
    if return_code == 0:
        print(f"{GREEN}📋 NEXT STEPS:{RESET}")
        print("""
1. git init
2. git add .
3. git commit -m "feat: Initial commit - AI Maintenance Task Optimizer v1.0"
4. git remote add origin https://github.com/YOUR_USERNAME/ai-maintenance-optimizer.git
5. git push -u origin main
6. Deploy to Streamlit Cloud!
        """)
    else:
        print(f"{YELLOW}📋 TO FIX:{RESET}")
        print("""
1. Review failed checks above
2. Fix missing files or content
3. Run this script again
4. Proceed when all checks pass
        """)
    
    return return_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Verification interrupted{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")
        sys.exit(1)
