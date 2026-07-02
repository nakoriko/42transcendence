<script setup>
import AppFilterTabs from '@/components/AppFilterTabs.vue';
import AppMetric from '@/components/AppMetric.vue';
import AppTooltip from '../AppTooltip.vue';
import { calcWinRate } from '@/utils/stats';
import { ref, watch, onMounted, onUnmounted, reactive } from 'vue'
import { apiFetch } from '@/utils/apiFetch';
import * as d3 from 'd3'
import { useUserStore } from '@/stores/user';

const userStore = useUserStore()

const period = ref('All')
const chartEl = ref(null)
const players = ref([])
const stats = ref({
    players: 0,
    matches: 0,
    reaction: null,
})

const tt = ref(null)
const ttData = reactive({
    nickname: '',
    color: '', 
    date_joined: '',
    total_matches: 0,
    wins: 0,
    losses: 0,
    win_rate: 0,
    avg_reaction_ms: null,
    hit_accuracy: null,
})



async function loadData(){
    const period_param = period.value === 'All' ? 'all' : period.value.toLowerCase()
    const res = await apiFetch(`/api/analytics/universe/?period=${period_param}`)
    if (!res) return
    const data = await res.json()

    players.value = data
    stats.value.players = data.length
    stats.value.matches = data.reduce((sum, player) => sum + player.total_matches, 0)
    // for(const player of data) {
    //     sum = sum + player.total_matches
    // }
    const withReaction = data.filter(player => player.avg_reaction_ms !== null)
    stats.value.reaction = withReaction.length 
        ? Math.round(withReaction.reduce((sum, player) => sum + player.avg_reaction_ms, 0) / withReaction.length )  
        : null
}

function drawChart() {
    if(!chartEl.value || !players.value.length) return

    d3.select(chartEl.value).selectAll('*').remove()

    const W = chartEl.value.getBoundingClientRect().width

    const H = chartEl.value.getBoundingClientRect().height || 400
    const PL = 20, PR = 20, PT = 40, PB = 20
    const CW = W - PL - PR
    const CH = H - PT - PB

    const svg = d3.select(chartEl.value)
        .append('svg')
        .attr('width', W)
        .attr('height', H)
    
    const maxMatches = d3.max(players.value, p => p.total_matches)
    const colorScale = d3.scaleSequential()
        .domain([0, maxMatches])
        .interpolator(d3.interpolateRgbBasis(['#4A8C9B', '#ABC7C3', '#F4C295', '#F8856D']))
    
    const scaleX = d3.scaleTime()
        .domain([
            d3.min(players.value, p => new Date(p.date_joined)), //earliest date
            d3.max(players.value, p => new Date(p.date_joined)) //latest
        ])
        .range([PL, W - PR])

    const scaleY = d3.scaleLinear()
        .domain([0, d3.max(players.value, p => p.total_matches)])
        .range([H - PB, PT])//from down to up
    
    //gradient for every line
    const defs = svg.append('defs')
    players.value.forEach((p, i) => {
        const color = colorScale(p.total_matches)
        const tipY = scaleY(p.total_matches)
        const baseY = H - PB

        const grad = defs.append('linearGradient')
            .attr('id', `spike-grad-${i}`)
            .attr('gradientUnits', 'userSpaceOnUse')
            .attr('x1', 0).attr('x2', 0)
            .attr('y1', baseY)
            .attr('y2', tipY)
        grad.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', color)
            .attr('stop-opacity', 0)
        grad.append('stop')
            .attr('offset', '30%')
            .attr('stop-color', color)
            .attr('stop-opacity', 0.50)
        grad.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', color)
            .attr('stop-opacity', 1)
    })

    svg.selectAll('line')
        .data(players.value)
        .join('line')
        .attr('x1', p => scaleX(new Date(p.date_joined)))
        .attr('y1', H - PB)
        .attr('x2', p => scaleX(new Date(p.date_joined)))
        .attr('y2', p => scaleY(p.total_matches))
        .attr('stroke', (p, i) =>`url(#spike-grad-${i})`)
        .attr('stroke-width', 0.3)

    // svg.selectAll('line')
    //     .data(players.value)
    //     .join('line')
    //     .attr('x1', p => scaleX(new Date(p.date_joined)))
    //     .attr('y1', H - PB)
    //     .attr('x2', p => scaleX(new Date(p.date_joined)))
    //     .attr('y2', p => scaleY(p.total_matches))
    //     .attr('stroke', p => colorScale(p.total_matches))
    //     .attr('stroke-opacity', 0.4)
    //     .attr('stroke-width', 1)
//CREAZIONE DI SPIKES + AGGIUNGERE COLOR INTERPOLATION
    svg.selectAll('circle')
        .data(players.value)
        .join('circle')
        .attr('cx', p => scaleX(new Date(p.date_joined)))
        .attr('cy', p =>scaleY(p.total_matches))
        .attr('r', p => p.id === userStore.currentUser.id ? 9 : 4.5)
        .attr('fill', p => colorScale(p.total_matches))
        .attr('fill-opacity', 0.85)
        .on('mouseover', function(event, p) {
            ttData.nickname = p.nickname
            ttData.color = colorScale(p.total_matches)
            ttData.date_joined = new Date (p.date_joined).toLocaleDateString('en-US', {month: 'short', year: 'numeric'})
            ttData.total_matches = p.total_matches
            ttData.wins = p.wins
            ttData.losses = p.losses
            ttData.avg_reaction_ms = p.avg_reaction_ms
            ttData.hit_accuracy = p.hit_accuracy

            const x = scaleX(new Date(p.date_joined))
            const y = scaleY(p.total_matches)
            const tooltipWidth = 180
            const xPos = x + tooltipWidth > W ? x - tooltipWidth - 12 : x + 12
            tt.value.show(xPos, y - 10)
        })
        .on('mouseout', () => tt.value.hide())
//baseline
    svg.append('line')
        .attr('x1', PL)
        .attr('y1', H -PB)
        .attr('x2', W - PR)
        .attr('y2', H - PB)
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-width', 1)
//dates under base line
    const xAxis = d3.axisBottom(scaleX)
    .ticks(5)
    .tickFormat(d3.timeFormat('%b, %Y'))
    .tickSize(0)

    svg.append('g')
        .attr('transform', `translate(0, ${H -PB})`)
        .call(xAxis)
        .call(g => g.select('.domain').remove())
        .selectAll('text')
        .attr('fill', 'rgba(255,255,255,0.3)')
        .attr('font-size', '10px')
        .attr('dy', '1.2em')
}

