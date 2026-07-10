<script setup>
import AppAvatar from '../AppAvatar.vue';


defineProps({
    currentUser: Object,
    opponent: {
        type: Object,
        default: null
    }
})

</script>

<template>
    <div class="card flex flex-col gap-5 px-10 py-10">

        <p class="input-label mb-5">Match</p>

        <!-- Игрок 1 -->
        <div class="flex items-center gap-3">
            <AppAvatar :nickname="currentUser?.nickname" :is-online="true"  size="lg" />
            <div class="flex flex-col">
                <span class="text-xl text-white font-medium truncate">{{ currentUser?.nickname }}</span>
                <span class="text-xs text-muted">You</span>
            </div>
        </div>

        <span class="pl-[3.75rem] text-xs text-muted/50 uppercase tracking-widest">vs</span>

        <!-- Игрок 2 -->
        <div class="flex items-center gap-3 mb-5">
            <template v-if="opponent">
                <AppAvatar :nickname="opponent?.nickname" :is-online="opponent.is_online" size="lg" />
                <span class="text-xl text-white font-medium truncate">{{ opponent.nickname }}</span>
            </template>
            <template v-else>
                <div class="w-16 h-16 rounded-full border border-dashed border-white/20
                            flex items-center justify-center text-muted/40 text-sm flex-shrink-0">?</div>
                <span class="text-xl text-muted/40">Select opponent</span>
            </template>
        </div>

        <!-- Кнопка приходит снаружи -->
        <slot />

    </div>
</template>