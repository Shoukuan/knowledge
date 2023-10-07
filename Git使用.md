# Git使用

# 新增修改过程

git clone git_url

git branch

git branch branch_name

git checkout branch_name

.......

git status

git diff

git add .

->>>>>>

git commit -m "description"(提交到本地库)

git status

git checkout master

git pull --rebase origin master

git merge branch_name(把自己分支上改动的代码，合并到主分支上)

git push origin master (提交到远程库)
git push -u origin master

git log (查看历史提交记录)

# 回退到某commit

回退commit
git reset --soft // 回退到指定commit，该commit之后的提交内容，保留工作目录，并把重置 HEAD 所带来的新的差异放进暂存区

git reset --hard // 回退到指定commit，该commit之后的提交内容，工作区和暂存区的内容都被抹掉

git reset 或 git reset --mixed // 不带参数,或带参数–mixed(默认参数)，与git reset --soft 不同，它将会把差异放到工作区
