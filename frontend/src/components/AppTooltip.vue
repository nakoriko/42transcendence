<script setup>
import { ref, nextTick } from 'vue'
import { placeTooltip } from '@/utils/tooltip';

const el = ref(null)

defineExpose({
    async show(x, y) {
        await nextTick()
        const tip = el.value
        const box = tip?.offsetParent
        if(!tip || !box) return
        const { left, top } = placeTooltip(x, y, 
            { width: tip.offsetWidth, height: tip.offsetHeight},
            { width: box.clientWidth, height: box.clientHeight })
        tip.style.left = left + 'px'
        tip.style.top = top + 'px'
        tip.style.opacity = 1
    },
    hide() {
       if(el.value) el.value.style.opacity = 0
    }
})
</script>

<template>
    <div ref="el"
        class = "absolute pointer-events-none opacity-0 transition-opacity duration-100 z-20"
        style="top:0; left:0">
        <div class="bg-[rgba(15,22,41,0.97)] border border-white/[0.11] rounded-xl px-4 py-3 min-w-[170px] max-w-[170px] break-words">
            <slot/>
        </div>

    </div>
</template>