<script setup>
import { ref, onMounted, onUnmounted, watch, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import * as d3 from 'd3'
import AppTooltip from '../AppTooltip.vue'
// import { apiFetch } from '@/utils/apiFetch'

const props = defineProps({
    match:  { type: Object, default: null },
    events: { type: Array,  default: () => [] }
})

const userStore = useUserStore()
const tt = ref(null)
const ttData = reactive(({ type: '', index: '', player: '', react: '', color: ''}))


// const tooltip  = ref(null)
// const ttName   = ref(null)
// const ttIndex  = ref(null)
// const ttReact  = ref(null)
// const ttPlayer = ref(null)
const container = ref(null)
let simulation = null

async function renderViz(match, events) {
    if (!match || !container.value || !events.length) return

    d3.select(container.value).selectAll('*').remove()
    if (simulation) simulation.stop()

    const W = container.value.clientWidth - 50
    const H = (container.value.clientHeight || 400) - 50

    // const profileResponse = await apiFetch('/api/users/profile/')
    // const profile = await profileResponse.json()
    const currentUserId   =  userStore.currentUser.id
    const currentUserName = userStore.currentUser.nickname ?? userStore.currentUser.username ?? 'You'

    const nodes = events.map((e, i) => ({
        id: i,
        type: e.event_type,
        player: e.player,
        playerName: e.player === currentUserId ? currentUserName : match.opponent_nickname,
        posY: e.pos_y ?? 0.5,
        react: e.reaction_time_ms,
        color: e.event_type === 'goal' ? '#4A8C9B'
            :  e.event_type === 'miss' ? '#F8856D'
            : '#ABC7C3',
        radius: e.event_type === 'goal' ? 14 : 7,
    }))

    const links = events.slice(0, -1).map((_, i) => ({
        source: i,
        target: i + 1
    }))

    nodes.forEach(n => {
        n.x = W / 2 + (Math.random() - 0.5) * 80
        n.y = H / 2 + (Math.random() - 0.5) * 80
    })

    const svg = d3.select(container.value)
        .append('svg')
        .attr('width', W)
        .attr('height', H)
        .style('overflow', 'visible')

    const linkEls = svg.append('g')
        .selectAll('path')
        .data(links).join('path')
        .attr('fill', 'none')
        .attr('stroke', '#ffffff')
        .attr('stroke-opacity', 0.15)
        .attr('stroke-width', 0.5)

    const TYPE_NAMES = { goal: 'Goal scored', hit: 'Hit / save', miss: 'Miss / out' }

    const nodeEls = svg.append('g')
        .selectAll('circle')
        .data(nodes).join('circle')
        .attr('r', d => d.radius)
        .attr('fill', d => d.color)
        .attr('fill-opacity', 0.85)
        .style('cursor', 'grab')

    svg.append('circle')
        .attr('r', nodes[0].radius + 6)
        .attr('fill', 'none')
        .attr('stroke', '#ABC7C3')
        .attr('stroke-opacity', 0.5)
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '3,3')
        .attr('class', 'start-ring')

    // ── DRAG ──────────────────────────────────────────────
    const drag = d3.drag()
        .on('start', function(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
            d3.select(this).style('cursor', 'grabbing')
        })
        .on('drag', function(event, d) {
            d.fx = event.x
            d.fy = event.y
        })
        .on('end', function(event, d) {
            if (!event.active) simulation.alphaTarget(0)
            // d.fx = null  
            // d.fy = null
            simulation.alpha(0.3).restart()
            d3.select(this).style('cursor', 'grab')
        })

    nodeEls.call(drag)
    // ──────────────────────────────────────────────────────

    nodeEls
    .on('mouseover', function(event, d) {
        // не показываем тултип во время drag
        if (event.buttons) return

        const prev = d.id - 1
        const next = d.id + 1

        nodeEls
            .transition().duration(200)
            .attr('fill-opacity', n =>
                n.id === d.id || n.id === prev || n.id === next ? 1 : 0.15
            )
            .attr('r', n =>
                n.id === d.id               ? n.radius * 2.2
                : n.id === prev || n.id === next ? n.radius * 1.5
                : n.radius
            )

        linkEls
            .transition().duration(200)
            .attr('stroke-opacity', l =>
                (l.source.id === prev && l.target.id === d.id) ||
                (l.source.id === d.id && l.target.id === next) ? 0.45 : 0.04
            )
            .attr('stroke-width', l =>
                (l.source.id === prev && l.target.id === d.id) ||
                (l.source.id === d.id && l.target.id === next) ? 1.2 : 0.5
            )

            
        ttData.type   = TYPE_NAMES[d.type]
        ttData.color   = d.color
        ttData.index = `#${d.id + 1}`
        ttData.player = d.playerName
        ttData.react  = d.react ? `${d.react} ms` : '—'
        tt.value.show(W-220, 16)
        // tooltip.value.style.opacity = 1
    })
    .on('mouseout', function() {
        nodeEls
            .transition().duration(200)
            .attr('fill-opacity', 0.85)
            .attr('r', n => n.radius)

        linkEls
            .transition().duration(200)
            .attr('stroke-opacity', 0.15)
            .attr('stroke-width', 0.5)

        tt.value.hide()
        // tooltip.value.style.opacity = 0
    })

    function curvePath(d) {
        const sx = d.source.x, sy = d.source.y
        const tx = d.target.x, ty = d.target.y
        const dx = tx - sx, dy = ty - sy
        const len = Math.sqrt(dx*dx + dy*dy) || 1
        const k  = len * 0.28
        const cx = (sx + tx) / 2 - (dy / len) * k
        const cy = (sy + ty) / 2 + (dx / len) * k
        return `M${sx} ${sy} Q${cx} ${cy} ${tx} ${ty}`
    }

    // tooltip.value.style.left = (W - 220) + 'px'
    // tooltip.value.style.top  = '16px'

    simulation = d3.forceSimulation(nodes)
        .force('link',    d3.forceLink(links).id(d => d.id).distance(60))
        .force('charge',  d3.forceManyBody().strength(-40))
        .force('center',  d3.forceCenter(W / 2, H / 2))
        .force('collide', d3.forceCollide(d => d.radius + 3.5))
        .force('px',      d3.forceX(d => d.player === currentUserId ? W * 0.28 : W * 0.72).strength(0.07))
        .on('tick', () => {
            nodes.forEach(n => {
                n.x = Math.max(n.radius + 5, Math.min(W - n.radius - 5, n.x))
                n.y = Math.max(n.radius + 5, Math.min(H - n.radius - 5, n.y))
            })
            svg.selectAll('path').attr('d', curvePath)
            nodeEls.attr('cx', d => d.x).attr('cy', d => d.y)
            svg.select('.start-ring')
                .attr('cx', nodes[0].x)
                .attr('cy', nodes[0].y)
        })
    }

