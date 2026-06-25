<script setup>
import DashMatchHistory from '@/components/dashboard/DashMatchHistory.vue';
import DashPlayerStats from '@/components/dashboard/DashPlayerStats.vue';
import DashRallyTimeline from '@/components/dashboard/DashRallyTimeline.vue';
import DashUniverse from '@/components/dashboard/DashUniverse.vue';
//store
// import { userUserStore } from '@/stores/user'

//
const currentUser = true
</script>
<template>
    <div class="min-h-screen px-12 py-14 pb-24">

        <!--TItle-->
        <div class="mb-10"> <!--protection while assync fetchUsers finish his a request: v-if="currentUser"-->
            <p class="input-label mb-1">Transcend · Dashboard</p>
            <h1 class="page-title">Analytics</h1>
        </div>


        <!--Pong Universe-->
        <section class="py-6 border-b border-white/[0.04]">
            <!--DashUNiverse will be here-->
           <DashUniverse></DashUniverse>
        </section>


        <!--PLayer Stats + Rally timeline-->
        <section class="py-6 border-b border-white/[0.04]">
            <div class="grid grid-cols-[2fr_3fr] gap-6">
                <DashPlayerStats></DashPlayerStats>
                <DashRallyTimeline></DashRallyTimeline>
            </div>
        </section>


        <!--Match history-->
        <section class="py-6">
            <!--DashMatch Stats-->
            <DashMatchHistory></DashMatchHistory>
        </section>
    </div>
</template>