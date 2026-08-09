# 个人事实库结构

将事实库作为 JSON 文件保存在 Skill 文件夹之外。保留每条事实的来源，使所有简历主张都可以追溯。默认使用 `candidate-profile.json`，以便在不安装第三方解析库的情况下进行校验。

如用户启用跨任务复用，必须同时读取 [persistent-candidate-vault.md](persistent-candidate-vault.md)，并将本文件作为资料库中的事实层，而不是唯一文件。原始材料和哈希索引分别保存在 `evidence/` 与 `evidence-index.json`。

字段名和枚举值使用英文，以确保程序兼容；事实内容和说明可以使用中文。

## 最小 JSON 结构

```json
{
  "profile_version": 1,
  "status": "draft",
  "updated_at": "YYYY-MM-DD",
  "candidate": {
    "name": "",
    "contact": {"phone": "", "email": "", "location": "", "links": []},
    "target_preferences": {"languages": [], "page_count": null},
    "education": [],
    "experience": [],
    "case_studies": [],
    "projects": [],
    "skills": [],
    "research": [],
    "publications": [],
    "patents": [],
    "awards": [],
    "certifications": [],
    "unresolved": []
  },
  "sources": []
}
```

## 来源对象

```json
{
  "id": "src-001",
  "path_or_label": "主简历.docx",
  "type": "resume",
  "supplied_by_user": true,
  "extracted_at": "YYYY-MM-DD"
}
```

## 工作或项目经历对象

```json
{
  "id": "exp-001",
  "organization": "示例公司",
  "role": "算法实习生",
  "start": "2025-01",
  "end": "2025-06",
  "location": "上海",
  "facts": [{
    "id": "exp-001-f01",
    "statement": "使用 PyTorch 训练目标检测模型。",
    "evidence": [{"source_id": "src-001", "source_text": "……"}],
    "state": "confirmed",
    "ownership": "contributed",
    "metrics": [],
    "technologies": ["Python", "PyTorch"]
  }]
}
```

非技术岗位的 `case_studies` 可复用相同的 `facts` 结构，并增加 `context`、`objective`、`actions`、`stakeholders`、`deliverables` 和 `outcomes`。没有证据时，不得为这些字段补写数字或影响。

## 技能对象

```json
{
  "name": "Python",
  "level": null,
  "evidence_fact_ids": ["exp-001-f01"],
  "state": "confirmed"
}
```

技能也可以直接使用来源证据，例如课程或主简历中的能力陈述：`"evidence": [{"source_id": "src-001", "source_text": "……"}]`。已确认技能必须至少包含 `evidence_fact_ids` 或直接 `evidence` 之一。

除非用户明确提供或确认，不得推断“专家”“熟练”或“高级”等能力等级。能够证明使用过某项技能，不等于能够证明已经精通。

## 待解决问题对象

```json
{
  "id": "issue-001",
  "type": "conflicting_date",
  "description": "两份材料中的实习结束日期不一致。",
  "affected_fact_ids": ["exp-001"],
  "options": ["2025-05", "2025-06"],
  "material_for_current_jd": false
}
```

只有待解决问题会影响简历准确性或当前 JD 时才询问用户。重要歧义经过用户确认后，才能将整个事实库的 `status` 改为 `confirmed`。
