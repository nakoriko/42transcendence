<script setup>
import { ref, onMounted, onUnmounted, watch, reactive, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import * as d3 from 'd3'
import AppTooltip from '../AppTooltip.vue'
import { apiFetch } from '@/utils/apiFetch'
import { formatShortDate } from '@/utils/date.js'
import { useResizeObserver } from '@/composables/useResizeObserver.js'




// Player Connection Graph (ego-network, 2-hop).

// Design decisions:
// - Hosted inside DashboardView as a top section, not a separate /dashboard/graph page.
//   Reason: keeps all analytics in one place; graph is first for screenshot/demo visibility.
// - MatchEchoViz copied as skeleton (drag/hover/tooltip paradigm reused).
//   Force-simulation params retuned for network graph (distance 100, charge -300).
// - "Breathing" effect via alphaTarget(0.02) + alphaMin(0.001) — mimics Obsidian.
// - Drag releases fx/fy on end (Obsidian-style): nodes stay in flow, not pinned.
// - Glow via SVG filter in <defs>; applied to nodes as filter="url(#glow)".
// - Node radius: scaleSqrt(degree), range [3,10], +2px bonus for current user.
// - Node color: diverging scale coral→sage→teal by winRate (0 → 0.5 → 1).
// - Edge thickness fixed at 1px (scaled width postponed — see "Future" below).

// Known limitations:
//   Graph does not re-render on container resize. TODO 
// - Tooltip (AppTooltip) kept from skeleton but not yet wired to graph data.
//   Content template still shows event-type fields — to be remapped in Step 5
//   to show nick / W-L / winRate / degree.

// Future (deferred by plan):
// - Edge thickness scaled by edges[].matches — Step 5.
// - Empty state message ("Play some matches to see your network grow") — Step 5.
// - Loader during fetch — Step 5.
// - Click node → navigate to player profile — out of 2-day scope.
// - Zoom/pan — out of 2-day scope.
// - WS realtime update on match_finished — out of 2-day scope.






const userStore = useUserStore()
const ttEdge = ref(null)
const ttEdgeData = reactive (({
    sourceName: '',
    targetName: '',
    matches: 0,
    winsSource: 0,
    winsTarget: 0,
    draws: 0,
    lastPlayed: '',
    verdict: '',
}))
const container = ref(null)
let simulation = null
let lastData = null
const isEmpty = ref(false)
const isLoading = ref(false)
const props = defineProps({ period: { type: String, default: 'All' } })
const emit = defineEmits(['node-hover', 'node-click'])
const toNodeInfo = d => ({
    nickname: d.nickname,
    wins: d.wins,
    losses: d.losses,
    draws: d.draws,
    degree: d.degree,
    isCurrent: d.is_current,
})


const emptyMessage = computed(() =>
    props.period === 'All'
    ? "Play some matches to see your network grow"
    : "No matches in this period. Try a wider range"
)


async function renderGraph(data) {
    if(!container.value) return
    d3.select(container.value).selectAll('*').remove()
    if (simulation) simulation.stop()

    if(!data?.nodes?.length || !data?.edges?.length) {
        isEmpty.value = true
        return
    }
    isEmpty.value = false

    

    const W = container.value.clientWidth - 50
    const H = (container.value.clientHeight || 400) - 50

    const svg = d3.select(container.value)
        .append('svg')
        .attr('width', W)
        .attr('height', H)
        // .style('overflow', 'visible')

    const defs = svg.append('defs')
    const filter = defs.append('filter')
        .attr('id', 'glow')
        .attr('x', '-50%')
        .attr('y', '-50%')
        .attr('width', '200%')
        .attr('height', '200%')
    filter.append('feGaussianBlur')
        .attr('stdDeviation', 3)
        .attr('result', 'coloredBlur')

    const feMerge = filter.append('feMerge')
    feMerge.append('feMergeNode').attr('in', 'coloredBlur')
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

    //define radius for nodes by scaleSqrt, based on quantity of unique opponents
    const r = d3.scaleSqrt()
        .domain([0, d3.max(data.nodes, d => d.degree)])
        .range([3, 10])

    const nodeR = d => d.is_current ? r(d.degree) + 2 : r(d.degree)

    //define color by winRate (coral -> sage -> teal)
    const color = d3.scaleLinear()
        .domain([0, 0.5, 1])
        .range(['#F8856D', '#ABC7C3', '#4A8C9B'])

    //edges
    const linkHitEls = svg.append('g')
        .attr('class', 'link-hits')
        .selectAll('line')
        .data(data.edges).join('line')
        .attr('stroke', 'transparent')
        .attr('stroke-width', 10)
        .attr('cursor', 'pointer')
    
    const linkEls = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.edges).join('line')
        .attr('stroke', '#ffffff')
        .attr('stroke-opacity', 0.3)
        .attr('stroke-width', 1)

    //nodes
    const nodeEls = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(data.nodes).join('circle')
        .attr('r', nodeR)
        .attr('fill', d => color (d.wins / (d.wins + d.losses) || 0))
        // .attr('filter', 'url(#glow)')
        .style('cursor', 'grab')

    //drag
    const drag = d3.drag()
        .on('start', function(event, d) {
            if(!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
            d3.select(this).style('cursor', 'grabbing') 
        })
        .on('drag', function(event, d) {
            d.fx = clampX(event.x, d)
            d.fy = clampY(event.y, d)
        })
        .on('end', function(event, d) {
            if(!event.active) simulation.alphaTarget(0.02)
            // simulation.alpha(0.3).restart()
            d.fx = null
            d.fy = null
            d3.select(this).style('cursor', 'grab')
        })

    nodeEls.call(drag)
    nodeEls.on('click', (event, d) => {
        if(!d.is_current) emit('node-click', d.nickname)
    })

    //helper: get neighbors
    function getNeighbors(nodeId) {
        const neighbors = new Set ()
        data.edges.forEach(e => {
            if(e.source.id === nodeId) neighbors.add(e.target.id)
            if(e.target.id === nodeId) neighbors.add(e.source.id)
        })
        return neighbors
    }
    //helper: build verdict
    function buildVerdict(d, meId) {
        const { wins_source, wins_target, source, target } = d
        if(wins_source === wins_target) return 'even'

        if(meId === source.id) {
            return wins_source > wins_target
            ? `${wins_source} - ${wins_target} in your favor`
            : `${wins_target} - ${wins_source} in ${target.nickname}'s favor` 
        }
        if(meId === target.id) {
            return wins_target > wins_source
            ? `${wins_target} - ${wins_source} in your favor`
            : `${wins_source} - ${wins_target} in ${source.nickname}'s favor` 
        }
        const [winnerName, winnerWins, loserWins] = wins_source > wins_target
            ? [source.nickname, wins_source, wins_target]
            : [target.nickname, wins_target, wins_source]
        return `${winnerWins}-${loserWins} to ${winnerName}`
    }

    //helper: tooltip coordinates
    function tooltipXY(event) {
        const rect = container.value.getBoundingClientRect()
        return [event.clientX - rect.left + 12, event.clientY - rect.top + 12]
    }

    const clampX = (x, d) => Math.max(nodeR(d), Math.min(W - nodeR(d), x))
    const clampY = (y, d) => Math.max(nodeR(d), Math.min(H - nodeR(d), y))

    const meId = data.nodes.find(n => n.is_current)?.id
    function highlight(id) {
        const neighbors = getNeighbors(id)
        nodeEls
            .transition().duration(200)
            .attr('fill-opacity', n =>
                n.id === id || neighbors.has(n.id) ? 1 : 0.2
            )
        linkEls
            .transition().duration(200)
            .attr('stroke-opacity', l =>
                l.source.id === id || l.target.id === id ? 0.6 : 0.05
            )

    }

    nodeEls
        .on('mouseover', function(event, d) {
            if(event.buttons) return //do not trigger if it's on drag
            emit('node-hover', toNodeInfo(d))
            highlight(d.id)
        })
        // .on('mousemove', function(event) {
        //     const [x, y] = tooltipXY(event)
        //     tt.value?.show(x, y)
        // })
        .on('mouseout', () => highlight(meId))

    //tooltiop matches on edges  
    linkHitEls
        .on('mouseover', function(event, d) {
            if(event.buttons) return
            const [x, y] = tooltipXY(event)
            const me = userStore.currentUser?.id
            ttEdgeData.sourceName = d.source.nickname
            ttEdgeData.targetName = d.target.nickname
            ttEdgeData.matches = d.matches
            ttEdgeData.winsSource = d.wins_source
            ttEdgeData.winsTarget = d.wins_target
            ttEdgeData.draws = d.draws
            ttEdgeData.lastPlayed = formatShortDate(d.last_played_at)
            ttEdgeData.verdict = buildVerdict(d, me)
            ttEdge.value?.show(x, y)
        })
        .on('mousemove', function(event) {
            const [x, y] = tooltipXY(event)
            ttEdge.value?.show(x, y)
        })
        .on('mouseout', function() {
            ttEdge.value?.hide()
        })

    simulation = d3.forceSimulation(data.nodes)
        .force('link',    d3.forceLink(data.edges)
            .id(d => d.id)
            .distance(d => Math.max(40, 140 - d.matches * 8)))
        .force('charge',  d3.forceManyBody().strength(-300))
        .force('center',  d3.forceCenter(W / 2, H / 2).strength(0.05))
        .force('collide', d3.forceCollide().radius(d => r(d.degree) + 3))
        .force('x', d3.forceX(W / 2).strength(0.06))
        .force('y', d3.forceY(H / 2).strength(0.08))
        .alphaDecay(0.05)
        .alphaMin(0.001)
        .on('tick', () => {
            data.nodes.forEach(d => {
                d.x = clampX(d.x, d)
                d.y = clampY(d.y, d)
            })
            linkEls
                .attr('x1', d=> d.source.x)
                .attr('y1', d=> d.source.y)
                .attr('x2', d=> d.target.x)
                .attr('y2', d => d.target.y)
            linkHitEls
                .attr('x1', d=> d.source.x)
                .attr('y1', d=> d.source.y)
                .attr('x2', d=> d.target.x)
                .attr('y2', d => d.target.y)
            nodeEls
                .attr('cx', d => d.x)
                .attr('cy', d => d.y)
        })

    simulation.alphaTarget(0.02)
    highlight(meId)
}

async function loadGraph() {
    isLoading.value = true
    try {
        const res = await apiFetch(`/api/analytics/player-graph/?period=${props.period.toLowerCase()}`)
        if(!res) return
        const data = await res.json()
        lastData = data
        if (isVisible) renderGraph(data)
        const me = data.nodes?.find(n => n.is_current)
        emit('node-hover', me ? toNodeInfo(me) : null)
    } finally {
        isLoading.value = false
    }
}

watch(() => props.period, () => loadGraph())

useResizeObserver(container, () => {
    if (lastData && isVisible) renderGraph(lastData) }, 200)

let isVisible = false
const visibilityObserver = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return
    isVisible = true
    visibilityObserver.disconnect()
    if (lastData) renderGraph(lastData)
}, { threshold: 0.3 })

