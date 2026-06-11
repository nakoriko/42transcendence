<script setup>
    defineProps({
        variant: {
            type: String,
            default: 'primary',
        }
    })
</script>

<template>
    <button
        :class="variant === 'primary' ? 'px-8 py-3 rounded-pill min-w-40 border border-teal text-teal hover:bg-sage hover:border-transparent hover:text-navy-900' 
            :variant === 'large' ? 'px-10 py-4 rounded-pill text-base border border-teal text-teal hover:bg-sage hover:border-transparent hover:text-navy-900'
            :variant === 'cta' ? 'px-12 py-4 rounded-pill text-lg min-w-64 bg-navy-900 text-sage border border-sage hover:bg-sage hover:text-navy-900'
            :                       'px-5 py-2 rounded-pill border border-teal text-teal hover:bg-sage hover:border-transparent hover:text-navy-900'"
        class="transition">
        <slot></slot>
    </button>
</template>
