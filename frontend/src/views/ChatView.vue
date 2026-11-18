<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ChatContactList from '@/components/chat/ChatContactList.vue';
import ChatWindow from '@/components/chat/ChatWindow.vue';
import { apiFetch } from '@/utils/apiFetch';
import { useChatStore } from '@/stores/chat';
import { usePresenceStore } from '@/stores/presence';
import AppPageHeader from '@/components/AppPageHeader.vue';
import AppBadge from '@/components/AppBadge.vue';

const chatStore = useChatStore()
const presenceStore = usePresenceStore()
const friends = ref([]) // plain users: { id, nickname, is_online, ... }

const activeContact = computed(() =>
    friends.value.find(f => f.id === chatStore.activeContactId) ?? null)

async function loadFriends() {
    const res = await apiFetch('/api/users/friends/')
    if (!res?.ok) return
    const data = await res.json()
    friends.value = (data.friends ?? []).map(rel => rel.friend)
}

onMounted(() => {
    loadFriends()
    window.addEventListener('friends-updated', loadFriends) // new friend accepted -> appears in contacts
})

onUnmounted(() => {
    window.removeEventListener('friends-updated', loadFriends)
})

</script>


<template>
<div class="pb-16 flex flex-col gap-12">
        <AppPageHeader crumb="Transcend · Chat" title="Messages">
            <AppBadge :label="presenceStore.onlineCount + ' online'" variant="teal" />
        </AppPageHeader>

        <!-- fixed height, so only the message list scrolls, not the whole page.
             below lg: one panel at a time - contacts, or the open chat -->
        <div class="grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)] gap-8
                    h-[clamp(420px,calc(100svh_-_300px),820px)]">
            <ChatContactList :friends="friends"
                :class="{ 'max-lg:hidden': activeContact }"
                class="min-h-0" />
            <ChatWindow :contact="activeContact"
                @back="chatStore.activeContactId = null"
                :class="{ 'max-lg:hidden': !activeContact }"
                class="min-h-0 lg:border-l border-white/[0.07] lg:pl-8" />
        </div>
    </div>
</template>
