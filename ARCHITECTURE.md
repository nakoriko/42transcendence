# Project Architecture — ft_transcendence (Transcend)

mandatory disclaimer goes here

## 1. About the project
 
**Transcend** — a Pong platform with chat, a friends system, and match analytics.

## 2. Docker containers
 
```
┌─────────────────────────────────────────────────────────────┐
│                          nginx :443/:80                      │
│              reverse proxy + HTTPS + static files            │
└──────────┬──────────────────────────────┬────────────────────┘
           │                              │
    ┌──────▼──────┐                ┌──────▼──────┐
    │  frontend   │                │   backend   │
    │  Vue + Vite │                │   Django    │
    │  :5173      │                │  Daphne     │
    └─────────────┘                │  :8000      │
                                   └──────┬──────┘
                                          │
                          ┌───────────────┴────────────────┐
                          │                                │
                   ┌──────▼──────┐                 ┌──────▼──────┐
                   │     db      │                 │    redis    │
                   │ PostgreSQL  │                 │   :6379     │
                   │  :5432      │                 │  WS broker  │
                   └─────────────┘                 └─────────────┘
```
 
| Container  | Image / Build         | Purpose                                 | 
|------------|-----------------------|-----------------------------------------|----------------|
| `nginx`    | `nginx:alpine`        | HTTPS, reverse proxy, ports 80/443      | 
| `frontend` | `./frontend`          | Vue SPA, Vite HMR                       | 
| `backend`  | `./backend`           | Django API + Django Channels (WS)       | 
| `db`       | `postgres:15`         | Database, named volume                  | 
| `redis`    | `redis:7`             | Message broker for WebSocket            | 
| `websocket`| `./websocket`         | Separate WS container                   | 

> **Note:** WebSocket (Django Channels) was embedded in the `backend` container. The separate `websocket` container is commented out in docker-compose.yml — a team decision, to keep onboarding simple.

## 3. Repository structure
 
```
transcend/
│
├── docker-compose.yml
├── .env.example
├── README.md
│
├── frontend/                    # Vue 
│   └── src/
│       ├── views/               # Page screens
│       ├── components/          # Reusable components
│       │   └── chat/            # Chat components (ChatContactList, ChatWindow) 
│       │   ├── dashboard/       # Dashboard components
│       │   ├── game/            # Game components
│       │   ├── lobby/           # Lobby components
│       │   ├── profile/         # Profile components
│       └── App*.vue             # Auxiliary reusable components
│       ├── stores/              # Pinia (user.js, chat.js, presence.js)
│       ├── services/            # wsService.js — singleton WebSocket client
│       ├── composables/         # useResizeObserver.js (used in DashRallyTimeline)
│       ├── router/              # Vue Router
│       └── utils/               # Helpers (apiFetch, stats, date, period)
│
├── backend/                     # Django + DRF
│   ├── core/                    # settings, urls, asgi
│   ├── users/                   # Auth, User, Friends
│   ├── game/                    # Match, MatchEvent
│   ├── analytics/               # Analytics with its own views
│   ├── chat/                    # Chat (skeleton)
│   ├── ws/                      # WebSocket consumers. auth+presence+chat
│   ├── tournament/              # Tournaments (skeleton)
│   ├── tournament/              # Tournaments (skeleton)
│   └── db.sqlite3/              # legacy artifact, in .gitignore, not used
│
├── db/                          # init.sql
├── nginx/                       # nginx.conf + TLS certificates
├── websocket/                   # Dockerfile (commented out)
└── help/                        # Supplementary documentation
```
 
---

## 4. nginx/

**File:** `nginx/nginx.conf` | **Image:** `nginx:alpine`

### Routing

```
Browser
  │
  ├─ HTTP :80  → 301 redirect → HTTPS :443
  │
  └─ HTTPS :443 (self-signed cert)
       │
       ├─ /        → http://frontend:5173   (Vite dev server, HMR via WebSocket upgrade)
       ├─ /api/    → http://backend:8000    (Django REST API, X-Real-IP forwarded)
       ├─ /media/  → http://backend:8000    (avatars and other uploaded files)
       ├─ /admin/  → http://backend:8000    (Django Admin, X-Real-IP forwarded)
       └─ /ws/     → http://backend:8000    (WebSocket, upgrade headers)
```

