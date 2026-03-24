# 数据集发布包说明

本目录是对外发布入口，目标是让第三方可以快速完成数据理解与加载。

## 目录内容

- dataset_manifest.txt: 样本清单（TSV，UTF-8）
- STATS.txt: 样本总数与情感分布
- DATASET_CARD.md: 数据来源、字段定义、使用限制
- PUBLISH_CONTENTS.txt: 发布文件清单

## 样本规模

- total_samples: 1500
- emotion:
	- calm: 764
	- excited: 736

说明：本仓库默认仅保留发布清单与统计文件，音频目录 `dataset/dataset_wavs/` 可按需单独存储或通过发布包分发。

## 清单字段定义

dataset_manifest.txt 的列如下：

1. sample_id: 发布包样本编号
2. audio_file: 音频文件名（相对 dataset_wavs）
3. emotion: 情感标签（calm / excited）
4. intensity: 情感强度（当前发布版为 1.0）
5. question_id: 来源问题编号
6. text: 清洗后的中文文本

## 快速校验（清单）

在仓库根目录执行：

```bash
python -c "import pandas as pd; from pathlib import Path; manifest = Path('dataset/dataset_publish/dataset_manifest.txt'); df = pd.read_csv(manifest, sep='\t'); print('rows:', len(df)); print('emotion distribution:'); print(df['emotion'].value_counts())"
```

如本地已放置 `dataset/dataset_wavs/`，可额外校验音频文件完整性：

```bash
python -c "import pandas as pd; from pathlib import Path; manifest = Path('dataset/dataset_publish/dataset_manifest.txt'); audio_dir = Path('dataset/dataset_wavs'); df = pd.read_csv(manifest, sep='\t'); missing = [f for f in df['audio_file'] if not (audio_dir / f).exists()]; print('missing audio files:', len(missing))"
```

## 使用示例

当某一行 audio_file 为 psyqa_aug_00000.wav 时，对应音频路径为：

dataset/dataset_wavs/psyqa_aug_00000.wav

## 注意事项

- 本发布包包含合成增强样本。
- 若用于严格评测，建议先进行抽检与听感一致性复核。
- 对外二次发布前，请根据你的使用场景补充合规审查。
