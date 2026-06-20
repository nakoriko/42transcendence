<script setup>
    import { ref, watch, onMounted } from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    import AppSidebar from './components/AppSidebar.vue'
    import { apiFetch } from './utils/apiFetch.js'

    const router = useRouter()
    const route = useRoute()

    const isLoggedIn = ref(!!localStorage.getItem('access'))
    const user = ref({nickname: 'Player'})
    const incomingRequests=ref([])

    async function loadSideBarData() {
      if(!isLoggedIn.value) return

      try{
        const [profileRes, friendsRes] = await Promise.all([
          apiFetch('/api/users/profile/'),
          apiFetch('/api/users/friends/')
        ])
        const profileData = await profileRes.json()
        const friendsData = await friendsRes.json()

        user.value = profileData

        incomingRequests.value = (friendsData.incoming ?? []).map( r=> ({
          id: r.id,
          username: r.friend.nickname
        }))

      } catch(e) {
        console.error('Sidebar data load failed', e)
      }
    }

    onMounted(() => {
      if(isLoggedIn.value) loadSideBarData()
    })

    watch(route, () => {
        isLoggedIn.value = !!localStorage.getItem('access')
        if(isLoggedIn.value) loadSideBarData()
    })

    function logout() {
        localStorage.removeItem('access')
        isLoggedIn.value = false
        user.value = {nickname: 'Player' }
        incomingRequests.value = []
        router.push('/login')
    }


    async function acceptRequest(id) {
      await apiFetch(`/api/users/friends/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ action: 'accept'})
      })
      await loadSideBarData()
    }

    async function declineRequest(id) {
      await apiFetch(`/api/users/friends/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify({action: 'reject'})
      })
      await loadSideBarData()
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
    
    <div class="flex-1 min-w-0 flex flex-col">
      <RouterView />
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
