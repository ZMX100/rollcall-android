#!/bin/bash
# 推送到 GitHub 脚本
# 使用方法: ./push-to-github.sh 你的GitHub用户名

if [ -z "$1" ]; then
    echo "请提供GitHub用户名"
    echo "用法: ./push-to-github.sh your-username"
    exit 1
fi

USERNAME=$1
REPO_NAME="rollcall-android"

echo "设置远程仓库..."
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git" 2>/dev/null || git remote set-url origin "https://github.com/$USERNAME/$REPO_NAME.git"

echo "重命名分支为 main..."
git branch -M main

echo "推送到 GitHub..."
git push -u origin main

echo "完成！"
echo "请在浏览器中访问: https://github.com/$USERNAME/$REPO_NAME"
echo ""
echo "然后前往 Actions 页面查看构建状态:"
echo "https://github.com/$USERNAME/$REPO_NAME/actions"
