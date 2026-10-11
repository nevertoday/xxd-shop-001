<div align="center">

# 🦁 XXD Shop 001 | Premium Commercial Key Visual

### Let a quiet, real, airy brand world grow out of the product itself

<a href="README.md">简体中文</a> · <strong>English</strong>

</div>

> Original brief: [Simplified Chinese original](references/original-prompt/zh-CN.md) · [English reading translation](references/original-prompt/en.md)

## Samples

No samples yet. The commands below are usage examples, not visual evidence.

## What it solves

Most weak e-commerce images are not "ugly" — the product looks pasted in: floating, flatly lit, on a cheap podium, upstaged by the background, with packaging text the model quietly rewrote.

**Shop 001** fixes exactly that. The product stays the same; light, footing, environment and colour are rebuilt so it reads like a key visual shot by a mature brand.

### Good for

- **Upgrading an existing product photo** — white-background, real-life or packaging shots; shape, packaging text and logo stay intact.
- **Starting from only a product name or a creative proposition** — a believable product form and world built from category, material, usage context and brand character.
- **Quiet premium, not promotional** — restrained background, only props that explain the product, a title only when needed.
- **One product, many placements** — 1:1 listing image, 3:4 detail page, 9:16 splash, 16:9 banner, each a separate full composition.

### Quick start

Send a product photo to your agent and say:

> Use XXD Shop 001 to make a listing image for this product; recommend a size first.

## Is XXD Shop 001 right for you?

| Question | Answer |
|---|---|
| **What you get** | A brand-level e-commerce main image, product poster or brand key visual |
| **Signature traits** | A product with weight · real footing and contact shadow · soft directional light · colour grown from the product · restrained space · optional bold title |
| **How it respects your input** | The product photo is the top authority: shape, proportions, packaging text and logo are not changed; only light, shadow, reflection and setting are rebuilt |
| **What it will not do** | Invent prices, specs, sales, rankings or certifications; add cheap podiums, meaningless decoration or promo-sticker clutter |

## Getting started

```bash
git clone https://github.com/nevertoday/xxd-shop-001.git
mkdir -p ~/.claude/skills
ln -s "$(pwd)/xxd-shop-001" ~/.claude/skills/xxd-shop-001
```

Codex users link the same folder to `~/.codex/skills/xxd-shop-001`. Restart the agent session after installing.

```text
/xxd-shop-001 ./cold-brew.png --use "listing image" --size 1:1,3:4 --text prompt --locale en-US
```

Uploading just a product photo also works; the Skill asks only for size, count and text settings that are still unresolved.

### Parameters

| Flag | Purpose |
|---|---|
| `--product "..."` | Product name, category or creative proposition; the creative basis when there is no photo |
| `--use "..."` | Placement: listing image, detail page, poster, brand KV, social, banner… |
| `--size` | `auto`, `source`, `1:1`, `3:4`, `9:16`, `16:9`… or `WIDTHxHEIGHT`; several allowed |
| `--count N` | Independent compositions per size, default 1 |
| `--text prompt / exact / plan / none` | Model writes copy per the brief / your copy verbatim / your copy as a plan to tighten / no added text |
| `--copy "..."` | Your copy; verbatim by default, a copy plan with `--text plan` |
| `--facts "..."` | Facts allowed on the image, e.g. price, size, origin |
| `--locale` | Language of visible text, e.g. `zh-CN`, `en-US`, `ja-JP` |
| `--logo` / `--ref path=role` | Brand mark / a reference image with an explicit role |
| `--out` | Output root |
| `--prefs last / edit / new / off / clear` | Reuse, edit, ignore, skip saving or clear the last delivery preference |

Full specification: [SKILL.md](SKILL.md) · [family runtime](references/shop-runtime.md) · [original brief](references/original-prompt/zh-CN.md)

## Original brief first, no second art director

`references/original-prompt/zh-CN.md` keeps the original prompt verbatim and is the only creative and aesthetic authority. The Skill adds no palette, pre-written title or aesthetic theory; it only tells the image model which product this is, what each reference image is for, which facts may appear, and the requested size and text.

## Boundaries and trust

- Each product is used only in its own job; nothing is borrowed from other products, earlier results or samples.
- Anything that reads as fact (price, spec, origin, efficacy, sales, ranking, award, certification, date) comes only from you, from legible packaging, or from facts verified during this job — otherwise it is left out.
- Every invocation creates a fresh task folder; identical inputs are regenerated.
- Deliverables are PNG bitmaps, never SVG, HTML or programmatic drawings.
- Images go through the `responses` mode only, never a per-image credit path; you pick the drawing line once per task. The bridge never prints keys, headers, prompts or response bodies.

