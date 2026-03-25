# wllbe HTML PPT 生成与抽卡审查系统设计方案

## 项目定位

`wllbe` 是一个面向内容生成、页面抽卡选择、最终组装与发布的一体化 HTML PPT 系统。  
系统具备以下核心能力：

1. 同一份内容生成多个版本或多个页面变体
2. 在浏览器中完成“抽卡式”挑选与混搭
3. 直接导出最终 HTML 成品
4. 在确认无误后发布到公司内部网站或展示系统

其中，“抽卡模式”是 `wllbe` 主流程中的核心审查阶段。

## 系统配置

| 决策项 | 方案 |
|--------|------|
| 系统名称 | `wllbe` |
| Skill 定位 | 独立 HTML PPT 生成系统 |
| 部署方式 | Docker 容器化发布系统 |
| 主题方向 | 深色科技 + 浅色白底，支持快捷键与按钮切换 |
| 多版本流程 | 首次生成多个版本 -> 抽卡挑选 -> 混合组装 -> 发布 |

## 核心能力

系统整体体验如下：

```text
生成多个版本 -> 合成一个 review HTML -> 浏览器内逐页抽卡选择
-> 最后一页确认所有选择 -> 一键导出最终版 -> 本地预览 -> 发布
```

系统能力边界如下：

1. 生成多个完整版本及页面变体
2. 以单一 review HTML 提供统一审查入口
3. 支持逐页抽卡选择与自动记录
4. 支持最终版 HTML 导出与发布

## 用户工作流

```text
① 用户提供内容并调用 wllbe / html-ppt Skill
        ↓
② 系统生成 N 个版本，每页有 2-3 个布局或内容变体
        ↓
③ combine.py --review 将所有版本合成为一个审查版 HTML
        ↓
④ 用户在浏览器中通过“抽卡模式”逐页挑选满意版本
        ↓
⑤ 系统记录每页选择结果，并在最后一页展示确认面板
        ↓
⑥ 用户确认后直接导出最终 HTML 成品
        ↓
⑦ 本地预览无误后，发布到 Docker 化发布系统
```

## 抽卡模式设计

### 设计定位

抽卡模式是 `wllbe` 在多版本生成之后的核心审查层。  
它负责将 `v1/`、`v2/`、`v3/` 等目录下的完整 PPT，组织成“按页聚合”的浏览体验。

在该模式下，用户通过一个 review HTML 完成以下操作：

1. 逐页浏览内容
2. 在当前页上下切换不同版本
3. 自动记录每页当前选择
4. 在确认面板中复核全部选择
5. 导出最终 HTML

### 核心概念

```text
┌─────────── Page 1 ───────────┐  ┌─────────── Page 2 ───────────┐
│  ┌── V1 ──┐  ┌── V2 ──┐     │  │  ┌── V1 ──┐  ┌── V2 ──┐     │
│  │ 封面A  │  │ 封面B  │ ... │  │  │ 目录A  │  │ 目录B  │ ... │
│  └────────┘  └────────┘     │  │  └────────┘  └────────┘     │
│       ↑↓ 切换版本            │  │       ↑↓ 切换版本            │
│       ←→ 翻页               │  │       ←→ 翻页               │
└─────────────────────────────┘  └─────────────────────────────┘

播放时：←→ 翻页 | ↑↓ 同页切换版本 | 当前选中自动记录
最后一页后：弹出确认面板 -> 确认 -> 自动输出最终版 HTML
```

### 交互原则

1. 页面导航与版本选择解耦
2. 用户当前视图即当前选择，避免额外确认动作
3. 当前页选择应即时可见、即时可改
4. 所有选择必须在最终导出前统一复核一次
5. 普通 PPT 播放模式不应被抽卡逻辑污染

## 交互设计

### 操作方式

| 键 / 操作 | 功能 |
|-----------|------|
| `←` / `→` | 翻页 |
| `↑` / `↓` | 切换当前页的不同版本 |
| `Space` | 下一页 |
| `Backspace` | 上一页 |
| `T` | 深色 / 浅色主题切换 |
| `F` | 全屏 |
| `S` | 演讲者视图 |
| `O` | 总览模式 |
| `G` + 数字 | 跳转指定页 |
| 触屏左右滑 | 翻页 |
| 触屏上下滑 | 切换版本 |
| 最后一页按 `→` | 打开确认面板 |

