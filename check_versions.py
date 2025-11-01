#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查Python和SQLite版本信息的脚本
用于诊断ChromaDB与SQLite版本兼容性问题
"""

import sys
import sqlite3
import importlib.util
import os

def check_python_version():
    """检查Python版本"""
    print("=== Python版本信息 ===")
    print(f"Python版本: {sys.version}")
    print(f"主版本号: {sys.version_info.major}")
    print(f"次版本号: {sys.version_info.minor}")
    print(f"微版本号: {sys.version_info.micro}")
    
    # 检查是否满足项目要求
    if sys.version_info < (3, 10):
        print("❌ 警告: Python版本低于3.10，可能导致兼容性问题")
    else:
        print("✅ Python版本满足项目要求 (>=3.10)")
    print()

def check_sqlite_version():
    """检查SQLite版本"""
    print("=== SQLite版本信息 ===")
    print(f"SQLite版本: {sqlite3.sqlite_version}")
    
    # 解析版本号
    version_parts = sqlite3.sqlite_version.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])
    patch = int(version_parts[2].split('-')[0])  # 处理可能的额外信息
    
    # 检查是否满足ChromaDB要求 (>=3.35.0)
    if (major, minor, patch) >= (3, 35, 0):
        print("✅ SQLite版本满足ChromaDB要求 (>=3.35.0)")
    else:
        print("❌ 警告: SQLite版本低于3.35.0，这可能导致ChromaDB初始化失败")
    print()

def check_chromadb_installed():
    """检查ChromaDB是否已安装"""
    print("=== ChromaDB安装检查 ===")
    
    # 检查模块是否存在
    spec = importlib.util.find_spec("chromadb")
    if spec is None:
        print("❌ ChromaDB未安装")
        return False
    
    # 尝试导入并获取版本
    try:
        import chromadb
        print(f"ChromaDB版本: {chromadb.__version__}")
        
        # 检查是否满足项目要求
        version_parts = chromadb.__version__.split('.')
        if len(version_parts) >= 2 and version_parts[0] == '1' and int(version_parts[1]) >= 0:
            print("✅ ChromaDB版本满足项目要求 (>=1.0.0)")
        else:
            print("❌ 警告: ChromaDB版本可能不兼容，建议使用1.0.x版本")
        
        return True
    except Exception as e:
        print(f"❌ ChromaDB导入失败: {e}")
        return False
    print()

def check_pysqlite3_installed():
    """检查pysqlite3是否已安装"""
    print("=== pysqlite3安装检查 ===")
    
    # 检查模块是否存在
    spec = importlib.util.find_spec("pysqlite3")
    if spec is None:
        print("❌ pysqlite3未安装")
        print("  提示: 可以尝试安装pysqlite3-binary来解决SQLite版本问题")
        return False
    
    # 尝试导入并获取信息
    try:
        import pysqlite3
        print("✅ pysqlite3已安装")
        if hasattr(pysqlite3, "sqlite_version"):
            print(f"pysqlite3绑定的SQLite版本: {pysqlite3.sqlite_version}")
        return True
    except Exception as e:
        print(f"❌ pysqlite3导入失败: {e}")
        return False
    print()

def check_venv_info():
    """检查虚拟环境信息"""
    print("=== 虚拟环境信息 ===")
    
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        print(f"✅ 正在使用虚拟环境: {sys.prefix}")
        
        # 检查是否在项目的env目录
        if 'env' in sys.prefix and 'TradingAgents-CN' in sys.prefix:
            print("✅ 使用的是项目自带的虚拟环境")
        else:
            print("⚠️ 使用的不是项目自带的虚拟环境")
    else:
        print("⚠️ 未使用虚拟环境，这可能导致依赖冲突")
    print()

def main():
    """主函数"""
    print("===== ChromaDB兼容性诊断工具 =====\n")
    
    check_python_version()
    check_sqlite_version()
    chromadb_installed = check_chromadb_installed()
    check_pysqlite3_installed()
    check_venv_info()
    
    print("\n===== 诊断完成 =====")
    print("基于诊断结果的建议:")
    
    # 解析SQLite版本以提供建议
    version_parts = sqlite3.sqlite_version.split('.')
    major = int(version_parts[0])
    minor = int(version_parts[1])
    patch = int(version_parts[2].split('-')[0])
    
    if (major, minor, patch) < (3, 35, 0):
        print("1. SQLite版本过低，建议:")
        print("   a. 安装pysqlite3-binary: pip install pysqlite3-binary")
        print("   b. 修改代码，在导入chromadb前替换sqlite3模块")
        print("      import pysqlite3; import sys; sys.modules['sqlite3'] = pysqlite3")
    
    if not chromadb_installed:
        print("2. 安装ChromaDB: pip install chromadb>=1.0.12")
    
    if sys.version_info < (3, 10):
        print("3. 升级到Python 3.10或更高版本")

if __name__ == '__main__':
    main()