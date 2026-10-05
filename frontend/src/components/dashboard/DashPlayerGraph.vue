<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import * as d3 from 'd3'
import AppTooltip from '../AppTooltip.vue'
import { apiFetch } from '@/utils/apiFetch'

const userStore = useUserStore()
const tt = ref(null)
const ttData = reactive(({ type: '', index: '', player: '', color: ''}))
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

    //get neighbors
    function getNeighbors(nodeId) {
        const neighbors = new Set ()
        data.edges.forEach(e => {
            if(e.source.id === nodeId) neighbors.add(e.target.id)
            if(e.target.id === nodeId) neighbors.add(e.source.id)
        })
        return neighbors
    }

    nodeEls
        .on('mouseover', function(event, d) {
            if(event.buttons) return //do not trigger if it's on drag
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
        .on('mouseout', function() {
            nodeEls
                .transition().duration(200)
                .attr('fill-opacity', 0.85)
            linkEls
                .transition().duration(200)
                .attr('stroke-opacity', 0.3)
        })

    simulation = d3.forceSimulation(data.nodes)
        .force('link',    d3.forceLink(data.edges).id(d => d.id).distance(100))
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
        <div class="flex justify-between items-center mb-2">
            <div class="text-xs font-medium" :style="{ color: ttData.color }">{{ ttData.type }}</div>
            <span class="text-[10px] text-muted ml-2">{{ ttData.index }}</span>
        </div>
        <div class="flex justify-between items-center mb-1">
            <span class="text-[10px] text-muted">Player</span>
            <span class="text-[10px]">{{ ttData.player }}</span>
        </div>
    </AppTooltip>
</div>
</template>