### Config blocks

| Location | Upstream | Notes |
|---|---|---|
| `/` | `frontend:5173` | `proxy_set_header Upgrade $http_upgrade` — for Vite HMR |
| `/api/` | `backend:8000` | `X-Real-IP` → Django sees the real browser IP |
| `/media/` | `backend:8000` | serves uploaded files (avatars), Django serves them via `MEDIA_URL`/`MEDIA_ROOT` when `DEBUG=True` |
| `/admin/` | `backend:8000` | same as `/api/` |
| `/ws/` | `backend:8000` | WebSocket upgrade — for Django Channels |

### SSL

```
Certificate: /etc/nginx/certs/selfsigned.crt  (self-signed, 365 days)
Key:         /etc/nginx/certs/selfsigned.key
```

---

## 5. Backend

| Technology | Role |
|---|---|
| Django | Web framework |
| Django REST Framework | REST API |
| Django Channels | WebSocket support |
| Daphne | ASGI server (instead of runserver) |
| SimpleJWT | JWT authentication |
| PostgreSQL (Django ORM) | Database |


**Modules:**
| App | Status |
|---|---|
| users — Auth, profile, friends | ✅ working |
| game — matches, match events | ✅ working |
| analytics — analytics | ✅ working |
| chat — chat | ✅ working (via WebSocket) |
| ws — WebSocket consumers | ✅ working |
| tournament — tournaments | ⬜ out of scope |
 
**API:** `/api/users/` — registration, login, JWT refresh, profile, friends
`/api/game/` — create/invite a match, events, history, finish a match
 
> ⚠️ `DEBUG=True`, `ALLOWED_HOSTS=[]` — deliberately left unaddressed before submission.


---

## 6. API endpoints

### Auth & Users (`/api/users/`)
| Method | URL | Description | Access |
|---|---|---|---|
| POST | `/register/` | Registration | public |
| POST | `/login/` | Login, returns JWT | public |
| POST | `/logout/` | Logout | 🔒 |
| POST | `/token/refresh/` | Refresh access token | public |
| GET/PATCH | `/profile/` | Own profile | 🔒 |
| PATCH | `/avatar/` | Avatar upload | 🔒 |
| GET | `/list/` | List of all users | 🔒 |
| GET | `/<pk>/` | Public profile | 🔒 |
| GET | `/friends/` | Friends list + requests | 🔒 |
| POST | `/friends/request/` | Send a request | 🔒 |
| PATCH/DELETE | `/friends/<pk>/` | Accept/remove a friend | 🔒 |

### Game (`/api/game/`)
| Method | URL | Description | Access |
|---|---|---|---|
| POST | `/matches/start/` | Create a LOCAL match | 🔒 |
| POST | `/matches/invite/` | Create a REMOTE match | 🔒 |
| PATCH | `/matches/<id>/status/` | Update match status | 🔒 |
| PATCH | `/matches/<id>/finish/` | Finish a match | 🔒 |
| GET | `/matches/` | Match history (?limit=N) | 🔒 |
| POST | `/matches/events/` | Record an event | 🔒 |
| POST | `/matches/events/bulk/` | Bulk event recording | 🔒 |
| GET | `/matches/<id>/events/` | Events of a specific match | 🔒 |
| GET | `/events/` | All events of a user | 🔒 |

### Analytics (`/api/analytics/`)
| Method | URL | Description | Access |
|---|---|---|---|
| GET | `/universe/` | Global statistics (?period=7d/30d/all) | 🔒 |
| GET | `/player-stats/` | Player statistics (?period=) | 🔒 |

---

## 7. Frontend
 
### Stack
| Technology | Role |
|---|---|
| Vue 3 (Composition API) | UI framework |
| Vite | Build + HMR (`usePolling` for WSL) |
| Tailwind CSS | Styling |
| Pinia | Global state |
| Vue Router 4 | Navigation + route guards |
| D3.js | Dashboard visualizations |


