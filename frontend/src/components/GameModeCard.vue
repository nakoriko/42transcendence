<script setup>
    defineProps ({
        icon: String,
        title: String,
        subtitle: String, 
        selected: Boolean,
        disabled: Boolean,
    })
</script>

<template>
    <div @click="!disabled && $emit('select')"
        :class="[
            selected ? 'border-l-4 border-l-teal border-teal/20' : 'border-white/[0.07]',
            disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer',
            !disabled && !selected ? 'hover:border-teal/40' : ''
        ]"
        class="bg-navy-800 border rounded-[12px] px-4 py-3 flex items-center gap-3 transition"
    >
        <span>{{ icon }}</span>
        <div class="flex flex-col">
            <span class="text-base text-white">{{ title }}</span>
            <span v-if="subtitle" class="text-xs text-muted">{{ subtitle }}</span>
            <span v-if="disabled" class="text-xs text-teal">Soon</span>
        </div>

    </div>
</template>