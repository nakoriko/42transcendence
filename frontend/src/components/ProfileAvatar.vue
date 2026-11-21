<script setup>
import { Upload } from 'lucide-vue-next'
import { formatLongDate } from '@/utils/date.js'

defineProps({
    user: Object,
    canUpload: { //should be false fo public profiles
        type: Boolean,
        default: false
    },

})
const emit = defineEmits(['upload'])


function handleFileSelect(event) {
    const file = event.target.files[0]
    if(file) emit('upload', file)
    event.target.value = '' // lets the same file be chosen again after an error
}
</script>

<template>
    <!-- sm..lg: avatar on the left, details on the right; otherwise centered column -->
    <div class="flex flex-col items-center gap-4 text-center
                sm:flex-row sm:items-center sm:gap-6 sm:text-left
                lg:flex-col lg:items-center lg:gap-4 lg:text-center">

        <div class="relative flex-shrink-0">
            <img v-if="user.avatar"
                :src="user.avatar"
                class="w-24 h-24 rounded-full object-cover border-2 border-teal/30"
                alt="avatar">
            <div v-else
                class="w-24 h-24 rounded-full bg-teal/20 border-2 border-teal/30
                       flex items-center justify-center text-3xl font-light text-white">
                {{ user.nickname?.[0]?.toUpperCase() }}
            </div>
            <label v-if="canUpload" title="Upload avatar"
                class="absolute bottom-0 left-0 w-8 h-8 rounded-full bg-navy-900 border border-white/[0.15]
                       flex items-center justify-center text-muted cursor-pointer transition
                       hover:text-white hover:border-teal/50 focus-within:text-white focus-within:border-teal">
                <Upload :size="14" aria-hidden="true" />
                <input type="file" accept="image/*" aria-label="Upload avatar" class="sr-only" @change="handleFileSelect">
            </label>
        </div>

        <!-- sm..lg: details and slot content in one row (wraps for full-width items) -->
        <div class="w-full min-w-0 sm:flex-1 sm:flex sm:flex-wrap sm:items-center sm:gap-x-8
                    lg:block lg:flex-none">
            <div class="min-w-0">
                <div class="text-xl font-light text-white truncate">{{ user.nickname }}</div>
                <div class="text-xs text-muted mt-1 break-all">{{ user.email }}</div>
                <div v-if="user.date_joined" class="text-xs text-muted mt-1">
                    Joined {{ formatLongDate(user.date_joined) }}
                </div>
                <div class="text-xs text-green-400 mt-1">Online</div>
            </div>
            <!-- extra content next to / under the details, e.g. the edit button -->
            <slot />
        </div>

    </div>
</template>
