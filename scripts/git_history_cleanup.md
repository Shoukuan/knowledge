# Git 历史清理指南（安全步骤）
<!-- TOC -->


<!-- TOC END -->


目的：从 Git 历史中移除已提交的“大文件”以缩小仓库体积。该文档给出使用 `git filter-repo` 或 BFG 的安全流程与示例命令。执行前务必备份并与团队协调。

重要原则：
- 永远先备份仓库（镜像克隆）。
- 在本地和临时远端上验证结果，确认无误后再强制推送到中央仓库。
- 操作会重写历史，所有协作者需要重新克隆或重写他们的本地分支。

前提工具：
- `git` 已安装
- 推荐：`git-filter-repo`（https://github.com/newren/git-filter-repo）
- 备选：`bfg-repo-cleaner`（https://rtyley.github.io/bfg-repo-cleaner/）

安全流程概览：

1) 生成要移除的文件清单（已在 `reports/large_files.csv` 中）。

2) 备份仓库（镜像）：

```powershell
git clone --mirror <repo_url> repo-backup.git
``` 

3) 在镜像仓库上进行测试性过滤（示例：使用 `git filter-repo`）：

```powershell
cd repo-backup.git
# 从 CSV 中提取要删除的路径并保存到 paths-to-remove.txt
# 确保 paths 使用仓库相对路径并用 UNIX 风格分隔符（/）。
# 例如：
# 仿真工具/A006 CPA封装参数提取 2/....rlgcFreq.rlgcdata

# 运行过滤（示例 - 删除指定路径）：
git filter-repo --paths-from-file ../scripts/paths-to-remove.txt --invert-paths
```

说明：`--invert-paths` 会保留 `paths-to-remove.txt` 中指定的内容的反集，即删除这些路径。

4) 验证结果（查看仓库大小、文件是否已移除）：

```powershell
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git verify-pack -v .git/objects/pack/pack-*.idx | sort -k3 -n
```

5) 当确认无误后，强制推送到远端（谨慎）：

```powershell
git push --force --all
git push --force --tags
```

6) 通知团队：所有协作者需重新克隆仓库或运行 `git fetch` + 重置他们的分支。

BFG 示例（备选）：

```bash
# 使用 BFG 删除所有 .zip 文件
bfg --delete-files '*.zip' repo-mirror.git
cd repo-mirror.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push
```

回滚策略：如果出问题，使用备份镜像或备份分支恢复。

小结：我同时提供一个 PowerShell 脚本 `remove_large_files.ps1`，用于从 `reports/large_files.csv` 提取路径并创建 `paths-to-remove.txt`，以及演示在镜像仓库中运行 `git filter-repo` 的命令（该脚本不会自动执行危险的 push）。请在同意并确认备份后运行过滤操作。

