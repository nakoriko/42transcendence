# CLAUDE_CONTEXT.md — ft_transcendence

> Update at the end of each working day.

---

## Project

**Name:** Transcend
**What it is:** Pong with remote two-player matches, tournaments, AI opponent, chat, and friends.
**Differentiator:** Smart post-match analytics — where you miss the ball, reaction time trends, comparison with friends.
**School:** 42, final Common Core project (ft_transcendence)
**Deadline:** June 9 – July 9, 2026

---

## Team

- **Now:** 2 people
- **Expected:** +2 people (70% probability, no confirmed dates)
- **My role:** Tech Lead + PO + Developer
- **Onboarding principle:** each module is isolated — new person takes one service and doesn't touch the rest. Documentation in each service's README.

---

## Solo → Team strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                  ZONE 1 — MINE ONLY ✅ DONE                     │
│                                                                  │
│   [Docker + structure]  [Auth system]  [DB schema]              │
│   [Privacy Policy + ToS]  [Pong game]  [User management]        │
│                                                                  │
│   Foundation. Nobody touches this.                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ZONE 2 — IN PROGRESS                           │
│                                                                  │
│   [Analytics — me]  [Design system — me]                        │
│   [WebSockets — teammate]  [Remote players — teammate]          │
│                                                                  │
│   I design the API contract. Teammate implements in their folder.│
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ZONE 3 — LEFT FOR THE TEAM                     │
│                                                                  │
│   [Tournament]  [OAuth]  [2FA]  [PWA]  [Languages]             │
│   [AI Opponent]  [Gamification]  [File upload]  [Spectator]     │
│                                                                  │
│   Isolated modules. Take one — build it — deliver it.           │
└─────────────────────────────────────────────────────────────────┘
```

### Onboarding rule
A new teammate receives:
- README for their service (what it does, why it exists)
- API contract (what it accepts, what it returns)
- Access only to their folder in the repository

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

## Stack

| Layer | Technology | Knowledge level |
|---|---|---|
| Frontend | Vue + Tailwind | learning from scratch |
| Backend | Django + Django REST Framework | learning from scratch |
| Database | PostgreSQL | learning from scratch |
| Deploy | Docker Compose | minimal experience |
| Auth | JWT + bcrypt | learning from scratch |
| Real-time | WebSockets (Django Channels) | learning from scratch |

**Background knowledge:** C/C++, basic HTML/CSS/JS, Git (messy with merge/PR).

---

## Project modules

### My modules

| Module | Type | Pts | Status |
|---|---|---|---|
| IV.1 Framework frontend + backend (Vue + Django) | Major | 2 | ✅ done |
| IV.1 ORM (Django ORM built-in) | Minor | 1 | ✅ done |
| IV.1 Custom design system (10+ reusable components) | Minor | 1 | ✅ done |
| IV.1 User Interaction (chat + profile + friends) | Major | 2 | ⬜ after WebSocket. Profile and friends done |
| IV.3 Standard User management (profile, avatar, friends) | Major | 2 | ✅ done (add one endpoint) |
| IV.3 User activity dashboard | Minor | 1 | ✅ in progress |
| IV.6 Web-based game Pong | Major | 2 | ✅⚠️ needs fixes  |
| IV.8 Advanced analytics | Major | 2 | ⬜ in progress |

**My total: 13 pts**

### Teammate (Sabino)

| Module | Type | Pts | Status |
|---|---|---|---|
| IV.1 WebSockets | Major | 2 | ⬜ in progress |
| IV.6 Remote players | Major | 2 | ⬜ in progress |

**Total with team: 17 pts ✅**

### Team (if they join, or Sabino if he has time)

| Module | Type | Pts |
|---|---|---|
| IV.4 AI Opponent | Major | 2 |
| IV.6 Tournament system | Minor | 1 |
| IV.6 Game customization | Minor | 1 |
| IV.3 OAuth | Minor | 1 |
| IV.3 2FA | Minor | 1 |
| IV.1 PWA | Minor | 1 |
| IV.2 Multiple languages | Minor | 1 |

### Easy modules for new teammates

IV.6 Spectator mode, IV.6 Gamification, IV.1 File upload

---

## Architecture

```
transcend/
├── docker-compose.yml
├── .env.example
├── frontend/          # Vue — separate container
├── backend/           # Django + Django Channels — separate container
├── redis/             # Redis — separate container. Broker for WebSocket connections
├── db/                # PostgreSQL
├── nginx/             # HTTPS, reverse proxy
└── CLAUDE_CONTEXT.md  # this file
```

> WebSocket (Django Channels) is embedded in the backend container.
> Redis is a separate container, broker for WebSocket connections.
> Online presence (online status) goes through WebSocket, not REST.

---

## My level (honestly)

**Know well:** C/C++, logic, algorithms, design, infographics, data visualization
**Know basically:** HTML/CSS/JS (no frameworks), Git
**Minimal experience:** Docker (barely passed one project with it)
**Learning from scratch:** Vue, Django, PostgreSQL, WebSockets

**Important for mentor:**
- Explain through C/C++ analogies where possible
- Don't skip steps — I'm a web beginner
- I must be able to explain every line of code at the defense

---

## Weekly plan

### ✅ Done (May 18 – June 7)
- everything starts up, services can see each other
- user can register and log in
- two players can play a match on one computer

- [x] Repository folder structure
- [x] docker-compose.yml (frontend, backend, db, redis, nginx)
- [x] Vue — hello world in browser
- [x] Django — hello world via API
- [x] PostgreSQL — connected to Django
- [x] nginx — HTTPS locally
- [x] .env.example filled in
- [x] Privacy Policy + Terms of Service pages
- [x] Auth: registration, login, JWT
- [x] DB models: User, Match, MatchEvent, FriendRelation
- [x] Basic UI: login/register/profile pages
- [x] Protected routes (frontend + backend)
- [x] Pong: game loop on canvas
- [x] Local multiplayer (two players, one keyboard)
- [x] Logging every hit and ball position to MatchEvent
- [x] User management: profile, avatar, friends list
- [x] Basic match result save to DB
- [x] Auto-run migrate on docker-compose up

### Week 1 (June 9–15) — Analytics
Goal: close 9 pts.

- [x] UI + Custom design system: Button, Card, Avatar, Logo, Input, Badge, Modal, Chart, Leaderboard, Navbar — minimum 10 components
- [x] Define color palette (3–5 colors)
- [x] Define typography (1–2 fonts)
- [x] Choose icon set 
- [x] Build 10+ reusable components
- [x] User activity dashboard (wins/losses, match history, leaderboard) — IV.3, 1pt
- [x] PATCH /api/users/profile/ — update profile data (nickname, email) (to complete module IV.3)

### Weeks 2–4 (June 16–July 6) — Finalization
Goal: 14+ pts, project ready for submission.

- [ ] Advanced analytics (heatmap, charts, export) — IV.8, 2pt
- [ ] README.md per subject requirements (Team Info, Stack, DB Schema, Modules)
- [ ] Testing in Chrome, clean console
- [ ] docker-compose up — everything starts with one command
- [ ] Remove backend port 8000 from external exposure
- [ ] Defense prep (evaluation simulation with Claude)

### Parallel (teammate)
- [ ] WebSockets — Phase 1
- [ ] Remote Players — Phase 2

---

## Rules for working with Claude

### Principles
1. Paste this file at the start of every new chat
2. State the chat type in the first message
3. Update "Progress" and "Open questions" every day
4. Never copy-paste code without understanding it

### Chat types and prompt templates

**[ARCHITECTURE]** — design before writing code
```
[ARCHITECTURE]
[paste CLAUDE_CONTEXT.md]
Task: design [what exactly].
Don't write code — structure, diagrams, questions only.
Start by clarifying my understanding of the task.
```

**[STUDY: topic]** — understand a concept
```
[STUDY: topic name]
[paste CLAUDE_CONTEXT.md]
I have never worked with [topic].
First ask what I already understand.
Explain the concept through an analogy, then a minimal example.
At the end give me 2–3 questions to check my understanding.
```

**[IMPLEMENTATION: feature]** — working with specific code
```
[IMPLEMENTATION: feature name]
[paste CLAUDE_CONTEXT.md]
Implementing: [what exactly].
Current code: [paste or describe].
Problem / question: [be specific].
Explain every decision before writing code.
```

**[DEFENSE]** — evaluation simulation
```
[DEFENSE]
[paste CLAUDE_CONTEXT.md]
I have implemented: [module or feature].
Ask me questions like a strict 42 evaluator.
If my answer is imprecise — point out the gap, don't give the answer immediately.
Keep score: what I know well / what needs review.
```

**[ONBOARDING]** — when a new team member joins
```
[ONBOARDING]
[paste CLAUDE_CONTEXT.md]
A new person joined the team. Their level: [description].
Their module: [what they're taking].
Help me write a README for them with: project context,
their service description, API contract with other services,
steps to run locally.
```

---

## Progress

### Done
- [x] Repository folder structure
- [x] docker-compose.yml (5 services: frontend, backend, db, redis, nginx)
- [x] .env.example
- [x] .gitignore
- [x] Vue — hello world in browser
     - Node.js 20 installed in WSL
     - Vite + Vue project created in frontend/
     - HMR works via usePolling (project on /mnt/c/)
     - Understood: component = .vue file with <template> block
- [x] Django — hello world via API
     - Dockerfile for backend written
     - requirements.txt: django, djangorestframework, psycopg2-binary
     - Django project `core` created
     - App `api` created
     - First endpoint GET /api/hello/ returns JSON
     - StatReloader works (hot reload)
     - Django Admin accessible at /admin/
- [x] PostgreSQL — connected to Django
     - Named volume postgres_data (WSL compatibility)
     - import os + DATABASES configured via env variables
     - migrate run manually, 10 built-in Django tables created
- [x] nginx — HTTPS locally
     - self-signed certificate (openssl, 365 days)
     - nginx.conf: reverse proxy for frontend/backend, http→https redirect
     - .dockerignore for frontend and backend
     - frontend/Dockerfile written
- [x] Privacy Policy + Terms of Service pages
     - Created views/PrivacyPolicy.vue and views/TermsOfService.vue
     - vue-router configured: routes /privacy and /terms
     - <RouterView> added to App.vue
     - Footer with links on both pages — accessible from any page
     - Understood: views/ = screen pages, components/ = reusable UI pieces
     - Understood: <RouterView> = "slot" where router inserts the right component
- [x] DB models
     - Created `users/` app
     - AbstractUser extended: nickname, avatar, wins, losses, is_online
     - AUTH_USER_MODEL = 'users.User' set in settings.py
     - MEDIA_URL and MEDIA_ROOT configured for avatars
     - CSRF_TRUSTED_ORIGINS = ['https://localhost'] added
     - Pillow added to requirements.txt
     - Model Match: player1, player2, score_player1, score_player2, started_at, ended_at, winner
     - Model MatchEvent: match, event_type, player, pos_x, pos_y, reaction_time_ms, timestamp
     - Model FriendRelation: from_user, to_user, status, created_at
     - Migrations applied
     - All models registered in Django Admin
     - nginx configured for /admin/
     - Superuser created manually
- [x] Auth endpoints + JWT
     - djangorestframework-simplejwt installed
     - JWT configured in settings.py (DEFAULT_AUTHENTICATION_CLASSES)
     - CustomUserManager created (email as USERNAME_FIELD)
     - RegisterSerializer (write_only password, create_user)
     - POST /api/users/register/ — works
     - POST /api/users/login/ — returns access + refresh tokens
     - POST /api/users/logout/ — backend returns 200 OK
     - GET /api/users/profile/ — protected route, checks JWT
- [x] Basic UI: login/register/profile pages
     - LoginView.vue: form, fetch, JWT → localStorage, redirect, try/catch
     - RegisterView.vue: form, fetch, redirect to /login, try/catch
     - ProfileView.vue: fetch with Bearer token, display user data
     - All inputs have id, name, autocomplete attributes
- [x] Protected routes (Vue Router guard + backend JWT)
     - meta: { requiresAuth: true } on /profile
     - router.beforeEach checks token before each navigation
- [x] Game loop + MatchEvent logging
     - MatchEvent model updated: pos_x, pos_y (FloatField), reaction_time_ms (IntegerField), all null=True
     - API endpoints: StartMatchView, LogMatchEventView
     - Routes: POST /api/game/match/start/, POST /api/game/match/events/
     - GameView.vue: game loop on canvas via requestAnimationFrame
     - Ball physics: movement, wall bounces (fix via Math.abs)
     - Two paddles: W/S (player 1), ArrowUp/ArrowDown (player 2)
     - Collision detection: ball vs paddles with Math.abs fix
     - Score system: ball resets in random direction
     - Win condition: first to 5 points, loop stops
     - Logging: initMatch() gets userId and matchId before start
     - events[] collects hits, saveMatch() sends to DB on win
     - Coordinates normalised 0..1 (pos_x = ball.x / canvas.width)
     - Keyboard via e.code — layout independent
     - JWT lifetime 8h in settings.py for development
     - Verified: 13 MatchEvents recorded in PostgreSQL after an active match
- [x] Moved game to Django app game/
- [x] Logout on frontend (button + localStorage clear)
- [x] container_name set in docker-compose.yml
- [x] Created empty apps: analytics, tournament, chat
- [x] Register link on Login page
- [x] LogoutView protected
- [x] Save match result to DB (winner, ended_at, score)
- [x] URLs moved: /api/game/ instead of /api/users/game/
- [x] Lobby: choose opponent from user list before match
     - GET /api/users/list/ — list of registered players (excluding current)
     - LobbyView.vue — dropdown + "Start match" button → /game?player2=5
- [x] User management: profile, avatar, friends list
     - PATCH /api/users/avatar/ — avatar upload (FormData, ImageField, Pillow)
     - GET /api/users/friends/ — friends list, incoming/outgoing requests
     - POST /api/users/friends/request/ — send request (Q check both directions)
     - PATCH/DELETE /api/users/friends/<pk>/ — accept/reject/delete
     - FriendsView.vue — friends + incoming + allUsers + online status
     - apiFetch() helper — single point for authorised requests
     - App.vue nav — RouterLink + watch(route) + logout
     - Router: / and catch-all → redirect /login
[x] Lobby redesigned (sidebar layout, game mode selection, opponent selection, toggle)
[x] AppNavbar → AppSidebar (new app shell layout)
[x] AppButton — variants: primary / large / cta / ghost
[x] Fixed memory leak in GameView + arrow key page scroll
[x] Auth pages updated to match design system
[x] EventType choices for MatchEvent model (hit/miss/goal) + migration
[x] Log miss and goal events in game loop with coordinates
[x] PublicProfileView GET /api/users/<pk>/
[x] Refactor GameView: player1/player2 objects instead of scattered variables
[x] Real player nicknames on win screen and scoreboard
[x] wins/losses are now correctly saved to DB after match ends (FinishMatchView updated)
[x] AppStatsCard connected to real data from /api/users/profile/
[x] Memory leak in GameView fixed
[x] Avatar: initials circle in profile
[x] PATCH /api/users/profile/ : update nickname and email
    - ProfileUpdateSerializer (partial=True, fields: nickname, email)
    - ProfileView.patch(), secured via request.user (IDOR-safe)
    - Tested via DevTools Console 
[x] ProfileView full rebuild (Week 2)
     - ProfileView.vue — 2-column grid, 4 cards
     - apiFetch everywhere instead of manual fetch (except FormData)
     - Promise.all for parallel loading of profile/friends/matches
     - ProfileAvatar.vue — hover overlay for avatar upload, canUpload prop
     - ProfileStatsCard.vue — wins/losses/winRate computed inside component
     - RecentMatchesList.vue — WIN/LOSS badge, date formatting
     - GET /api/game/matches/?limit=N — new match history endpoint
     - MatchHistorySerializer — computes opponent/score/result relative to request.user
     - style.css — added .card, .card-label, .online-dot, .badge-win, .badge-loss
[x] /game route protection
      - meta: { requiresAuth: true, requiresGame: true } on /game route
      - router.beforeEach: if no to.query.player2 → redirect to /lobby
      - direct URL /game without params → /lobby

[x] Refresh token — full cycle
      - LoginView.vue: saves data.refresh to localStorage
      - users/urls.py: TokenRefreshView at token/refresh/
      - apiFetch.js: tryRefresh() on 401 — fetches new access token,
        retries original request
      - user does not notice token refresh
      - after 7 days refresh expires → redirect to /login
- [x] Remote Players — backend ready (Week 3)
      - Match model: added status field (pending/active/finished) and mode field (local/remote/ai)
      - Migration 0003_match_mode_match_status applied
      - StartMatchView updated: explicitly sets status=ACTIVE, mode=LOCAL
      - MatchCreateSerializer: status, mode — read_only
      - MatchInviteSerializer: all fields read_only (logic handled in view)
      - POST /api/game/match/invite/ — creates pending match, accepts opponent_id
      - PATCH /api/game/match/<id>/status/ — updates match status (for teammate's WS consumer)
      - User imported via get_user_model()
      - API contract for teammate — REMOTE_PLAYERS_CONTRACT_IT.md delivered
- [x] Lobby — full UI redesign (June 22)
    - Layout: two columns (opponents + filter left, match card right)
    - GameModeCard → pills with dot indicator, default mode: local
    - PlayCard — style unified with GameModeCard (height, dividers, selection)
    - LobbyVsRow — vertical player layout, slot for button and error message
    - AppFilterTabs — reusable filter component (used in lobby, ready for dashboard)
    - AppAvatar — added lg size (w-12 h-12)
    - AppButton — added compact variant (px-6 py-2 rounded-xl)
    - Opponent list scroll: max-h-[420px], custom scrollbar (.scroll-thin)
    - Default states: mode = local, filter = All Players
- [x] Friends block in profile (ProfileFriendsBlock.vue)
      - Created self-contained component src/components/profile/ProfileFriendsBlock.vue
      - Logic: loadFriends, removeFriend, sendRequest, toggleDropdown
      - Filters: all / online / pending (pending = outgoing requests)
      - "+" dropdown to add friends with filtering of already added users
      - Delete: click on card → X appears
      - Auto-refresh via CustomEvent 'friends-updated' (App.vue → ProfileFriendsBlock)
      - AppAvatar: online status dot (teal = online, muted = offline)
      - Backend: added outgoing to FriendsListView
      - /friends route removed from router, FriendsView.vue kept as dead code
- [x] Refactor(profile): extract ProfileInfoCard, redesign profile header layout
     - extract profile info + edit form into ProfileInfoCard component
     - emit 'updated' to parent on save and avatar upload
     - redesign Edit button to match app filter tabs style
     - fix page top padding to match dashboard/lobby
- [x] MatchEchoViz.vue — D3 force simulation visualization of match events (June 25)
      - Component accepts props: match (Object), events (Array)
      - events are fetched in parent (MatchHistoryDashboard), not inside component
      - D3 force simulation: forceLink, forceManyBody, forceCenter, forceCollide, forceX (player separation)
      - Nodes: goal = blue (#4A8C9B, r=14), miss = coral (#F8856D, r=7), hit = sage (#ABC7C3, r=7)
      - Links: curved lines (quadratic bezier via curvePath function)
      - Dashed ring around first node (start-ring) — match start marker
      - Hover: highlight current + neighbor nodes, dim others, highlight neighbor links
      - Drag behavior: grab and drag nodes, return to position on release (fx/fy = null + alpha restart)
      - Tooltip: fixed position (top right corner), shows event type, player, reaction time
      - overflow: visible on SVG — nodes not clipped when scaled up
      - ResizeObserver — redraws on container resize
      - Start animation: nodes spawn from center with random 80px spread

- [x] MatchHistoryDashboard.vue — match history dashboard (June 25)
      - Two blocks: RecentMatchesList left, MatchEchoViz right
      - Fetches events when match is selected (watch on selectedMatch)
      - Computes stats from events: myGoals, oppGoals, hits, misses
      - AppMetric component already exists — value/label/color props
      - currentUserId fetched in parallel with matches via Promise.all


### Open questions
*(update as you go)*
- Move project to ~/projects/ for native HMR (not urgent)
- backend port 8000 exposed externally — remove when nginx is stable
- [known issue] CSP warning "blocks use of eval" in DevTools Issues panel — comes from vite-plugin-vue-devtools, not nginx. Console is clean, functionality not broken. Will disappear in production build. Fix: remove vite-plugin-vue-devtools from vite.config.js before submission.
- [ ] Sidebar: improve appearance, replace Logout button with a plain link,
      logo links to '/', nav order: Profile → Game → Dashboard → Chat
- [ ] Add solo/training mode (one player, one keyboard) —
      no data written to DB, controls hint updates accordingly
- [ ] Local game with opponent (two browsers, one or two computers):
      currently match is not established — opponent receives no notification
      and has no way to know they were challenged. Requires WebSocket + invite mechanic.
      Coordinate with teammate as part of Remote Players module
- [ ] Define disconnect behaviour in remote game:
      WS event handling, win for remaining player, UI feedback —
      coordinate with teammate
- [ ] Clarify lobby mode logic: which mode launches
      when opponent is selected vs not selected
- [ ] Surrender button: counts as a loss for current player,
      calls finishMatch() with opponent as winner.
      Decide whether it applies in training mode
- [ ] Lobby frontend: connect InviteMatchView, handle game_start → /game


### TODO
- [ ] Advanced analytics — win/loss charts, match history, heatmap (IV.8, 2pt)
- [ ] Lobby and profile page refactor — align with design system 
      (apiFetch, card classes, visual consistency across all pages)
- [ ] UX polish — consistent loading states, empty states, error messages
- [ ] Responsive design — test on mobile (375px), tablet (768px), desktop (1280px)
      Pages: login, register, lobby, profile, friends
      Expected issues: sidebar (needs hamburger or bottom nav),
      grids (grid-cols-2 → grid-cols-1 on mobile)
- [ ] Add seed-script to fill database for dashboard
- [ ] reaction_time_ms in MatchEchoViz always null — logic not implemented in GameView
- [ ] pos_y used in forceY but data may be null — default 0.5
- [ ] MatchEchoViz: profile fetched inside component — can be moved to parent as currentUserId prop

     
### Lobby (current priority)
- [ ] Remote tab: Challenge button → POST /api/game/match/invite/ → waiting screen
- [ ] Listen to WS event game_start → redirect /game?match_id=42&role=player1
- [ ] Opponent online status via WebSocket (currently static)

---

## Decisions already made (not up for debate)

| Decision | Reason |
|---|---|
| Django over Node | Fast start, built-in ORM, less boilerplate |
| Vue over React | Easier for a beginner, same concepts |
| usePolling in vite.config.js | HMR doesn't work on /mnt/c/ in WSL — polling as workaround |
| Named volume for Postgres | WSL doesn't allow bind mount permissions |
| PostgreSQL | Reliability, support for complex analytics queries |
| WebSocket inside backend | Team decided not to separate — easier for newcomers, Django Channels embeds into existing service |
| Online presence via WebSocket | Vue only renders; status stored in DB, transport — WS Gateway |
| No custom Session model | JWT doesn't need sessions. django.contrib.sessions kept for Admin only. No custom model. |
| frontend volumes in docker-compose | Without bind mount the container uses image files from build time. Required: ./frontend:/app + /app/node_modules |
| username in create_user = email | AbstractUser has username field with unique constraint. Set username=email via extra_fields.setdefault() to avoid IntegrityError on second registration |
| Daphne instead of runserver | Django Channels requires an ASGI server. Replaces manage.py runserver because standard runserver uses WSGI and does not support WebSockets |