# octo — 冻结小模型＋外部记忆的千人千面个性化

[English](README.md) | **中文**

> 🐙 **给冻结模型一千张面孔。** *同一个模型，对每个客户说不同的话。*
> *（机制库＋可复现基准；能力结论待验——见 [CLAIMS](docs/zh/CLAIMS.md)）*

**octo（千人千面）**：在冻结小模型**外部**编排**每客户记忆＋人格**，让回复贴合每个客户的处境——
不做每用户微调。记忆存在外部、可审计、可删除的每用户 store；模型保持共享。

> **状态：机制库＋可复现个性化基准。能力结论待验。** 引用数字前先读 [`CLAIMS.md`](docs/zh/CLAIMS.md)——
> **负结果也在里面**，且是主要贡献。

## 诚实的发现

我们测了三条「聪明机制护城河」假设，**全失败**：

| 假设 | 结果 |
|---|---|
| 独特语气机制是护城河 | ❌ commodity |
| 原生 K/V 记忆 ground 精确事实 | ❌ 不可靠——模型编出与注入事实矛盾的数 |
| 学习编排胜过规则＋随数据复利 | ❌ 训出的 ReFT 干预**低于**一句强制引用规则，数据多了也不涨 |

**真正有效**的很简单：**富客户画像＋强制引用指令**让个性化翻~3 倍（specificity 0.076→0.238）。
这杠杆是**胶——可抄**。故可防御优势**不在机制**，在**累积客户数据＋产品场景＋编排 know-how**。

本仓以「负结果即贡献」的精神，发布机制＋可复现基准＋诚实边界。

## 内容
- `octo/` 编排库：`schema`（数据契约）/`prompt`（强制引用杠杆）/`memory`（RAG 自包含＋可选 BKV）/
  `judge`（specificity＋合规）/`store`（每用户＋被遗忘权）/`agent`（编排）。
- `benchmarks/personalization/` 可复现**利用缺口＋强制杠杆**基准，**0.8B/4B CPU**。
- `tests/` 离线单测（无需模型/GPU）。
- [`docs/zh/CLAIMS.md`](docs/zh/CLAIMS.md) 已证/已否证/待验。
- [`docs/zh/EXPERIMENTS.md`](docs/zh/EXPERIMENTS.md) run-271→279 完整旅程：护城河假设如何一步步被否证。

## 快速上手
```bash
pip install -e .
python -m pytest tests/ -q          # 离线单测
python benchmarks/personalization/run_bench.py --model /path/to/Qwen3.5-0.8B --device cpu
```
预期 specificity `C0_thin < C1_rich < C2_force`。**排序**是稳健发现，绝对值随底座变。

## 姊妹项目
- 🐱 [huamao-memory-bench](https://github.com/greatwhitesharklab/huamao-memory-bench) 原生 K/V 记忆引擎。
- 🦫 [kapi-interactive-review](https://github.com/greatwhitesharklab/kapi-interactive-review) 交互式审查。

## 范围与诚实
- 数据全**合成、非商业**；不分发真实客户数据/密钥/模型权重。
- 仅机制验证；**能力结论须真实语料**（待验）。
- 底座 Qwen3.5 为 Apache-2.0；权重**不**随仓分发，自行下载。

## 许可
Apache-2.0，见 [LICENSE](LICENSE)。
