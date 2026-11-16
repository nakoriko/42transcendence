<script setup>
import  { ref, onMounted, onUnmounted, watch, computed, reactive } from 'vue'
import  { useUserStore } from '@/stores/user'
import AppToolTip from '@/components/AppTooltip.vue'
import AppTooltipRow from '../AppTooltipRow.vue'
import { useResizeObserver } from '@/composables/useResizeObserver.js'

const props = defineProps({
    match: { type: Object, default: null},
    events: { type: Array, default: () => []}
})

const canvas = ref(null)
const container = ref(null)
const tt = ref(null)
const ttData = reactive ({
    num: 0,
    total: 0,
    hits: 0,
    won: false,
    score: '',
})

const COLORS = {
    coral: '#F8856D',
    sage:  '#ABC7C3',
    teal: '#4A8C9B'
}

let animProgress = []
let rafId = null 
const userStore = useUserStore()

//computed ralli (recalcolute every call)
const rallies = computed(() => {
    if (!props.match || !props.events.length|| !userStore.currentUser) return []
    const uid = userStore.currentUser.id
    const result = []
    let hits = 0;
    let score = [0, 0]
    for(const e of props.events) {
            if(e.event_type === 'hit') {
                hits++
            } else if (e.event_type === 'goal') {
                    const won = e.player === uid
                    won ? score[0]++ : score[1]++
                    result.push({
                        hits: hits || 1,
                        won,
                        score: `${score[0]} - ${score[1]}`,
                    })
                    hits = 0
                }
            }
        return result.map((r, i) => ({...r, num: i + 1}))
    })

//draw graph on canvas
function draw() {
    if (!canvas.value || !rallies.value.length) return
    const ctx = canvas.value.getContext('2d')
    const W = canvas.value.width
    const H = canvas.value.height
    const PL = 12, PR = 12, PT = 12, PB = 24
    
    //woekspace
    const CW = W - PL - PR
    const CH = H - PT - PB
    const GAP = CW / rallies.value.length
    const maxH = Math.max(...rallies.value.map (r => r.hits))
    const MIN_SPIKE = 20
    ctx.clearRect(0, 0, W, H)
    
    //basement
    ctx.strokeStyle = 'rgba(255,255,255,0.08)'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(PL, H - PB)
    ctx.lineTo(W - PR, H - PB)
    ctx.stroke()

    //draw spikes
    rallies.value.forEach((r, i) => {

        const prog = animProgress[i] ?? 0
        const x = PL + ( i + 0.5) * GAP
        const baseY = H - PB
        const fullH = Math.max(MIN_SPIKE, (r.hits / maxH) * CH)
        const tipY = baseY - fullH * prog
        ctx.globalAlpha = Math.min(1, prog * 2)

        //vertical line
        ctx.beginPath()
        ctx.strokeStyle = 'rgba(72,140,155,0.15)' //teal 
        ctx.lineWidth = 1
        ctx.moveTo(x, baseY)
        ctx.lineTo(x, tipY)
        ctx.stroke()

        const visibleHits = Math.floor(r.hits * prog)

        for(let j = 0; j < visibleHits; j++) {
            const isTop = j === r.hits - 1
            const frac = r.hits > 1 ? j / (r.hits - 1) : 1
            const dotY = baseY - frac * fullH * prog
            if(isTop) {
                ctx.beginPath()
                ctx.arc(x, dotY, 4.5, 0, Math.PI * 2)

                if(r.won) {
                    ctx.fillStyle = COLORS.teal
                    ctx.fill()
                } else {
                    ctx.fillStyle = 'rgba(179,199,195,0.1)'
                    ctx.strokeStyle = COLORS.coral
                    ctx.lineWidth = 1.5
                    ctx.fill()
                    ctx.stroke()
                }
            } else {
                ctx.beginPath()
                ctx.arc(x, dotY, frac > 0.6 ? 2.2 : 1.8, 0, Math.PI * 2)
                ctx.fillStyle = `rgba(171,199,195,${frac > 0.6 ? 0.65 : 0.35})`
                ctx.fill()
            }
        }
        ctx.globalAlpha = 1
    })

}