### Stack

| Technology | Role |
|---|---|
| Vue 3 (Composition API) | UI framework |
| Vite | Build + HMR (for wsl) |
| Tailwind CSS | Styling |
| Pinia | Global state |
| Vue Router | Navigation + route guards |
| D3.js | Dashboard visualizations |
| lucide-vue-next | Icons |
| jsPDF + html2canvas-pro | Dashboard/analytics export to PDF |

### Skeleton files (src/)
 
| File | What it does |
|---|---|
| `main.js` | Entry point: `createPinia()` → `createRouter()` → `app.mount()` |
| `App.vue` | Root component: layout, sidebar, logout, friend requests |
| `style.css` | Global styles: `.card`, `.badge-win/loss`, `.online-dot`, `.scroll-thin` |


### Skeleton files (src/)

| File | What it does |
|---|---|
| `main.js` | Entry point: Pinia initialization → router connection → `app.mount('#app')` |
| `App.vue` | Root component: layout, responsive sidebar (`sidebarMode`, `mobileMenuOpen`), logout, friend requests |
| `style.css` | Global styles: `.card`, `.card-label`, `.badge-win/loss`, `.online-dot`, `.scroll-thin` |

### App.vue
  
**State:** `isLoggedIn`, `user` — computed from `userStore`; `incomingRequests[]`
 
**Logic:**
- `loadIncoming()` — GET `/api/users/friends/`, called on mount (if logged in) and on every `watch(route)`
- `logout()` — `userStore.logout()`, resets `incomingRequests`, redirects to `/login`
- `acceptRequest(id)` / `declineRequest(id)` — PATCH `/api/users/friends/{id}/` + `CustomEvent('friends-updated')` + repeated `loadIncoming()`
- `chatStore` is wired in — the `:has-unread-messages="chatStore.hasUnread"` prop on `<AppSidebar>`, an unread indicator on the "Chat" item
> The single source of truth for the user is `userStore`. `App.vue` doesn't keep its own copy, it only reads via computed.
 
**Known limitation:** `incomingRequests` is only refreshed on route change, not in real time over WS — a subscription to the `friends-updated` event over WebSocket is prepared in the code but commented out (depends on the `friend_request_received` implementation on the backend).

---

### GameView.vue

Canvas Pong (800×600). Ball vx=4/vy=3 r=12, paddles 15×80px speed=5 (W/S and ↑/↓). Win at 5 points.

`initMatch()`: user → player1, GET opponent profile → player2, POST `/matches/start/` → matchId.

Events (hit/miss/goal) accumulate in memory → bulk POST `/matches/events/bulk/` on finish or when leaving the page.

Leaving early (`onBeforeRouteLeave`) = a forfeit for the player who leaves, the score isn't counted (a deliberate decision).

---

### views/ProfileView.vue

**State:** `user`, `matches[]`, `activeFilter` ('all'/'wins'/'losses'), `error`

**Computed:** `filteredMatches` — filters `matches` by `result` depending on `activeFilter`

**Loading:** `Promise.all([loadProfile(), loadMatches()])` on mount
- `loadProfile()` — GET `/api/users/profile/`
- `loadMatches()` — GET `/api/game/matches/?limit=5`

**Template:**
- Top block: `ProfileInfoCard` (nickname/email/avatar) + `ProfileStatsCard` (wins/losses)
- Below, a 2-column grid: `RecentMatchesList` (with filters) | `ProfileFriendsBlock`

---

### views/DashboardView.vue

**State:** `matches[]` (entire history, `?limit=200`), `lastEvents[]` (all events of all matches), `activeMatchId`

**Loading on mount:**
```javascript
Promise.all([
    GET /api/game/matches/?limit=200   → matches[]
    GET /api/game/events/              → lastEvents
])
```

**Coordination between components:**
```
DashRallyTimeline ──emit('matchSelected', id)──► DashboardView.onMatchSelected()
                                                         │
                                                  activeMatchId.value = id
                                                         │
                                              DashMatchHistory (:activeMatchId)
                                                  → highlights the relevant match
```

