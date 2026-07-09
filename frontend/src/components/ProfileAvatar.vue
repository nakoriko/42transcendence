<script setup>
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
}
</script>

<template>
    <div class="flex items-center gap-5">

        <div class="relative flex-shrink-0 group cursor-pointer">
            <img v-if="user.avatar"
                :src="user.avatar"
                class="w-15 h-15 rounded-full object-cover border-2 border-teal/30"
                alt="avatar">
            <div v-else
                class="w-15 h-15 rounded-full bg-teal/20 border-2 border-teal/30
                       flex items-center justify-center text-2xl font-light text-white">
                {{ user.nickname?.[0]?.toUpperCase() }}
            </div>
            <label v-if="canUpload"
                class="absolute inset-0 rounded-full bg-black/50
                       flex items-center justify-center
                       opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                <i class="ti ti-upload text-white text-sm" aria-hidden="true"></i>
                <input type="file" accept="image/*" class="hidden" @change="handleFileSelect">
            </label>
            <div class="online-dot bg-green-400 !bottom-1 !right-1"></div>
        </div>

        <div class="flex-1 min-w-0">

            <div class="text-base font-light text-white">{{ user.nickname }}</div>
            <div class="text-sm text-muted mt-0.5 break-all">{{ user.email }}</div>
        </div>

    </div>
</template>
