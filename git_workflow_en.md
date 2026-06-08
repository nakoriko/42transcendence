# Git Workflow — Team Rules

Hi! Here are our Git rules — please read before you start.

## Rules
- No direct pushes to `main` — GitHub will block it
- Each task = its own branch: `feature/websocket`, `feature/oauth`, `feature/analytics`, etc.
- Never merge your own PR — wait for your teammate's approval

## Step 1 — Update from main
```bash
git checkout main
git pull origin main
```

## Step 2 — Create your branch for the task
```bash
git checkout -b feature/task-name
```
For example: `git checkout -b feature/websocket`

## Step 3 — Work and commit
```bash
git add .
git commit -m "feat: describe what you did"
```

## Step 4 — When the task is done, test locally first
```bash
docker-compose up --build
```
Make sure everything works and there are no errors in the browser console.
**Do not create a PR before testing.**

## Step 5 — Push your branch and message me
```bash
git push origin feature/task-name
```
Open a PR on GitHub (Base: `main`, Compare: `feature/your-branch`),
write 2–3 lines describing what you did — then send me the link in chat.

## What happens next
- I will test on my side
- If everything is ok — I approve, you merge
- If I have questions — I will comment in the PR
- If the conflict is complex — we jump on a call, discuss, then merge

## Golden rule
If you break main — message the team immediately and fix it before anything else.
