<script setup>
import { apiFetch } from '@/utils/apiFetch'
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppFilterTabs from '../AppFilterTabs.vue'
import ProfileFriendRow from './ProfileFriendRow.vue'
import { Gamepad2, MessageCircle, Plus, Search, X } from 'lucide-vue-next'
import { usePresence } from '@/composables/usePresence.js'
import { useChatStore } from '@/stores/chat.js'
import { rankOpponents } from '@/utils/opponents.js'

const router = useRouter()
const chatStore = useChatStore()
const { isOnline } = usePresence()

const friends = ref([])
const outgoing = ref([])
const incoming = ref([])
const allUsers = ref([])

const activeFilter = ref('all')
const showAdd = ref(false)
const query = ref('')
const searchInput = ref(null)
const confirmRemoveId = ref(null)
const actionError = ref('')

const emptyText = { all: 'No friends yet', online: 'No friends online', pending: 'No sent requests' }

const onlineFriends = computed(() => friends.value.filter(f => isOnline(f.friend)))
const counts = computed(() => ({
    all: friends.value.length,
    online: onlineFriends.value.length,
    pending: outgoing.value.length,
}))

const filteredList = computed(() => {
    const list = { all: friends.value, online: onlineFriends.value, pending: outgoing.value }[activeFilter.value]
    const q = query.value.trim().toLowerCase()
    return list.filter(f => f.friend.nickname.toLowerCase().includes(q))
})

const availableUsers = computed(() => {
    const taken = new Set([...friends.value, ...outgoing.value, ...incoming.value].map(f => f.friend.id))
    const candidates = allUsers.value.filter(u => !taken.has(u.id) && !u.is_friend)
    return rankOpponents(candidates, query.value, isOnline)
})

async function loadFriends() {
    const res = await apiFetch('/api/users/friends/')
    if (!res?.ok) return
    const data = await res.json()
    friends.value = data.friends ?? []
    outgoing.value = data.outgoing ?? []
    incoming.value = data.incoming ?? []
}

// runs a friend action, then updates this block, the sidebar and the chat contacts
async function runAction(url, options) {
    actionError.value = ''
    const res = await apiFetch(url, options)
    if (!res?.ok) {
        actionError.value = 'Something went wrong. Try again'
        return false
    }
    window.dispatchEvent(new CustomEvent('friends-updated'))
    return true
}

function answerRequest(relationId, action) {
    return runAction(`/api/users/friends/${relationId}/`, { method: 'PATCH', body: JSON.stringify({ action }) })
}

async function deleteRelation(relationId) {
    if (await runAction(`/api/users/friends/${relationId}/`, { method: 'DELETE' })) {
        allUsers.value = [] // is_friend in this list is out of date now
    }
    confirmRemoveId.value = null
}

function removeFriend(relationId) {
    if (confirmRemoveId.value === relationId) deleteRelation(relationId)
    else confirmRemoveId.value = relationId
}

async function sendRequest(userId) {
    const sent = await runAction('/api/users/friends/request/', {
        method: 'POST',
        body: JSON.stringify({ to_user_id: userId }),
    })
    if (sent) closeAdd()
}

function openChat(friendId) {
    chatStore.setActiveContact(friendId)
    router.push('/chat')
}

function inviteToGame(friendId) {
    router.push({ path: '/lobby', query: { opponent: friendId } })
}

function closeAdd() {
    showAdd.value = false
    query.value = ''
}

async function toggleAdd() {
    if (showAdd.value) return closeAdd()
    showAdd.value = true
    query.value = ''
    await nextTick()
    searchInput.value?.focus()
    if (allUsers.value.length) return
    const res = await apiFetch('/api/users/list/')
    if (res?.ok) allUsers.value = await res.json()
}

onMounted(() => {
    loadFriends()
    window.addEventListener('friends-updated', loadFriends)
})

onUnmounted(() => {
    window.removeEventListener('friends-updated', loadFriends)
})
</script>

