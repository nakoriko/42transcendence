<script setup>
    import { ref, watch } from 'vue'
    import { useRouter, useRoute } from 'vue-router'
    import AppSidebar from './components/AppSidebar.vue'

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
  <div class="flex min-h-screen bg-navy-900">
    
    <AppSidebar v-if="isLoggedIn" @logout="logout" />
    
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
