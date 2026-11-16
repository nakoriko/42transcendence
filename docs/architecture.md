# Architecture — Transcend (ft_transcendence)

How the project is put together: containers, request routing, backend apps and API, frontend structure and the main data flows. The WebSocket layer has its own document: [`websockets.md`](./websockets.md). Database tables and relations: [`db-schema.md`](./db-schema.md).

## 1. Containers

```
                 browser
                    │  https://localhost:5001
┌───────────────────▼──────────────────────────────┐
│ nginx  (TLS, self-signed certificate)            │
│  /         → frontend                            │
│  /api/  /admin/  /ws/  → backend                 │
│  /media/  /static/     → served from volumes     │
└───────┬──────────────────────────┬───────────────┘
        │                          │
┌───────▼────────┐        ┌────────▼─────────────────────┐
│ frontend       │        │ backend                      │
│ Vue 3 + Vite   │        │ Django + DRF + Channels      │
│ dev server     │        │ gunicorn, 3 uvicorn workers  │
│ :5173          │        │ :8000                        │
└────────────────┘        └───────┬──────────────┬───────┘
                                  │              │
                          ┌───────▼──────┐ ┌─────▼────────┐
                          │ db           │ │ redis        │
                          │ PostgreSQL 15│ │ channel layer│
                          └──────────────┘ └──────────────┘
```

| Container | Build / image | Purpose |
|---|---|---|
| `nginx` | `./nginx` (nginx:alpine, generates the certificate at build time) | HTTPS entry point on port 5001, HTTP on 5000 redirects to HTTPS |
| `frontend` | `./frontend` (node:20-alpine) | Vite dev server with hot reload |
| `backend` | `./backend` (python:3.11-slim) | REST API and WebSocket. On start: `migrate`, `collectstatic`, `reset_presence`, then gunicorn with uvicorn workers |
| `db` | `postgres:15` | Database, data in the `postgres_data` volume |
| `redis` | `redis:7` | Channel layer for Django Channels and per-user connection counters |

Several uvicorn workers handle requests in parallel. Because a WebSocket connection lives in one worker, messages between users go through Redis (see [`websockets.md`](./websockets.md)).

## 2. Repository structure

```
.
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml   # ruff + backend tests, frontend tests + build
├── nginx/                     # Dockerfile, nginx.conf
├── docs/                      # this file, db-schema.md, websockets.md
├── backend/
│   ├── core/                  # settings, root urls, asgi
│   ├── users/                 # User model, auth, profile, avatars, friends
│   ├── game/                  # Match, MatchEvent, match API, demo data commands
│   ├── analytics/             # dashboard endpoints (player map, player graph)
│   └── ws/                    # WebSocket consumer, routing, notify_group helper
└── frontend/src/
    ├── views/                 # one component per page
    ├── components/            # App* design system + chat/ dashboard/ game/ lobby/ profile/
    ├── stores/                # Pinia: user, matches, chat, presence
    ├── services/wsService.js  # the single WebSocket connection
    ├── composables/           # usePresence, useResizeObserver
    ├── router/                # routes and auth guard
    └── utils/                 # apiFetch, stats, dates, periods, pdf, tooltips
```

## 3. Backend API

All endpoints except registration, login and token refresh require a JWT access token (`Authorization: Bearer <token>`).

### Users — `/api/users/`

| Method | URL | Description |
|---|---|---|
| POST | `register/` | Create an account |
| POST | `login/` | Email + password → access and refresh tokens |
| POST | `token/refresh/` | New access token from a refresh token |
| POST | `logout/` | Blacklist the refresh token |
| GET / PATCH | `profile/` | Own profile (includes `date_joined`) / edit nickname and email |
| PATCH | `avatar/` | Upload an avatar |
| GET | `list/` | All users with win/loss counters, for the lobby |
| GET | `<id>/` | Public data of one user |
| GET | `friends/` | Friends, incoming and outgoing requests |
| POST | `friends/request/` | Send a friend request |
| PATCH / DELETE | `friends/<id>/` | Accept or reject a request / remove a friend or cancel a request |

### Game — `/api/game/`

