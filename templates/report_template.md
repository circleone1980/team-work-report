# {{ month }}团队工作月报

## 一、核心业务进展

{% for business in businesses %}
### {{ loop.index }}. {{ business.name }}
{{ business.summary }}

**工时**：{{ business.total_hours }}h | **团队**：{{ business.people|join('、') }}

{% endfor %}

---

{% if unmatched_tasks %}
## 二、其他工作（待确认）

{% for task in unmatched_tasks %}
- **{{ task.person }}**（{{ task.hours }}h）：{{ task.detail }}

{% endfor %}

---

{% endif %}

---

**报告生成时间**：{{ generated_at }}
