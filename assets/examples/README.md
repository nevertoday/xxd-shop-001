# XXD Shop 001 样张

每张都是本编号按 `references/sample-workflow.md` 一次生成、目视通过的原图，像素未改，只清理了元数据。商品是虚构的演示品牌，画面上的价格、规格等数字都是演示设定。

| 文件 | 用途 | 实际像素 | 输入 | 文字方式 | visual_review |
|---|---|---|---|---|---|
| `c01-category-4x5-1122x1402.png` | 高端主图 | 1122x1402 | 商品图 `product-xunyu-shoe.jpg`、Logo `logo-xunyu.png` | plan zh-CN | passed |
| `c02-category-1x1-1254x1254.png` | 高端主图 | 1254x1254 | 商品图 `product-sc-watch.jpg`、Logo `logo-shengchuan.png` | plan zh-CN | passed |
| `c03-category-16x9-1672x941.png` | 品牌 KV | 1672x941 | 原图 `fabric-silk.jpg`、Logo `logo-nanzhi.png` | plan zh-CN | passed |
| `c04-category-3x4-1086x1448.png` | 详情页首屏 | 1086x1448 | 商品图 `product-wuyu-candle.jpg`、Logo `logo-wuyu.png` | plan zh-CN | passed |
| `c05-category-1x1-1254x1254.png` | 高端主图 | 1254x1254 | 商品图 `product-mqx-catfood.jpg`、Logo `logo-maoqiuxing.png` | plan zh-CN | passed |
| `c06-category-4x5-1122x1402.png` | 社媒 | 1122x1402 | 商品图 `product-xxg-bottle.jpg`、Logo `logo-xiaoxiangguo.png` | plan zh-CN | passed |
| `s01-size-1x1-1254x1254.png` | 高端主图 | 1254x1254 | 商品图 `product-qibai-serum.jpg`、Logo `logo-qibai.png` | plan zh-CN | passed |
| `s02-size-3x4-1086x1448.png` | 详情页首屏 | 1086x1448 | 商品图 `product-qibai-serum.jpg`、Logo `logo-qibai.png` | plan zh-CN | passed |
| `s03-size-9x16-940x1672.png` | 开屏 | 940x1672 | 商品图 `product-qibai-serum.jpg`、Logo `logo-qibai.png` | plan zh-CN | passed |
| `s04-size-16x9-1672x941.png` | 品牌 KV | 1672x941 | 商品图 `product-qibai-serum.jpg`、Logo `logo-qibai.png` | plan zh-CN | passed |
| `s05-category-3x4-1086x1448.png` | 详情页首屏 | 1086x1448 | 商品图 `product-baiyao-mug.jpg`、Logo `logo-baiyao.png` | prompt zh-CN | passed |
| `s06-category-1x1-1254x1254.png` | 高端主图 | 1254x1254 | 商品图 `product-sc-headphones.jpg`、Logo `logo-shengchuan.png` | prompt zh-CN | passed |
| `s07-category-16x9-1672x941.png` | 品牌 KV | 1672x941 | 商品图 `product-nuandao-fryer.jpg`、Logo `logo-nuandao.png` | plan zh-CN | passed |
| `s08-special-4x5-1122x1402.png` | 社媒 | 1122x1402 | 商品图 `product-wuyu-perfume.jpg`、Logo `logo-wuyu.png` | none | passed |
| `s09-special-4x5-1122x1402.png` | 社媒 | 1122x1402 | 商品图 `product-wuyu-perfume.jpg`、Logo `logo-wuyu.png` | exact zh-CN | passed |
| `s10-special-4x5-1122x1402.png` | 社媒 | 1122x1402 | 商品图 `product-wuyu-perfume.jpg`、Logo `logo-wuyu.png` | exact en-US | passed |

## 输入素材

`sources/` 里是生成时交给本编号的输入缩样，模拟商家手里的素材：带包装与 Logo 的商品图、品牌 Logo，个别为原图。
演示品牌、Logo 和商品图由本项目生成；其中以 Unsplash 照片为底的，署名如下，适用 [Unsplash License](https://unsplash.com/license)，**不属于**本仓库的 PolyForm Noncommercial 授权范围。

| 输入 | 说明 · 来源 |
|---|---|
| `sources/fabric-silk.jpg` | 原图 [zp6wHVSm-0c](https://unsplash.com/photos/zp6wHVSm-0c) · @susan_wilkinson |
| `sources/logo-baiyao.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-maoqiuxing.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-nanzhi.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-nuandao.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-qibai.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-shengchuan.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-wuyu.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-xiaoxiangguo.png` | 演示品牌 Logo，本项目生成 |
| `sources/logo-xunyu.png` | 演示品牌 Logo，本项目生成 |
| `sources/product-baiyao-mug.jpg` | 演示商品图，本项目生成；底图 [he_xuL-CyyI](https://unsplash.com/photos/he_xuL-CyyI) · @mediamodifier |
| `sources/product-mqx-catfood.jpg` | 演示商品图，本项目生成 |
| `sources/product-nuandao-fryer.jpg` | 演示商品图，本项目生成 |
| `sources/product-qibai-serum.jpg` | 演示商品图，本项目生成；底图 [GjJZ5HBl2qQ](https://unsplash.com/photos/GjJZ5HBl2qQ) · @normals |
| `sources/product-sc-headphones.jpg` | 演示商品图，本项目生成；底图 [dBwadhWa-lI](https://unsplash.com/photos/dBwadhWa-lI) · @cdx2 |
| `sources/product-sc-watch.jpg` | 演示商品图，本项目生成 |
| `sources/product-wuyu-candle.jpg` | 演示商品图，本项目生成；底图 [smNzhFQRktg](https://unsplash.com/photos/smNzhFQRktg) · @jfdelp |
| `sources/product-wuyu-perfume.jpg` | 演示商品图，本项目生成；底图 [iDDGJt3veps](https://unsplash.com/photos/iDDGJt3veps) · @scentspiracy |
| `sources/product-xunyu-shoe.jpg` | 演示商品图，本项目生成 |
| `sources/product-xxg-bottle.jpg` | 演示商品图，本项目生成 |
