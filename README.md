# upstream-gate

把一个候选目录的 `upstream.md` 当合同来审：借鉴了谁、什么许可、能不能搬代码、我们到底改了什么。

「AGPL 只能抄思路、MIT 可以搬」这句话人人会说，落到目录里就常常变成一句 `## 上游` 加三个形容词。这个工具把三段结构、许可分级和思路级声明做成硬判定——缺一段、许可认不出、非宽松许可却没说只抄思路，都直接失败。

## 做什么

读 `upstream.md`，要求齐三段：**来源 / 许可 / 改了什么**。来源必须是 `owner/repo` 行，每条带 `took`（借鉴了什么）和 `license`。然后按许可分级（宽松 / 非宽松 / 认不出）判它是否允许搬代码，再拿 README 与目录里的实物对一遍。

判定结果三档：`PASS`、`WARN`、`FAIL`。只有错误拦发布；警告是「你得自己看一眼」。`--strict` 把警告也升级为失败，适合 CI。

### 规则

| id | 级别 | 判什么 |
|---|---|---|
| U101 | 错误/警告 | 缺 `upstream.md`；缺 `LICENSE` 只警告 |
| U102 | 错误 | `upstream.md` 缺三段之一 |
| U103 | 错误 | 来源段没有 `owner/repo` 行，或行写不成 owner/repo |
| U104 | 警告 | 许可认不出，按 idea-only 处理 |
| U105 | 错误 | 有非宽松许可的上游，README 却没声明思路级 |
| U106 | 警告 | 声明了思路级，目录里却带着 `LICENSE.upstream` / `vendor/`，要确认没搬 |
| U107 | 错误 | README 缺 `## 原创` 或 `## 上游` |
| U108 | 错误 | 同一仓库重复登记 |
| U109 | 错误/警告 | `LICENSE` 文本认不出与登记对不上（错误）；写的许可与登记不一致（警告） |
| U110 | 警告 | 超过 1MB 的二进制没说明来源 |
| U111 | 警告 | 源码里的 SPDX 头与登记的许可冲突 |
| U112 | 错误 | 登记了仓库但没写 `took` |

宽松集合：MIT、Apache-2.0、BSD-2/3-Clause、ISC、0BSD、Unlicense、CC0-1.0。非宽松：GPL / AGPL / LGPL / MPL / EUPL 全系。其余一律按认不出。

### upstream.md 长什么样

```markdown
## 来源

- repo: owner/name
  took: 借鉴了哪个具体做法
  license: MIT
```

表格式（`| repo | took | license |`）也认。字段缩进必须两格，`took` 空格子照样算漏。

## 怎么跑

Python 3.8+，标准库即可。

```bash
python -m upstream_gate path/to/candidate          # 判定
python -m upstream_gate --json path/to/candidate   # 机器可读
python -m upstream_gate --strict path/to/candidate # 警告也算失败
```

退出码：`0` 通过（含只有警告）、`1` 有错误、`2` 用法错误或目录不存在。

三个候选目录互为样本，本目录也在内：

```bash
python -m upstream_gate ../geom-lint
python -m upstream_gate .
```

测试：

```bash
python -m unittest discover -s . -t .
```

`fixtures/` 下十组目录各自触发一条规则，测试直接引用它们，不现造字符串。

## 上游

`blotato/contentskills`（AGPL-3.0）：按许可分层、只对宽松来源放行代码复用的思路。

`tt-a1i/archify`（Apache-2.0）：把禁忌写成可 grep 的字符串而不是形容词——这里的规则表就是这条的直系后代。

细节在 `upstream.md`。

## 许可

本项目 MIT，见 `LICENSE`。

上游 `contentskills` 是 AGPL-3.0，因此**只到思路级**：规则编号、判定表、解析器、CLI 都是自写，没有粘贴它的代码，故未附上游 LICENSE。若日后真要搬它的片段，需补 `LICENSE.upstream`，届时 U106 会提醒复核。

`archify` 是 Apache-2.0，本身允许搬；当前同样只借思路。

## 原创

两处上游都停在「把话说清」：写清许可、写清禁忌，靠人记得住、看得见。这里往前一步，把话变成**可执行的判定**——三段缺一即败、许可按分级决定能不能搬、非宽松却没说思路级就拦下、声明与实物（SPDX 头、LICENSE 文本）互相校验，最后给出退出码。

同时它也审自己：本目录的 `upstream.md` 登记了一条 AGPL，README 因此必须写出「思路级」，否则自己的闸门先不放过。
