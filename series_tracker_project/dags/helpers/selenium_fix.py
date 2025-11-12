import os
import sys

# КРИТИЧЕСКИЕ НАСТРОЙКИ ДЛЯ БЛОКИРОВКИ АВТОЗАГРУЗКИ
os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_SSL_VERIFY'] = '0' 
os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
os.environ['SE_CACHE'] = '0'

# Блокируем импорт webdriver-manager
import builtins
_original_import = builtins.__import__

def _block_webdriver_import(name, *args, **kwargs):
    if any(keyword in name for keyword in ['webdriver_manager', 'webdriver-manager']):
        raise ImportError(f"BLOCKED: {name}")
    return _original_import(name, *args, **kwargs)

builtins.__import__ = _block_webdriver_import

print("✅ Selenium fix applied: auto-download blocked")