#!/usr/bin/env python3
"""
ドキュメント自動生成スクリプト
仕様書から各種ドキュメントを自動生成します。
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class DocumentGenerator:
    def __init__(self, base_path: str = "docs/specifications"):
        self.base_path = Path(base_path)
        self.requirements_path = self.base_path / "requirements"
        self.design_path = self.base_path / "design"
        self.technical_path = self.base_path / "technical"
        
    def parse_requirements(self) -> Dict[str, Any]:
        """要件定義書を解析"""
        requirements = {
            "functional": [],
            "non_functional": [],
            "user_stories": []
        }
        
        # 機能要件の解析
        func_file = self.requirements_path / "functional.md"
        if func_file.exists():
            requirements["functional"] = self._parse_functional_requirements(func_file)
            
        # 非機能要件の解析
        non_func_file = self.requirements_path / "non-functional.md"
        if non_func_file.exists():
            requirements["non_functional"] = self._parse_non_functional_requirements(non_func_file)
            
        return requirements
    
    def _parse_functional_requirements(self, file_path: Path) -> List[Dict[str, Any]]:
        """機能要件を解析"""
        requirements = []
        current_req = {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 要件IDのパターンマッチング
        pattern = r'- \*\*要件ID\*\*: (FR-\d+)\n- \*\*機能名\*\*: (.+?)\n- \*\*優先度\*\*: (.+?)\n- \*\*詳細\*\*:\n((?:  - .+?\n)*)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            req_id, func_name, priority, details = match
            details_list = [line.strip()[3:] for line in details.strip().split('\n') if line.strip().startswith('  -')]
            
            requirements.append({
                "id": req_id,
                "name": func_name,
                "priority": priority,
                "details": details_list
            })
            
        return requirements
    
    def _parse_non_functional_requirements(self, file_path: Path) -> List[Dict[str, Any]]:
        """非機能要件を解析"""
        requirements = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 要件IDのパターンマッチング
        pattern = r'- \*\*要件ID\*\*: (NFR-\d+)\n- \*\*項目\*\*: (.+?)\n- \*\*詳細\*\*:\n((?:  - .+?\n)*)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            req_id, item, details = match
            details_list = [line.strip()[3:] for line in details.strip().split('\n') if line.strip().startswith('  -')]
            
            requirements.append({
                "id": req_id,
                "item": item,
                "details": details_list
            })
            
        return requirements
    
    def generate_summary_report(self, requirements: Dict[str, Any]) -> str:
        """サマリーレポートを生成"""
        report = f"""# 要件定義サマリーレポート

生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 機能要件 ({len(requirements.get('functional', []))}件)

"""
        
        for req in requirements.get('functional', []):
            report += f"### {req['id']}: {req['name']}\n"
            report += f"- 優先度: {req['priority']}\n"
            report += f"- 詳細項目数: {len(req['details'])}\n\n"
            
        report += f"""## 非機能要件 ({len(requirements.get('non_functional', []))}件)

"""
        
        for req in requirements.get('non_functional', []):
            report += f"### {req['id']}: {req['item']}\n"
            report += f"- 詳細項目数: {len(req['details'])}\n\n"
            
        return report
    
    def generate_json_export(self, requirements: Dict[str, Any]) -> str:
        """JSON形式でエクスポート"""
        return json.dumps(requirements, ensure_ascii=False, indent=2)
    
    def generate_test_cases(self, requirements: Dict[str, Any]) -> str:
        """テストケースを生成"""
        test_cases = """# 自動生成テストケース

## 機能要件テストケース

"""
        
        for req in requirements.get('functional', []):
            test_cases += f"""### {req['id']}: {req['name']}

```python
def test_{req['id'].lower().replace('-', '_')}():
    \"\"\"
    テストケース: {req['name']}
    要件ID: {req['id']}
    優先度: {req['priority']}
    \"\"\"
    # TODO: 実装
    pass
```

"""
            
        return test_cases
    
    def run(self):
        """メイン処理"""
        print("ドキュメント生成を開始します...")
        
        # 要件の解析
        requirements = self.parse_requirements()
        
        # 出力ディレクトリの作成
        output_dir = self.base_path / "generated"
        output_dir.mkdir(exist_ok=True)
        
        # サマリーレポートの生成
        summary = self.generate_summary_report(requirements)
        with open(output_dir / "summary-report.md", 'w', encoding='utf-8') as f:
            f.write(summary)
            
        # JSONエクスポート
        json_export = self.generate_json_export(requirements)
        with open(output_dir / "requirements.json", 'w', encoding='utf-8') as f:
            f.write(json_export)
            
        # テストケースの生成
        test_cases = self.generate_test_cases(requirements)
        with open(output_dir / "test-cases.md", 'w', encoding='utf-8') as f:
            f.write(test_cases)
            
        print(f"ドキュメント生成完了: {output_dir}")

if __name__ == "__main__":
    generator = DocumentGenerator()
    generator.run() 