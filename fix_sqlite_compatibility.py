#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复ChromaDB与SQLite版本兼容性问题的脚本
"""

import os
import subprocess
import sys

def install_pysqlite3():
    """安装pysqlite3-binary包"""
    print("正在安装pysqlite3-binary...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pysqlite3-binary"])
        print("✅ pysqlite3-binary安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ pysqlite3-binary安装失败: {e}")
        return False

def create_fix_module():
    """创建SQLite修复模块"""
    fix_module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tradingagents", "utils", "sqlite_fix.py")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(fix_module_path), exist_ok=True)
    
    # 创建修复模块内容
    fix_module_content = '''#!/usr/bin/env python3
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
'''
    
    try:
        with open(fix_module_path, 'w', encoding='utf-8') as f:
            f.write(fix_module_content)
        print(f"✅ SQLite修复模块创建成功: {fix_module_path}")
        return True
    except Exception as e:
        print(f"❌ SQLite修复模块创建失败: {e}")
        return False

def modify_main_scripts():
    """修改主脚本文件，添加SQLite修复导入"""
    # 要修改的文件列表
    main_scripts = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "app.py"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli", "main.py")
    ]
    
    fix_import = "from tradingagents.utils.sqlite_fix import apply_sqlite_fix; apply_sqlite_fix()"
    
    for script_path in main_scripts:
        if not os.path.exists(script_path):
            print(f"⚠️ 脚本不存在: {script_path}")
            continue
        
        try:
            # 读取文件内容
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            # 检查是否已经包含修复代码
            if any(fix_import in line for line in content):
                print(f"✅ 脚本已包含修复: {script_path}")
                continue
            
            # 在文件开头添加修复导入（在shebang之后）
            if content and content[0].startswith("#!/"):
                # 有shebang行，插入到第二行
                content.insert(1, fix_import + "\n")
            else:
                # 没有shebang行，插入到第一行
                content.insert(0, fix_import + "\n")
            
            # 写回文件
            with open(script_path, 'w', encoding='utf-8') as f:
                f.writelines(content)
            
            print(f"✅ 已修改脚本: {script_path}")
        except Exception as e:
            print(f"❌ 修改脚本失败: {script_path}, 错误: {e}")

def main():
    """主函数"""
    print("===== ChromaDB SQLite兼容性修复工具 =====\n")
    
    # 1. 安装pysqlite3-binary
    install_pysqlite3()
    
    # 2. 创建修复模块
    create_fix_module()
    
    # 3. 修改主脚本文件
    modify_main_scripts()
    
    print("\n===== 修复完成 =====")
    print("修复说明:")
    print("1. 已安装pysqlite3-binary包，它提供了较新版本的SQLite")
    print("2. 已创建SQLite修复模块，会在运行时替换默认的sqlite3模块")
    print("3. 已修改主脚本文件，添加了修复代码的导入")
    print("\n现在您可以尝试运行项目了。如果问题仍然存在，请先运行check_versions.py查看详细的版本信息。")

if __name__ == '__main__':
    main()