onMounted(() => {
    if(container.value) visibilityObserver.observe(container.value)
    loadGraph()
})

onUnmounted(() => visibilityObserver.disconnect())
</script>

<template>
<div class="flex flex-col h-full">
    <div class="mb-4">
        <div>
            <div class="input-label">Player network</div>
            <div class="text-xs text-muted mt-1">Who you've played, and how often</div>
        </div>
    </div>


    <div class="flex-1 relative w-full min-h-[400px]">
        <div ref="container" class="w-full h-full min-h-[400px] flex items-center justify-center overflow-hidden"></div>
        <div v-if="isEmpty" class="absolute inset-0 flex flex-col items-center justify-center gap-2 pointer-events-none">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" class="text-muted/40">
                <circle cx="6" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="18" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/>
                <circle cx="12" cy="18" r="2.5" stroke="currentColor" stroke-width="1.5"/>
                <line x1="7.5" y1="7" x2="11" y2="16" stroke="currentColor" stroke-width="1" stroke-dasharray="2 2"/>
                <line x1="16.5" y1="7" x2="13" y2="16" stroke="currentColor" stroke-width="1" stroke-dasharray="2 2"/>
            </svg>
            <span class="text-sm text-muted">{{ emptyMessage }}</span>
        </div>
        <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
            <div class="w-8 h-8 border-2 border-muted/20 border-t-teal rounded-full animate-spin"></div>
        </div>
        <AppTooltip ref="ttEdge">
            <!-- pair -->
            <div class="flex items-center justify-center gap-1.5 mb-1">
                <span class="text-xs font-medium">{{ ttEdgeData.sourceName }}</span>
                <span class="text-xs text-muted">vs</span>
                <span class="text-xs font-medium">{{ ttEdgeData.targetName }}</span>

            </div>
            <!-- matches -->
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-muted">Matches</span>
                <span class="text-[10px] tabular-nums">{{ ttEdgeData.matches }}</span>
            </div>
            <!-- verdict -->
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-muted">Score</span>
                <span class="text-[10px]">{{ ttEdgeData.verdict }}</span>

            </div>
            <!-- draws (if) -->
            <div v-if="ttEdgeData.draws" class="flex justify-between items-center mb-1">
                <span class="text-[10px]  text-muted">Draws</span>
                <span class="text-[10px] tabular-nums">{{ ttEdgeData.draws }}</span>
            </div>
            <!-- last played -->
            <div class="flex justify-between items-center">
                <span class="text-[10px]  text-muted">Last played</span>
                <span class="text-[10px]">{{ ttEdgeData.lastPlayed }}</span>
            </div>

        </AppTooltip>
    </div>
</div>
</template>