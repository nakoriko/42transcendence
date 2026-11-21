<script setup>
// one "label — value" line inside AppTooltip
// value can be passed as prop, or as slot when it needs its own color / format
defineProps({
    label: { type: String, required: true },
    value: { type: [String, Number], default: '' },
})
</script>

<template>
    <div class="flex justify-between items-baseline gap-4 mb-1 last:mb-0">
        <span class="text-[10px] text-muted flex-shrink-0">{{ label }}</span>
        <!-- min-w-0 lets the value shrink and wrap instead of overflowing the tooltip -->
        <span class="text-[10px] tabular-nums text-right min-w-0 break-words">
            <slot>{{ value }}</slot>
        </span>
    </div>

</template>