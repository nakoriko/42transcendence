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
            selected ? 'bg-teal/[0.06]' : '',
            disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:bg-white/[0.04]',
        ]"
        class="rounded-full px-6 py-3 flex items-center gap-2 transition"
    >
        <div :class="selected ? 'bg-biege' : 'bg-white/20'"
             class="w-2 h-2 rounded-full flex-shrink-0"></div>

        <span :class="selected ? 'text-white' : 'text-white/50'"
              class="text-base transition">{{ title }}</span>
    </div>
</template>


<!-- <template>
    <div>
        <div @click="!disabled && $emit('select')"
            :class="[
                selected ? 'bg-teal/[0.06]' : '',
                disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:bg-white/[0.04]',
            ]"
            class="rounded-[12px] px-4 py-6 flex items-center gap-3 transition"
        >
            <div :class="selected ? 'bg-biege' : 'bg-white/20'"
                 class="w-3 h-3 rounded-full flex-shrink-0"></div>

            <span :class="selected ? 'text-white font-medium' : 'text-white/50'"
                  class="text-base flex-1 transition">{{ title }}</span>

            <span class="text-xs text-muted">{{ disabled ? 'Coming soon' : subtitle }}</span>
        </div>
    </div>
</template> -->


<!-- 
<template>
    <div @click="!disabled && $emit('select')"
        :class="[
            selected ? 'bg-teal/[0.06]' : '',
            disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer hover:bg-white/[0.04]',
        ]"
        class="rounded-[12px] px-4 py-6 flex items-center gap-3 transition"
    >
        <div :class="selected ? 'bg-biege' : 'bg-white/20'"
             class="w-3 h-3 rounded-full flex-shrink-0">
        </div>

        <span :class="selected ? 'text-white font-medium' : 'text-white/50'"
              class="text-base flex-1 transition">
            {{ title }}
        </span>

        <span class="text-xs text-muted">
            {{ disabled ? 'Coming soon' : subtitle }}
        </span>
    </div>
</template> -->


<!-- <template>
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
</template> -->