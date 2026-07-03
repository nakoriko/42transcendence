<script setup>
  import { ref, watch, onMounted, computed } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import AppSidebar from './components/AppSidebar.vue'
  import { apiFetch } from './utils/apiFetch.js'
  import { useUserStore } from './stores/user.js'


  const userStore = useUserStore()

  const router = useRouter()
  const route = useRoute()

  const isLoggedIn =  computed(() =>!!userStore.currentUser)
  const user =  computed(() => userStore.currentUser ?? {nickname: 'Player'})
  const incomingRequests=ref([])



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
  })

  watch(route, () => {
      if(isLoggedIn.value) loadIncoming()
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
      :user="user"
      :incoming-requests="incomingRequests"
      @logout="logout"
      @accept-request="acceptRequest"
      @decline-request="declineRequest" />
      
    
    <div class="flex-1 min-w-0 flex flex-col h-screen overflow-y-scroll scroll-thin">
        <div class="max-w-[1700px] mx-auto w-full px-10 py-10 flex-1">
          <RouterView />
        </div>
      <!-- футер переезжает сюда, убираем fixed -->
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
