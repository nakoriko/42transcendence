<script setup>
import { ref } from 'vue'

const el = ref(null)

defineExpose({
    show(x, y) {
        el.value.style.left = x + 'px'
        el.value.style.top = y + 'px'
        el.value.style.opacity = 1
    },
    hide() {
        el.value.style.opacity = 0
    }
})
</script>

<template>
    <div ref="el"
        class = "absolute pointer-events-none opacity-0 transition-opacity duration-100 z-20"
        style="top:0; left:0">
        <div class="bg-[rgba(15,22,41,0.97)] border border-white/[0.11] rounded-xl px-4 py-3 min-w-[170px]">
            <slot/>
        </div>

    </div>
</template>