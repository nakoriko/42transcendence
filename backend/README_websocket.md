# WebSocket Module — ft_transcendence

## Before you start — read this (2–3 hours)

1. **What is WebSocket** — https://javascript.info/websocket (first page only)
2. **Django apps** — https://docs.djangoproject.com/en/5.0/intro/tutorial01/ (up to "Creating the Polls app" only)
3. **Django Channels** — https://channels.readthedocs.io/en/latest/tutorial/part_1.html (tutorial part 1)

After this the README will make sense.

---

## What it is and why

Your task is to add real-time communication to the game.
Right now two players play on the same computer. Your module will let them play from different devices.

**How to know the work is done:**
You open two browsers in different tabs → log in as different users → start a match → the paddle moves in both windows at the same time.

---

## Stack

| What | Technology |
|---|---|
| Backend | Django + Django Channels |
| Message broker | Redis (already running) |
| Frontend | Vue (not your zone) |

---

## Project architecture

```
transcend/
├── docker-compose.yml      ← don't touch
├── .env                    ← don't touch
├── frontend/               ← don't touch
├── backend/                ← your zone
│   ├── core/               ← only add lines to settings.py and asgi.py
│   ├── api/                ← don't touch
│   ├── game/               ← you can read this to understand the game logic
│   └── ws/                 ← your folder (create with the command below)
├── nginx/                  ← don't touch (already configured for /ws/)
└── redis/                  ← don't touch
```

**Rule:** in other people's files you only add lines — never delete or modify existing ones.

---

## How to run locally

### 1. Clone the repo
```bash
git clone https://github.com/nakoriko/42transcendence.git
```

### 2. Create .env from the example
```bash
cp .env.example .env
```

### 3. Start everything
```bash
docker-compose up --build
```

### 4. Verify it works
- Site: https://localhost (accept the self-signed certificate)
- API: https://localhost/api/hello/
- Django Admin: https://localhost/admin/ (useful for tracking DB changes)

---

## What is already set up for you

- ✅ Redis running in docker-compose as service `redis` on port `6379`
- ✅ nginx proxies `/ws/` to backend (already configured)
- ✅ `channels` and `channels-redis` added to `requirements.txt`
- ✅ `REDIS_URL=redis://redis:6379` in `.env`
- ✅ DB models: `User`, `Match`, `MatchEvent`, `FriendRelation` already exist in `game/models.py`

---

## Backend setup (done once)

### 1. Create your app

In Django, `core/` is the skeleton. An app is an isolated block of logic in its own folder. We already have `api/` and `game/`. Yours will be called `ws/`.

```bash
docker-compose exec backend python manage.py startapp ws
```

This creates `backend/ws/` with the right structure. Write all your code there.

### 2. In `core/settings.py` — add only:

```python
INSTALLED_APPS = [
    ...
    'channels',   # add
    'ws',         # add — your app (isolated block of logic)
]

ASGI_APPLICATION = 'core.asgi.application'   # ASGI protocol for WebSocket. Base asgi.py already exists — extend it

# Redis as broker between WebSocket connections
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}
```

### 3. In `core/asgi.py` — replace the default with Channels routing

---

## Phase 1 — WebSocket

**What you implement:**
- WebSocket connection between browser and server
- Player online status (who is currently online)

**Done when:** echo server works, `/ws/` responds, online status is visible in the lobby.

### First task (2–4 hours)

Build an echo server — a WebSocket that receives any message and sends it back. This verifies the entire infrastructure works.

Test it in the browser console:
```javascript
const ws = new WebSocket('wss://localhost/ws/test/');
ws.onmessage = (e) => console.log(e.data);
ws.send('hello');
// should return 'hello'
```

### API contract — Phase 1

> Numbers below are format examples, not real values.

**Authentication (required for all WebSocket endpoints)**

After connecting, the client must send this as the first message:
```json
{ "type": "auth", "token": "<access token from localStorage>" }
```
The token is the same JWT access token received from `POST /api/users/login/` — no need to create a new one.

Server responses:
```json
{ "type": "auth_success" }
```
Server closes the connection if: token is invalid or not received within 5 seconds.

**Online presence endpoint:**
```
wss://localhost/ws/presence/
```
```json
{ "type": "user_online", "user_id": 5 }
{ "type": "user_offline", "user_id": 5 }
```

### Phase 1 — Implementation Log

> Backend setup, echo server, authentication, and online status are done and tested. Frontend integration (Vue side opening the connection automatically) is still pending.

- Backend now runs on Daphne instead of `runserver`, so it can handle both HTTP and WebSocket traffic.
- `ws/` app created with `consumers.py` (the WebSocket handler) and `routing.py` (maps `/ws/test/` to it).
- Echo server tested end-to-end: browser → nginx → backend → browser. Confirmed working.
- Authentication implemented: client sends the JWT access token as the first message after connecting; server validates it, looks up the user, and closes the connection if the token is missing or invalid within 5 seconds. Tested and working with a real token from `localStorage` (key: `access`).
- Online status implemented: on successful authentication, `is_online` is set to `True` on the user; on disconnect, it's set back to `False`. Verified both directions in Django Admin.
- Next planned step (per team decision): remote players (Phase 2) before chat.

### Phase 1 timeline
- Week 1 — echo server works
- Week 2 — WebSocket + online status

---

## Phase 2 — Remote Players

**What you implement:**
- Real-time game state synchronisation (ball position, paddles, score)
- All events must be saved to the existing `Match` and `MatchEvent` models
- A match between two browsers

**Done when:** two browsers, two different users, play against each other in real time.

### Important: game loop moves to the server

Right now ball physics are calculated in the browser (`frontend/src/views/GameView.vue`).
For remote players this needs to move to the server.

**Why:** two browsers will calculate physics differently → the game desyncs.

**How it should work:**
- server calculates ball movement, collisions, score
- browsers only send input (keys) and render what they receive
- ball coordinates go from server to both players via WebSocket

### API contract — Phase 2

> Numbers below are format examples, not real values.

**Game endpoint:**
```
wss://localhost/ws/game/<match_id>/
```

**Messages from client to server:**
```json
{ "type": "player_input", "key": "ArrowUp" }
{ "type": "player_input", "key": "ArrowDown" }
```

**Messages from server to client:**
```json
{
  "type": "game_state",
  "ball": { "x": 0.5, "y": 0.3 },
  "paddle_left": 0.4,
  "paddle_right": 0.6,
  "score": { "left": 2, "right": 1 }
}
```

### Phase 2 timeline
- Week 3 — Remote players works
- Week 4 — bugs + defense prep