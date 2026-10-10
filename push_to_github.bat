@echo off
REM Creates github.com/Tulasikrishna3227/voice-rag and pushes. Requires: git + GitHub CLI (https://cli.github.com), run "gh auth login" once.
git init -b main
git add .
git commit -m "Voice RAG: Telugu/Hindi/English document assistant"
gh repo create voice-rag --public --source=. --remote=origin --push
pause
