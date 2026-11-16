<script setup>
import { ref, onMounted, nextTick } from 'vue'
import DashMatchHistory from '@/components/dashboard/DashMatchHistory.vue';
import DashPlayerStats from '@/components/dashboard/DashPlayerStats.vue';
import DashUniverse from '@/components/dashboard/DashUniverse.vue';
import DashPlayerGraph from '@/components/dashboard/DashPlayerGraph.vue';
import  { usePresenceStore } from '@/stores/presence';
import { useMatchesStore } from '@/stores/matches';
import AppBadge from '@/components/AppBadge.vue';
import AppButton from '@/components/AppButton.vue';
import { Download } from 'lucide-vue-next';
import html2canvas from 'html2canvas-pro'
import jsPDF from 'jspdf'
import { fitPdfPage } from '@/utils/pdf';
import { apiFetch } from '@/utils/apiFetch';
import DashNodeInfo from '@/components/dashboard/DashNodeInfo.vue'
import DashKpiRow from '@/components/dashboard/DashKpiRow.vue';
import AppPageHeader from '@/components/AppPageHeader.vue';

const rootRef = ref(null)
const exportFailed = ref(false)
const statsRef = ref(null)
const universeRef = ref(null)
const historyRef = ref(null)
const playerGraphRef = ref(null)
const matchesStore = useMatchesStore()
const presenceStore = usePresenceStore()
const activeMatchId = ref(null)
const hoveredNode = ref(null)
const players = ref([]) // all players: shared by Universe chart and KPI rank

async function captureSection(el) {
    const canvas = await html2canvas(el, {
        backgroundColor: '#0f1629',
        scale: 2,
        ignoreElements: (node) => node.classList.contains('no-capture')
    })
    return canvas
}

async function exportToPdf() {
    exportFailed.value = false
    try {
        await buildPdf()
    } catch (err) {
        console.error('PDF export failed', err)
        exportFailed.value = true
    }
}

async function buildPdf() {
    const scrollables = rootRef.value.querySelectorAll('.scroll-thin') //only dashboard lists, not the App.vue container
    scrollables.forEach(el => {
        el.dataset.prevMaxHeight = el.style.maxHeight
        el.style.maxHeight = 'none'
        el.style.overflow = 'visible'
    }) //temporary opens full list, to make all render after
    await nextTick() // wait until the browser redraws the actual layout

    const sections = [playerGraphRef.value, statsRef.value, universeRef.value]
    const canvases = []
    try {
        for (const section of sections) {
            canvases.push(await captureSection(section))
        }
    } finally {
        //always restore layout, even if html2canvas fails
        scrollables.forEach(el => {
            el.style.maxHeight = el.dataset.prevMaxHeight || ''
            el.style.overflow = ''
        })
    }

    const pages = canvases.map(c => fitPdfPage(c.width, c.height))
    const pdf = new jsPDF({
        orientation: pages[0].orientation,
        unit: 'pt',
        format: [pages[0].width, pages[0].height] //creates page ruight to image 
    })

    canvases.forEach((canvas, i) => {
        const { width, height, orientation } = pages[i]
        if (i > 0) {
            pdf.addPage([width, height], orientation)
        }
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, width, height)
    })
    pdf.save('dashboard-analytics.pdf')
}

async function onNodeClick(nickname) {
    const match = matchesStore.matches.find(m => m.opponent_nickname === nickname)
    if(!match) return
    activeMatchId.value = null
    await nextTick()
    activeMatchId.value = match.id
    historyRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start'})

}

async function loadPlayers() {
    const res = await apiFetch('/api/analytics/universe/')
    if (!res?.ok) return
    players.value = await res.json()
}

onMounted(async () => {
    await Promise.all([matchesStore.load(), loadPlayers()])
})
</script>

<template>
    <div ref="rootRef" class="pb-16 flex flex-col gap-20">

        <AppPageHeader crumb="Transcend · Dashboard" title="Analytics">
            <AppBadge :label="presenceStore.onlineCount+' online'" variant="teal" />
            <span v-if="exportFailed" class="text-xs text-coral">Export failed</span>
            <AppButton variant="tag" @click="exportToPdf" class="no-capture">
                <Download :size="11"></Download>
                Export PDF
            </AppButton>
        </AppPageHeader>

        <!--Pong Universe-->
        <section ref="universeRef">
            <!--DashUNiverse will be here-->
           <DashUniverse :players="players"></DashUniverse>
        </section>

        <!--PLayer graph -->
        <section ref="playerGraphRef" class="lg:h-[60vh] lg:min-h-[480px]">
            <!---PLayer graph-->
            <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_260px] gap-6 h-full">

                <DashPlayerGraph 
                @node-hover="hoveredNode = $event"
                @node-click="onNodeClick"></DashPlayerGraph>
                <aside class="border-t lg:border-t-0 lg:border-l border-white/[0.07] pt-6 lg:pt-0 lg:pl-6">
                    <DashNodeInfo :node="hoveredNode"></DashNodeInfo>
                </aside>
            </div>
        </section>

        <!-- KPI row -->
        <div ref="statsRef" class="flex flex-col gap-12">
            <DashKpiRow :players="players"></DashKpiRow>
            <!--Match history + player stats -->
            <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] gap-12">
                <section ref="historyRef" class="lg:h-[50vh] lg:min-h-[360px]">
                    <DashMatchHistory :activeMatchId></DashMatchHistory>
                </section>
                <section class="lg:h-[50vh] lg:min-h-[360px]">
                    <div class="h-[320px] lg:h-full">
                        <DashPlayerStats></DashPlayerStats>
                    </div>
                </section>
            </div>
        </div>
    </div>
</template>