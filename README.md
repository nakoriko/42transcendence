*This project has been created as part of the 42 curriculum by nakoriko, scarlucc.*
*(this line must remain in English and italicized in the final README — this is a subject requirement)*



# Transcend — ft_transcendence

## Table of Contents

- [Description](#description)
- [Team Information](#team-information)
- [Project Management](#project-management)
- [Technical Stack](#technical-stack)
- [Database Schema](#database-schema)
- [Architecture](#architecture)
- [Instructions](#instructions)
- [Features List](#features-list)
- [Modules](#modules)
- [Individual Contributions](#individual-contributions)
- [Known Limitations](#known-limitations)
- [Resources](#resources)
- [License & Credits](#license--credits)

---

## Description

**Transcend** is a real-time multiplayer Pong platform, built as part of the 42 `ft_transcendence` project. Two players can play classic Pong locally, chat with each other, add each other as friends, and after a match — review match analytics.

The goal of the project is to demonstrate a full-featured, containerized, real-time web application built by a team: a Vue SPA frontend, a Django backend (REST + WebSocket), a PostgreSQL database, and Nginx as a reverse proxy, all brought up with a single command `docker-compose up --build -d`.

### Key features

- **Account and profile management** — registration, login (JWT), avatar upload, editable nickname, win/loss statistics.
- **Friends system** — send/accept/decline friend requests, real-time online status display.
- **Real-time chat** — private messages between users over WebSocket.
- **Local and remote Pong** — Pong on canvas, available on a single keyboard (locally)
- **Post-match analytics dashboard** — force-graph of match events, rally timeline, global leaderboard, per-period player stats, PDF export.
- **Online presence** — real-time online/offline status via WebSocket.

---

## Team Information

| Member | Login | Role(s) | Area of responsibility |
|---|---|---|---|
| [Natalia] | `nakoriko` | Product Owner · Technical Lead · Developer | Defined the product vision and feature priorities; responsible for architecture, stack choices, and code quality; implemented the framework setup, authentication system, DB schema, standard user management, the Pong game, the design system, and analytics. |
| [Name] | `<login2>` | Developer | Implemented the WebSocket infrastructure (auth, presence, chat transport) and remote multiplayer. |

> With a team of 2–4 people, roles overlap by definition (see subject §II.1.1): the same person can simultaneously be PO, PM, and Tech Lead.

---

## Project Management

**Work organization:** the project is split into three zones so that a small (and growing) team can work in parallel safely:

1. **Foundation** (Docker setup, repo structure, auth, DB schema, Pong core, standard user management) — built solo first, as the base that all other modules depend on.
2. **Modules in progress, contract-based** (analytics, design system, WebSockets, remote players) — the Tech Lead designs the API/data contract for the module in advance; each teammate then implements their module independently against that contract, in their own part of the repository.
3. **Modules open to the team** (tournaments, OAuth, 2FA, PWA, AI opponent, etc.) — isolated, self-contained modules that a new or additional teammate can pick up, implement, and deliver without touching anyone else's code.

Every new module goes through the same four-step cycle: **study** the concept → **design the architecture** before writing code → **implementation** → **defense** (a self-check confirming the module is genuinely understood before it's considered done).

---

## Technical Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Vue 3 (Composition API) + Vite | A smoother learning curve than React for a team working with frontend frameworks for the first time, while keeping the same core concepts (components, reactivity, SPA routing). |
| Styling | Tailwind CSS | A utility-first approach, on top of which a small custom design system (10+ reusable components) is built, without pulling in a heavy component library. |
| State | Pinia | The official state-management solution for Vue, a simple API for a small SPA. |
| Real-time client | Native WebSocket via a singleton service (`wsService.js`) | One persistent connection, shared for chat, presence, and game events. |
| Data visualization | D3.js | Custom, interactive visualizations for the analytics dashboard (force-graph, timelines, leaderboards) that aren't covered by off-the-shelf chart libraries. |
| Backend | Django + Django REST Framework | An out-of-the-box framework with a built-in ORM and admin panel, reducing boilerplate for a team learning backend development from scratch. |
| Real-time server | Django Channels + Daphne (ASGI) | Adds WebSocket support to Django; `daphne` replaces `runserver` because the standard dev server only works over WSGI and cannot serve WebSocket connections. |
| Authentication | SimpleJWT (JWT) | Stateless authentication; no server-side session storage needed for the API, which simplifies scaling and matches a REST-oriented design. |
| Database | PostgreSQL | Chosen over SQLite for reliability under concurrent access and better support for the relational, analytics-heavy queries the dashboard needs (match history, aggregated stats). |
| Message broker | Redis | Channel layer for Django Channels, so WebSocket messages can be routed between consumers/processes. |
| Reverse proxy | Nginx | A single HTTPS entry point (self-signed certificate) routing `/`, `/api/`, `/media/`, `/admin/`, and `/ws/` to the right container. |
| Deployment | Docker Compose | The entire stack (nginx, frontend, backend, db, redis) is brought up with a single `docker-compose up` command. |

Detailed breakdown of technical decisions and trade-offs: see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## Database Schema

PostgreSQL, accessed through the Django ORM. Four core tables:

- **User** — extends Django's `AbstractUser`; email-based login, unique nickname, avatar, win/loss counters, online status.
- **FriendRelation** — friend requests/relations between two users, with a status (`pending`, etc.).
- **Match** — a single game between two players: mode (local), current score, winner.
- **MatchEvent** — individual events within a match (hit/miss/goal), used for the analytics dashboard.

The relation design follows one general rule: relations that are meaningless without both sides (e.g. a friendship) cascade on delete; relations representing a historical fact that should outlive the deletion of a participant (a match, a match event) use `SET_NULL` — so match history and statistics are preserved even after an account is deleted.

Full field list, types, constraints, and the ER diagram: see [`DB_SCHEMA.md`](./DB_SCHEMA.md).

---

## Architecture

The application runs as five containers behind an Nginx reverse proxy: `frontend` (Vue/Vite), `backend` (Django + Channels, served by Daphne, includes the WebSocket layer), `db` (PostgreSQL), `redis` (channel layer broker for WebSocket), and `nginx` (HTTPS termination and routing). Django Channels is embedded directly in the `backend` container rather than run as a separate service — to keep onboarding simpler for the team.

Full container diagram, repository structure, per-module breakdown (frontend components/stores/views, backend apps, list of API endpoints, Nginx routing table): see [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## Instructions

### Prerequisites

- Docker and Docker Compose
- Git
- A modern browser (development and testing were done on the latest stable version of Google Chrome)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd transcend
   ```
2. Copy the environment variable template and fill in the required values:
   ```bash
   cp .env.example .env
   ```
3. Build and start all services with a single command:
   ```bash
   docker-compose up --build
   ```
4. Open the app in your browser:
   ```
   https://localhost
   ```
   The self-signed TLS certificate will trigger a browser warning on first visit — this is expected, confirm to proceed.

### Stopping

```bash
docker-compose down
```

To also clear the database volume:
```bash
docker-compose down -v
```

---

## Features List

| Feature | Description | Implemented by |
|---|---|---|
| Registration and JWT login | Email/password registration, hashed and salted passwords, JWT access/refresh | nakoriko |
| Profile management | Edit nickname/email, avatar upload, view win/loss statistics | nakoriko |
| Friends system | Send/accept/decline friend requests, remove friends | nakoriko |
| Online presence | Real-time online/offline indicator via WebSocket | scarlucc |
| Real-time chat | Private messages between users over WebSocket | nakoriko (frontend) / scarlucc (backend transport) |
| Local Pong | Two players, one keyboard, match rendered on canvas | nakoriko |
| Custom design system | 10+ reusable Vue components (buttons, cards, inputs, avatars, badges, etc.) | nakoriko |
| Analytics dashboard | Rally timeline, match event force-graph, global leaderboard, player statistics, PDF export | nakoriko |
| Privacy Policy and Terms of Service | Static pages, accessible via link | nakoriko |

---

## Modules

| # | Module | Category | Type | Points | Implemented by |
|---|---|---|---|---|---|
| 1 | Use a framework for the frontend + backend (Vue + Django) | IV.1 Web | Major | 2 | nakoriko |
| 2 | Use an ORM (Django ORM) | IV.1 Web | Minor | 1 | nakoriko |
| 3 | Custom design system (10+ reusable components) | IV.1 Web | Minor | 1 | nakoriko |
| 4 | User interaction (chat) | IV.1 Web | Major | 2 | nakoriko (frontend) / scarlucc (backend transport) |
| 5 | Standard user management | IV.3 User Management | Major | 2 | nakoriko |
| 6 | User activity dashboard | IV.3 User Management | Minor | 1 | nakoriko |
| 7 | Web-based game — Pong | IV.6 Gaming & UX | Major | 2 | nakoriko |
| 8 | Advanced analytics (custom post-match analytics) | IV.8 Data & Analytics | Major | 2 | nakoriko |
| 9 | WebSockets (real-time infrastructure: auth, presence, chat transport) | IV.1 Web | Major | 2 | scarlucc |

**Total: 15 points** — the subject's minimum is 14.

---

## Individual Contributions

### nakoriko — Product Owner / Tech Lead / Developer

- Set up the initial Docker Compose environment, repository structure, and Nginx reverse proxy with HTTPS.
- Designed and implemented the database schema (see [`DB_SCHEMA.md`](./DB_SCHEMA.md)) and the authentication system (JWT, hashed passwords).
- Implemented standard user management: profile editing, avatar upload, friends system, user activity dashboard.
- Implemented the local Pong game (canvas rendering, score tracking, match/event recording).
- Built the custom design system (10+ Vue components) and used it to redesign the lobby and profile page.
- Built the analytics dashboard: rally timeline, match event force-graph, global leaderboard, player statistics, PDF export.

**Challenges faced:**
- **No prior experience with web frameworks before the project.** Vue, Django, PostgreSQL, and WebSockets were learned from scratch while working on the project. Solution — a strict "study → architecture → implementation → self-check" cycle for every new concept before writing code (see [Resources](#resources)).
- **Parallel requests during token refresh.** Resolved with proactive refresh — added a check for the token's expiration before it actually expires.

### `<login2>` — Developer

- Implemented the WebSocket layer on the backend: authentication over WebSocket, online-presence broadcasting, and the chat transport (consumers, routing).
- Implemented remote multiplayer matchmaking and gameplay.

**Challenges faced:**
- **[TODO: describe a real challenge `<login2>` faced — e.g. keeping presence state consistent across reconnects, synchronizing paddle/ball state for remote play, a Channels/Redis routing issue — and how it was resolved.]**

---

## Known Limitations

- `DEBUG=True` and an open `ALLOWED_HOSTS` are used for the submission environment — this is a deliberate, documented trade-off for a local deployment/defense, not for production.
- Sent chat messages are not rolled back on network failure/disconnect — acceptable for the minimally working chat required by the subject, but not a production-level delivery guarantee.
- The incoming friend requests list refreshes on route change rather than instantly over WebSocket; a real-time listener is written but currently disabled pending final confirmation of the backend event.

---

## Resources

### References

- [Django documentation](https://docs.djangoproject.com/)
- [Django REST Framework documentation](https://www.django-rest-framework.org/)
- [Django Channels documentation](https://channels.readthedocs.io/)
- [Vue 3 documentation](https://vuejs.org/)
- [Pinia documentation](https://pinia.vuejs.org/)
- [PostgreSQL documentation](https://www.postgresql.org/docs/)
- [D3.js documentation](https://d3js.org/)
- [MDN — WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [JWT.io — introduction to JSON Web Tokens](https://jwt.io/introduction)

### How AI was used

AI (Claude) was used as a study aid and pair-programming tool throughout the project, following a fixed, documented workflow (kept in `CLAUDE_CONTEXT.md`, updated daily and pasted at the start of every AI conversation) with four types of sessions:

- **Study sessions** — used to learn a new concept (e.g. WebSockets, JWT, Django ORM) before touching any code: first the team member explains what they already understand, then the concept is explained through an analogy, then through a minimal example, and finally a couple of comprehension questions.
- **Architecture design sessions** — used to design a module's structure, API contract, or data flow
- **Implementation sessions** — used while writing a specific feature, given the large number of new concepts and syntax involved; understood before it is added to the codebase, rather than being pasted in "as is."
- **Defense sessions** — used after a feature is implemented, to check one's own understanding.

We did not use code-writing agents built into VS Code.
---