Generation needs the host agent's built-in bitmap capability or an already configured compatible route (GPT Image 2 preferred). The bridge needs Python 3.11+ and Pillow.

<!-- xxd-shop-tail -->
## Project structure

```text
xxd-shop-001/
├── SKILL.md
├── README.md / README.en.md
├── LICENSE
├── agents/openai.yaml
├── assets/examples/
├── scripts/
│   ├── configured_imagegen.py
│   └── shop_preferences.py
└── references/
    ├── shop-runtime.md
    ├── runtime-preferences.md
    ├── sample-workflow.md
    └── original-prompt/
        ├── README.md
        ├── zh-CN.md
        └── en.md
```

<!-- xxd-readme-ads:start -->
## About XXD

XXD is Xiaoxiaodong's abbreviated brand name. This project is created and maintained by [@xiaoxiaodong01](https://x.com/xiaoxiaodong01).

## Xiaoxiaodong multi-platform membership · CNY 699/year

> **Advertising disclosure:** The QR code, membership, and paid-service links below are XXD promotional information. Scanning or purchasing is entirely optional and does not affect access to this open-source project.

One annual membership unlocks three benefits together: **Knowledge Planet + the XXD Member Prompt Library + membership for all General Skills**. They are included in one membership; no separate purchase is required.

<!-- xxd-shop-command-system:start -->

### How the Skills work together

| Level | Included | What it does |
|---|---|---|
| **General** | `xxd-shop-all` | Detects available numbered Skills, recommends them by product, placement and visual need, and organizes multi-style and batch tasks. |
| **Soldier** | `xxd-shop-NNN` | Each numbered Skill follows its own original brief and aesthetic to complete the specific task assigned by the General. |

<!-- xxd-shop-command-system:end -->

### What you receive

1. **One-to-one WeChat AI learning and project support**
   Add Xiaoxiaodong on WeChat via the QR code below to discuss AI learning, tools, and real projects one to one, with practical guidance and answers. Representative questions may be organized into member resources.
2. **A growing member prompt library**
   The [XXD Member Prompt Library](https://vip.xiaoxiaodong.ai/) currently contains about 32,000 prompts and will keep expanding, with a goal of exceeding 100,000.
3. **All General Skills and usage support**
   One membership covers every General Skill, with usage guidance and Q&A when you need help.
4. **Priority for high-need requests**
   Frequently requested, high-need prompts and Skills are reviewed and developed first where appropriate.

### How to join

- [Activate membership on the member website](https://vip.xiaoxiaodong.ai/).
- Or scan the QR code below to add Xiaoxiaodong on WeChat for one-to-one activation support.

<p align="center"><a href="https://xiaoxiaodong.pages.dev/assets/wechat-qr.png"><img src="https://xiaoxiaodong.pages.dev/assets/wechat-qr.png" alt="Contact Xiaoxiaodong" width="280"></a></p>
<!-- xxd-readme-ads:end -->

## License

This project—including its Skill, prompts, scripts, documentation, and accompanying samples—is released under the **PolyForm Noncommercial License 1.0.0**. The complete legal text is in [LICENSE](LICENSE); the official page is <https://polyformproject.org/licenses/noncommercial/1.0.0>.

In plain language:

- You may use it for personal study, research, experiments, testing, hobbies, and private entertainment. Charities, educational institutions, public research/safety/health organisations, environmental-protection organisations, and government institutions may also use it.
- For **noncommercial purposes**, you may use, copy, modify, create derivative works, and share the project. When sharing, include this license (or the link above) and every `Required Notice:` line supplied by the author.
- Commercial products or services, paid delivery, selling access or licenses, and uses with an anticipated commercial application are not allowed. Obtain separate written permission from the copyright holder for commercial use.
- The license grants only the stated copyright and limited patent rights. It grants no trademark, brand, or other unstated rights, and you may not sublicense or transfer your license.
- If you receive written notice of a violation, you have 32 days to come into full compliance and take practical corrective steps; otherwise the licenses end. A written patent-infringement claim also ends the patent license.
- The project is provided **as is**, without warranties, and you accept the risks and any resulting liability to the extent permitted by law.
