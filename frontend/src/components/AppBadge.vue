<script setup>
defineProps({
    label: String,
    variant: {type: String, default:'sage'} //'teal' | 'coral ' | 'sage'
})
</script>

<template>
    <span :class="{
        'bg-teal/10 text-teal border-teal/20 border-transparent': variant === 'teal',
        'bg-coral/10 text-coral border-coral/20 border-transparent ': variant === 'coral',
        'bg-sage/10 text-sage border-sage/20 border-transparent': variant === 'sage',
    }"
    class="text-[10px] px-2 py-0.5 rounded-full border">
        {{ label }}
    </span>
</template>


<!--Usage:

<AppBadge :label="winRate + '%'" />                  -- teal by default --
<AppBadge label="Win" />                              -- teal --
<AppBadge label="Loss" variant="coral" />             -- coral --
<AppBadge label="Soon" variant="sage" />              -- sage --

-->