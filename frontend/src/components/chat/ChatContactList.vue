<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { apiFetch } from '@/utils/apiFetch';
    import { useChatStore } from '@/stores/chat';
    import PlayCard from '../PlayCard.vue';
    import AppFilterTabs from '../AppFilterTabs.vue';
    import { usePresenceStore } from '@/stores/presence.js';

    const chatStore =  useChatStore()
    const friends = ref([])
    const activeFilter = ref('all')
    const presenceStore = usePresenceStore()

    const liveFriends = computed(() => 
        friends.value.map(rel => ({
            ...rel,
            friend: {
                ...rel.friend,
                is_online: presenceStore.online[rel.friend.id] ?? rel.friend.is_online
            }
        }))
    )


    const filteredFriends = computed(() => {
        if(activeFilter.value === 'online')
            return liveFriends.value.filter(rel => rel.friend.is_online)
        return liveFriends.value
    })

    async function loadFriends() {
        const res =  await apiFetch('/api/users/friends/')
        if(res?.ok) {
            const data = await res.json()
            friends.value = data.friends
        }
    }

    function selectContact(id) {
        chatStore.setActiveContact(id)
    }
    onMounted(loadFriends)
</script>

<template>
    <div class="chat-contact-list">
        <div class="chat-contact-header">
            <span class="input-label">Contacts</span>
            <AppFilterTabs
            :options="['all', 'online']"
            :model-value="activeFilter"
            @update:model-value="activeFilter = $event">
            </AppFilterTabs>
        </div>
        
        <div class="chat-contact-scroll scroll-thin">
            <div v-for="rel in filteredFriends" :key="rel.friend.id" class="relative">
                <PlayCard 
                    :user="rel.friend"
                    :selected="chatStore.activeContactId === rel.friend.id"
                    :show-stats="false"
                    @select="selectContact" ></PlayCard>
                <span
                    v-if="chatStore.unreadPeers[rel.friend.id]"
                    class="absolute right-4 top-1/2 -translate-y-1/2 w-2.5 h-2.5 bg-coral rounded-full border-2 border-navy-800"
                ></span>
            </div>
            
            <div v-if="!filteredFriends.length" 
            class="text-[11px] text-muted text-center py-6"> Nobody's here yet</div>
        </div>
    </div>
</template>

<style scoped>
    .chat-contact-list {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .chat-contact-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px  12px 12px;
        flex-shrink: 0;
    }

    .chat-contact-scroll {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        position: relative;
    }


</style>