let resizeTimer = null
const resizeObserver = new ResizeObserver(() => {
    clearTimeout(resizeTimer)
    resizeTimer = setTimeout(() => {
        if (props.match) renderViz(props.match, props.events)
    }, 200)
})

onMounted(() => {
    resizeObserver.observe(container.value)
    renderViz(props.match, props.events)
})
watch(() => props.events, (newEvents) => renderViz(props.match, newEvents))
onUnmounted(() => {
    resizeObserver.disconnect()
    if (simulation) simulation.stop()
})
</script>

<template>
<div class="relative w-full min-h-[400px]">
    <div ref="container" class="w-full min-h-[400px]"></div>
    <AppTooltip ref="tt">
        <div class="flex justify-between items-center mb-2">
            <div class="text-xs font-medium" :style="{ color: ttData.color }">{{ ttData.type }}</div>
            <span class="text-[10px] text-muted ml-2">{{ ttData.index }}</span>
        </div>
        <div class="flex justify-between items-center mb-1">
            <span class="text-[10px] text-muted">Player</span>
            <span class="text-[10px]">{{ ttData.player }}</span>
        </div>
        <div class="flex justify-between gap-4">
            <span class="text-[10px] text-muted">Reaction</span>
            <span class="text-[10px]">{{ ttData.react }}</span>
        </div>
    </AppTooltip>
    <!-- <div ref="tooltip"
        class="absolute pointer-events-none opacity-0 transition-opacity duration-100 z-20"
        style="top:0;left:0">
        <div class="bg-[rgba(15,22,41,0.97)] border border-white/[0.11] rounded-xl px-4 py-3 min-w-[160px]">
            <div class="flex justify-between items-center mb-2">
                <div ref="ttName" class="text-xs font-medium flex-1"></div>
                <span ref="ttIndex" class="text-[10px] text-muted ml-2"></span>
            </div>
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-muted">Player</span>
                <span ref="ttPlayer" class="text-[10px]"></span>
            </div>
            <div class="flex justify-between gap-4">
                <span class="text-[10px] text-muted">Reaction</span>
                <span ref="ttReact" class="text-[10px]"></span>
            </div>
        </div>
    </div> -->
</div>
</template>