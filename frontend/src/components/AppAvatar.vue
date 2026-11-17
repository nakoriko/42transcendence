<script setup>
    defineProps({
        nickname: String,
        avatar: { type: String, default: null },
        isOnline: Boolean,
        size: {type: String, default: 'md' } // 'sm' | 'md' | 'lg'
    })


    function initial(nickname) {
        return nickname ? nickname.charAt(0).toUpperCase() : '?'
    }

    const colors = ['bg-coral', 'bg-teal', 'bg-sage', 'bg-sand']

    function avatarColor(nickname) {
        if (!nickname) return 'bg-coral'
        return colors[nickname.charCodeAt(0) % colors.length]
    }
</script>

<template>
    <div :class="[size === 'sm' ? 'w-7 h-7 text-xs' : size === 'lg' ? 'w-16 h-16 text-base' : 'w-9 h-9 text-sm', avatarColor(nickname)]"
        class="relative rounded-full flex items-center justify-center text-navy-900 flex-shrink-0">
            <img v-if="avatar" :src="avatar" alt=""
                class="absolute inset-0 w-full h-full rounded-full object-cover">
            <template v-else>{{ initial(nickname) }}</template>
            <div :class="[
                size === 'lg' ? 'w-3 h-3 bottom-0.5 right-0.5' : 'w-2.5 h-2.5 bottom-0 right-0',
                isOnline ? 'bg-green-400' : 'bg-gray-400'
            ]"
            class="absolute rounded-full border-2 border-navy-800"></div>
    </div>
</template>
