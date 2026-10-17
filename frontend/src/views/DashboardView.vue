<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { apiFetch } from '@/utils/apiFetch';
import DashMatchHistory from '@/components/dashboard/DashMatchHistory.vue';
import DashPlayerStats from '@/components/dashboard/DashPlayerStats.vue';
import DashRallyTimeline from '@/components/dashboard/DashRallyTimeline.vue';
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


const statsRef = ref(null)
const universeRef = ref(null)
const historyRef = ref(null)
const playerGraphRef = ref(null)
const matchesStore = useMatchesStore()
const lastEvents = ref([])
const presenceStore = usePresenceStore()
const activeMatchId = ref(null)

async function captureSection(el) {
    // throw new Error('debug B26: simulated capture failure')
    const canvas = await html2canvas(el, {
        backgroundColor: '#0f1629',
        scale: 2,
        ignoreElements: (node) => node.classList.contains('no-capture') //
    })
    return canvas
}

async function exportToPdf() {
    const scrollables = document.querySelectorAll('.scroll-thin')
    scrollables.forEach(el => {
        el.dataset.prevMaxHeight = el.style.maxHeight
        el.style.maxHeight = 'none'
        el.style.overflow = 'visible'
    }) //temporary opens full list, to make all render after
    await nextTick() // aspettiamo finche browser redraw actual layout

    const sections = [universeRef.value, statsRef.value, historyRef.value]
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



function onMatchSelected(matchId) {
    activeMatchId.value = matchId
}

onMounted(async () => {
    const [, eventsRes ] = await Promise.all([
        matchesStore.load(),
        apiFetch('/api/game/events/')
    ])
    if(eventsRes) lastEvents.value = (await(eventsRes.json()))
})



</script>
<template>
    <div class="pb-16">
        <div class="mb-10 flex items-center justify-between flex-wrap gap-4">
            <div> <!--protection while assync fetchUsers finish his a request: v-if="currentUser"-->
                <p class="input-label mb-1">Transcend · Dashboard</p>
                <h1 class="page-title">Analytics</h1>
            </div>
            <div class="flex items-center gap-4">
                <AppBadge :label="presenceStore.onlineCount+' online'" variant="teal" />
                <AppButton variant="tag" @click="exportToPdf" class="no-capture">
                    <Download :size="11"></Download>
                    Export PDF
                </AppButton>
            </div>
        </div>
        <!--TItle-->




        <!--PLayer graph -->
        <section ref="playerGraphRef" class="py-10 border-b border-white/[0.04]">
            <!---PLayer graph-->
           <DashPlayerGraph></DashPlayerGraph>
        </section>

        <!--Pong Universe-->
        <section ref="universeRef" class="py-10 border-b border-white/[0.04]">
            <!--DashUNiverse will be here-->
           <DashUniverse></DashUniverse>
        </section>



        <!--PLayer Stats + Rally timeline-->
        <section ref="statsRef" class="py-10 border-b border-white/[0.04]">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch lg:min-h-[380px]">
                <div class="min-h-[380px] lg:min-h-0">
                    <DashPlayerStats></DashPlayerStats>
                </div>
                <div class="min-h-[380px] lg:min-h-0">
                    <DashRallyTimeline 
                    :matches="matchesStore.matches" 
                    :events="lastEvents"
                    @matchSelected="onMatchSelected"></DashRallyTimeline>
                </div>
            </div>
        </section>




        <!--Match history-->
        <section ref="historyRef" class="py-10">
            <!--DashMatch Stats-->
            <DashMatchHistory :activeMatchId></DashMatchHistory>
        </section>
    </div>
</template>