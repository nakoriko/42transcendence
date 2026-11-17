<script setup>
    import { ref, computed } from 'vue'
    import { useChatStore } from '@/stores/chat';
    import AppFilterTabs from '../AppFilterTabs.vue';
    import { usePresence } from '@/composables/usePresence.js';
    import AppAvatar from '../AppAvatar.vue';
    import { formatTime } from '@/utils/date.js';
    

    const props = defineProps({ friends: { type: Array, default: () => [] } })

    const chatStore =  useChatStore()
    const { isOnline } = usePresence()
    const activeFilter = ref('all')

    const visibleFriends = computed(() => 
        activeFilter.value === 'online'
        ? props.friends.filter(f => isOnline(f))
        : props.friends)

    const lastMessage = (id) => 
        chatStore.messages[id]?.at(-1) ?? null

</script>

<template>
    <div class="flex flex-col min-h-0">
        <!-- same header line as Recent Matches: title + tabs -->
        <div class="flex items-center justify-between h-11 border-b border-white/[0.07]">
            <span class="input-label">Contacts</span>
            <AppFilterTabs v-model="activeFilter" :options="['all', 'online']" />
        </div>

        <div class="flex-1 min-h-0 max-h-[40vh] lg:max-h-none overflow-y-auto scroll-thin py-2">
            <button v-for="f in visibleFriends" :key="f.id"
                @click="chatStore.setActiveContact(f.id)"
                :class="chatStore.activeContactId === f.id ? 'bg-white/[0.04]' : 'hover:bg-white/[0.02]'"
                class="w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left transition">
                <AppAvatar :nickname="f.nickname" :is-online="isOnline(f)" :avatar="f.avatar" />

                <div class="flex-1 min-w-0">
                    <div class="text-sm text-white truncate">{{ f.nickname }}</div>
                    <div class="text-xs text-muted truncate">
                        {{ lastMessage(f.id)?.content ?? (isOnline(f) ? 'Online' : 'Offline') }}
                    </div>
                </div>

                <div class="flex flex-col items-end gap-1.5 self-start pt-0.5 flex-shrink-0">
                    <span v-if="lastMessage(f.id)" class="text-[10px] text-muted tabular-nums">
                        {{ formatTime(lastMessage(f.id).timeStamp) }}
                    </span>
                    <span v-if="chatStore.unreadPeers[f.id]" class="w-2 h-2 rounded-full bg-coral"></span>
                </div>
            </button>

            <div v-if="!visibleFriends.length" class="text-xs text-muted text-center py-8">
                {{ friends.length ? 'Nobody online right now' : 'No friends yet. Add them on your profile' }}
            </div>
        </div>
    </div>
</template>

