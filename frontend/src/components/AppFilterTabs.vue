<script setup>
defineProps ({
    modelValue: {type: String, required: true},
    options:  {type: Array, required: true},
    disabledOptions: {type: Array, default: () => []}
})
const emit = defineEmits(['update:modelValue'])
</script>


<template>
    <div class="flex gap-0.5 bg-white/[0.04] rounded-md p-0.5 flex-shrink-0">
        <button v-for="option in options"
        :key="option"
        :disabled="disabledOptions.includes(option)"
        @click="emit('update:modelValue', option)"
        :class="[
            option === modelValue
            ? 'bg-white/[0.08] text-sage'
            : 'text-muted hover:text-white',
            'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:text-muted'
        ]"
        class="px-2.5 py-1 text-[11px] font-light tracking-widest uppercase rounded transition">
                {{ option }}
        </button>
    </div>
</template>