function animate() {
    const SPEED = 0.06
    let allDone = true
    rallies.value.forEach((_, i) => {
        if(animProgress[i] < 1) { 
            const startThreshold = i * 0.012 
            if (animProgress[i - 1] === undefined || animProgress[i - 1] > startThreshold) {
                animProgress[i] = Math.min(1, animProgress[i] + SPEED)
            }
            if(animProgress[i] < 1) allDone = false
        }
    })
    draw()
    if(!allDone) rafId = requestAnimationFrame(animate)
}

function startAnimation() {
    if (rafId) cancelAnimationFrame(rafId)
    animProgress = rallies.value.map(() => 0)
    rafId = requestAnimationFrame(animate)
}

//canvas and hover
function setupCanvas() {
    if(!canvas.value || !container.value) return
    canvas.value.width = container.value.clientWidth
    canvas.value.height = container.value.clientHeight
    startAnimation()
}

function onMouseMove(e) {
    if(!rallies.value.length) return
    const canvasRect = canvas.value.getBoundingClientRect()
    const containerRect = container.value.getBoundingClientRect()
    const mx = e.clientX - canvasRect.left //mouse postion related to canvas and clients window
    const W = canvasRect.width
    const PL = 12, PR = 12
    const GAP = (W - PL - PR) / rallies.value.length
    const idx = Math.floor((mx - PL) / GAP)// index of spike uner cursor
    if(idx < 0 || idx >= rallies.value.length) {
        tt.value?.hide()
        return 
    }
    const spikeX = PL + (idx + 0.5) * GAP
    const HOVER_RADIUS = 8
    if(Math.abs(mx - spikeX) > HOVER_RADIUS) {
        tt.value?.hide()
        return
    }

    const r = rallies.value[idx]
    ttData.num = r.num
    ttData.total = rallies.value.length
    ttData.hits = r.hits
    ttData.won = r.won
    ttData.score = r.score
    tt.value?.show(e.clientX - containerRect.left, e.clientY - containerRect.top)
}

function onMouseLeave() {
    tt.value?.hide()
}

//control of containers resize
useResizeObserver(container, setupCanvas, 150)

onMounted (() => {
    setupCanvas()
})

watch(rallies, () =>setupCanvas())

onUnmounted(() => {
    if(rafId) cancelAnimationFrame(rafId)
})


</script>

<template>
    <div class="flex flex-col h-full">  <!--DashRally timeline-->
        <!-- <div class="flex items-center justify-between mb-4">
            <div class="input-label">Rally timeline</div>
            <div v-if="props.match" class="text-[10px] text-muted">
                vs {{  props.match.opponent_nickname }} | {{ formatShortDate(props.match.ended_at) }}
            </div>
        </div> -->
        <div class="flex-1 relative" ref="container">
            <div v-if="!props.match"
                class="absolute inset-0 flex items-center justify-center text-muted text-xs">
                Select a match to see its rally structure</div>
                <canvas v-else ref="canvas"
                    @mousemove="onMouseMove"
                    @mouseleave="onMouseLeave"
                    class="w-full absolute bottom-0 block">
                </canvas>

<AppToolTip ref="tt">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-xs font-medium"
                            :style="{color: ttData.won ? '#ABC7C3' : '#F8856D'}">
                            Rally #{{ ttData.num }}
                        </span>
                        <span class="text-[10px] text-muted ml-2">
                            {{ ttData.num }} from {{ ttData.total }}
                        </span>
                    </div>
                    <!-- <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">vs</span>
                        <span class="text-[10px]">{{ ttData.opponent }}</span>
                    </div> -->
                    <!-- <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">Match date</span>
                        <span class="text-[10px]">{{ ttData.date }}</span>
                    </div> -->
                    <AppTooltipRow label="Exchanges" :value="ttData.hits" />
                    <AppTooltipRow label="Result">
                        <span :style="{ color: ttData.won ? '#4A8C9B' : '#F8856D' }">
                            {{ ttData.won ? 'Your point' : "Opponent's point" }}
                        </span>
                    </AppTooltipRow>
                    <AppTooltipRow label="Score" :value="ttData.score" />
                    <!-- <div class="mt-3 pt-2 border-t border-white/[0.07]">
                        <span class="text-[9px] text-muted tracking-widest uppercase">
                            Click to view match ↓
                        </span>
                    </div> -->
                </AppToolTip>
        </div>
    </div>
</template>