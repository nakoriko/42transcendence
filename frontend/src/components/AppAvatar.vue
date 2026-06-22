<script setup>
    defineProps({
        nickname: String,
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
    <div :class="size === 'sm' ? 'w-7 h-7 text-xs' :size === 'lg' ? 'w-16 h-16 text-base' : 'w-9 h-9 text-sm', avatarColor(nickname)"
        class="relative rounded-full flex items-center justify-center text-navy-900 flex-shrink-0">
            {{ initial(nickname) }}
            <div v-if="isOnline" class="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-teal border-2 border-navy-800"></div>
    </div>
</template>
