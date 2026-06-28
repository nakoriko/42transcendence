<script setup>
import AppButton from '@/components/AppButton.vue'
import GameControls from '@/components/GameControls.vue'
import GameScoreBoard from '@/components/GameScoreBoard.vue'
import { ref, reactive, onMounted, onUnmounted} from 'vue'
import { useRoute, onBeforeRouteLeave } from 'vue-router'
import { apiFetch } from '@/utils/apiFetch'

    const gameCanvas = ref(null)
    const route = useRoute()
    const player1 = reactive({id:null, nickname: 'Player 1'})
    const player2 = reactive({id: Number(route.query.player2), nickname: 'Player 2'})
    let animationId = null
    let matchId = null // moved here. Need to be acceible from onBeforeRouteLeave (end of script)
    const score_p1 = ref(0)
    const score_p2 = ref(0)
    const gameOver = ref(false)
    const winnerText = ref('')

    const keys = {}
    function handleKeyDown(e) {
        if (['ArrowUp', 'ArrowDown'].includes(e.key)) e.preventDefault()
        keys[e.code] = true
    }

    function handleKeyUp(e) {
        keys[e.code] = false
    }

    async function finishMatch(winnerId) {
        await apiFetch(`/api/game/matches/${matchId}/finish/`, {
            method: 'PATCH',
            body: JSON.stringify({
                winner: winnerId,
                score_player1: score_p1.value,
                score_player2: score_p2.value,
                ended_at: new Date().toISOString() //convert to ISO 8601: 2026-06-05T14:23:11...., because jangpo is waiting for this format
            })
        })
    }

    function startGame() {
        const canvas = gameCanvas.value
        const ctx = canvas.getContext('2d')
        const events = []

        //ball position
        const ball = {
            x: 400, 
            y: 300,
            vx: 4,  //speed px/frame
            vy: 3,
            radius: 12
        }

        let leftPaddlehit = false
        let RightPaddleHit = false

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

        // let score_p1 = 0
        // let score_p2 = 0;

        //moves:
        document.addEventListener('keydown', handleKeyDown)
        document.addEventListener('keyup', handleKeyUp)

        async function initMatch() {
            // const token = localStorage.getItem('access')

            //get currnet user ID and nickname
            const profile = await apiFetch(`/api/users/profile/`)
            const profileData = await profile.json()
            player1.id = profileData.id
            player1.nickname = profileData.nickname

            //get opponent ID and nickname
            const profile2 = await apiFetch(`/api/users/${player2.id}/`)
            const profile2Data = await profile2.json()
            player2.nickname = profile2Data.nickname

            const match = await apiFetch ('/api/game/matches/start/', {
                method: 'POST',
                body: JSON.stringify({ player1: player1.id, player2: player2.id })
            })
            const matchData = await match.json()
            matchId = matchData.id
            render()
        }

        async function saveMatch() {
            //bulk instead of for cycle for every event
            await apiFetch ('/api/game/matches/events/bulk/', {
                method: 'POST',
                body: JSON.stringify(events)
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
                if(matchId) events.push({
                    match: matchId, event_type: 'miss', player: player1.id,
                    pos_x: +(ball.x / canvas.width).toFixed(4), //trasform s to float and leave 4 signs after point
                    pos_y: +(ball.y / canvas.height).toFixed(4),
                    reaction_time_ms: null
                })
                if(matchId) events.push({
                    match: matchId, event_type: 'goal', player: player2.id,
                    pos_x: +(ball.x / canvas.width).toFixed(4), //trasform s to float and leave 4 signs after point
                    pos_y: +(ball.y / canvas.height).toFixed(4),
                    reaction_time_ms: null
                })
                score_p2.value++
                resetBall()
            }
             //wall collisions (right wall)
            if (ball.x + ball.radius >= canvas.width) {
                if(matchId) events.push({
                    match: matchId, event_type: 'miss', player: player2.id,
                    pos_x: +(ball.x / canvas.width).toFixed(4), //trasform s to float and leave 4 signs after point
                    pos_y: +(ball.y / canvas.height).toFixed(4),
                    reaction_time_ms: null
                })
                if(matchId) events.push({
                    match: matchId, event_type: 'goal', player: player1.id,
                    pos_x: +(ball.x / canvas.width).toFixed(4), //trasform s to float and leave 4 signs after point
                    pos_y: +(ball.y / canvas.height).toFixed(4),
                    reaction_time_ms: null
                })
                score_p1.value++
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
                if(!leftPaddlehit) {
                    ball.vx = Math.abs(ball.vx)
                    leftPaddlehit = true
                    if(matchId) events.push({
                        match: matchId, event_type: 'hit', player: player1.id,
                        pos_x: +(ball.x / canvas.width).toFixed(4), //trasform s to float and leave 4 signs after point
                        pos_y: +(ball.y / canvas.height).toFixed(4),
                        reaction_time_ms: null })
                }
            } else {
                leftPaddlehit = false
            }
            //paddle_collisions (right paddle)
            if((ball.x + ball.radius >= r_paddle.x) 
                && (ball.y + ball.radius >= r_paddle.y && ball.y + ball.radius <= r_paddle.y + r_paddle.height)) {
            if(!RightPaddleHit) {
                    ball.vx = -Math.abs(ball.vx)
                    RightPaddleHit = true
                    if(matchId) events.push({
                        match: matchId, event_type: 'hit', player: player2.id,
                        pos_x: +(ball.x / canvas.width).toFixed(4),
                        pos_y: +(ball.y / canvas.height).toFixed(4),
                        reaction_time_ms: null
                    })
                }
            } else {
                RightPaddleHit = false
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
            ctx.fillStyle = '#1a1d2e'
            ctx.fillRect(0, 0, canvas.width, canvas.height)

        

            // центральная вертикальная линия (пунктир)
            ctx.setLineDash([5, 5])
            ctx.strokeStyle = '#ABC7C3'
            ctx.lineWidth = 0.5

            ctx.beginPath()
            ctx.moveTo(canvas.width / 2, 0)
            ctx.lineTo(canvas.width / 2, canvas.height)
            ctx.stroke()
            ctx.setLineDash([]) // сбрасываем пунктир

            // горизонтальная линия по центру
            ctx.strokeStyle = 'rgba(255,255,255,0.2)'
            ctx.lineWidth = 0.5
            ctx.beginPath()
            ctx.moveTo(0, canvas.height / 2)
            ctx.lineTo(canvas.width, canvas.height / 2)
            ctx.stroke()

            // ─────────────────────────────────────────────
           

            //Match_result
            if(score_p1.value >= 5 || score_p2.value >= 5) {
                cancelAnimationFrame(animationId)
                await saveMatch()
                const winnerId = score_p1.value >= 5 ? player1.id : player2.id
                await finishMatch(winnerId)
                //write result
                winnerText.value = score_p1.value >= 5 ? `${player1.nickname} wins!`: `${player2.nickname} wins!`
                gameOver.value = true
                return 
            }

            //crate ball in center
            ctx.fillStyle = 'white'
            ctx.beginPath() //start new path for drawing
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2) //Math.PI * 2 - end of arc (360)
            ctx.fill()

            //create paddles
            ctx.fillStyle = 'white'
            ctx.beginPath()
            ctx.roundRect(l_paddle.x, l_paddle.y, l_paddle.width, l_paddle.height, 30)
            ctx.fill()

            ctx.beginPath()
            ctx.roundRect(r_paddle.x, r_paddle.y, r_paddle.width, r_paddle.height, 30)
            ctx.fill()



            //current id = next frame
            animationId = requestAnimationFrame(render)
        }

        initMatch()
    }

    function stopGame() {
        cancelAnimationFrame(animationId)
        document.removeEventListener('keydown', handleKeyDown)
        document.removeEventListener('keyup', handleKeyUp)
    }
    onMounted(startGame)
    onUnmounted(stopGame)
    onBeforeRouteLeave(async () => {
        if(gameOver.value) return true

        const confirmed = confirm('Leave the game? This will count as a loss')
        if(!confirmed) return false
        stopGame()

        if(matchId) {
            try {
                const winnerId = player2.id
                // const winnerId = score_p1.value >= score_p2.value
                // ? player2.id
                // : player1.id
                await finishMatch(winnerId)
            } catch(e) {
                console.error('Failed to save abandoned mathc', e)
            }
        }
        winnerText.value = 'Game abandoned'
        gameOver.value = true
        return true
    })

</script>

<template>
    <div class="min-h-screen bg-navy-900 flex flex-col items-center px-4">
        <div class="flex-1 flex flex-col items-center justify-center gap-6">
            <GameScoreBoard :p1="score_p1" :p2="score_p2" :name1="player1.nickname" :name2="player2.nickname"></GameScoreBoard>

        <div class="relative">
            <canvas
                ref="gameCanvas"
                width="800" height="600"
                class="rounded-2xl border border-white/[0.07]"
            ></canvas>

            <div v-if="gameOver"
                class="absolute inset-0 flex flex-col items-center justify-center bg-navy-900/80 rounded-2xl gap-8">
                <p class="text-5xl font-light text-white">{{ winnerText }}</p>
                <RouterLink to="/lobby">
                    <AppButton variant="large">Play again</AppButton>
                </RouterLink>
            </div>
        </div>
        <GameControls></GameControls>            
        </div>
    </div>
</template>