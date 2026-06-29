# Remote Players — API Contract
## Per il teammate: modulo WebSockets + Remote Players

> Stato: concordato con il Tech Lead  
> Deadline: 9 luglio 2026  
> Stack: Django Channels + Redis + Vue

---

## Contesto

Le basi sono già pronte:
- Sistema di autenticazione (JWT)
- Modelli DB: `User`, `Match`, `MatchEvent`, `FriendRelation`
- Lobby: il giocatore A sceglie un avversario dalla lista → clicca "Start match"
- Il gioco locale su canvas funziona già (due giocatori, una tastiera)
- Il container Redis è attivo e pronto

Il tuo compito: fare in modo che due giocatori possano giocare **su browser diversi** su **macchine diverse**.

---

## Architettura

```
Browser A          Backend (Django Channels)       Browser B
   |                         |                         |
   |-- WS connect ---------->|                         |
   |                         |<-------- WS connect ----|
   |                         |                         |
   |-- game_invite --------->|-- game_invite --------->|
   |                         |                         |
   |                         |<-------- game_accept ---|
   |<-- game_start ----------|-- game_start ---------->|
   |                         |                         |
   |-- paddle_move --------->|-- game_state ---------->|
   |<-- game_state ----------|                         |
```

Redis viene usato come **channel layer** — intermediario tra le connessioni WS.  
Senza Redis, Django Channels non può trasmettere messaggi tra due connessioni diverse.

---

## Modello Match (aggiornato)

Il Tech Lead aggiunge due campi. Tu li leggerai e aggiornerai:

```python
class Match(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'Waiting for opponent'
        ACTIVE   = 'active',   'In progress'
        FINISHED = 'finished', 'Finished'

    class Mode(models.TextChoices):
        LOCAL  = 'local',  'Local (same machine)'
        REMOTE = 'remote', 'Remote (two browsers)'

    player1        = ForeignKey(User, ...)
    player2        = ForeignKey(User, ...)
    score_player1  = IntegerField(default=0)
    score_player2  = IntegerField(default=0)
    started_at     = DateTimeField(auto_now_add=True)
    ended_at       = DateTimeField(null=True)
    winner         = ForeignKey(User, null=True)
    status         = CharField(choices=Status, default=Status.PENDING)   # ← nuovo
    mode           = CharField(choices=Mode,   default=Mode.LOCAL)        # ← nuovo
```

---

## Endpoint REST (li fa il Tech Lead)

| Metodo | URL | Cosa fa |
|---|---|---|
| `POST` | `/api/game/match/invite/` | Crea una partita con stato `pending`, restituisce `match_id` |
| `PATCH` | `/api/game/match/<id>/status/` | Aggiorna lo stato della partita (pending → active → finished) |

### POST /api/game/match/invite/

Request:
```json
{ "opponent_id": 7 }
```

Response:
```json
{
  "match_id": 42,
  "status": "pending",
  "player1": { "id": 3, "nickname": "alice" },
  "player2": { "id": 7, "nickname": "bob" }
}
```

---

## Eventi WebSocket (li fai tu)

### Connessione

```
wss://localhost/ws/game/
```

Il client si connette quando entra nella lobby. Autenticazione — il token JWT viene passato nella query string:

```
wss://localhost/ws/game/?token=eyJ...
```

Il tuo Consumer deve:
1. Estrarre il token da `scope["query_string"]`
2. Verificarlo tramite `simplejwt`
3. Associare la connessione allo `user_id`

---

### Eventi: invito alla partita

#### 1. Il giocatore A invia l'invito
*Trigger: A ha cliccato "Start match" nella lobby, il REST ha creato la partita con `match_id`*

```json
{
  "type": "game_invite",
  "match_id": 42,
  "to_user_id": 7
}
```

#### 2. Il giocatore B riceve l'invito

```json
{
  "type": "game_invite",
  "match_id": 42,
  "from_user": {
    "id": 3,
    "nickname": "alice"
  }
}
```

#### 3. Il giocatore B accetta

```json
{
  "type": "game_accept",
  "match_id": 42
}
```

*Dopo di ciò il Consumer: aggiorna lo stato della partita nel DB a `active`*

#### 4. Entrambi ricevono il segnale di inizio

```json
{
  "type": "game_start",
  "match_id": 42,
  "your_role": "player1"
}
```

> `your_role` — `"player1"` o `"player2"`. Il frontend lo usa per assegnare i controlli (W/S vs ↑/↓).

---

### Eventi: svolgimento della partita

#### Client → Server: movimento della racchetta

```json
{
  "type": "paddle_move",
  "match_id": 42,
  "y": 0.63
}
```

> `y` — posizione normalizzata da 0 a 1 (come già implementato in MatchEvent)

#### Server → Client: stato del gioco

```json
{
  "type": "game_state",
  "ball":    { "x": 0.52, "y": 0.34 },
  "paddle1": { "y": 0.5 },
  "paddle2": { "y": 0.63 },
  "score":   { "player1": 2, "player2": 1 }
}
```

> Il server è la **fonte di verità**. Calcola la fisica, i client si occupano solo del rendering.  
> Frequenza: ~30 volte al secondo (ogni ~33ms).

---

### Eventi: fine partita e disconnessione

#### Fine partita (dal server)

```json
{
  "type": "game_over",
  "winner_id": 3,
  "score": { "player1": 5, "player2": 2 }
}
```

*Dopo di ciò il Consumer: aggiorna Match nel DB (winner, ended_at, status=finished)*

#### Disconnessione

Se un giocatore si disconnette durante una partita `active`:
- Il secondo giocatore vince automaticamente
- Il Consumer aggiorna il DB
- Il giocatore rimasto riceve:

```json
{
  "type": "opponent_disconnected",
  "match_id": 42,
  "winner_id": 3
}
```

---

## Gruppi (Django Channels)

Per recapitare messaggi a un giocatore specifico usa un **gruppo personale**:

```python
# Al momento della connessione, aggiungi l'utente al suo gruppo personale
group_name = f"user_{user_id}"
await self.channel_layer.group_add(group_name, self.channel_name)

# Per inviare a un giocatore specifico
await self.channel_layer.group_send(
    f"user_{opponent_id}",
    { "type": "game.invite", "match_id": 42, ... }
)

# Per la partita (broadcast a entrambi) — crea un gruppo stanza
room_group = f"match_{match_id}"
```

---

## Cosa NON fai tu

- Endpoint REST — li fa il Tech Lead
- Rendering canvas — già pronto, il Tech Lead collegherà game_state
- Modelli DB — li gestisce il Tech Lead (tu leggi/aggiorni solo lo stato)
- Logica JWT — già pronta, usa simplejwt per la verifica

---

## Ordine di implementazione (consigliato)

```
Fase 1: Connessione WS
  → Il Consumer si connette, verifica il JWT, logga user_id

Fase 2: Gruppi personali
  → Ogni user_id = gruppo proprio
  → Test: invia un messaggio echo a te stesso

Fase 3: flusso game_invite
  → A invia invite → B riceve
  → B risponde accept → lo stato della partita cambia

Fase 4: game_start
  → Entrambi ricevono your_role
  → Il frontend fa redirect a /game?match_id=42

Fase 5: game loop
  → paddle_move dai client
  → Il server calcola la fisica, distribuisce game_state

Fase 6: game_over + disconnect
  → La vittoria viene salvata nel DB
  → La disconnessione viene gestita
```

---

## Domande?

Concordati con il Tech Lead prima di iniziare ogni fase.  
Non modificare gli endpoint REST né i modelli senza accordo.
