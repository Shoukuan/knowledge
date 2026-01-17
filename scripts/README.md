# scripts

包含用于仓库维护的小脚本。

- `find_large_files.py`：查找超过指定大小的文件并导出 CSV/Markdown 报告。

示例：

```
python scripts/find_large_files.py --path . --threshold 1 --out reports/large_files.csv --md
```

这会在 `reports/` 下生成 `large_files.csv` 和 `large_files.md`。