**PDF export:** `exportToPdf()` — expands scrollable lists, captures 3 sections (`DashPlayerStats+DashRallyTimeline`, `DashUniverse`, `DashMatchHistory`) via `html2canvas-pro`, assembles a multi-page PDF via `jsPDF` (one page per section), saves it as `dashboard-analytics.pdf`

**Online status:** the `"N online"` badge in the header — data from `presenceStore` (`usePresenceStore`)

**Template:** 3 sections:
```
1. DashPlayerStats + DashRallyTimeline  — 2-column grid; clicking the rally timeline → changes activeMatchId
2. DashUniverse                          — global leaderboard
3. DashMatchHistory                      — list of matches (contains MatchEchoViz for match events)
```

---

### router/index.js

| Route | Component | Guard |
|---|---|---|
| `/` | — | redirect → `/login` |
| `/:pathMatch(.*)*` | — | redirect → `/login` |
| `/privacy` | `PrivacyPolicy` | public |
| `/terms` | `TermsOfService` | public |
| `/login` | `LoginView` | `guestOnly` — if a token exists → `/profile` |
| `/register` | `RegisterView` | `guestOnly` |
| `/lobby` | `LobbyView` | `requiresAuth` |
| `/game` | `GameView` | `requiresAuth` + `requiresGame` |
| `/game/remote` | `RemoteGameView` | `requiresAuth` + `requiresGame` |
| `/profile` | `ProfileView` | `requiresAuth` |
| `/dashboard` | `DashboardView` | `requiresAuth` |
| `/chat` | `ChatView` | `requiresAuth` |
| `/friends` | — | route commented out, import missing |

**beforeEach:**
```
token = localStorage.getItem('access')
requiresAuth && !token         → /login
requiresGame && !query.player2 → /lobby
guestOnly && token             → /profile
requiresAuth && token          → await userStore.fetchUser() + wsService.connect(token)
```

---

### utils/apiFetch.js

```
apiFetch(url, options)
  ├─ no token → redirect to /login
  ├─ token about to expire → proactive refresh before the request
  ├─ fetch with Authorization: Bearer <token>
  └─ 401 → refresh + retry the request, failure → redirect to /login
```
Parallel calls made while the token is stale share a single common refresh request (no race on token rotation). Doesn't work with FormData (hard-codes `Content-Type: application/json`).

### utils/stats.js
```javascript
calcWinRate(wins, losses)      // → 0..100
calcTotalMatches(wins, losses) // → wins + losses
```

### utils/date.js
```javascript
formatShortDate(isoString)   // → "5 Jul"
```

### utils/period.js
```javascript
filterByPeriod(items, dateField, period) // 'All' | '7d' | '30d'
```

---

### stores/ (Pinia)

**user.js** — `currentUser {id, nickname, avatar}`. `fetchUser()`, `login()` (stores tokens, connects WS), `logout()` (clears tokens, disconnects WS), `refreshUser()`.

**chat.js** — `messages {peerId: [...]}`, `activeContactId`, `unreadPeers {peerId: true}`. `sendMessage()`, `receiveMessage()`, `receiveError()`. `hasUnread` — whether there are unread messages.
> ⚠️ A sent message isn't rolled back on error/network drop. Not a bug, the subject requires a minimally working chat. 

**presence.js** — `onlineCount`, `online {userId: boolean}`. `setCount()`, `setStatus()`. Populated from `wsService.js` via the `presence_update` event.


---

### components/ — Design System and other components

#### Design system (App*)

