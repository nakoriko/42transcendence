# WebSockets

*Author: Sabino Carlucci (`scarlucc`)*

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
WebSockets. Because of this, the backend runs on an ASGI server (gunicorn with
uvicorn workers) instead of `runserver`.

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
- **Match results** — `match_finished_event` broadcasts the final score and
  winner of a match to the `dashboard_updates` group as soon as it's saved. The
  frontend does not consume this event yet: the dashboard reloads its data after
  the player's own match instead.

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
attempted; it is **not** part of the delivered feature set. This code was later
removed from the main branch and is kept in the `feature/ws/remote_game` branch.

### Current status

- ✅ WebSocket connection + JWT authentication
- ✅ Online presence (is_online, multi-connection safe via Redis counter)
- ✅ Personal groups per user
- ✅ Real-time chat between friends
- ✅ Real-time friend-request notifications
- ✅ Real-time match-result notifications (sent by the server, not used by the frontend yet)
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