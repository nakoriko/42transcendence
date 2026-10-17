<template>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Record -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Record</div>
            <div class="flex items-baseline gap-3 text-4xl font-light leading-none">
                <span class="text-teal">—</span>
                <span class="text-2xl text-muted">/</span>
                <span class="text-coral">—</span>
            </div>
            <div class="text-xs text-muted">— matches</div>
        </div>

        <!-- Win rate -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Win rate</div>
            <div class="text-4xl font-light leading-none">
                —<span class="text-base text-muted ml-1">%</span>
            </div>
            <div class="text-xs text-muted">wins of all matches</div>
        </div>

        <!-- Current streak -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Current streak</div>
            <div class="text-4xl font-light leading-none">—</div>
            <div class="flex gap-1">
                <span v-for="i in 7" :key="i" class="w-5 h-[22px] rounded bg-white/[0.06]"></span>
            </div>
        </div>

        <!-- Rank -->
        <div class="panel flex flex-col gap-2.5">
            <div class="card-label mb-0">Rank</div>
            <div class="text-4xl font-light leading-none">
                #—<span class="text-base text-muted ml-1">of —</span>
            </div>
            <div class="text-xs text-muted">—</div>
        </div>
    </div>
</template>
