#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQLite版本修复模块
在导入chromadb之前替换sqlite3模块以解决版本兼容性问题
"""

import sys
import importlib.util

def apply_sqlite_fix():
    """应用SQLite修复，替换默认的sqlite3模块"""
    # 检查是否已经应用了修复
    if hasattr(sys, '_sqlite_fix_applied') and sys._sqlite_fix_applied:
        return True
    
    try:
        # 检查pysqlite3是否已安装
        if importlib.util.find_spec("pysqlite3") is None:
            print("⚠️ pysqlite3未安装，无法应用修复")
            return False
        
        # 导入pysqlite3并替换默认的sqlite3模块
        import pysqlite3
        sys.modules['sqlite3'] = pysqlite3
        
        # 标记修复已应用
        sys._sqlite_fix_applied = True
        
        # 打印版本信息
        print(f"✅ SQLite修复应用成功: {pysqlite3.sqlite_version}")
        return True
    except Exception as e:
        print(f"❌ 应用SQLite修复失败: {e}")
        return False

# 自动应用修复
apply_sqlite_fix()