### 版本指示器 UI

页面右侧显示竖向圆点指示器，用于标识当前页可选版本和当前已选版本：

```text
      ● V1  <- 选中（高亮 + 动画）
      ○ V2
      ○ V3
```

设计要求：

1. 默认弱显，鼠标移入或键盘交互时增强可见性
2. 点击任意版本点可直接切换
3. 版本数量可动态适配，不写死为 2 或 3 个

### 选中状态指示

在右下角导航区域的页码旁显示当前页选中的版本，例如：

```text
‹ 03 / 07 · V2 ›
```

行为要求：

1. 切换版本时即时更新
2. 翻到下一页时自动保留当前页选择
3. 返回上一页时应恢复该页上次已记录的版本

### 最终确认面板

当播放到最后一页后再次前进，或者点击“确认方案”按钮，弹出全屏确认面板：

```text
╔═══════════════════════════════════════════════╗
║  方案确认                                     ║
║                                               ║
║  第 1 页: V1  ✓     第 2 页: V2  ✓            ║
║  第 3 页: V1  ✓     第 4 页: V3  ✓            ║
║  第 5 页: V2  ✓     第 6 页: V1  ✓            ║
║  第 7 页: V1  ✓                               ║
║                                               ║
║  [返回修改]              [确认并导出]         ║
╚═══════════════════════════════════════════════╝
```

确认面板必须支持：

1. 列出所有页面当前选中的版本
2. 点击任意页面条目可跳回对应页修改
3. 明确区分“返回修改”和“确认导出”两个动作
4. 导出前再次校验是否每页都有有效选择

## 主题系统

系统提供两套基础主题，通过 CSS 变量驱动：

```css
/* dark-tech.css */
[data-theme="dark"] {
  --bg: #0B1426;
  --surface: #1A2332;
  --primary: #00A3FF;
  --secondary: #00E5A0;
  --accent: #7B61FF;
  --text: #FFFFFF;
  --text-muted: #8892A0;
}

/* light-clean.css */
[data-theme="light"] {
  --bg: #FFFFFF;
  --surface: #F5F7FA;
  --primary: #2563EB;
  --secondary: #059669;
  --accent: #7C3AED;
  --text: #1A1A2E;
  --text-muted: #6B7280;
}
```

主题切换要求：

1. 快捷键 `T` 可切换
2. 右上角提供显式切换按钮
3. 审查模式与最终导出版都应继承同一套主题能力

## 系统结构

### Part 1: `html-ppt` Skill

```text
.agent/skills/html-ppt/
├── SKILL.md
├── themes/
│   ├── dark-tech.css
│   └── light-clean.css
├── templates/
│   ├── base.html
│   ├── review.html
│   └── layouts/
│       ├── cover.html
│       ├── toc.html
│       ├── one-column.html
│       ├── two-column.html
│       ├── three-column.html
│       ├── full-image.html
│       ├── chart.html
│       └── ending.html
├── engine/
│   ├── slide-engine.js
│   ├── version-picker.js
│   ├── version-picker.css
│   ├── transitions.css
│   ├── theme-switcher.js
│   └── presenter-mode.js
└── scripts/
    ├── build.py
    └── combine.py
```

### Part 2: 发布系统（Docker）

```text
publishing-system/
├── Dockerfile
├── docker-compose.yml
├── frontend/
│   ├── index.html
│   ├── viewer.html
│   ├── style.css
│   └── app.js
├── server/
│   ├── server.js
│   ├── routes/
│   │   ├── upload.js
│   │   ├── presentations.js
│   │   └── share.js
│   └── data/
│       ├── db.json
│       └── presentations/
├── nginx.conf
└── package.json
```

发布系统职责：

1. 存储最终导出的 HTML PPT
2. 提供上传、列表、详情、更新、删除和分享能力
3. 承接 `wllbe` 最终审稿完成后的成品分发

## 系统实现设计

### 引擎层

#### `engine/version-picker.js`

独立模块 `VersionPicker` 负责抽卡审查模式的全部逻辑。

职责包括：

