<script setup>
    import { ref, watch } from 'vue'
    import { useRouter, useRoute } from 'vue-router'

    const router = useRouter()
    const route = useRoute()

    const isLoggedIn = ref(!!localStorage.getItem('access'))

    watch(route, function() {
        isLoggedIn.value = !!localStorage.getItem('access')
    })

    function logout() {
        localStorage.removeItem('access')
        isLoggedIn.value = false
        router.push('/login')
    }
</script>

<template>
    <nav v-if="isLoggedIn">
      <RouterLink to="/lobby">Lobby</RouterLink>
      <RouterLink to="/profile">Profile</RouterLink>
      <RouterLink to="/friends">Friends</RouterLink>
      <button @click="logout">Logout</button>
  </nav>

  <RouterView />

  <footer class="fixed bottom-0 w-full py-4 text-center text-xs text-muted/40 bg-navy-900">
    <a href="/privacy" class="hover:text-muted transition">Privacy Policy</a>
    <span class="mx-2 text-muted/20"> | </span>
    <a href="/terms" class="hover:text-muted transition">Terms of Service</a>
  </footer>

</template>

<style scoped>
</style>
