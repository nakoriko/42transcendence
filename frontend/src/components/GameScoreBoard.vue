<script setup>
    defineProps({
        p1: Number,
        p2: Number,
        name1: String,
        name2: String
    })
</script>

<template>
    <div class="flex items-center gap-8">
        <div class="flex flex-col items-center gap-1">
            <span class="text-xs text-muted uppercase tracking-widest">{{name1}}</span>
            <span class="text-5xl font-light text-white"> {{ p1 }}</span>
        </div>

        <div class="flex flex-col items-center gap-1">
            <span class="text-xs text-muted uppercase tracking-widest">{{name2}}</span>
            <span class="text-5xl font-light text-white"> {{ p2 }}</span>
        </div>

    </div>
</template>