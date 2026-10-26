<script setup>
import { ref, onMounted, watch, computed, reactive } from 'vue'
import * as d3 from 'd3'
import AppTooltip from '../AppTooltip.vue';
import AppTooltipRow from '../AppTooltipRow.vue';

import { useMatchesStore } from '@/stores/matches.js';
import { filterByPeriod, PERIOD_DAYS } from '@/utils/period.js';
import { useResizeObserver } from '@/composables/useResizeObserver.js';
import { rollingWinRate } from '@/utils/stats.js';
import AppFilterTabs from '../AppFilterTabs.vue';


const WINDOW = 10 //for matches in the rolling window
const MIN_POINTS = 3
const period = ref('All')
const tt = ref(null)
const ttData = reactive({ date: '', rate: 0, result: 0, dayCount: 0, full: true})
const chartEl = ref(null)
const matchesStore = useMatchesStore()
const points = computed(() => filterByPeriod(rollingWinRate(matchesStore.matches, WINDOW), 'date', period.value))
const isEmpty = computed(() => points.value.length < MIN_POINTS)


function drawChart() {
    const el = chartEl.value
    if (!el) return
    d3.select(el).selectAll('*').remove()
    if (isEmpty.value) return

    const data = points.value
    const { width, height } = el.getBoundingClientRect()
    const margin = { top: 12, right: 12, bottom: 24, left: 36 }
    const W = width - margin.left - margin.right
    const H = height - margin.top - margin.bottom
    const GAP = 12
    const rateH = Math.round(H * 0.72)   // top zone: win rate
    const volTop = rateH + GAP           // bottom zone: volume
    const volH = H - volTop

    // volume buckets: days for 7d/30d, weeks for All
    const interval = period.value === 'All' ? d3.timeWeek : d3.timeDay
    const now = new Date()
    const start = period.value === 'All'
        ? interval.floor(data[0].date)
        : d3.timeDay.floor(d3.timeDay.offset(now, -PERIOD_DAYS[period.value]))
    const x = d3.scaleTime()
        .domain([start, interval.ceil(now)])
        .range([0, W])

    const buckets = d3.rollups(data, v => v.length, p => +interval.floor(p.date))
        .map(([t, count]) => ({ start: new Date(t), count }))
    const dayCounts = d3.rollup(data, v => v.length, p => +d3.timeDay.floor(p.date))

    const yRate = d3.scaleLinear().domain([0, 100]).range([rateH, 0])
    const yVol = d3.scaleLinear()
        .domain([0, d3.max(buckets, b => b.count)])
        .range([volH, 0])

    const svg = d3.select(el)
        .append('svg')
        .attr('width', width)
        .attr('height', height)

    const grad = svg.append('defs').append('linearGradient')
        .attr('id', 'grad-rate')
        .attr('x1', 0).attr('y1', 0)
        .attr('x2', 0).attr('y2', 1)
    grad.append('stop').attr('offset', '0%').attr('stop-color', '#4A8C9B').attr('stop-opacity', 0.25)
    grad.append('stop').attr('offset', '100%').attr('stop-color', '#4A8C9B').attr('stop-opacity', 0)

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)

    // 50% line: above it - winning more than losing
    g.append('line')
        .attr('x1', 0).attr('x2', W)
        .attr('y1', yRate(50)).attr('y2', yRate(50))
        .attr('stroke', 'rgba(255,255,255,0.15)')
        .attr('stroke-dasharray', '2 3')

    g.selectAll('.rate-label')
        .data([0, 50, 100])
        .join('text')
        .attr('class', 'rate-label')
        .attr('x', -8)
        .attr('y', d => yRate(d))
        .attr('dy', '0.32em')
        .attr('text-anchor', 'end')
        .attr('fill', 'rgba(255,255,255,0.3)')
        .attr('font-size', '10px')
        .text(d => d + '%')

    // bottom of the rate zone
    g.append('line')
        .attr('x1', 0).attr('x2', W)
        .attr('y1', rateH).attr('y2', rateH)
        .attr('stroke', 'rgba(255,255,255,0.07)')

    const area = d3.area()
        .x(p => x(p.date))
        .y0(rateH)
        .y1(p => yRate(p.rate))
        .curve(d3.curveMonotoneX)

    const line = d3.line()
        .x(p => x(p.date))
        .y(p => yRate(p.rate))
        .curve(d3.curveMonotoneX)

    g.append('path')
        .datum(data)
        .attr('fill', 'url(#grad-rate)')
        .attr('d', area)

    // whole line dashed, then solid on top where the window is full
    g.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#4A8C9B')
        .attr('stroke-width', 1.5)
        .attr('stroke-dasharray', '3 3')
        .attr('d', line)
    g.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#4A8C9B')
        .attr('stroke-width', 1.5)
        .attr('d', line.defined(p => p.full))

    // volume bars
    g.append('g')
        .attr('transform', `translate(0, ${volTop})`)
        .selectAll('rect')
        .data(buckets)
        .join('rect')
        .attr('x', b => x(b.start))
        .attr('width', b => Math.max(1, x(interval.offset(b.start, 1)) - x(b.start) - 2))
        .attr('y', b => yVol(b.count))
        .attr('height', b => volH - yVol(b.count))
        .attr('fill', 'rgba(171,199,195,0.25)')

    // dates under the volume zone
    const xAxis = d3.axisBottom(x)
        .ticks(period.value === '7d' ? 7 : 5)
        .tickFormat(d3.timeFormat(period.value === 'All' ? '%b' : '%d %b'))
        .tickSize(0)
    g.append('g')
        .attr('transform', `translate(0, ${H})`)
        .call(xAxis)
        .call(a => a.select('.domain').attr('stroke', 'rgba(255,255,255,0.1)'))
        .selectAll('text')
        .attr('fill', 'rgba(255,255,255,0.3)')
        .attr('font-size', '10px')
        .attr('dy', '1.2em')

    // crosshair: snaps to the nearest match
    const hoverLine = g.append('line')
        .attr('y1', 0).attr('y2', H)
        .attr('stroke', 'rgba(255,255,255,0.2)')
        .attr('stroke-dasharray', '3 3')
        .attr('opacity', 0)
    const hoverDot = g.append('circle')
        .attr('r', 3.5)
        .attr('fill', '#4A8C9B')
        .attr('opacity', 0)

    const bisect = d3.bisector(p => p.date).center
    // const TT_W = 170

    // transparent layer on top catches the mouse over the whole chart
    g.append('rect')
        .attr('width', W)
        .attr('height', H)
        .attr('fill', 'transparent')
        .style('cursor', 'crosshair')
        .on('mousemove', event => {
            const [mx] = d3.pointer(event)
            const p = data[bisect(data, x.invert(mx))]
            const px = x(p.date)
            const py = yRate(p.rate)
            hoverLine.attr('x1', px).attr('x2', px).attr('opacity', 1)
            hoverDot.attr('cx', px).attr('cy', py).attr('opacity', 1)

            ttData.date = d3.timeFormat('%d %b %Y')(p.date)
            ttData.rate = p.rate
            ttData.result = p.result
            ttData.dayCount = dayCounts.get(+d3.timeDay.floor(p.date))
            ttData.full = p.full

            // const tx = px + TT_W + 16 > W
            //     ? margin.left + px - TT_W - 16
            //     : margin.left + px + 16
            tt.value?.show(margin.left + px, margin.top + py)
        })
        .on('mouseleave', () => {
            hoverLine.attr('opacity', 0)
            hoverDot.attr('opacity', 0)
            tt.value?.hide()
        })
}

