<script setup>
import { ref, onMounted, onBeforeUnmount, onUnmounted, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import * as d3 from 'd3'
import AppTooltip from '../AppTooltip.vue'
import AppTooltipRow from '../AppTooltipRow.vue'
import { apiFetch } from '@/utils/apiFetch'
import { formatShortDate } from '@/utils/date.js'
import { useResizeObserver } from '@/composables/useResizeObserver.js'




// Player connection graph: the current player, their opponents and the opponents' opponents (2 hops).
// - d3 force simulation keeps a slight "breathing" motion (alphaTarget 0.02); dragged nodes are released on drag end.
// - Node radius grows with the number of unique opponents (scaleSqrt), color shows win rate (coral -> sage -> teal).
// - Desktop: hover highlights a node with its links. Touch: a tap does the same and updates the info card.

//highlight: hovered node + its neighbors are active, the res is dimmed
const NODE_ACTIVE = 1
const NODE_DIM = 0.45
const LINK_ACTIVE = 0.6
const LINK_DIM = 0.12


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
const emit = defineEmits(['node-hover', 'node-click'])
const toNodeInfo = d => ({
    nickname: d.nickname,
    wins: d.wins,
    losses: d.losses,
    draws: d.draws,
    degree: d.degree,
    isCurrent: d.is_current,
})
const isTouchDevice = () => window.matchMedia('(hover: none)').matches



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
    if (W <= 0) return //no size yet: useResizeObserver redraws when it appears

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
        //no hover on touch devices: a tap selects the node
        if(isTouchDevice()) {
            emit('node-hover', toNodeInfo(d))
            highlight(d.id)
            return
        }
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
        return [event.clientX - rect.left, event.clientY - rect.top]
    }

    const clampX = (x, d) => Math.max(nodeR(d), Math.min(W - nodeR(d), x))
    const clampY = (y, d) => Math.max(nodeR(d), Math.min(H - nodeR(d), y))

    const meId = data.nodes.find(n => n.is_current)?.id
    function highlight(id) {
        const neighbors = getNeighbors(id)
        nodeEls
            .transition().duration(200)
            .attr('fill-opacity', n =>
                n.id === id || neighbors.has(n.id) ? NODE_ACTIVE : NODE_DIM
            )
        linkEls
            .transition().duration(200)
            .attr('stroke-opacity', l =>
                l.source.id === id || l.target.id === id ? LINK_ACTIVE : LINK_DIM
            )
    }

    nodeEls
        .on('mouseover', function(event, d) {
            if(event.buttons || isTouchDevice()) return //do not trigger if it's on drag or emulated by a tap
            emit('node-hover', toNodeInfo(d))
            highlight(d.id)
        })
        // .on('mousemove', function(event) {
        //     const [x, y] = tooltipXY(event)
        //     tt.value?.show(x, y)
        // })
        .on('mouseout', () => {
            if(!isTouchDevice()) highlight(meId)
        })

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
        const res = await apiFetch(`/api/analytics/player-graph/`)
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

//stops ticks before the svg is removed from DOM
onBeforeUnmount(() => { if (simulation) simulation.stop() })
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
        <span class="text-sm text-muted">Play some matches to see your network grow</span>        </div>
        <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
            <div class="w-8 h-8 border-2 border-muted/20 border-t-teal rounded-full animate-spin"></div>
        </div>
        <AppTooltip ref="ttEdge">
            <!-- pair: plain inline text, so long nicknames wrap instead of overflowing -->
            <div class="text-xs font-medium text-left break-words mb-2 pb-2 border-b border-white/[0.07]">
                {{ ttEdgeData.sourceName }}
                <span class="text-muted font-normal">vs</span>
                {{ ttEdgeData.targetName }}
            </div>
            
            <AppTooltipRow label="Matches" :value="ttEdgeData.matches" />
            <AppTooltipRow label="Score" :value="ttEdgeData.verdict" />
            <AppTooltipRow v-if="ttEdgeData.draws" label="Draws" :value="ttEdgeData.draws" />
            <AppTooltipRow label="Last played" :value="ttEdgeData.lastPlayed" />
        </AppTooltip>
    </div>
</div>
</template>