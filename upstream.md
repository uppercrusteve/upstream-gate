# 上游

## 来源

- repo: blotato/contentskills
  took: 按许可分层、只对宽松来源放行代码复用的分类法
  license: AGPL-3.0

- repo: tt-a1i/archify
  took: 把禁忌写成可 grep 的字符串，而不是形容词
  license: Apache-2.0

## 许可

`contentskills` 是 AGPL-3.0，只能重写思路，本项目代码全为自写，未粘贴其片段，故不附 `LICENSE.upstream`。

`archify` 是 Apache-2.0，允许搬代码；当前也只借了「规则要可 grep」这一层，规则表本身自写。

本项目自身按 MIT 发布，见 `LICENSE`。

## 改了什么

上游给了分类法和书写要求，判定仍在人脑里。这里把它做成可执行：三段结构解析、许可分级、思路级声明与实物互检、SPDX 头比对，全部落到规则编号与退出码上。`fixtures/` 十组目录是十种坏样本，闸门自身也要过自己那一关。