watch(points, drawChart)
useResizeObserver(chartEl, drawChart, 200)
onMounted(drawChart)
</script>


<template>
    <div class="flex flex-col h-full">
        <!-- header: title + period tabs, same height and line as Recent Matches -->
        <div class="flex items-center justify-between gap-4 h-11 border-b border-white/[0.07]">
            <div class="input-label">Player Stats</div>
            <AppFilterTabs v-model="period" :options="['7d', '30d', 'All']" class="no-capture" />
        </div>

        <!-- legend -->
        <div class="flex gap-4 text-xs text-muted py-3 mb-1">
            <span class="flex items-center gap-1.5">
                <span class="w-3 h-px bg-teal"></span>
                Win rate · last {{ WINDOW }}
            </span>
            <span class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-sm bg-sage/40"></span>
                Matches / {{ period === 'All' ? 'week' : 'day' }}
            </span>
        </div>

        <div class="relative flex-1">
            <div ref="chartEl" class="absolute inset-0" />
            <div v-if="isEmpty"
                class="absolute inset-0 flex items-center justify-center text-sm text-muted pointer-events-none">
                Play a few more matches to see your trend
            </div>
            <AppTooltip ref="tt">
                <div class="text-xs font-medium mb-2 pb-2 border-b border-white/[0.07]">{{ ttData.date }}</div>
                <AppTooltipRow label="Win rate">
                    <span class="text-teal">{{ ttData.rate }}%</span>
                </AppTooltipRow>
                <div v-if="!ttData.full" class="text-[10px] text-muted mb-1">
                    fewer than {{ WINDOW }} matches so far
                </div>
                <AppTooltipRow label="This match">
                    <span class="uppercase"
                        :class="ttData.result === 'win' ? 'text-teal' : ttData.result === 'loss' ? 'text-coral' : 'text-muted'">
                        {{ ttData.result }}
                    </span>
                </AppTooltipRow>
                <AppTooltipRow label="Matches that day" :value="ttData.dayCount" />
            </AppTooltip>
        </div>
    </div>
</template>           
