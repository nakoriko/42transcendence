# CLAUDE_CONTEXT.md — ft_transcendence

> Update at the end of each working day.

---

## Project

**Name:** Transcend
**Description:** Multiplayer Pong with tournaments, AI opponent, chat, and friends.
**Key feature:** Smart post-match analytics — where you miss the ball, reaction dynamics, comparison with friends. A fitness tracker for gamers.
**School:** 42, final Common Core project (ft_transcendence)
**Deadline:** 1 month

---

## Team

- **Currently:** solo
- **Expected:** +1–3 people (90% probability, no specific dates)
- **My role:** Tech Lead + PO. Responsible for architecture and onboarding new members.
- **Onboarding principle:** each module is isolated, a new person takes one service and doesn't touch the rest. Documentation in each service's README.

---

## Strategy: solo → team

```
┌─────────────────────────────────────────────────────────────────┐
│                     ZONE 1 — MINE ONLY                          │
│              Foundation. Nobody touches this.                    │
│                                                                  │
│   [Docker + structure]  [Auth system]  [DB schema]              │
│   [Privacy Policy + ToS]                                        │
│                                                                  │
│   A new team member cannot break what they don't touch.         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              ZONE 2 — I START, TEAM PICKS UP                    │
│                                                                  │
│   [WebSockets]    [Remote players]    [AI Opponent]             │
│                                                                  │
│   I design the service API contract.                            │
│   Teammate implements inside — without touching zone 1.         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ZONE 3 — LEAVE FOR THE TEAM                    │
│                                                                  │
│   [Tournament]  [OAuth]  [2FA]  [PWA]  [Languages]             │
│   [Gamification]  [File upload]  [Spectator]                    │
│                                                                  │
│   Isolated modules. Pick it up — build it — ship it.           │
│   No dependency on internal logic of zones 1 and 2.             │
└─────────────────────────────────────────────────────────────────┘
```

### Onboarding rule
A new teammate receives:
- README for their service (what it does, why it exists)
- API contract (input/output interface)
- Access only to their folder in the repository
- A first task completable in 2–4 hours

### Workflow for each new feature
```
[STUDY] → understand the concept before building
     ↓
[ARCHITECTURE] → design before writing code
     ↓
[IMPLEMENTATION] → write the code
     ↓
[DEFENSE] → verify understanding after implementation (ask Claude to test your knowledge)
```

---

## Tech Stack

| Layer | Technology | Knowledge Level |
|---|---|---|
| Frontend | Vue + Tailwind | learning from scratch |
| Backend | Django + DRF | learning from scratch |
| Database | PostgreSQL | learning from scratch |
| Deploy | Docker Compose | minimal experience |
| Auth | JWT + bcrypt | learning from scratch |
| Real-time | WebSockets (Django Channels) | learning from scratch |

**Background knowledge:** C/C++, basic HTML/CSS/JS, Git (some issues with merge/PR).

---

## Project Modules

### Doing solo (goal: 9 pts in 3 weeks)

| Module | Type | Pts | Status |
|---|---|---|---|
| Frontend + Backend framework (Vue + Django) | Major | 2 | ⬜ not started |
| User management (profile, avatar, friends) | Major | 2 | ⬜ not started |
| Basic Pong game ⚠️ needed before everything else | Major | 2 | ⬜ not started |
| ORM (Django ORM built-in) | Minor | 1 | ⬜ not started |
| Analytics dashboard (win/loss, history, leaderboard) | Minor | 1 | ⬜ not started |

### With team (goal: +6 pts)

| Module | Type | Pts | Assigned to |
|---|---|---|---|
| WebSockets + Remote players | Major | 2 | team/me |
| AI Opponent | Major | 2 | team/me |
| Tournament system | Minor | 1 | team |
| Game customization | Minor | 1 | team |
| OAuth | Minor | 1 | team |

### Bonus — only if Phases 1–4 are fully complete

| Module | Type | Pts | Note |
|---|---|---|---|
| Advanced Analytics (heatmap, real-time charts, PDF/CSV export) | Major | +2 | IV.8 — my signature feature |
| 2FA | Minor | +1 | easy, for team |
| PWA | Minor | +1 | easy, for team |
| Multiple languages | Minor | +1 | easy, for team |

### Easy modules for new teammates (2–4 hours each)

Spectator mode, Gamification, File upload, Sentiment analysis

**Total goal: 15 base pts, up to 20 pts with team and bonuses**

---

## Architecture

