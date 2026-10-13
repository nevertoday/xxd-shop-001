---
name: xxd-shop-001
description: "Create XXD Shop 001 brand-level product key visuals (高级商业产品主视觉) as finished PNGs from a product photo, packaging shot, product image directory, or just a product name or creative proposition, treating the bundled original brief as the sole aesthetic authority: the product keeps its exact identity and packaging text, rests on a believable base with a real contact shadow, under soft directional light, in a restrained environment whose colour grows from the product, with an optional bold readable title. Supports any product category, multiple ratios or exact sizes, several independent compositions per size, prompt-generated, user-exact, user-plan, or text-free copy, and supplied facts only. Use when the user invokes xxd-shop-001 or asks for the Shop 001 style: 电商主图、产品海报、品牌 KV、高级商品主视觉、安静高级的产品摄影."
---

# XXD Shop 001｜高级商业主视觉

用本次用户提供的商品图、商品图目录或商品名称，生成成熟品牌级的电商主图、产品海报或品牌 KV，交付 PNG。

每次生成前，完整读取 `references/original-prompt/zh-CN.md`。这份中文原始提示词是唯一的创作与审美权威；不总结、不翻译、不混用，也不用本文件、README、样张或其他编号替代它。

每次构建生图请求前，完整读取 `references/shop-runtime.md`。它是参数、偏好沿用、目录批量、问询、事实纪律、提示词拼接、出图、输出隔离与验收的唯一家族运行合同。本 Skill 不另写第二套美术指导，也不另写第二套运行规则。

所有成品直接写进 `~/Desktop/xxd/xxd-shop-001/` 下新建的一个任务目录（或用户用 `--out` 指定的根目录），文件名不冲突；不建子目录，不自动生成拼贴总览。

## 本编号覆盖条款

**两条输入分支由真实输入触发。** 有商品图走原稿第一段（商品图是最高依据，只重建光影、反射、透视和环境色；原图背景杂乱时可以先抠出商品）；只有名称、品类或创意命题走第二段。只有一个创意命题（例如“秋天的第一杯”）、却没说清是什么商品时，先问商品品类，不替用户决定卖什么。

**一张图一个商品。** 原稿围绕“商品自身”展开。组合装、礼盒、套装按一件商品处理，用它的整体名称；几件互不相关的商品放进同一张图，不在本编号范围内，按家族多图规则先问清本次是哪一件。

**标题是“若需要”才出现。** `--text prompt` 时由图像模型按原稿判断要不要标题；画面上没有标题是正常结果，不算失败。一旦出现标题，原稿的要求全部生效：尺度大胆、字形完整、缩小后可读，纹理、插画和复杂背景不得穿过主要字形。

**道具只解释商品。** 原稿要求前景与周围“只出现真正能够解释商品的器物、原料、材质或细节”。Agent 不替用户加道具。用户点名的道具，原话放进“用户其他明确要求”；Agent 认为它和这条原稿要求冲突时（例如与商品无关的装饰），生成前说明一次，按用户的决定执行。

**选对编号**（用户拿不准时说明）：要价格、卖点分组和转化，用 `xxd-shop-009`；已有一张产品照、想用光效表达功能，用 `xxd-shop-011`；要安静、真实、有空气感、标题可有可无的品牌主视觉，留在 001。

**追加验收：** 商品有明确落点与接触阴影，没有悬浮感；没有模板化展台、机械对称或平均打光；背景和道具没有抢过商品；环境色从商品延展，没有与商品无关的强调色；出现标题时，标题是商品之外最清楚的视觉核心之一，且没有被纹理穿过。

**写入提示词：** 以下句子原话放进交付块的“本编号约束”；其余覆盖条款由 Agent 执行与验收，不进入提示词。

- 商品稳稳落在一个真实的支撑面上，有接触阴影，不悬浮、不飘在空中。

## 参考文件

- `references/shop-runtime.md`：生成时使用的家族运行合同
- `references/original-prompt/zh-CN.md`：运行时使用的原始提示词
- `references/original-prompt/README.md`：译文索引与权威说明
- `references/runtime-preferences.md`：安全的交付偏好沿用
- `references/sample-workflow.md`：仅用于维护样张，不是运行前提
- `scripts/configured_imagegen.py`：已配置通道的脱敏位图桥接
- `scripts/shop_preferences.py`：读写家族共用的交付偏好
