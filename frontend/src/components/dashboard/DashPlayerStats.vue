<script setup>
import AppFilterTabs from '../AppFilterTabs.vue';
import { ref, onMounted, watch, onUnmounted, computed, nextTick, reactive } from 'vue'
import * as d3 from 'd3'
import { apiFetch } from '@/utils/apiFetch.js';
import { calcWinRate } from '@/utils/stats.js';
import AppTooltip from '../AppTooltip.vue';

const tt = ref(null)
const ttData = reactive({ date: 0, wins: 0, losses: 0, total: 0})

const period = ref('All')
const visibleSeries = ref({ wins: true, losses: true, total: true })

const totalWins = computed(() =>chartData.value?.wins?.reduce((s, v) => s + v, 0) ?? 0)
const totalLosses = computed(() => chartData.value?.losses?.reduce((s, v) => s + v, 0) ?? 0)
const winRate = computed(() => calcWinRate(totalWins.value, totalLosses.value))


let resizeObserver = null
let resizeTimer = null
const chartData = ref(null)
const chartEl = ref(null)

function toggleSeries(key) {
    visibleSeries.value[key] = !visibleSeries.value[key]
    drawChart()
}

async function loadData(){
    const res = await apiFetch(`/api/analytics/player-stats/?period=${period.value.toLowerCase()}`)
    if(!res) return
    chartData.value = await res.json()
    // d3.select(chartEl.value).select('svg').remove()
}

 function drawChart() {

    if(!chartData.value) return
    const data = chartData.value
    d3.select(chartEl.value).selectAll('*').remove()


    const el = chartEl.value
    const labels = data.labels
    const { width, height } = el.getBoundingClientRect()
    const margin = { top: 16, right: 16, bottom: 28, left: 12  }
    const W = width - margin.left - margin.right
    const H = height - margin.top - margin.bottom

    const xScale = d3.scalePoint() //dont need to parse the dates like scaleTime in POngUniverse
        .domain(labels)
        .range([0, W])

    // const yMax = d3.max([...data.total, ...data.wins, ...data.losses]) //check max in every array
    const visibleData = []
    if(visibleSeries.value.wins) visibleData.push(...data.wins)//spread oprator for push single array elemnts instead of whole array
    if(visibleSeries.value.losses) visibleData.push(...data.losses)
    if(visibleSeries.value.total) visibleData.push(...data.total)
    const yMax = d3.max(visibleData) || 1
    const yScale = d3.scaleLinear()// (from bottom to top)
        .domain([0, yMax * 1.2])// add 1.2 to leave space on top
        .range([H, 0]) // in svg starts from top to bottom, like we did in pong universe
    
    const svg = d3.select(el)
        .append('svg')
        .attr('width', width)
        .attr('height', height)

    //gradient fill
    const defs = svg.append('defs')

    const winsGrad = defs.append('linearGradient')
        .attr('id', 'grad-wins')
        .attr('x1', '0').attr('y1', '0')
        .attr('x2', '0').attr('y2', '1')

    winsGrad.append('stop')
        .attr('offset', '0')
        .attr('stop-color', '#4A8C9B')
        .attr('stop-opacity', 0.3)

    winsGrad.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#4A8C9B')
        .attr('stop-opacity', 0)

    const lossesGrad = defs.append('linearGradient')
        .attr('id', 'grad-losses')
        .attr('x1', '0').attr('y1', '0')
        .attr('x2', '0').attr('y2', '1')

    lossesGrad.append('stop')
        .attr('offset', '0')
        .attr('stop-color', '#F8856D')
        .attr('stop-opacity', 0.3)


    lossesGrad.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#F8856D')
        .attr('stop-opacity', 0)
    

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)

    //vertical line
    const yTicks = yScale.ticks(4) // just some number of ticks
    g.selectAll('grid')
        .data(yTicks)
        .join('line')
        .attr('x1', 0).attr('x2', W)
        .attr('y1', d => yScale(d)).attr('y2', d => yScale(d))
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-dasharray', '1.8')

    //generation of coordinates
    const lineGen = d3.line() //creates coordinates for x,Y
        .x((_, i) => xScale(labels[i])) // since we need just its number, not a valu, we put it like '_', i
        .y(d => yScale(d)) // here we rake the value
        // .curve(d3.curveCatmullRom.alpha(0.05))
        .curve(d3.curveMonotoneX)

    //area generation (for fill)
    const areaGen = d3.area()
        .x((_, i) => xScale(labels[i]))
        .y0(H)
        .y1(d => yScale(d))
        .curve(d3.curveMonotoneX)

    if(visibleSeries.value.wins) {
        g.append('path')
            .datum(data.wins) //creates array of elemnts, instead of one element for every value (like in data())
            .attr('fill', 'url(#grad-wins)')
            .attr('stroke', 'none')
            .attr('d', areaGen)
        g.append('path')
            .datum(data.wins) //creates array of elemnts, instead of one element for every value (like in data())
            .attr('fill', 'none')
            .attr('stroke', '#4A8C9B')
            .attr('stroke-width', 0.5)
            .attr('d', lineGen)
    }

    if(visibleSeries.value.losses) {
        g.append('path')
            .datum(data.losses) //creates array of elemnts, instead of one element for every value (like in data())
            .attr('fill', 'url(#grad-losses)')
            .attr('stroke', 'none')
            .attr('d', areaGen)
        g.append('path')
            .datum(data.losses) //creates array of elemnts, instead of one element for every value (like in data())
            .attr('fill', 'none')
            .attr('stroke', '#F8856D')
            .attr('stroke-width', 0.5)
            .attr('d', lineGen)
    }

    if(visibleSeries.value.total) {
        g.append('path')
            .datum(data.total) //creates array of elemnts, instead of one element for every value (like in data())
            .attr('fill', 'none')
            .attr('stroke', '#ABC7C3')
            .attr('stroke-width', 0.5)
            .attr('stroke-dasharray', '2.5')
            .attr('d', lineGen)
    }

    ///////////////LeftLine
    g.append('line')
        .attr('x1', 0).attr('x2', 0)
        .attr('y1', 0).attr('y2', H)
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-width', 1)


    ///////////////Bottob line with dates
    const MAX_LABELS = 10

    const xAxis = d3.axisBottom(xScale)
        .tickSize(-H)

    const axisG = g.append('g')
        .attr('transform', `translate(0, ${H})`)
        .call(xAxis)

    const ticks = axisG.selectAll('.tick')
    
    ticks.select('line')
        .attr('stroke', 'rgba(255,255,255,0.07)')
    ticks.select('text')
        .attr('fill', 'rgba(255,255,255,0.3)')
        .attr('font-size', '10px')
        .attr('dy', '1.2em')
    ticks.style('display', labels.length > MAX_LABELS ? 'none' : null)
    
    axisG.select('.domain')
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-width', 1)

    // axisG.selectAll('text')
    //     .attr('fill', 'rgba(255,255,255,0.3)')
    //     .attr('font-size', '10px')
    //     .attr('dy', '1.2em')
    //     .style('display', labels.length > MAX_LABELS ? 'none' : null)

    //helpline for tooltip
    const hoverLine = g.append('line')
        .attr('y1', 0)
        .attr('y2', H)
        .attr('stroke', 'rgba(255,255,255,0.2)')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '3.3')
        .attr('opacity', 0)

    //invisible hover dots for tooltip




    labels.forEach((label, i) => {
        const x = xScale(label)
        const yVal = visibleSeries.value.total ? data.total[i]
                    : visibleSeries.value.wins ? data.wins[i]
                    :data.losses[i]
        g.append('circle')
            .attr('cx', x)
            .attr('cy', yScale(yVal))
            .attr('r', 10)
            .attr('fill', 'transparent') 
            .style('cursor', 'crosshair')
            .on('mouseover', () => {
                if(!tt.value) return
                ttData.date = label
                ttData.wins = data.wins[i]
                ttData.losses = data.losses[i]
                ttData.total = data.total[i]
                const tooltipX = (margin.left + x) + 16
                const tooltipY = margin.top + yScale(yVal) - 10
                hoverLine
                    .attr('x1', x).attr('x2', x)
                    .attr('opacity', 1)
                    .transition().duration(80)
                    .attr('x1', x).attr('x2', x)
                tt.value.show(tooltipX, tooltipY)
            })
            .on('mouseout', () => {
                hoverLine.attr('opacity', 0)
                tt.value?.hide()
            })
    })
}

