<script setup>
import AppAvatar from './AppAvatar.vue';

    defineProps({
        user: Object,
        selected: Boolean
    })

    defineEmits(['select'])
</script>

<template>
    <div @click="$emit('select', user.id)"
        :class="selected ? 'border-l-teal border-l-4 border-teal/20 bg-navy-700' 
        : 'border-white/[0.07] hover:border-teal/40'"
        class="bg-navy-800 border rounded-[12px] px-4 py-3 flex items-center gap-3 cursor-pointer transition">
    <AppAvatar :nickname="user.nickname" :isOnline="user.isOnline" />
    <span class="text-base text-white flex-1">{{ user.nickname }}</span>
    <span class="text-xs text-muted">{{ user.wins }} wins</span>
    </div>
</template>