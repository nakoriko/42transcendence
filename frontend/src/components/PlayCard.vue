<script setup>
import { calcWinRate, calcTotalMatches } from '@/utils/stats.js';
import { computed } from 'vue'
import AppAvatar from './AppAvatar.vue';
import AppBadge from './AppBadge.vue';


    const props = defineProps({
        user: Object,
        selected: Boolean
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

            <AppAvatar size="sm" :nickname="user.nickname" :isOnline="user.is_online" />

            <span class="text-base font-light text-white flex-1 min-w-0 truncate">
                {{ user.nickname }}
            </span>

            <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-xs text-muted">{{ totalMatches }} matches</span>
                <AppBadge :label="winRate + '%'" />
            </div>
        </div>

    </div>
</template>


<!-- <template>
    <div @click="$emit('select', user.id)"
        :class="selected
            ? 'bg-teal/[0.08] border-teal/20'
            : 'border-transparent hover:bg-white/[0.04]'"
        class="border rounded-[12px] px-4 py-3 flex items-center gap-3 cursor-pointer transition">
    <AppAvatar size="sm" :nickname="user.nickname" :isOnline="user.is_online" />

    <span class="text-base font-light text-white flex-1 min-w-0 truncate">{{ user.nickname }}</span>
    <div class="flex items-center gap-2 flex-shrink-0">
        <span class="text-xs text-muted ">{{ totalMatches }} matches</span>
        <AppBadge :label="winRate + '%'" />
    </div>
    </div>
</template> -->