let resizeTimer = null
const resizeObserver = new ResizeObserver(() => {
    clearTimeout(resizeTimer)
    resizeTimer = setTimeout(() => {
        requestAnimationFrame(() => drawChart())
    }, 200)
})


onMounted(async () => {
    await loadData()
    drawChart()
    if(chartEl.value) resizeObserver.observe(chartEl.value)
 })

watch(period, loadData)
watch(players, drawChart)
watch(() => userStore.currentUser, drawChart, { deep: true }) 

onUnmounted(() => {
    resizeObserver.disconnect()
})


</script>



<template>
    <div>  <!--DashPlayer Stats-->
        <div class="flex items-center justify-between mb-5">
            <div class="text-2xl uppercase mb-4">Pong universe</div>
            <AppFilterTabs v-model="period" :options="['7d', '30d', 'All']"></AppFilterTabs>
        </div>
        <div class="flex gap-8">
            <div class="flex flex-col gap-6 w-56 flex-shrink-0">
                <div class="text-xs text-muted">All players ranked by first match date. Height = total matches played. Color = activity level. Hover any spike to see full player stats.</div>
                <div class="border-t border-white/[0.07]"></div>  <!-- ← дивайдер -->

                <div class="flex flex-col gap-3 mb-1">
                    <div class="input-label">Platform Stats</div>
                    <AppMetric :value="String(stats.players)" label="Total players" color="biege" ></AppMetric>
                    <AppMetric :value="String(stats.matches)" label="Matches played" color="sage" ></AppMetric>
                    <AppMetric :value="stats.reaction ? String(stats.reaction + ' ms') : '-'" label="Global avg reaction" color="teal" ></AppMetric>
                </div>
                <div class="flex items-center gap-2 mt-1">
                    <span class="text-[9px] text-muted uppercase tracking-widest">new</span>
                    <div class="flex-1 h-px bg-gradient-to-r from-teal via-sage to-coral mb-1"></div>
                    <span class="text-[9px] text-muted uppercase tracking-widest">veteran</span>
                </div>
            </div>
            <div class="flex-1 relative">
                <div ref="chartEl" class="w-full h-[400px] overflow-hidden"></div>
                <AppTooltip ref="tt">
                    <div class="text-xs font-medium mb-3" :style="{color: ttData.color}">{{ ttData.nickname }}</div>
                    <div class="flex justify-between gap-4 mb-1">
                        <span class="text-[10px] text-muted">First match</span>
                        <span class="text-[10px]">{{ ttData.date_joined }}</span>
                    </div>
                    <div class="flex justify-between gap-4 mb-3">
                        <span class="text-[10px] text-muted">Total matches</span>
                        <span class="text-[10px]">{{ ttData.total_matches }}</span>
                    </div>
                    <div class="border-b border-white/[0.07] my-2"></div>
                    <div class="text-[9px] text-muted uppercase tracking-widest mb-2">Stats</div>
                    <div class="flex justify-between gap-4 mb-1">
                        <span class="text-[10px] text-muted">Wins</span>
                        <span class="text-[10px]">{{ ttData.wins }}</span>
                    </div>
                    <div class="flex justify-between gap-4 mb-1">
                        <span class="text-[10px] text-muted">Losses</span>
                        <span class="text-[10px]">{{ ttData.losses }}</span>
                    </div>
                    <div class="flex justify-between gap-4 mb-3">
                        <span class="text-[10px] text-muted">Win Rate</span>
                        <span class="text-[10px]">{{ calcWinRate(ttData.wins, ttData.losses) }}%</span>
                    </div>
                    <div class="border-b border-white/[0.07] my-2"></div>
                    <div class="flex justify-between gap-4 mb-1">
                        <span class="text-[10px] text-muted">Reaction</span>
                        <span class="text-[10px]">{{ ttData.avg_reaction_ms ? ttData.avg_reaction_ms + 'ms' : '-' }}</span>
                    </div>
                    <div class="flex justify-between gap-4">
                        <span class="text-[10px] text-muted">Accuracy</span>
                        <span class="text-[10px]">{{ ttData.hit_accuracy ? Math.round(ttData.hit_accuracy * 100) + '%' : '-' }}</span>
                    </div>
                </AppTooltip>
            </div>
        </div>
    </div>

</template>
