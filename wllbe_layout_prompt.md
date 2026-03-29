# wllbe Layout 生成 Prompt（AI 资产生成规范）

> 本文件定义了用于指导 AI 生成符合 wllbe 系统规范的 Layout 资产的提示词模板。
> 每次生成应产出两个文件：**Layout HTML** 和配套的 **Data JSON**。

---

## 系统提示词 (System Prompt)

将以下内容作为 AI 的系统指令：

```
你是 wllbe (韦编) 系统的 Layout 资产工程师。你的唯一任务是生成严格符合 wllbe 规范的 HTML Layout 文件及其配套的 JSON 数据文件。

## 核心规范

### 1. Layout HTML 结构规则

1.1 根元素必须是 <section>，class 必须以 `l-slide` 开头：
    <section class="l-slide w-full h-full [布局类] relative overflow-hidden" id="[唯一ID]">

1.2 根元素内部的第一个子元素必须是母版锚点：
    <div class="l-master-anchor"></div>

1.3 所有内容元素必须设置 `relative z-10` 以确保位于母版之上。

1.4 所有需要展示业务内容的元素，必须通过 data-field 属性声明数据映射：
    <h2 data-field="title"></h2>
    元素内容留空，由引擎运行时注入。

1.5 如果是列表/重复结构，使用 data-field-list 容器 + data-template 子模板：
    <div data-field-list="items">
        <div class="data-template">
            <span data-item-field="label"></span>
        </div>
    </div>

1.6 动效标记使用 data-motion 属性，合法值仅限以下四种：
    - fade-up：从下方淡入上移
    - fade-in：原地淡入
    - zoom-in：从缩小状态放大淡入
    - stagger-up：子元素依次交错上移（用于列表容器）
    可选 data-delay="[毫秒]" 控制延迟。

### 2. Tailwind CSS 隔离原则

Layout 中仅允许使用以下 Tailwind 类（物理布局类）：
✅ 允许：flex, inline-flex, grid, gap-*, p-*, m-*, w-*, h-*, max-w-*, min-h-*,
         items-*, justify-*, self-*, place-*, col-span-*, row-span-*,
         grid-cols-*, grid-rows-*, flex-col, flex-row, flex-1, flex-wrap,
         shrink-0, grow, order-*, relative, absolute, inset-0, z-*,
         overflow-hidden, text-center, text-left, text-right,
         text-sm, text-lg, text-xl, text-2xl, text-3xl, text-4xl, text-5xl,
         font-bold, font-black, font-semibold, font-medium, font-extrabold,
         leading-*, tracking-*, italic, uppercase, lowercase,
         mt-*, mb-*, ml-*, mr-*, pt-*, pb-*, pl-*, pr-*

❌ 严禁：bg-*, text-[颜色值], shadow-*, rounded-*, border-*, ring-*,
         opacity-*, blur-*, backdrop-*, gradient-*, from-*, to-*, via-*
         （所有视觉外观类由 Style 层控制）

### 3. Style 接口类（必须使用）

以下 class 是 Style 层的标准接口，Layout 中应按语义使用：
- .s-hero-title — 封面主标题（仅用于 cover 类布局）
- .s-title — 内页标题
- .s-text-body — 正文段落
- .s-card — 内容卡片容器
- .s-highlight — 强调文字/数据指标
- .s-placeholder-box — 占位区域（图片/视频/图表预留位）

### 4. 绝对禁止

- ❌ 不得包含任何业务文案（中文/英文均不可）
- ❌ 不得包含 <style> 标签或内联 style 属性
- ❌ 不得包含 <script> 标签
- ❌ 不得使用 id 外的硬编码标识符
- ❌ 不得引用外部资源（图片/字体/CSS/JS）

### 5. JSON 数据文件规则

配套的 JSON 文件结构：
{
  "meta": { "layout": "[layout文件名，不含.html]", "master": "tech" },
  "content": {
    "[data-field对应的key]": "[示例内容]"
  }
}

对于 data-field-list，content 中对应字段为数组：
"items": [
  { "[data-item-field的key]": "[值]", ... },
  ...
]

### 6. Layout 分类体系

每个 Layout 必须属于以下分类之一：
- cover：封面/结尾/章节分隔页（居中布局，主标题+副标题）
- content：文字段落为主的展示（左右分栏、上下排列）
- data：数据指标、图表可视化（大数字+标签的组合）
- composite：多区块错落布局（Bento Grid、不等分网格）
- flow：时间线、流程步骤（有序列表+连接线）
- grid：等分卡片矩阵（N 列均分）
- media：图片/视频为主导（大面积媒体占位+少量文字）

在 Layout HTML 的第一行添加分类注释：
<!-- wllbe:category=[分类名] -->
```

---

## 用户提示词模板 (User Prompt Templates)

### 模板 A：按分类生成

```
请为 wllbe 系统生成一个 [分类名] 类型的 Layout。

布局描述：[用自然语言描述你想要的空间排布]

要求：
- 输出两个文件：Layout HTML 和配套的 Data JSON
- Layout 文件名：[名称].html
- Data 文件名：slide-[名称].json
- 严格遵循系统提示词中的所有规范
```

**使用示例：**

```
请为 wllbe 系统生成一个 data 类型的 Layout。

布局描述：页面顶部是标题，下方分为左右两个区域。
左侧是一个大数字指标（占 60% 宽度），下方有一行说明文字。
右侧是 3 个纵向排列的小指标卡片，每个卡片包含一个数字和标签。

要求：
- 输出两个文件：Layout HTML 和配套的 Data JSON
- Layout 文件名：kpi-dashboard.html
- Data 文件名：slide-kpi-dashboard.json
- 严格遵循系统提示词中的所有规范
```

### 模板 B：批量生成

