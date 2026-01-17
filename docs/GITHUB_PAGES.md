# 使用 GitHub Pages 部署 `docs/`

此说明将 `docs/` 目录部署到 GitHub Pages（`gh-pages` 分支），通过仓库内的 Actions 自动化实现。

工作流位置：`.github/workflows/deploy-docs.yml`。

操作说明：

1. 我已在仓库中添加工作流文件：推送到 `master` 时（或手动触发）会把 `docs/` 内容发布到 `gh-pages` 分支。
2. 该工作流使用内置 `GITHUB_TOKEN`（不需要额外 secret）。
3. 部署后，打开仓库 Settings → Pages，确保 Pages 源已设置为 `gh-pages` 分支（路径 `/`），并保存。

注意：第一次启用 Pages 之后，URL 可能需要几分钟生效。

回滚与调试：
- 若需要手动推送内容到 `gh-pages`，可在本地运行：
```
git worktree add /tmp/gh-pages gh-pages
cp -r docs/* /tmp/gh-pages/
cd /tmp/gh-pages
git add -A
git commit -m "chore: update docs"
git push origin gh-pages
```

安全提示：工作流使用 `GITHUB_TOKEN`，仓库管理员可以在 Actions 设置中限制谁可以触发工作流。
