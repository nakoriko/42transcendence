<template>
    <div class="flex flex-col h-full">
        <div class="input-label">At a glance</div>
        <div class="text-sm text-muted mt-1 mb-2">Patterns from your matches</div>

        <div v-for="label in ['Best opponent', 'Toughest matchup', 'Avg rally length', 'Favourite time']"
            :key="label"
            class="flex flex-col gap-0.5 py-3 border-b border-dashed border-white/[0.07] last:border-b-0">
            <span class="text-[11px] text-muted uppercase tracking-widest">{{ label }}</span>
            <span class="text-xl font-semibold">—</span>
        </div>
    </div>
</template>