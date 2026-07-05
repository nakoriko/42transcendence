<script setup>
import  { ref, onMounted, onUnmounted, watch, computed, reactive } from 'vue'
import  { useUserStore } from '@/stores/user'
import AppToolTip from '@/components/AppTooltip.vue'
import AppFilterTabs from '../AppFilterTabs.vue'
import { useResizeObserver } from '@/composables/useResizeObserver.js'
import { filterByPeriod } from '@/utils/period.js'
import { formatShortDate } from '@/utils/date.js'

const props = defineProps({
    matches: { type: Array, default: () => []},
    events: { type: Array, default: () => []}
})

const period = ref('All')
const filteredMatches = computed (() => 
    filterByPeriod(props.matches, 'ended_at', period.value)
) 

const emit = defineEmits(['matchSelected'])
const canvas = ref(null)
const container = ref(null)
const tt = ref(null)
const ttData = reactive ({
    num: 0,
    total: 0,
    hits: 0,
    won: false,
    score: '',
    opponent: '',
    date: '',
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
    if (!filteredMatches.value.length|| !userStore.currentUser) return []

    const uid = userStore.currentUser.id
    const result = []
    const ordered = [...filteredMatches.value].reverse() //reverse order for inter array

    for(const m of ordered) {
            const matchEvents = props.events.filter(e => e.match === m.id)
            let hits = 0;
            let score = [0, 0]

            for(const e of matchEvents) {
                if(e.event_type === 'hit') {
                    hits++
                } else if (e.event_type === 'goal') {
                        const won = e.player === uid
                        won ? score[0]++ : score[1]++
                        result.push({
                            hits: hits || 1,
                            won,
                            score: `${score[0]} - ${score[1]}`,
                            matchId: m.id,
                            matchDate: m.ended_at,
                            opponent:  m.opponent_nickname,
                        })
                        hits = 0
                    }
                }
            }
        const filtered = result.filter(r => r.hits > 1)
        return filtered.map((r, i) => ({...r, num: i + 1}))
    })

//limits for bottom timeline


const matchGroups = computed(() => {
    const groups = []
    rallies.value.forEach((r, i) => {
        const last = groups[groups.length - 1]
        if(last && last.matchId === r.matchId) {
            last.endIndex = i
        } else {
            groups.push({ matchId: r.matchId, matchDate: r.matchDate, startIndex: i, endIndex: i})
        }
    })
    return groups
})

//draw graph on canvas

function draw() {
    if (!canvas.value || !rallies.value.length) return

    const ctx = canvas.value.getContext('2d')
    const W = canvas.value.width
    const H = canvas.value.height

    const PL = 12, PR = 12, PT = 12, PB = 18
    
    //woekspace
    const CW = W - PL - PR
    const CH = H - PT - PB
    const GAP = CW / rallies.value.length
    const maxH = Math.max(...rallies.value.map (r => r.hits))
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
        //30/06: added dividers beteen groups of matches
        if(i > 0 && r.matchId !== rallies.value[i - 1].matchId) {
            const sepX = PL + i * GAP 
            ctx.save()
            ctx.globalAlpha = 1
            ctx.beginPath()
            ctx.strokeStyle = 'rgba(255,255,255,0.2)'
            ctx.lineWidth = 0.5
            ctx.setLineDash([2, 2])
            ctx.moveTo(sepX, PT)
            ctx.lineTo(sepX, H - PB)
            ctx.stroke()
            ctx.restore()
        }


        const prog = animProgress[i] ?? 0
        const x = PL + ( i + 0.5) * GAP
        const baseY = H - PB
        const fullH = (r.hits / maxH) * CH
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
            const frac = r.hits > 1 ? j / (r.hits - 1) : 0
            const dotY = baseY - frac * fullH
            const isTop = j === r.hits - 1
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

    const MAX_LABELS = 10 //add fast solution to avoid a mess with dates on timeline
    if(matchGroups.value.length <= MAX_LABELS) { //just for 10 matches
        matchGroups.value.forEach(g => {
            const centerX = PL + ((g.startIndex + g.endIndex) / 2 + 0.5) * GAP
            ctx.save()
            ctx.globalAlpha = 1
            ctx.fillStyle = 'rgba(255,255,255,0.35)'
            ctx.font = '9px sans-serif'
            ctx.textAlign = 'center'
            ctx.fillText (formatShortDate(g.matchDate), centerX, H - 4)
            ctx.restore() 
        }
    )}
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
    const rect = canvas.value.getBoundingClientRect()
    const mx = e.clientX - rect.left //mouse postion related to canvas and clients window
    const W = canvas.value.width
    // const GAP = (W - PL + PR) / rallies.value.length
    const GAP = (W - 24) / rallies.value.length

    const idx = Math.floor((mx-12) / GAP)// index of spike uner cursor
    if(idx < 0 || idx >= rallies.value.length) {
        tt.value?.hide()
        return 
    }

    const r = rallies.value[idx]
    ttData.num = r.num
    ttData.total = rallies.value.length
    ttData.hits = r.hits
    ttData.won = r.won
    ttData.score = r.score
    ttData.opponent = r.opponent ?? '-'
    ttData.date = formatShortDate(r.matchDate)

    const x = 12 + (idx + 0.5) * GAP
    const tooltipWidth = 170
    const xPos = x + tooltipWidth + 12 > W
        ? x - tooltipWidth - 12
        : x + 12
    tt.value?.show(xPos, 20)
}

function onCanvasClick(e) {
    const rect = canvas.value.getBoundingClientRect()
    const mx = e.clientX - rect.left
    const GAP = (canvas.value.width - 2) / rallies.value.length
    const idx = Math.floor((mx - 12) / GAP)

    if(idx >= 0 && idx < rallies.value.length) {
        emit('matchSelected', rallies.value[idx].matchId)
    }
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
        <div class="flex items-center justify-between mb-4">
            <div class="input-label">Ralli timeline</div>
            <AppFilterTabs v-model="period" :options="['7d', '30d', 'All']" />
        </div>
        <div class="flex-1 relative" ref="container">
                <canvas ref="canvas"
                    @mousemove="onMouseMove"
                    @mouseleave="onMouseLeave"
                    @click="onCanvasClick"
                    class="w-full absolute bottom-0 cursor-crosshair block">
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
                    <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">vs</span>
                        <span class="text-[10px]">{{ ttData.opponent }}</span>
                    </div>
                    <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">Match date</span>
                        <span class="text-[10px]">{{ ttData.date }}</span>
                    </div>
                    <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">Exchanges</span>
                        <span class="text-[10px]">{{ ttData.hits }}</span>
                    </div>
                    <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">Result</span>
                        <span class="text-[10px]"
                        :style="{ color: ttData.won ? '#4A8C9B' : '#F8856D'} ">
                            {{ ttData.won ? 'Your point' : "Opponent's Point" }}
                        </span>
                    </div>
                    <div class="flex justify-between mb-1">
                        <span class="text-[10px] text-muted">Score</span>
                        <span class="text-[10px]">{{ ttData.score }}</span>
                    </div>
                    <div class="mt-3 pt-2 border-t border-white/[0.07]">
                        <span class="text-[9px] text-muted tracking-widest uppercase">
                            Click to view match ↓
                        </span>
                    </div>
                </AppToolTip>
        </div>
    </div>
</template>