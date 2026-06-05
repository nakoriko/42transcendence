<script setup>
    import { ref, onMounted, onUnmounted} from 'vue'
import { routeLocationKey, useRoute } from 'vue-router'

    const gameCanvas = ref(null)
    const route = useRoute()
    const player2Id = Number(route.query.player2)
    let animationId = null


    function startGame() {
        const canvas = gameCanvas.value
        const ctx = canvas.getContext('2d')

        let matchId = null
        let currentUserId = null
        const events = []

        //ball position
        const ball = {
            x: 400, 
            y: 300,
            vx: 4,  //speed px/frame
            vy: 3,
            radius: 12
        }

        const l_paddle = {
            x: 10,
            y: canvas.height / 2 - 40,
            width: 15,
            height: 80, 
            speed: 5
        }

        const r_paddle = {
            x: canvas.width - 10 - 15,
            y: canvas.height / 2 - 40,
            width: 15,
            height: 80, 
            speed: 5
        }

        let score_p1 = 0
        let score_p2 = 0;

        //moves:
        const keys = {}
        document.addEventListener('keydown', function(e) { keys[e.code] = true})
        document.addEventListener('keyup', function(e) { keys[e.code] = false})

        async function initMatch() {
            const token = localStorage.getItem('access')

            //get user ID
            const profile = await fetch('/api/users/profile/', {
            headers: { 'Authorization': `Bearer ${token}` },
            })
            const profileData = await profile.json()
            currentUserId = profileData.id

            const match = await fetch ('/api/game/match/start/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ player1: currentUserId, player2: player2Id })
            })
            const matchData = await match.json()
            matchId = matchData.id
            render()
        }

        async function saveMatch() {
            const token = localStorage.getItem('access')
            for (const event of events) {
                await fetch ('/api/game/match/events/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(event)
                })
            }
        }

        async function finishMatch(winnerId) {
            const token = localStorage.getItem('access')
            await fetch(`/api/game/match/${matchId}/finish/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    winner: winnerId,
                    score_player1: score_p1,
                    score_player2: score_p2,
                    ended_at: new Date().toISOString() //convert to ISO 8601: 2026-06-05T14:23:11...., because jangpo is waiting for this format
                })
            })
        }


        function resetBall() {
            ball.x = canvas.width / 2
            ball.y = canvas.height / 2
            ball.vx = 4 * (Math.random() > 0.5 ? 1 : -1)
            ball.vy = 3 * (Math.random() > 0.5 ? 1 : -1)
        }

        async function render() {
            //updating ball possition
            ball.x = ball.x + ball.vx
            ball.y = ball.y + ball.vy

            //wall collisions (left wall)
            if (ball.x - ball.radius <= 0) {
                score_p2++
                resetBall()
            }
             //wall collisions (right wall)
            if (ball.x + ball.radius >= canvas.width) {
                score_p1++
                resetBall()
            }



           //wall collisions (top wall)
            if(ball.y - ball.radius <= 0)
                ball.vy = Math.abs(ball.vy)
            //wall collisions (bottom wall)
            if (ball.y + ball.radius >= canvas.height)
                ball.vy = -Math.abs(ball.vy)
                // ball.vy = ball.vy * -1
                
            //paddle_collisions (left paddle)
            if((ball.x - ball.radius <= l_paddle.x + l_paddle.width) 
                && (ball.y - ball.radius >= l_paddle.y && ball.y - ball.radius <= l_paddle.y + l_paddle.height)) {
                ball.vx = Math.abs(ball.vx)
                if(matchId) events.push({
                    match: matchId, event_type: 'hit', player: currentUserId,
                    pos_x: +(ball.x / canvas.width).toFixed(4), //trasform s to float and leave 4 signs after point
                    pos_y: +(ball.y / canvas.height).toFixed(4),
                    reaction_time_ms: null
                })
            }
            //paddle_collisions (right paddle)
            if((ball.x + ball.radius >= r_paddle.x) 
                && (ball.y + ball.radius >= r_paddle.y && ball.y + ball.radius <= r_paddle.y + r_paddle.height)) {
                ball.vx = -Math.abs(ball.vx)
                if(matchId) events.push({
                    match: matchId, event_type: 'hit', player: player2Id,
                    pos_x: +(ball.x / canvas.width).toFixed(4),
                    pos_y: +(ball.y / canvas.height).toFixed(4),
                    reaction_time_ms: null
                })
            }

            if(keys['KeyW'] == true)
                l_paddle.y = l_paddle.y - l_paddle.speed
            if(keys['KeyS'] == true)
                l_paddle.y = l_paddle.y + l_paddle.speed

            if(keys['ArrowUp'] == true)
                r_paddle.y = r_paddle.y - r_paddle.speed
            if(keys['ArrowDown'] == true)
                r_paddle.y = r_paddle.y + r_paddle.speed

            if(l_paddle.y < 0) l_paddle.y = 0
            if(l_paddle.y + l_paddle.height > canvas.height) l_paddle.y = canvas.height - l_paddle.height
            if(r_paddle.y < 0) r_paddle.y = 0
            if(r_paddle.y + r_paddle.height > canvas.height) r_paddle.y = canvas.height - r_paddle.height

            //clean:
            ctx.clearRect(0, 0, canvas.width, canvas.height)


            //fill field
            ctx.fillStyle = '#1a1a2e'
            ctx.fillRect(0, 0, canvas.width, canvas.height)

            //count
            ctx.fillStyle = 'white'
            ctx.font = '32px monospace'
            ctx.textAlign = 'center'
            ctx.fillText(score_p1 + ':' + score_p2, canvas.width / 2, 40)

            //Match_result
            if(score_p1 >= 5 || score_p2 >= 5) {
                cancelAnimationFrame(animationId)
                ctx.fillStyle = 'white'
                ctx.font = '48px monospace'
                ctx.textAlign = 'center'
                await saveMatch()
                const winnerId = score_p1 >= 5 ? currentUserId : player2Id
                //write result
                await finishMatch(winnerId)
                ctx.fillText(score_p1 >= 5 ? 'Player 1 wins!': 'Player 2 wins!', canvas.width / 2, canvas.height / 2)
                return 
            }

            //crate ball in center
            ctx.fillStyle = 'white'
            ctx.beginPath() //start new path for drawing
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2) //Math.PI * 2 - end of arc (360)
            ctx.fill()

            //create paddles
            ctx.fillStyle = 'white'
            ctx.fillRect(l_paddle.x, l_paddle.y, l_paddle.width, l_paddle.height)
            ctx.fillRect(r_paddle.x, r_paddle.y, r_paddle.width, r_paddle.height)


            //current id = next frame
            animationId = requestAnimationFrame(render)
        }

        initMatch()
    }

    function stopGame() {
        cancelAnimationFrame(animationId)
    }
    onMounted(startGame)
    onUnmounted(stopGame)

</script>

<template>
    <div>
        <canvas ref="gameCanvas" width="800" height="600"></canvas>
    </div>
</template>