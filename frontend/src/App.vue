<script setup>
  import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
  import { Menu } from 'lucide-vue-next'
  import { useRouter, useRoute } from 'vue-router'
  import AppSidebar from './components/AppSidebar.vue'
  import { apiFetch } from './utils/apiFetch.js'
  import { useUserStore } from './stores/user.js'
  import { useChatStore } from './stores/chat.js'


  const userStore = useUserStore()
  const chatStore = useChatStore()
  const router = useRouter()
  const route = useRoute()
  const isLoggedIn =  computed(() =>!!userStore.currentUser)
  const user =  computed(() => userStore.currentUser ?? {nickname: 'Player'})
  const incomingRequests=ref([])
  const sidebarMode = ref('full')
  const mobileMenuOpen = ref(false)

  function updateSidebarMode() {
    const w = window.innerWidth
    if(w < 768) sidebarMode.value = 'hidden'
    else if (w < 1280) sidebarMode.value = 'collapsed'
    else sidebarMode.value = 'full' //>=1280
    if(sidebarMode.value !== 'hidden') mobileMenuOpen.value = false
  }


  async function  loadIncoming() {
    if(!isLoggedIn.value) return
    try {
      const friendsRes = await apiFetch('/api/users/friends/')
      const friendsData = await friendsRes.json()

      incomingRequests.value = (friendsData.incoming ?? []).map( r=> ({
          id: r.id,
          username: r.friend.nickname
        }))

    } catch (e) {
      console.error('Sidebar friends data load failed')
    }
    
  }


  onMounted(async () => {
    if(isLoggedIn.value) {
      await userStore.fetchUser()
      loadIncoming()
    }
    updateSidebarMode()
    window.addEventListener('resize', updateSidebarMode)
    window.addEventListener('friends-updated', loadIncoming) //NAT: uncomment when Sabino will finish on backend

  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateSidebarMode)
    window.removeEventListener('friends-updated', loadIncoming) //NAT: uncomment when Sabino will finish on backend

  })

  watch(route, () => {
      if(isLoggedIn.value) loadIncoming()
      mobileMenuOpen.value = false
  })

  function logout() {
      userStore.logout()
      incomingRequests.value = []
      router.push('/login')
  }


  async function acceptRequest(id) {
    await apiFetch(`/api/users/friends/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ action: 'accept'})
    })
    window.dispatchEvent(new CustomEvent('friends-updated'))
    await loadIncoming()
  }

  async function declineRequest(id) {
    await apiFetch(`/api/users/friends/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({action: 'reject'})
    })
    window.dispatchEvent(new CustomEvent('friends-updated'))
    await loadIncoming()
  }

    
</script>

<template>
  <div class="flex min-h-screen bg-navy-900">
    
    <AppSidebar 
      v-if="isLoggedIn"
      :mode="sidebarMode"
      :mobile-open="mobileMenuOpen"
      :user="user"
      :incoming-requests="incomingRequests"
      :has-unread-messages="chatStore.hasUnread"
      @logout="logout"
      @accept-request="acceptRequest"
      @decline-request="declineRequest"
      @close-mobile="mobileMenuOpen = false" />

      <!-- burger when sidebar is hidden -->
    <button v-if="isLoggedIn && sidebarMode === 'hidden'"
      @click="mobileMenuOpen = true"
      class="fixed top-4 left-4 z-30 p-2.5 rounded-xl bg-navy-800/80 border border-white/[0.07]
              text-white backdrop-blur-sm"
      aria-label="Open Menu">
      <Menu :size="20"></Menu>
    </button>

      
    
    <div class="flex-1 min-w-0 flex flex-col h-screen overflow-y-scroll scroll-thin">
        <div class="max-w-[1700px] mx-auto w-full px-[var(--layout-px)] pb-[var(--layout-py)] flex-1"
          :style="{paddingTop: sidebarMode === 'hidden' ? '5rem' : 'var(--layout-py)'}">
          <RouterView />
        </div>
      <footer class="py-4 text-center text-xs text-muted/40 mt-auto">
        <a href="/privacy" class="hover:text-muted transition">Privacy Policy</a>
        <span class="mx-2 text-muted/20"> | </span>
        <a href="/terms" class="hover:text-muted transition">Terms of Service</a>
      </footer>
    </div>

  </div>
</template>

<style scoped>
</style>
