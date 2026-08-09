# Tailor Resume to Job

一个面向 Codex 的中文简历定制 Skill。它根据候选人的主简历、持久化事实资料库、补充材料和目标岗位 JD，生成真实、可编辑、经过视觉检查的 Word 简历。

它不仅适用于算法、开发、硬件、光学和研究岗位，也支持产品、运营、市场、销售、咨询、财务、人力、设计、教育等非技术岗位。

## 核心能力

- 分析岗位职责、必备条件、优先条件和资格限制。
- 从主简历、论文、代码、报告、作品集等材料中提取可追溯事实。
- 主动询问会影响岗位匹配的缺失信息，而不是虚构或机械改写。
- 为技术项目建立“目标、贡献、方法、验证、结果”证据链。
- 为非技术经历建立“业务情境、目标、行动、协作、交付物、影响”证据链。
- 根据 JD 调整经历顺序、表达和真实 ATS 关键词。
- 为学生和应届生默认生成视觉上恰好一页的简历。
- 支持专业中文模板、中文/英文 ATS 模板和证件照保留。
- 使用 DOCX 渲染结果逐页检查排版。
- 经用户同意后建立可跨任务复用的本地候选人资料库。

## 安装

将整个目录复制到 Codex 的个人 Skills 目录：

```text
~/.codex/skills/tailor-resume-to-job/
```

最终应至少包含：

```text
tailor-resume-to-job/
├── SKILL.md
├── agents/
├── assets/
├── references/
└── scripts/
```

复制完成后新建一个 Codex 任务，Skill 即可被发现。Word 创建与渲染需要可用的 `documents` Skill、Python、`python-docx`、Pillow 和 LibreOffice。

## 使用方法

首次定制：

```text
使用 $tailor-resume-to-job，根据我的主简历和这个岗位 JD 制作一份一页 Word 简历。请主动询问缺失的项目或业务事实，不要虚构经历。
```

复用候选人资料库：

```text
使用 $tailor-resume-to-job，读取我的候选人资料库，根据新的岗位 JD 重新定制简历。
```

非技术岗位：

```text
使用 $tailor-resume-to-job，为这个市场运营岗位定制简历。请重点深挖业务目标、我的行动、协作对象、交付物和结果。
```

无照片 ATS 版：

```text
使用 $tailor-resume-to-job，生成无照片的 ATS 极简 Word 简历。
```

## 工作流程

1. 读取主简历或已有候选人资料库。
2. 解析目标岗位 JD，并区分关键要求与资格限制。
3. 将岗位要求映射到有来源支持的候选人事实。
4. 对关键证据缺口提出少量、有针对性的问题，并邀请用户提供原始材料。
5. 根据岗位类型组织经历、案例或项目要点。
6. 选择模板并生成新的 DOCX，不覆盖主简历。
7. 渲染全部页面，修复溢出、空白、字体、照片和日期对齐问题。
8. 交付投递版，并增量更新用户已启用的候选人资料库。

## 候选人资料库

资料库不会放在 Skill 安装目录中。启用前必须取得用户同意，推荐结构如下：

```text
resume-vault/
├── vault-index.json
└── candidate-id/
    ├── vault.json
    ├── candidate-profile.json
    ├── evidence-index.json
    ├── evidence/
    ├── derived/
    └── applications/
```

`candidate-profile.json` 保存结构化事实，`evidence-index.json` 保存来源、路径和 SHA-256，`evidence/` 保存用户同意长期保留的文件。相同内容自动去重，更新后的材料保存为新版本。

资料库是本地目录，不是云数据库。跨设备使用时需要自行迁移或备份，且不要提交到公共代码仓库。

## 模板

- `assets/professional-resume-cn.docx`：支持照片的中文专业模板。
- `assets/ats-resume-cn.docx`：中文 ATS 极简模板。
- `assets/ats-resume-en.docx`：英文 ATS 极简模板。

模板中的文字都是结构占位符。生成投递版时必须全部替换或删除，不能把示例事实带入候选人简历。

## 脚本

- `scripts/candidate_vault.py`：初始化、登记和校验候选人资料库。
- `scripts/extract_docx_images.py`：提取 DOCX 中的图片候选项，供人工确认照片。
- `scripts/validate_candidate_profile.py`：校验事实库结构和证据引用。
- `scripts/build_professional_template.py`：重建中文专业模板。
- `scripts/build_ats_template.py`：重建 ATS 模板。

查看资料库命令示例：

```bash
python scripts/candidate_vault.py show --vault-dir /path/to/resume-vault/candidate-id
python scripts/candidate_vault.py validate --vault-dir /path/to/resume-vault/candidate-id
python scripts/validate_candidate_profile.py /path/to/candidate-profile.json
```

## 真实性原则

- 不虚构技能、项目、数据、任职经历、论文、专利、奖项或资格。
- 不把团队成果自动归为候选人个人成果。
- 不把一般相关经验升级成 JD 中更具体的工具、标准或职责。
- 对不明确事实先询问；用户无法补充时使用更窄表述。
- 所有投递版主张都应能追溯到用户材料或用户确认。

## 隐私与开源安全

本仓库不得包含候选人的真实简历、联系方式、照片、论文原稿、作品集、事实库、公司机密或生成结果。`.gitignore` 已排除常见的个人资料目录，但发布前仍应执行人工检查。

建议在发布前搜索：

```bash
rg -n --hidden '/Users/|姓名|手机号|邮箱|candidate-profile|resume-vault' .
```

搜索结果可能包含规则说明或占位文字，需要人工判断；不得只依赖关键词自动删除。

## 项目结构

```text
.
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── professional-resume-cn.docx
│   ├── ats-resume-cn.docx
│   └── ats-resume-en.docx
├── references/
└── scripts/
```

## 已知限制

- 自动读取动态招聘页面可能需要浏览器工具或用户粘贴 JD。
- Word 在不同字体和不同 LibreOffice/Microsoft Word 版本中的分页可能略有差异，因此必须渲染检查。
- “恰好一页”适合学生和经历较少的候选人；高年资候选人可能需要两页。
- 资料库中的 `draft` 或 `ambiguous` 事实不能作为无条件简历主张。


