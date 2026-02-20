# 推送到 GitHub 步驟

目前狀態：
- 已建立首次 commit
- 分支名稱：**init**
- `.env` 已加入 `.gitignore`，不會被推送

## 1. 在 GitHub 建立新 repo

1. 打開 https://github.com/new
2. **Repository name**：自訂（例如 `lg-remote`）
3. **Public** 或 **Private** 自選
4. **不要**勾選 "Add a README"、"Add .gitignore"、"Choose a license"
5. 按 **Create repository**

## 2. 在本機加入遠端並推送

建立好 repo 後，在終端機執行（請把 `YOUR_USERNAME` 和 `YOUR_REPO` 換成你的 GitHub 帳號與 repo 名稱）：

```bash
cd "/Users/joey/Downloads/LG remote"

# 加入遠端（擇一，看你是用 HTTPS 還是 SSH）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
# 或
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git

# 推送到 init 分支
git push -u origin init
```

例如 repo 名稱為 `lg-remote`、帳號為 `joey`：

```bash
git remote add origin https://github.com/joey/lg-remote.git
git push -u origin init
```

完成後，程式碼就會在 GitHub 的 **init** 分支上。