```
transcend/
├── docker-compose.yml
├── .env.example
├── frontend/          # Vue — separate container
├── backend/           # Django — separate container
├── websocket/         # Django Channels + Redis — separate container
├── db/                # PostgreSQL
├── nginx/             # HTTPS, reverse proxy
└── CLAUDE_CONTEXT.md  # this file
```

> Each service = separate Docker container = separate area of responsibility for a team member.
> Online presence (online status) goes through the WebSocket Gateway, not through REST.

---

## My Skill Level (honest)

**Know well:** C/C++, logic, algorithms, design, infographics, data visualization
**Know basically:** HTML/CSS/JS (no frameworks), Git
**Minimal experience:** Docker (submitted one project with difficulty)
**Learning from scratch:** Vue, Django, PostgreSQL, WebSockets

**Important for the mentor:**
- Explain through analogies with C/C++ where possible
- Don't skip steps — I'm a web beginner
- Visual metaphors work well (design background)
- I must be able to explain every line of code during the defense

---

## Weekly Plan

### Week 1 — Foundation
Goal: everything runs, services see each other.

- [x] Repository folder structure
- [x] docker-compose.yml with three services (frontend, backend, db)
- [x] Vue — hello world in browser
- [x] Django — hello world via API
- [x] PostgreSQL — connected to Django
- [x] nginx — HTTPS locally
- [x] .env.example filled in
- [x] **Privacy Policy + Terms of Service pages** ← required, project won't be accepted without them

### Week 2 — Auth + Database
Goal: user can register and log in.

- [x] Auth: registration, login, JWT, bcrypt
- [x] DB models: User, Session, Match, MatchEvent, FriendRelation
- [ ] Basic UI: login/register/profile pages
- [ ] Protected routes (frontend + backend)

### Week 3 — Game + User Management
Goal: two players can play a match on one computer.

- [ ] Pong: game loop on canvas
- [ ] Local multiplayer (two players, one keyboard)
- [ ] Logging every hit and ball position in MatchEvent
- [ ] User management: profile, avatar, friends list
- [ ] Basic match result saving to DB

### Week 4 — Analytics + Finalization
Goal: 15 pts, project submitted.

- [ ] Analytics dashboard (win/loss, match history, leaderboard)
- [ ] README.md per subject requirements (Team Info, Stack, DB Schema, Modules)
- [ ] Testing in Chrome, clean console
- [ ] docker-compose up — everything starts with one command
- [ ] Defense preparation (defense simulation with Claude)

### Buffer for team (parallel to weeks 3–4)
When teammates arrive — they pick from this list:
WebSockets, Remote players, AI Opponent, Tournament, OAuth, 2FA, PWA, File upload, Languages

---

## Rules for Working with Claude

### Principles
1. Paste this file at the beginning of each new chat
2. Specify the chat type in your first message
3. Update "Progress" and "Open questions" every day
4. Never copy-paste code without understanding it

### Chat Types and Prompt Templates

**[ARCHITECTURE]** — design before writing code
```
[ARCHITECTURE]
[paste CLAUDE_CONTEXT.md]
Task: design [exactly what].
Don't write code — only structure, diagrams, questions.
Start by clarifying my understanding of the task.
```

**[STUDY: topic]** — understand a concept
```
[STUDY: topic name]
[paste CLAUDE_CONTEXT.md]
I have never worked with [topic].
First ask what I already understand.
Explain the concept through analogy, then a minimal example.
At the end ask me 2–3 questions to check my understanding.
```

**[IMPLEMENTATION: feature]** — working with specific code
```
[IMPLEMENTATION: feature name]
[paste CLAUDE_CONTEXT.md]
Implementing: [exactly what].
Current code: [paste or describe].
Problem / question: [specific].
Explain every decision before writing code.
```

**[DEFENSE]** — evaluation simulation
```
[DEFENSE]
[paste CLAUDE_CONTEXT.md]
I implemented: [module or feature].
Ask me questions as a strict 42 evaluator.
If I answer imprecisely — point out the gap, don't give the answer immediately.
Keep score: what I know well / what needs review.
```

**[ONBOARDING]** — when a new team member joins
```
[ONBOARDING]
[paste CLAUDE_CONTEXT.md]
A new person has joined the team. Their level: [description].
Their module: [what they're taking].
Help me create a README for them with: project context,
service description, API contract with other services,
steps to run locally.
```

---

## Progress

### Done
- [x] Repository folder structure
- [x] docker-compose.yml (6 services: frontend, backend,
      websocket, db, redis, nginx)