| Component | Props | What it does | Notes |
|---|---|---|---|
| `AppAvatar` | nickname, isOnline, size (sm/md/lg) | Initial + color by charCode + online-dot | - |
| `AppBadge` | label, variant (teal/coral/sage) | Pill with a colored background | — |
| `AppButton` | variant (primary/large/cta/compact/ghost) | Button with rounded-pill | slot for content |
| `AppCard` | — | Wrapper: bg-navy-800, border, p-10 | template only, no script |
| `AppFilterTabs` | modelValue, options[] | v-model tab switcher | reused everywhere |
| `AppInput` | label, type, placeholder, autocomplete | Styled input with focus | `defineModel()` |
| `AppLogo` | — | "PONG" — 4 letters in circles | - |
| `AppMetric` | value (String), label, color | Large number + label | colorMap for text-* |
| `AppSidebar` | user, incomingRequests[], hasUnreadMessages | Navigation + friend requests + logout + unread-messages dot on "Chat" | - |
| `AppTooltip` | — | Absolute tooltip | `defineExpose: show(x,y) / hide()` |

#### Game components

| Component | Props | What it does |
|---|---|---|
| `GameModeCard` | title, selected, disabled | Mode pill button; disabled → opacity-40 |
| `GameControls` | — | Shows W/S and ↑/↓ controls |
| `GameScoreBoard` | p1, p2, name1, name2 | Score of two players |
| `game/ArrowsBadge` | label | Styled key badge |

#### Profile and matches

| Component | Props / Emits | What it does | Notes |
|---|---|---|---|
| `PlayCard` | user, selected → emit('select') | Card: avatar + nickname + matches + winRate | Lobby + ProfileFriendsBlock |
| `RecentMatchesList` | matches[], activeFilter, selectedMatchId, showScore → emit('filter-change', 'match-click') | List of matches with filters and highlighting | Profile + DashMatchHistory |
| `ProfileAvatar` | user, canUpload → emit('upload') | Avatar: img or initial + hover upload |  |
| `ProfileStatsCard` | wins, losses | 3 cards: Wins / Losses / Win Rate | uses `calcWinRate` |

#### Other components

**Dashboard — visualizations (D3 + Canvas)**
- `DashRallyTimeline` — canvas chart of rallies across all matches, click → select a match
- `DashUniverse` — D3 global player leaderboard by activity
- `MatchEchoViz` — D3 force-graph of match events (goals/hits/misses)
- `DashMatchHistory` — list of matches, synced with MatchEchoViz
- `DashPlayerStats` — D3 area chart of statistics (wins/losses) by period

**Auth & Lobby**
- `LoginView` / `RegisterView` — form + call to `userStore.login()` / register via the API
- `LobbyView` — opponent and mode selection (local/remote), matchmaking

**Friends and profile**
- `ProfileFriendsBlock` — friends list, requests, user search
- `ProfileInfoCard` — profile and avatar editing
- `LobbyVsRow` — "me vs opponent" display in the lobby

---

## 8. backend/ws/ — WebSocket (Presence + Chat)

### What it is and why

Several parts of the app need the server to **push** updates to the browser
without being asked — a friend coming online, an incoming friend request, a chat
message arriving, a match result being saved. Plain HTTP request/response can't do
this: the client would have to keep polling the server over and over to find out
if anything changed. **WebSockets** solve this by keeping a persistent, two-way
connection open between browser and server, so the server can send data the
moment something happens.

This module covers the Major feature from the subject:



- **IV.1 — Implement real-time features using WebSockets or similar technology**: real-time transport layer,
  authentication over the socket, and its main use cases — presence, direct
  messaging, and live notifications (friend requests, match results).

### Why Django Channels + Redis

Django's default server (`runserver`) speaks WSGI, which is request/response
only — it cannot keep a connection open. **Django Channels** extends Django to
support the ASGI protocol, which does support long-lived connections like
WebSockets. Because of this, the backend runs on **Daphne** (an ASGI server)
instead of `runserver`.

A single Django process can hold many open WebSocket connections, but by default
they can't talk to each other (e.g. one user's connection can't directly message
another user's connection). **Redis** is used as the *channel layer*: a broker
that lets different WebSocket connections — even across different backend
workers/processes — send messages to each other via named "groups". Every
connected user is added to a personal group (`user_<id>`), so the server can
target a message at exactly one user instead of broadcasting to everyone.

### Authentication