onMounted(() => {
    loadData()
    resizeObserver = new ResizeObserver(() => {
        clearTimeout(resizeTimer)
        resizeTimer = setTimeout(() => drawChart(), 200)
    })
    resizeObserver.observe(chartEl.value)
})

watch(period, loadData)
watch(chartData, async () => {
    await nextTick()
    drawChart()
})

onUnmounted(() => {
    resizeObserver?.disconnect()
})

</script>

<template>
    <div>
        <!-- строка 1: заголовок + фильтр периода -->
        <div class="flex items-center justify-between mb-2">
            <div class="input-label">Player Stats</div>
            <AppFilterTabs v-model="period" :options="['7d', '30d', 'All']" />
        </div>
        <!-- строка 3: график -->
         <div class="relative">
            <div ref="chartEl" class=" h-64" />
            <AppTooltip ref="tt">
                <div class="text-xs font-medium mb-2 pb-2 border-b border-white/[0.07]"> {{ ttData.date }}</div>
                <div class="flex justify-between gap-4 mb-1">
                    <span class="text-[10px] text-muted">Wins</span>
                    <span class="text-[10px] text-teal">{{ ttData.wins }}</span>
                </div>
                <div class="flex justify-between gap-4 mb-1 ">
                    <span class="text-[10px] text-muted">Losses</span>
                    <span class="text-[10px] text-coral">{{ ttData.losses }}</span>
                </div>
                <div class="flex justify-between gap-4 mb-1 ">
                    <span class="text-[10px] text-muted">Total</span>
                    <span class="text-[10px] text-sage">{{ ttData.total }}</span>
                </div>

            </AppTooltip>
         </div>
        <div class="flex items-center justify-between mt-6">
            <div class="flex items-center gap-6 text-sm text-muted">
                <span>Wins <span class="text-teal font-medium">{{ totalWins }}</span></span>
                <span class="opacity-30">|</span>
                <span>Losses <span class="text-coral font-medium">{{ totalLosses }}</span></span>
                <span class="opacity-30">|</span>
                <span>Win Rate <span class="text-sage font-medium">{{ winRate }}%</span></span>
            </div>
            <div class="flex gap-4">
                <button v-for="s in ['wins', 'losses', 'total']"
                    :key="s"
                    @click="toggleSeries(s)"
                    :class="['flex items-center gap-1.5 text-xs text-muted transition-opacity cursor-pointer',
                    visibleSeries[s] ? 'opacity-100' : 'opacity-30']"
                >
                    <span :class="[
                        'w-2 h-2 rounded-full',
                        s === 'wins'   ? 'bg-teal'  : '',
                        s === 'losses' ? 'bg-coral' : '',
                        s === 'total'  ? 'bg-sage'  : ''
                    ]" />
                    {{ s }}
                </button>
            </div>
        </div>
    </div>
</template>
                
                
