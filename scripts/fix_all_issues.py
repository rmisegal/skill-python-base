"""
Comprehensive fixer for all QA issues.
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qa_engine.infrastructure.detection import (
    BiDiDetector, CodeDetector, TOCDetector, TableDetector
)
from qa_engine.infrastructure.fixing import BiDiFixer, CodeFixer, DirectionFixer, TableFixer
from qa_engine.infrastructure.fixing.toc_fixer import TOCFixer


def fix_tex_files(base_path):
    tex_files = [f for f in base_path.glob("**/*.tex") if "test-cls-examples" not in str(f)]
    
    bidi_det = BiDiDetector()
    code_det = CodeDetector()
    table_det = TableDetector()
    bidi_fixer = BiDiFixer()
    code_fixer = CodeFixer()
    direction_fixer = DirectionFixer()
    table_fixer = TableFixer()
    
    stats = {"files": 0, "bidi": 0, "code": 0, "direction": 0, "table": 0}
    
    for f in tex_files:
        content = f.read_text(encoding="utf-8")
        original = content
        
        # Apply BiDi fixes
        bidi_issues = list(bidi_det.detect(content, str(f)))
        if bidi_issues:
            content = bidi_fixer.fix(content, bidi_issues)
            stats["bidi"] += len(bidi_issues)
        
        # Apply Code fixes
        code_issues = list(code_det.detect(content, str(f)))
        if code_issues:
            content = code_fixer.fix(content, code_issues)
            stats["code"] += len(code_issues)
        
        # Apply Direction fixes
        content, dir_result = direction_fixer.fix_content(content, str(f))
        stats["direction"] += dir_result.fixes_applied
        
        # Apply Table fixes
        table_issues = list(table_det.detect(content, str(f)))
        if table_issues:
            content = table_fixer.fix(content, table_issues)
            stats["table"] += len(table_issues)
        
        # Fix Hebrew in code blocks
        lines = content.split("\n")
        fixed_lines = []
        in_code = False
        
        for line in lines:
            if "begin{pythonbox" in line or "begin{lstlisting" in line:
                in_code = True
            if "end{pythonbox" in line or "end{lstlisting" in line:
                in_code = False
            
            if in_code:
                def wrap_heb(m):
                    txt = m.group(0)
                    pos = m.start()
                    before = line[max(0, pos-15):pos]
                    if "texthebrew{" in before or "hebtitle{" in before:
                        return txt
                    return "\texthebrew{" + txt + "}"
                line = re.sub(r"[\u0590-\u05FF]{2,}", wrap_heb, line)
            
            fixed_lines.append(line)
        
        content = "\n".join(fixed_lines)
        
        if content != original:
            f.write_text(content, encoding="utf-8")
            stats["files"] += 1
    
    return stats


def fix_cls_files(base_path):
    cls_files = [f for f in base_path.glob("**/*.cls") if "test-cls-examples" not in str(f)]
    toc_fixer = TOCFixer()
    stats = {"files": 0, "toc": 0}
    
    for f in cls_files:
        content = f.read_text(encoding="utf-8")
        original = content
        content, num_fixes = toc_fixer.fix_all_counter_issues(content)
        stats["toc"] += num_fixes
        
        if content != original:
            f.write_text(content, encoding="utf-8")
            stats["files"] += 1
    
    return stats


if __name__ == "__main__":
    base_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    print(f"Fixing: {base_path}")
    
    tex_stats = fix_tex_files(base_path)
    print(f"TEX: {tex_stats}")
    
    cls_stats = fix_cls_files(base_path)
    print(f"CLS: {cls_stats}")
    
    total = tex_stats["bidi"] + tex_stats["code"] + tex_stats["direction"] + tex_stats["table"] + cls_stats["toc"]
    print(f"TOTAL FIXES: {total}")