<template>
    <section class="flex flex-col gap-4">
        <div class="flex items-center justify-between gap-3">
            <div class="flex items-baseline gap-2">
                <span class="input-label !mb-0">Friends</span>
                <span class="text-xs text-muted">· {{ friends.length }} total</span>
            </div>
            <button type="button" @click="toggleAdd" :aria-expanded="showAdd"
                :class="showAdd ? 'bg-white/[0.04] text-muted hover:text-white' : 'bg-sage text-navy-900 hover:bg-sage/90'"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] tracking-widest uppercase transition">
                <X v-if="showAdd" :size="12" />
                <Plus v-else :size="12" />
                {{ showAdd ? 'Close' : 'Add friend' }}
            </button>
        </div>

        <div class="flex flex-wrap items-center gap-3">
            <div class="relative flex-1 min-w-[180px]">
                <Search :size="13" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                <input ref="searchInput" v-model="query" type="text"
                    :placeholder="showAdd ? 'Search players' : 'Search friends'"
                    :aria-label="showAdd ? 'Search players' : 'Search friends'"
                    @keydown.esc.prevent="showAdd ? closeAdd() : query = ''"
                    class="w-full bg-navy-900 border border-white/[0.07] rounded-lg pl-8 pr-3 py-2
                           text-sm text-white placeholder:text-muted/50
                           focus:outline-none focus:border-teal/50 transition" />
            </div>
            <AppFilterTabs v-if="!showAdd" v-model="activeFilter" :counts="counts"
                :options="['all', 'online', 'pending']" />
        </div>

        <p v-if="actionError" class="text-xs text-coral">{{ actionError }}</p>

        <!-- add a friend -->
        <div v-if="showAdd">
            <div v-if="availableUsers.length" class="max-h-[420px] overflow-y-auto scroll-thin">
                <ProfileFriendRow v-for="u in availableUsers" :key="u.id" :user="u">
                    <button type="button" @click="sendRequest(u.id)"
                        class="px-2 py-1.5 text-xs text-teal hover:text-white transition">
                        Add
                    </button>
                </ProfileFriendRow>
            </div>
            <p v-else class="text-xs text-muted py-4 border-t border-white/[0.07]">No players found</p>
        </div>

        <template v-else>
            <!-- incoming requests -->
            <div v-if="incoming.length">
                <div class="input-label !mb-3">Requests ({{ incoming.length }})</div>
                <ProfileFriendRow v-for="r in incoming" :key="r.id" :user="r.friend">
                    <button type="button" @click="answerRequest(r.id, 'accept')"
                        class="px-2 py-1.5 text-xs text-teal hover:text-white transition">
                        Accept
                    </button>
                    <button type="button" @click="answerRequest(r.id, 'reject')"
                        class="px-2 py-1.5 text-xs text-muted hover:text-white transition">
                        Decline
                    </button>
                </ProfileFriendRow>
            </div>

            <!-- friends or sent requests -->
            <div>
                <ProfileFriendRow v-for="f in filteredList" :key="f.id" :user="f.friend">
                    <template v-if="activeFilter !== 'pending'">
                        <button type="button" @click="inviteToGame(f.friend.id)"
                            aria-label="Invite to play" title="Invite to play"
                            class="w-9 h-9 rounded-md flex items-center justify-center
                                   text-teal hover:text-white hover:bg-white/[0.04] transition">
                            <Gamepad2 :size="15" />
                        </button>
                        <button type="button" @click="openChat(f.friend.id)"
                            aria-label="Message" title="Message"
                            class="w-9 h-9 rounded-md flex items-center justify-center
                                   text-muted hover:text-white hover:bg-white/[0.04] transition">
                            <MessageCircle :size="15" />
                        </button>
                    </template>
                    <button v-if="confirmRemoveId === f.id" type="button" @click="removeFriend(f.id)"
                        @blur="confirmRemoveId = null"
                        class="px-2 h-9 text-xs text-coral transition">
                        Sure?
                    </button>
                    <button v-else type="button" @click="removeFriend(f.id)"
                        :aria-label="activeFilter === 'pending' ? 'Cancel request' : 'Remove friend'"
                        :title="activeFilter === 'pending' ? 'Cancel request' : 'Remove friend'"
                        class="w-9 h-9 rounded-md flex items-center justify-center
                               text-muted hover:text-coral hover:bg-white/[0.04] transition">
                        <X :size="15" />
                    </button>
                </ProfileFriendRow>
                <div class="border-t border-white/[0.07] pt-4">
                    <p v-if="!filteredList.length" class="text-xs text-muted">
                        {{ query.trim() ? 'No players found' : emptyText[activeFilter] }}
                    </p>
                </div>
            </div>
        </template>

    </section>
</template>