1. 将 `<section class="slide" data-page="N" data-version="vX">` 按 `(page, version)` 建立二维索引
2. 在同一 page 内切换不同版本 slide 的显示状态
3. 维护 `selections = { 0: 'v1', 1: 'v2', ... }` 的页面选择记录
4. 驱动右侧版本指示器 UI
5. 控制确认面板的展示、跳转与导出逻辑
6. 根据选择结果提取对应页面，组装并下载最终 HTML

#### `engine/slide-engine.js`

`SlideEngine` 保持“通用放映引擎”的角色，不直接承担版本选择逻辑，只提供审查模式所需的回调钩子。

职责定义：

1. 构造函数包含 `this.reviewMode = options.reviewMode || false`
2. 键盘绑定中监听 `ArrowUp` / `ArrowDown`
3. 当 `reviewMode` 为 `true` 时，调用 `this.onVersionSwitch?.('up' | 'down')`
4. 当位于最后一页继续前进时，调用 `this.onReviewComplete?.()`

设计结果：

1. 普通模式不受影响
2. 抽卡模式逻辑集中在 `VersionPicker`
3. `SlideEngine` 仍保持低耦合

### 模板层

#### `templates/review.html`

审查模式专用模板，基于 `base.html` 扩展，职责如下：

1. 将所有版本的 slide 以 `data-page` + `data-version` 方式平铺在同一个 `.slides-container` 中
2. 引入 `version-picker.js` 和 `version-picker.css`
3. 初始化放映引擎时启用 `reviewMode: true`
4. 预置确认面板 overlay 结构

#### `engine/version-picker.css`

负责以下视觉部分：

1. 版本指示器
2. 确认面板
3. 同页版本切换的过渡动画
4. 审查模式下的额外状态徽章

### 脚本层

#### `scripts/combine.py`

`combine.py` 提供 review 合成与最终版组装两类能力。

功能定义：

1. 提供 `build_review_html()` 函数
2. 从各版本中提取 slides，并为每个 slide 注入 `data-page` 和 `data-version`
3. 基于 `review.html` 模板输出 `output/review/index.html`
4. 保留原有 `--map` 组合方式，作为回退或脚本化场景的备用方案

示例：

```bash
# 生成审查版
python3 combine.py <project_dir> --review

# 按指定映射直接组装
python3 combine.py <project_dir> --map "1:v2,2:v1,3:v3"
```

#### `SKILL.md`

`SKILL.md` 中的用户预览与选择章节应定义以下主流程：

```text
先生成多版本 -> combine.py --review -> 浏览器中抽卡选择
-> 确认面板复核 -> 导出最终版
```

命令行 `--map` 用于辅助路径或脚本化场景。

## 发布系统设计

### Docker 部署

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ppt-data:/app/data
    environment:
      - NODE_ENV=production
volumes:
  ppt-data:
```

### API 设计

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/upload` | 上传 PPT 文件 |
| `GET` | `/api/presentations` | 列表，支持搜索与分类 |
| `GET` | `/api/presentations/:id` | 详情 |
| `PUT` | `/api/presentations/:id` | 更新版本 |
| `DELETE` | `/api/presentations/:id` | 删除 |
| `GET` | `/view/:id` | 公开查看链接 |
| `POST` | `/api/presentations/:id/share` | 分享设置 |

## 验收标准

### 功能验收

1. 使用已有样例生成 3 个版本、每个版本 6-8 页的 HTML PPT
2. 运行 `combine.py --review`，生成审查版
3. 浏览器打开审查版，验证：
   - `←` / `→` 翻页正常
   - `↑` / `↓` 切换版本正常
   - 右侧版本指示器高亮与切换一致
   - 右下角页码旁的版本徽章正确更新
   - 深浅主题切换正常
4. 播放到最后一页继续前进，确认面板正确弹出
5. 在确认面板中点击任意页，能返回原页并修改选择
6. 点击“确认并导出”后浏览器下载 `final.html`
7. 打开导出的 `final.html`，验证内容与所选方案一致

### 兼容性要求

1. 普通模式下 `reviewMode` 默认为 `false`
2. 非审查模式中 `↑` / `↓` 不产生副作用
3. 抽卡模式不影响已有全屏、主题切换、演讲者模式与总览模式

## 系统总结

`wllbe` 的系统闭环如下：

```text
内容生成 -> 多版本输出 -> 抽卡审查 -> 最终导出 -> 发布管理
```

抽卡模式是系统中的选择中枢，连接前端生成体验与后续发布能力。
