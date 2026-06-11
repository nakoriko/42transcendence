# TEAM_CONTEXT.md — Transcend (ft_transcendence)

> Updated as the project progresses. For current status — contact Tech Lead.

---

## Project

**Name:** Transcend
**What it is:** Pong with remote two-player matches, tournaments, AI opponent, chat, and friends.
**Differentiator:** Post-match analytics — heatmaps, reaction time trends, comparison with friends.
**School:** 42, final Common Core project (ft_transcendence)
**Deadline:** June 9 – July 9, 2026

---

## Team

| Role | Who |
|---|---|
| Tech Lead / PO / Backend + Frontend | Natalia |
| Real-time & Multiplayer Developer | Sabino |
| Expected (+2 people) | TBC |

**Principle:** each module is isolated. Take one service — don't touch the rest.

---

## Ownership zones

```
┌─────────────────────────────────────────────────────────┐
│               ZONE 1 — FOUNDATION ✅ DONE                │
│                                                          │
│  Docker + structure   Auth system   DB schema            │
│  Privacy Policy + ToS   Pong game   User management      │
│                                                          │
│  Touch only with Tech Lead approval.                     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  ZONE 2 — IN PROGRESS                    │
│                                                          │
│  Analytics — Natalia       Design system — Natalia       │
│  WebSockets — Sabino       Remote players — Sabino       │
│                                                          │
│  API contract designed by Tech Lead. Implementation —    │
│  each person works in their own folder.                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           ZONE 3 — AVAILABLE FOR THE TEAM                │
│                                                          │
│  Tournament   OAuth   2FA   PWA   Multiple languages     │
│  AI Opponent  Gamification  File upload  Spectator mode  │
│                                                          │
│  Isolated modules. Take one — build it — deliver it.     │
└─────────────────────────────────────────────────────────┘
```

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3 + Tailwind CSS |
| Backend | Django + Django REST Framework |
| Database | PostgreSQL |
| Real-time | Django Channels (WebSockets) |
| Deploy | Docker Compose |
| Auth | JWT (djangorestframework-simplejwt) |
| Cache / broker | Redis |
| Proxy | nginx (HTTPS) |

---

## Modules — owners and status

### Natalia

| Module | Type | Pts | Status |
|---|---|---|---|
| IV.1 Framework frontend + backend (Vue + Django) | Major | 2 | ✅ done |
| IV.1 ORM (Django ORM) | Minor | 1 | ✅ done |
| IV.3 Standard User management (profile, avatar, friends) | Major | 2 | ✅ done |
| IV.6 Web-based game Pong | Major | 2 | ✅⚠️ needs fixes |
| IV.1 Custom design system (10+ components) | Minor | 1 | ✅ in progress |
| IV.1 User Interaction (chat + profile + friends) | Major | 2 | 🔄 chat waiting for WebSocket |
| IV.3 User activity dashboard (history, leaderboard) | Minor | 1 | 🔄 in progress |
| IV.8 Advanced analytics (heatmap, charts) | Major | 2 | 🔄 in progress |

**Natalia total: 13 pts**

### Sabino

| Module | Type | Pts | Status |
|---|---|---|---|
| IV.1 WebSockets (Django Channels) | Major | 2 | 🔄 in progress |
| IV.6 Remote players | Major | 2 | 🔄 in progress |

**Sabino total: 4 pts**

### Available for the team (if they join) or Sabino, if he has time

| Module | Type | Pts |
|---|---|---|
| IV.4 AI Opponent | Major | 2 |
| IV.6 Tournament system | Minor | 1 |
| IV.6 Game customization | Minor | 1 |
| IV.3 OAuth | Minor | 1 |
| IV.3 2FA | Minor | 1 |
| IV.1 PWA | Minor | 1 |
| IV.2 Multiple languages | Minor | 1 |
| IV.6 Spectator mode | Minor | 1 |
| IV.6 Gamification | Minor | 1 |
| IV.1 File upload | Minor | 1 |

---

**Total: 17 pts**

---

## Architecture

```
transcend/
├── docker-compose.yml
├── .env.example
├── frontend/          # Vue 3 — separate container
├── backend/           # Django + Django Channels — separate container
├── redis/             # Redis — separate container (WebSocket broker)
├── db/                # PostgreSQL
├── nginx/             # HTTPS, reverse proxy
└── TEAM_CONTEXT.md
```

**Important:**
- Django Channels (WebSocket) is embedded in the backend container, not a separate service.
- Redis is a separate container, broker for WebSocket connections.
- Online presence (online status) is transmitted via WebSocket, not REST polling.

---

## DB schema (core models)

| Model | Fields | App |
|---|---|---|
| User | nickname, email, avatar, wins, losses, is_online | users/ |
| Match | player1, player2, score_player1, score_player2, winner, started_at, ended_at | game/ |
| MatchEvent | match, event_type, player, pos_x, pos_y, reaction_time_ms, timestamp | game/ |
| FriendRelation | from_user, to_user, status, created_at | users/ |

---

## API endpoints (implemented)

| Method | URL | Description |
|---|---|---|
| POST | /api/users/register/ | Registration |
| POST | /api/users/login/ | Login → access + refresh tokens |
| POST | /api/users/logout/ | Logout |
| GET | /api/users/profile/ | Current user profile (JWT) |
| PATCH | /api/users/profile/ | Update nickname, email — **TODO** |
| PATCH | /api/users/avatar/ | Upload avatar |
| GET | /api/users/list/ | User list (lobby) |
| GET | /api/users/friends/ | Friends list + requests |
| POST | /api/users/friends/request/ | Send friend request |
| PATCH/DELETE | /api/users/friends/<pk>/ | Accept / reject / remove |
| POST | /api/game/match/start/ | Start a match |
| POST | /api/game/match/events/ | Log match events |
| PATCH | /api/game/match/<match_id>/finish/ | Finish a match |

---

## What already works

- `docker-compose up` brings up all services with one command
- HTTPS locally (self-signed certificate)
- Registration, login, JWT auth
- Protected routes (frontend + backend)
- Pong: game loop on canvas, local multiplayer, match result saved to DB
- Every hit and ball position logged to MatchEvent (data for analytics)
- User profile, avatar upload
- Friends list, incoming/outgoing requests
- Privacy Policy and Terms of Service pages

---

## Decisions already made (not up for debate)

| Decision | Reason |
|---|---|
| Django over Node | Built-in ORM, fast start |
| Vue over React | Easier for the team |
| WebSocket inside backend container | Easier onboarding, Django Channels embeds into Django |
| Online presence via WebSocket | Status stored in DB, transport — WS |
| JWT for auth | Token-based auth, no custom session model. Django's built-in sessions kept for Admin only |
| PostgreSQL | Reliability, support for complex analytics queries |
| Redis as separate container | Broker isolation, standard practice with Django Channels |