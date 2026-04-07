"""
Create sample Excel file for testing.
"""
import pandas as pd

# Create sample data
data = [
    # Header row
    ['姓名', '总工时', '项目', '工时', '工作明细', '明细工时', '日期', '每日工时'],
    # Person 1
    ['张三', 40, '项目A', 20, '需求分析', 10, '2026-03-01:完成需求文档', 8],
    ['', '', '', '', '开发工作', 10, '2026-03-02:完成API开发', 8],
    # Person 2
    ['李四', 35, '项目B', 15, '测试工作', 15, '2026-03-01:编写测试用例', 7],
    ['', '', '项目C', 20, '前端开发', 20, '2026-03-03:完成页面开发', 8],
]

# Create DataFrame
df = pd.DataFrame(data)

# Write to Excel
df.to_excel('tests/fixtures/sample_data.xlsx', index=False, header=False)
print("Sample Excel file created: tests/fixtures/sample_data.xlsx")
