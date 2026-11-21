<script setup>
import { computed } from 'vue'
import AppAvatar from '../AppAvatar.vue'
import { usePresence } from '@/composables/usePresence.js'
import { calcWinRate, calcTotalMatches } from '@/utils/stats.js'

const props = defineProps({ user: { type: Object, required: true } })

const { isOnline } = usePresence()
const online = computed(() => isOnline(props.user))
const total = computed(() => calcTotalMatches(props.user.wins, props.user.losses))
const winRate = computed(() => calcWinRate(props.user.wins, props.user.losses))
</script>

<template>
    <div class="flex items-center gap-4 py-4 border-t border-white/[0.07]">
        <AppAvatar :nickname="user.nickname" :is-online="online" :avatar="user.avatar" />
        <div class="flex-1 min-w-0">
            <div class="truncate text-sm text-white">{{ user.nickname }}</div>
            <div class="flex items-center gap-2 mt-1.5 text-xs text-muted tabular-nums">
                <span>{{ total }} {{ total === 1 ? 'match' : 'matches' }}</span>
                <template v-if="total">
                    <span class="text-muted/50">·</span>
                    <span class="w-8 h-0.5 rounded-full bg-white/[0.07] overflow-hidden flex-shrink-0">
                        <span class="block h-full bg-teal" :style="{ width: winRate + '%' }"></span>
                    </span>
                    <span class="text-white">{{ winRate }}%</span>
                </template>
            </div>
        </div>
        <div class="flex items-center justify-end gap-1 flex-shrink-0">
            <slot />
        </div>
    </div>
</template>