| Method | URL | Description |
|---|---|---|
| POST | `matches/start/` | Create a local match against `player2` |
| POST | `matches/events/bulk/` | Save the events of a match (hit / miss / goal) in one request |
| PATCH | `matches/<id>/finish/` | Save the score and winner, update win/loss counters |
| GET | `matches/` | Own finished matches, newest first (`?limit=`, max 200) |
| GET | `matches/<id>/events/` | Events of one match, for the rally timeline |

### Analytics — `/api/analytics/`

| Method | URL | Description |
|---|---|---|
| GET | `universe/` | All players with match counts and win rate (`?period=7d|30d|all`) |
| GET | `player-graph/` | The current player, their opponents and the opponents' opponents, with records and edges |

Real-time notifications (friend requests, match results) are sent from the views through `ws.notify.notify_group()`. A failure of the channel layer is logged and does not fail the request.

## 4. Frontend

### Pages

| Route | View | Access |
|---|---|---|
| `/login`, `/register` | `LoginView`, `RegisterView` | guests only |
| `/profile` | `ProfileView` — account data, W/L summary, friends with requests and search | logged in |
| `/lobby` | `LobbyView` — opponent picker, local mode (remote shown as "soon") | logged in |
| `/game?player2=<id>` | `GameView` — canvas Pong, first to 5 points | logged in |
| `/dashboard` | `DashboardView` — analytics | logged in |
| `/chat` | `ChatView` — direct messages with friends | logged in |
| `/privacy`, `/terms` | static pages | public |

Unknown routes redirect to `/login`. The router guard loads the current user and opens the WebSocket before any protected page.

### Data flows

**Requests and tokens.** Every API call goes through `utils/apiFetch.js`: it adds the access token, refreshes it shortly before it expires, retries once after a `401`, and sends the user to `/login` when the refresh token is no longer valid. Parallel calls share one refresh request.

**WebSocket.** `services/wsService.js` keeps one connection per tab and dispatches incoming messages by type: chat messages and errors go to the chat store, presence and online count to the presence store, friend request events fire a `friends-updated` browser event that the sidebar, profile and chat listen to.

**A match.** `GameView` creates the match (`matches/start/`), keeps events in memory during the game, and at the end sends them in one bulk request and finishes the match. Leaving the page through the app finishes the match as a loss for the player who leaves. The matches store is then invalidated, so the dashboard loads fresh data.

**Dashboard.** Blocks, top to bottom:

- `DashUniverse` — map of all players (`universe/`) with platform totals;
- `DashPlayerGraph` + `DashNodeInfo` — the player connection graph (`player-graph/`); hovering (or tapping on touch screens) a node shows that player's card, clicking it scrolls the match history to the latest match against that player;
- `DashKpiRow` — record, win rate and rank;
- `DashMatchHistory` — recent matches; a match expands into its rally timeline (`DashRallyTimeline`, events from `matches/<id>/events/`);
- `DashPlayerStats` — rolling win rate over the last 10 matches and match volume for 7 days / 30 days / all time.

The match list is loaded once into the `matches` store and shared by the blocks that need it. **Export PDF** renders each section with `html2canvas-pro` and assembles them with `jsPDF`.

### Stores

| Store | Holds |
|---|---|
| `user` | Current user; login, logout (revokes the refresh token, closes the WebSocket, clears the other stores) |
| `matches` | Own match history, loaded once and invalidated after a match |
| `chat` | Messages per contact, unread markers, last error |
| `presence` | Online status per user and the online count |

### Design system

Shared `App*` components in `components/`: `AppAvatar`, `AppBadge`, `AppButton`, `AppCard`, `AppFilterTabs`, `AppInput`, `AppLogo`, `AppMetric`, `AppPageHeader`, `AppSidebar`, `AppTooltip`, `AppTooltipRow`. Styling is Tailwind CSS with a small set of shared classes in `style.css`; charts use D3.js, the rally timeline is drawn on canvas.

## 5. Tests and CI

- Backend: Django test runner, `docker-compose exec backend python manage.py test`. Tests use an in-memory channel layer and mock Redis, so only PostgreSQL is needed.
- Frontend: Vitest + Vue Test Utils, `docker-compose exec frontend npm test`.
- GitHub Actions (`.github/workflows/ci.yml`) runs `ruff`, the backend tests on PostgreSQL, the frontend tests and the production build on every push.
