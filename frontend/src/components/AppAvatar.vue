<script setup>
    defineProps({
        nickname: String,
        isOnline: Boolean
    })

    function initial(nickname) {
        return nickname ? nickname.charAt(0).toUpperCase() : '?'
    }
</script>

<template>
    <div class="relative w-9 h-9 rounded-full bg-coral flex items-center justify-center text-navy-900 text-sm flex-shrink-0">
        {{ initial(nickname) }}
        <div v-if="isOnline" class="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-teal border-2 border-navy-800"></div>

    </div>
</template>