- [x] .env.example
- [x] .gitignore
- [x] Vue — hello world in browser
     - Node.js 20 installed in WSL
     - Vite + Vue project created in frontend/
     - HMR working via usePolling (project on /mnt/c/)
     - Understood: component = .vue file with <template> block
- [x] Django — hello world via API
     - Dockerfile for backend written
     - requirements.txt: django, djangorestframework, psycopg2-binary
     - Django project `core` created
     - App `api` created
     - First endpoint GET /api/hello/ returns JSON
     - StatReloader working (hot reload)
     - Django Admin accessible at /admin/
- [x] PostgreSQL — connected to Django
     - Named volume postgres_data (WSL compatibility)
     - import os + DATABASES configured via env variables
     - migrate run manually, 10 built-in Django tables created
     - TODO: auto-run migrate via Dockerfile (Week 2)
- [x] nginx — HTTPS locally
      - self-signed certificate (openssl, 365 days)
      - nginx.conf: reverse proxy for frontend/backend, http→https redirect
      - .dockerignore for frontend and backend
      - frontend/Dockerfile written
      - websocket block temporarily commented out (TODO: week 2)
- [x] Privacy Policy + Terms of Service pages
     - Created views/PrivacyPolicy.vue and views/TermsOfService.vue
     - vue-router configured: routes /privacy and /terms
     - <RouterView> added to App.vue
     - Footer with links on both pages — accessible from any page
     - Understood: views/ = screen pages, components/ = reusable UI pieces
     - Understood: <RouterView> = "slot" where the router inserts the right component
- [x] Database Models (Week 2)
     - Created `users/` app
     - Extended AbstractUser: nickname, avatar, wins, losses, is_online
     - AUTH_USER_MODEL = 'users.User' set in settings.py
     - MEDIA_URL and MEDIA_ROOT configured for avatars
     - CSRF_TRUSTED_ORIGINS = ['https://localhost'] added
     - Pillow added to requirements.txt
     - Model Match: player1, player2, score, started_at, ended_at, winner
     - Model MatchEvent: match, event_type, player, timestamp
     - Model FriendRelation: from_user, to_user, status, created_at
     - Migrations applied (0001_initial, 0002_friendrelation_match_matchevent)
     - All models registered in Django Admin
     - nginx configured for /admin/
     - Superuser created manually
- [x] Auth endpoints + JWT (Week 2)
     - djangorestframework-simplejwt installed
     - JWT configured in settings.py (DEFAULT_AUTHENTICATION_CLASSES)
     - CustomUserManager created (email as USERNAME_FIELD)
     - RegisterSerializer built (write_only password, create_user)
     - POST /api/users/register/ — works
     - POST /api/users/login/ — returns access + refresh tokens
     - POST /api/users/logout/ — backend returns 200 OK, 
       frontend (Vue) will delete token from localStorage — Week 3
     - GET /api/users/profile/ — protected route, validates JWT

### Open Questions
*(update as work progresses)*
- healthcheck for db (backend waits for PostgreSQL to be truly ready)
- How to organize the WebSocket service separately from main Django?
- How will a new team member get access to the repository?
- Move project to ~/projects/ for native HMR (not urgent)
- Auto-run migrate on docker-compose up (script in Dockerfile)
- healthcheck for db — backend starts before Postgres is ready
- websocket/Dockerfile is empty — needed in week 2
- backend port 8000 is exposed — remove when nginx is stable
- HMR with usePolling sometimes misses changes — investigate why
- Week 2 remaining: basic UI login/register/profile in Vue
- Protected routes on frontend (Vue Router guards)
- Recreate superuser via createsuperuser 
  (old one was created before CustomUserManager)

---

## Decisions Already Made (not up for debate)

| Decision | Reason |
|---|---|
| Django instead of Node | Fast start, built-in ORM, less boilerplate |
| Vue instead of React | Easier for a beginner, same concepts |
| usePolling in vite.config.js | HMR doesn't work on /mnt/c/ in WSL — polling as a workaround |
| Named volume for Postgres | WSL doesn't allow bind mount permissions |
| PostgreSQL | Reliability, complex query support for analytics |
| Separate container for WS | Team isolation, scalability |
| Analytics Minor (basic) + Advanced Major (bonus) | Subject IV.3=Minor, IV.8=Major; Advanced only if time allows |
| OAuth → team | Simpler solo, less risk; ORM schema must be ready before they start |
| Privacy Policy + ToS in Week 1 | Required subject condition — project won't be accepted without them |
| Online presence via WebSocket | Vue only renders; status stored in DB, transport — WS Gateway |
| No Session model — not needed with JWT | Django sessions kept for Admin only. No custom Session model created. |