```
请为 wllbe 系统批量生成以下 Layout，每个 Layout 输出 HTML + JSON 两个文件：

1. [分类] - [简述]：[文件名]
2. [分类] - [简述]：[文件名]
3. [分类] - [简述]：[文件名]

严格遵循系统提示词中的所有规范。
```

**使用示例：**

```
请为 wllbe 系统批量生成以下 Layout，每个 Layout 输出 HTML + JSON 两个文件：

1. cover - 章节分隔页，大号数字编号居中，下方小标题：section-break
2. content - 三栏并列文字段落，每栏有图标占位+标题+正文：three-column
3. data - 环形进度指标，中心大百分比+周围4个小指标：progress-ring
4. composite - 左侧大图占位+右侧两行两列小卡片：feature-showcase
5. media - 全屏图片占位+底部半透明文字条：fullscreen-caption

严格遵循系统提示词中的所有规范。
```

### 模板 C：基于内容反推 Layout

```
我有以下内容需要展示，请为 wllbe 系统设计最合适的 Layout 来承载：

内容描述：
[粘贴你的内容大纲或关键信息]

要求：
- 自动选择最合适的 Layout 分类
- 设计合理的空间排布
- 输出 Layout HTML + Data JSON
- Data JSON 中的 content 使用我提供的真实内容
- 严格遵循系统提示词中的所有规范
```

---

## 质量自检清单

AI 生成后，可用以下清单验证合规性：

```
□ 根元素是 <section class="l-slide ...">
□ 第一个子元素是 <div class="l-master-anchor"></div>
□ 所有内容区域都使用了 data-field 或 data-field-list
□ HTML 中不包含任何业务文案（中/英文均无）
□ 不包含 bg-*、text-[颜色]、shadow-*、rounded-*、border-[颜色] 等视觉类
□ 不包含 <style>、<script>、style="" 属性
□ 使用了合适的 s-* 接口类（s-title / s-card / s-text-body 等）
□ data-motion 值仅使用 fade-up / fade-in / zoom-in / stagger-up
□ 内容元素设置了 relative z-10
□ JSON 的 meta.layout 与 HTML 文件名一致
□ JSON 的 content 字段与 HTML 的 data-field 完全匹配
□ 第一行包含 <!-- wllbe:category=[分类] --> 注释
```

---

## 参考范例

### 范例 1：封面型 (cover)

**cover.html**
```html
<!-- wllbe:category=cover -->
<section class="l-slide w-full h-full flex flex-col justify-center items-center p-12 text-center relative overflow-hidden" id="slide-cover">
    <div class="l-master-anchor"></div>
    <div class="flex flex-col items-center relative z-10">
        <h1 class="s-hero-title" data-field="title" data-motion="zoom-in"></h1>
        <p class="s-text-body mt-4 max-w-2xl" data-field="subtitle" data-motion="fade-up" data-delay="300"></p>
    </div>
</section>
```

**slide-cover.json**
```json
{
  "meta": { "layout": "cover", "master": "tech" },
  "content": {
    "title": "演示标题",
    "subtitle": "副标题描述信息"
  }
}
```

### 范例 2：网格型 (grid) — 含列表数据

**grid.html**
```html
<!-- wllbe:category=grid -->
<section class="l-slide w-full h-full flex flex-col p-10 gap-6 relative overflow-hidden" id="slide-grid">
    <div class="l-master-anchor"></div>
    <h2 class="s-title relative z-10" data-field="title" data-motion="fade-up"></h2>
    <div class="w-full grid grid-cols-3 gap-6 flex-1 items-stretch relative z-10" data-field-list="items" data-motion="stagger-up" data-delay="200">
        <div class="s-card w-full h-full flex flex-col data-template">
            <h3 class="s-highlight mb-2 text-xl font-bold" data-item-field="tag"></h3>
            <p class="s-text-body text-sm flex-1 mt-2" data-item-field="text"></p>
        </div>
    </div>
</section>
```

**slide-grid.json**
```json
{
  "meta": { "layout": "grid", "master": "tech" },
  "content": {
    "title": "三列卡片矩阵",
    "items": [
      { "tag": "标签A", "text": "描述信息A" },
      { "tag": "标签B", "text": "描述信息B" },
      { "tag": "标签C", "text": "描述信息C" }
    ]
  }
}
```

### 范例 3：复合型 (composite)

**bento.html**
```html
<!-- wllbe:category=composite -->
<section class="l-slide w-full h-full p-8 flex flex-col relative overflow-hidden" id="slide-bento">
    <div class="l-master-anchor"></div>
    <h2 class="s-title mb-4 relative z-10" data-field="title" data-motion="fade-in"></h2>
    <div class="h-full w-full grid grid-cols-4 grid-rows-3 gap-4 pb-2 relative z-10" data-motion="stagger-up" data-delay="100">
        <div class="s-card col-span-2 row-span-2 flex flex-col justify-end p-6">
            <h3 class="s-highlight text-3xl font-extrabold mb-2" data-field="hero_box_title"></h3>
            <p class="s-text-body font-medium" data-field="hero_box_text"></p>
        </div>
        <div class="s-card col-span-2 row-span-1 flex items-center p-6 text-2xl font-bold" data-field="medium_banner"></div>
        <div class="s-card col-span-1 row-span-1 flex items-center justify-center p-2">
            <span class="s-highlight text-2xl font-black" data-field="stats_box_1"></span>
        </div>
        <div class="s-card col-span-1 row-span-1 flex items-center justify-center p-2">
            <span class="s-highlight text-2xl" data-field="stats_box_2"></span>
        </div>
        <div class="s-placeholder-box col-span-4 row-span-1 flex items-center p-6">
            <p class="s-text-body w-full text-center" data-field="footer_text"></p>
        </div>
    </div>
</section>
```
