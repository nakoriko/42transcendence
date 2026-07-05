<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { apiFetch } from '@/utils/apiFetch';
    import { useChatStore } from '@/stores/chat';
    import PlayCard from '../PlayCard.vue';
    import AppFilterTabs from '../AppFilterTabs.vue';

    const chatStore =  useChatStore()
    const friends = ref([])
    const activeFilter = ref('all')


    const filteredFriends = computed(() => {
        if(activeFilter.value === 'online')
            return friends.value.filter(rel => rel.friend.is_online)
        return friends.value
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
            <PlayCard v-for="rel in filteredFriends"
            :key="rel.friend.id"
            :user="rel.friend"
            :selected="chatStore.activeContactId === rel.friend.id"
            :show-stats="false"
            @select="selectContact" ></PlayCard>
            
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

    .chat-contact-scroll::after {
        content: '';
        position: absolute;
        top: 0;
        right: 4px;
        bottom: 0;
        width: 3px;
        background: rgba(255,255,255,0.08);
        border-radius: 999px;
        pointer-events: none;
    }

</style>