The frontend already has JWT auth (`djangorestframework-simplejwt`) for REST
calls. The same access token is reused for the socket instead of creating a
separate auth system: after connecting, the client's **first message** must be
`{ "type": "auth", "token": "<access token>" }`. The server verifies it with
`AccessToken(...)`, looks up the user, and closes the connection if no valid
token arrives within 5 seconds. This keeps auth logic in one place and avoids
introducing a second credential type just for WebSockets.

### Online presence

On successful auth the user is added to a `global_presence` group and their
`is_online` flag is set to `True` in the DB; on disconnect it's set back to
`False`. This is what powers the online/offline indicator in the lobby and
friends list, in real time, without polling.

A Redis counter (`ws_conn_count:<user_id>`) tracks how many connections a user
has open at once, so opening the app in two tabs (or two devices) doesn't
incorrectly mark the user offline when just one tab closes — the flag only flips
when the *last* connection drops. An online-user count is also broadcast to the
`global_presence` group whenever it changes.

### Direct messaging (chat)

`handle_chat_message` / `chat_message_event` let two friends exchange messages in
real time over the same authenticated connection, targeted via the recipient's
personal group (`user_<id>`). Before delivering a message, the server checks:

- the message isn't empty,
- the recipient exists,
- the two users are actually friends (`FriendRelation`, status `accepted`),
- the recipient is currently online.

If any check fails, the sender gets a `chat_error` back with a reason
(`invalid_message`, `user_not_found`, `not_friends`, `user_offline`) instead of
the message silently disappearing.

### Live notifications

The same personal-group mechanism is reused for other real-time notifications so
the frontend doesn't need to poll the REST API for updates:

- **Friend requests** — `friend_request_event` / `friend_request_accepted_event`
  notify a user instantly when they receive or when someone accepts a friend
  request.
- **Match results** — `match_finished_event` pushes the final score and winner
  of a match to the relevant users as soon as it's saved, so match history /
  dashboards can update live instead of requiring a page refresh.

### Message dispatcher

Incoming authenticated messages are routed through a `handlers` dict
(`message type → method`) inside `receive()`, rather than a long `if/elif`
chain. This keeps `consumers.py` easy to extend — adding a new event type is
just one new entry plus one new handler method.

### Remote play — started, then discontinued

Early work also went into an invite → accept → match-start flow
(`game_invite`, `game_accept`, `game_start`, plus a `match_<id>` group and a
`player_input` handler) with the intent of eventually syncing full Pong
gameplay (ball/paddle physics) between two separate browsers in real time.

**Due to time constraints, the team (Sabino + Natalia) decided not to pursue
full remote gameplay.** The server-authoritative game loop needed for synced
physics was never built, so this part was not carried through to a finished
feature. It's mentioned here only for transparency about work that was
attempted; it is **not** part of the delivered feature set.

### Current status

- ✅ WebSocket connection + JWT authentication
- ✅ Online presence (is_online, multi-connection safe via Redis counter)
- ✅ Personal groups per user
- ✅ Real-time chat between friends
- ✅ Real-time friend-request notifications
- ✅ Real-time match-result notifications
- ❌ Remote gameplay sync (started, not completed — see note above)

### Resources used

- https://channels.readthedocs.io/en/stable/tutorial/part_1.html (main source to study how to add WebSocket to Django with ASGI and asyncronous consumers)
- https://github.com/django/channels_redis/ (documents Redis backend used by Django Channels fopr channel layer)
- https://redis.io/docs/latest/develop/get-started/ (Redis quick start guide)
- https://redis.io/docs/latest/develop/pubsub/ (explains Redis role as messages/pub-sub system in real time)


**AI usage:** AI (Claude) was used for study support and documentation —
specifically to help understand WebSocket/Django Channels concepts while
learning them, and to help draft/organize this section of the README.


### Individual contribution — Sabino

- Designed and implemented the `ws` Django app (WebSocket layer):
  connection handling, JWT authentication over the socket, online presence.
- Implemented real-time chat between friends, with validation (friendship
  check, online check) before delivery.
- Wired up real-time notifications for friend requests and match results via
  personal user groups.
- Set up Redis as the Channels layer and multi-connection-safe presence
  tracking.
---