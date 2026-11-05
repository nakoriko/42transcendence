<script setup>
import { calcWinRate, calcTotalMatches } from '@/utils/stats.js';
import { computed } from 'vue'
import AppAvatar from './AppAvatar.vue';
import AppBadge from './AppBadge.vue';


    const props = defineProps({
        user: Object,
        selected: Boolean,
        showStats: { type: Boolean, default: true}
    })

    defineEmits(['select'])

    const winRate = computed(() => calcWinRate(props.user.wins, props.user.losses))
    const totalMatches = computed(() => calcTotalMatches(props.user.wins, props.user.losses))


</script>

<template>
    <div>
        <div @click="$emit('select', user.id)"
            :class="selected ? 'bg-teal/[0.06]' : 'hover:bg-white/[0.04]'"
            class="rounded-[12px] px-4 py-5 flex items-center gap-3 cursor-pointer transition">

            <AppAvatar :nickname="user.nickname" :isOnline="user.is_online" :avatar="user.avatar" />

            <span class="text-base font-light text-white flex-1 min-w-0 truncate">
                {{ user.nickname }}
            </span>

            <div v-if="showStats" class="flex items-center gap-2 flex-shrink-0">
                <span class="text-xs text-muted">{{ totalMatches }} matches</span>
                <AppBadge :label="winRate + '%'" />
            </div>
        </div>

    </div>
</template>