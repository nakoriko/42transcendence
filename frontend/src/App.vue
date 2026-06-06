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

  <footer>
    <a href="/privacy">Privacy Policy</a>
    <span> | </span>
    <a href="/terms">Terms of Service</a>
  </footer>

</template>

<style scoped>
footer {
  margin-top: 60px;
  padding: 20px;
  text-align: center;
  font-size: 0.85em;
  color: #888;
  border-top: 1px solid #eee;
}
footer a {
  color: #888;
  text-decoration: none;
}
footer a:hover {
  text-decoration: underline;
}
</style>
