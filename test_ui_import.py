import sys
sys.path.insert(0, r'c:\Users\taras\OneDrive\Plocha\Projects\App\Causa')
from src.ui import desktop, web
print('UI modules imported successfully')
print(f'Desktop class: {desktop.PyWebViewApp}')
print(f'Web class: {web.ReactViteApp}')