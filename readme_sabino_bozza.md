## WebSockets & Remote Players (Sabino)

### What it is and why

Pong originally ran with two players on the same keyboard, in the same browser tab.
To support **remote multiplayer** (two players on two different machines) the game
needed a way to push real-time updates between browsers — HTTP request/response
alone can't do this, since the server needs to *push* data to the client without
being asked. This is what WebSockets provide: a persistent, two-way connection
between browser and server.

This module covers a Major feature from the subject:

- **IV.1 — WebSockets (Django Channels)**: real-time transport layer, authentication
  over the socket, and online presence.


### Why Django Channels + Redis

Django's default server (`runserver`) speaks WSGI, which is request/response only —
it cannot keep a connection open. **Django Channels** extends Django to support
the ASGI protocol, which does support long-lived connections like WebSockets.
Because of this, the backend runs on **Daphne** (an ASGI server) instead of
`runserver`.

A single Django process can hold many open WebSocket connections, but by default
they can't talk to each other (e.g. player A's connection can't directly message
player B's connection). **Redis** is used as the *channel layer*: a broker that lets
different WebSocket connections — even across different backend workers/processes —
send messages to each other via named "groups". Every connected user is added to a
personal group (`user_<id>`), and every active match gets its own group
(`match_<id>`), so the server can target messages precisely (to one user, or to
both players in a match) instead of broadcasting to everyone.

### Authentication

The frontend already has JWT auth (`djangorestframework-simplejwt`) for REST calls.
The same access token is reused for the socket instead of creating a separate
auth system: after connecting, the client's **first message** must be
`{ "type": "auth", "token": "<access token>" }`. The server verifies it with
`AccessToken(...)`, looks up the user, and closes the connection if no valid token
arrives within 5 seconds. This keeps auth logic in one place and avoids introducing
a second credential type just for WebSockets.

### Online presence

On successful auth the user is added to a `global_presence` group and their
`is_online` flag is set to `True` in the DB; on disconnect it's set back to
`False`. A Redis counter (`ws_conn_count:<user_id>`) tracks how many connections a
user has open at once, so opening the app in two tabs (or two devices) doesn't
incorrectly mark the user offline when one tab closes — the flag only flips when
the *last* connection drops.

### Matchmaking flow (invites)

Implemented as a message exchange over the same socket, coordinated through the
personal (`user_<id>`) groups:

A → server:         game_invite      { match_id, to_user_id }
server → B:          game_invite      { match_id, from_user: {id, nickname} }
B → server:         game_accept      { match_id }
server → both:       game_start       { match_id, your_role }

On `game_accept`, the server updates the `Match` status to `active` in the DB and
tells both players their role (`player1` / `player2`), which the frontend uses to
assign controls.

[NOTE FOR SABINO — the contract also defines `invite_decline`, `invite_expired`
(timeout) and `invite_cancelled` (disconnect before response); these aren't in
`consumers.py` yet. Confirm status before writing this up as "done" vs "planned".]

### Match room & game loop

Once a match starts, both players are added to a `match_<id>` group so the server
can broadcast to both at once. Per the module's design principle, **the server is
meant to be the source of truth for game physics** (ball position, collisions,
score) — the two browsers must never compute physics independently, or the game
would desync between the two screens. Clients are only supposed to send input
(key presses) and render whatever state the server sends back.

[NOTE FOR SABINO — right now `handle_player_input` in `consumers.py` just
rebroadcasts the key/direction to the match group; the physics/scoring loop
itself still lives client-side in `GameView.vue` (this is the *local* two-player
version). Please confirm current status here: is server-side physics still to be
implemented for Phase 2, or has it moved elsewhere? This matters for the README
since "remote players" isn't truly playable end-to-end without it.]

### Message dispatcher

Incoming authenticated messages are routed through a `handlers` dict
(`message type → method`) inside `receive()`, rather than a long `if/elif` chain.
This keeps `consumers.py` easy to extend — adding a new event type is just one new
entry plus one new handler method.

[NOTE FOR SABINO — you had a TODO about extracting this dict into a module-level
`MESSAGE_HANDLERS` constant for tidiness; mention whether that refactor is done.]

### Chat (bonus, not part of the core Remote Players scope)

`handle_chat_message` / `chat_message_event` let two friends exchange direct
messages over the socket, with checks for: message not empty, recipient exists,
users are friends (`FriendRelation`), recipient is online. This piggybacks on the
same authenticated connection rather than opening a separate socket.

### Current status

- ✅ WebSocket connection + JWT authentication
- ✅ Online presence (is_online, multi-connection safe via Redis counter)
- ✅ Personal groups per user
- ✅ Invite → accept → match group flow
- ✅ Match status update to `active` in DB
- 🔄 Server-authoritative game loop (ball/paddle physics, score) for remote play
- 🔄 `game_over` + disconnect handling (auto-win for remaining player) per the
  contract in `REMOTE_PLAYERS_CONTRACT_IT.md`

[NOTE FOR SABINO — please confirm the two 🔄 rows above and fill in anything I've
mismarked; I only went by what's in `consumers.py`/GameView.vue right now.]

### Resources used

[NOTE FOR SABINO — list here: MDN/javascript.info WebSocket docs, Django Channels
tutorial, channels_redis docs, etc. Also required by the assignment: a short note
on **how AI was used** for this part of the project — e.g. which parts of
`consumers.py` or this documentation were drafted/reviewed with AI help. This is
mandatory for the README, I can't fill it in for you.]

### Individual contribution — Sabino

- Designed and implemented the `ws` Django app (WebSocket layer) from scratch:
  connection handling, JWT authentication over the socket, online presence.
- Implemented the remote-players negotiation flow: invites, accept, group
  management (personal groups + match groups) and match state transition to
  `active`.
- Set up Redis as the Channels layer and multi-connection-safe presence tracking.
- [NOTE FOR SABINO — add any specific challenges you hit and how you solved them,
  e.g. the multi-tab presence bug, debugging auth over query string vs first
  message, etc. — this is a required part of "Individual Contributions".]