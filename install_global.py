#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全局安装脚本 - 将team-work-report skill安装到Claude Code全局skills目录
"""
import os
import shutil
import sys
from pathlib import Path


def install_global_skill():
    """安装skill到全局目录"""

    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.absolute()

    # Claude Code全局skills目录
    skill_dir = Path.home() / ".claude" / "skills" / "team-work-report"

    print("[INFO] Installing team-work-report skill...")
    print(f"   Source: {current_dir}")
    print(f"   Target: {skill_dir}")

    # 创建目标目录
    skill_dir.mkdir(parents=True, exist_ok=True)

    # 需要复制的文件和目录
    items_to_copy = [
        "SKILL.md",
        "README.md",
        "requirements.txt",
        "scripts",
        "templates"
    ]

    # 复制文件
    for item in items_to_copy:
        src = current_dir / item
        dst = skill_dir / item

        if src.exists():
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()

            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

            print(f"   [OK] Copied: {item}")
        else:
            print(f"   [SKIP] {item} (not found)")

    # 检查依赖
    print("\n[CHECK] Checking dependencies...")
    try:
        import openpyxl
        import pandas
        import anthropic
        import jinja2
        print("   [OK] All dependencies installed")
    except ImportError as e:
        print(f"   [WARN] Missing dependency: {e}")
        print("   [INFO] Run: pip install -r requirements.txt")

    print(f"\n[SUCCESS] Installation complete!")
    print(f"\nUsage:")
    print(f"   In Claude Code:")
    print(f"   /team-work-report <Excel文件路径>")
    print(f"\n   Command line:")
    print(f"   python {skill_dir / 'scripts' / 'skill.py'} <excel_file> [options]")
    print(f"\nGitHub: https://github.com/circleone1980/team-work-report")


def uninstall_global_skill():
    """卸载全局skill"""
    skill_dir = Path.home() / ".claude" / "skills" / "team-work-report"

    if skill_dir.exists():
        shutil.rmtree(skill_dir)
        print(f"✅ 已卸载: {skill_dir}")
    else:
        print(f"⚠️  未找到: {skill_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_global_skill()
    else:
        install_global_skill()
