<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { apiFetch } from '@/utils/apiFetch';
import DashMatchHistory from '@/components/dashboard/DashMatchHistory.vue';
import DashPlayerStats from '@/components/dashboard/DashPlayerStats.vue';
import DashRallyTimeline from '@/components/dashboard/DashRallyTimeline.vue';
import DashUniverse from '@/components/dashboard/DashUniverse.vue';
import DashPlayerGraph from '@/components/dashboard/DashPlayerGraph.vue';
import  { usePresenceStore } from '@/stores/presence'
import AppBadge from '@/components/AppBadge.vue';
import AppButton from '@/components/AppButton.vue';
import { Download } from 'lucide-vue-next';
import html2canvas from 'html2canvas-pro'
import jsPDF from 'jspdf'


const statsRef = ref(null)
const universeRef = ref(null)
const historyRef = ref(null)
const playerGraphRef = ref(null)

async function captureSection(el) {
    const canvas = await html2canvas(el, {
        backgroundColor: '#0f1629',
        scale: 2,
        ignoreElements: (node) => node.classList.contains('no-capture') //
    })
    return canvas
}

async function exportToPdf() {
    document.querySelectorAll('.scroll-thin').forEach(el => {
        el.dataset.prevMaxHeight = el.style.maxHeight
        el.style.maxHeight = 'none'
        el.style.overflow = 'visible'
    }) //temporary opens full list, to make all render after
    await nextTick() // aspettiamo finche browser redraw actual layout

    const sections = [universeRef.value, statsRef.value, historyRef.value]
    const canvases = []
    for (const section of sections) {
        canvases.push(await captureSection(section))
    }
    //puts list elements on how it was before
    document.querySelectorAll('.scroll-thin').forEach(el => {
        el.style.maxHeight = el.dataset.prevMaxHeight || ''
        el.style.overflow = ''
    })


    const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'px',
        format: [canvases[0].width, canvases[0].height] //creates page ruight to image 
    })

    canvases.forEach((canvas, i) => {
        if (i > 0) {
            pdf.addPage([canvas.width, canvas.height], 'landscape')
        }
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, canvas.width, canvas.height)
    })
    pdf.save('dashboard-analytics.pdf')
}

const presenceStore = usePresenceStore()

const matches = ref([])
const lastEvents = ref([])

const activeMatchId = ref(null)

function onMatchSelected(matchId) {
    activeMatchId.value = matchId
}

onMounted(async () => {
    const [matchRes, eventsRes ] = await Promise.all([
        apiFetch('/api/game/matches/?limit=200'),
        apiFetch('/api/game/events/')
    ])
    if(matchRes) matches.value = (await (matchRes.json()))
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



        <!--PLayer Stats + Rally timeline-->
        <section ref="statsRef" class="py-10 border-b border-white/[0.04]">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch lg:min-h-[380px]">
                <div class="min-h-[380px] lg:min-h-0">
                    <DashPlayerStats></DashPlayerStats>
                </div>
                <div class="min-h-[380px] lg:min-h-0">
                    <DashRallyTimeline 
                    :matches="matches" 
                    :events="lastEvents"
                    @matchSelected="onMatchSelected"></DashRallyTimeline>
                </div>
            </div>
        </section>

        <!--Pong Universe-->
        <section ref="universeRef" class="py-10 border-b border-white/[0.04]">
            <!--DashUNiverse will be here-->
           <DashUniverse></DashUniverse>
        </section>



        <!--Match history-->
        <section ref="historyRef" class="py-10">
            <!--DashMatch Stats-->
            <DashMatchHistory :activeMatchId></DashMatchHistory>
        </section>
    </div>
</template>