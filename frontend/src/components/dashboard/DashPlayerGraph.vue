<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import * as d3 from 'd3'
import AppTooltip from '../AppTooltip.vue'
import { apiFetch } from '@/utils/apiFetch'
import { formatShortDate } from '@/utils/date.js'




// Player Connection Graph (ego-network, 2-hop).

// Design decisions:
// - Hosted inside DashboardView as a top section, not a separate /dashboard/graph page.
//   Reason: keeps all analytics in one place; graph is first for screenshot/demo visibility.
// - MatchEchoViz copied as skeleton (drag/hover/tooltip paradigm reused).
//   Force-simulation params retuned for network graph (distance 100, charge -300).
// - "Breathing" effect via alphaTarget(0.02) + alphaMin(0.001) — mimics Obsidian.
// - Drag releases fx/fy on end (Obsidian-style): nodes stay in flow, not pinned.
// - Glow via SVG filter in <defs>; applied to nodes as filter="url(#glow)".
// - Node radius: scaleSqrt(degree), range [5,20], +4px bonus for current user.
// - Node color: diverging scale coral→sage→teal by winRate (0 → 0.5 → 1).
// - Edge thickness fixed at 1px (scaled width postponed — see "Future" below).

// Known limitations:
// - Resize observer not re-added yet (was tied to old props-based renderViz).
//   Graph does not re-render on container resize. TODO 
// - Tooltip (AppTooltip) kept from skeleton but not yet wired to graph data.
//   Content template still shows event-type fields — to be remapped in Step 5
//   to show nick / W-L / winRate / degree.

// Future (deferred by plan):
// - Period filter (7d/30d/all) via AppFilterTabs — Step 5.
// - Edge thickness scaled by edges[].matches — Step 5.
// - Empty state message ("Play some matches to see your network grow") — Step 5.
// - Loader during fetch — Step 5.
// - Click node → navigate to player profile — out of 2-day scope.
// - Zoom/pan — out of 2-day scope.
// - WS realtime update on match_finished — out of 2-day scope.






const userStore = useUserStore()
const tt = ref(null)
const ttData = reactive(({ 
    nickname: '', 
    avatar: null,
    wins: 0,
    losses: 0,
    draws: 0,
    winRate: null,
    degree: 0,
    isCurrent: false,  
    }))
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
const isEmpty = ref(false)


async function renderGraph(data) {
    if(!container.value) return
    if(!data?.nodes?.length) {
        isEmpty.value = true
        return
    }
    isEmpty.value = false

    
    d3.select(container.value).selectAll('*').remove()
    if (simulation) simulation.stop()

    const W = container.value.clientWidth - 50
    const H = (container.value.clientHeight || 400) - 50

    const svg = d3.select(container.value)
        .append('svg')
        .attr('width', W)
        .attr('height', H)
        .style('overflow', 'visible')

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
        .range([5, 20])

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
        .attr('r', d => d.is_current ? r(d.degree) + 4 : r(d.degree))
        .attr('fill', d => color (d.wins / (d.wins + d.losses) || 0))
        .attr('filter', 'url(#glow)')
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
            d.fx = event.x
            d.fy = event.y
        })
        .on('end', function(event, d) {
            if(!event.active) simulation.alphaTarget(0.02)
            // simulation.alpha(0.3).restart()
            d.fx = null
            d.fy = null
            d3.select(this).style('cursor', 'grab')
        })

    nodeEls.call(drag)

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

    nodeEls
        .on('mouseover', function(event, d) {
            if(event.buttons) return //do not trigger if it's on drag
            const total = d.wins + d.losses
            const [x, y] = tooltipXY(event)
            ttData.nickname = d.nickname
            ttData.avatar = d.avatar
            ttData.wins = d.wins
            ttData.losses = d.losses
            ttData.draws = d.draws
            ttData.winRate = total > 0 ? d.wins / total : null
            ttData.degree = d.degree
            ttData.isCurrent = d.is_current
            tt.value?.show(x, y)

            const neighbors = getNeighbors(d.id)

            nodeEls
                .transition().duration(200)
                .attr('fill-opacity', n =>
                    n.id === d.id || neighbors.has(n.id) ? 1 : 0.2
                )
            linkEls
                .transition().duration(200)
                .attr('stroke-opacity', l =>
                    l.source.id === d.id || l.target.id === d.id ? 0.6 : 0.05
                )
        })
        .on('mousemove', function(event) {
            const [x, y] = tooltipXY(event)
            tt.value?.show(x, y)
        })
        .on('mouseout', function() {
            tt.value?.hide()
            nodeEls
                .transition().duration(200)
                .attr('fill-opacity', 0.85)
            linkEls
                .transition().duration(200)
                .attr('stroke-opacity', 0.3)
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
        .force('collide', d3.forceCollide().radius(d => r(d.degree) + 5))
        .alphaDecay(0.01)
        .alphaMin(0.001)
        .on('tick', () => {
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
}



onMounted(async () => {
    const res = await apiFetch('/api/analytics/player-graph/?period=all')
    if(!res) return
    const data = await res.json()
    renderGraph(data)
})

</script>

<template>
<div class="relative w-full h-full min-h-[400px]">
    <div ref="container" class="w-full h-full min-h-[400px] flex items-center justify-center"></div>
    <div v-if="isEmpty" class="absolute inset-0 flex items-center justify-center">
        <span class="text-sm text-muted"> No events recorded - match was stopped early</span>
    </div>
    <AppTooltip ref="tt">
        <!-- Avatar -->
        <div class="flex items-center gap-2 mb-2">
            <img
                v-if="ttData.avatar"
                :src="ttData.avatar"
                class = "w-6 h-6 rounded-full object-cover"
                alt=""></img>
            <div
                v-else
                class="w-6 h-6 rounded-full bg-muted/30 flex items-center justify-center text-[10px]">
            {{ ttData.nickname?.[0]?.toUpperCase() }}
            </div>
            <span class="text-xs font-medium"> {{ ttData.nickname }}</span>
            <span
                v-if="ttData.isCurrent"
                class="text-[9px] px-1.5 py-0.5 rounded bg-teal/20 text-teal uppercase tracking-wide">you</span>
        </div>

        <!-- WLD -->
        <div class="flex justify-between items-center mb-1">
            <span class="text-[10px] text-muted">Record</span>
            <span class="text-[10px] tabular-nums">
                {{ ttData.wins }}-{{ ttData.losses }}<span v-if="ttData.draws">-{{ ttData.draws }}</span>
            </span>
        </div>

        <!-- WinRate -->
         <div class="flex justify-between items-center mb-1">
            <span class="text-[10px] text-muted">Win rate</span>
            <span class="text-[10px] tabular-nums">
                {{ ttData.winRate === null ? '-' : (ttData.winRate * 100).toFixed(0) + '%' }}
            </span>
        </div>

        
        <!-- Degree -->
        <div class="flex justify-between items-center">
            <span class="text-[10px] text-muted">Opponents</span>
            <span class="text-[10px] tabular-nums">{{ ttData.degree }}</span>
        </div>
    </AppTooltip>
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
</template>