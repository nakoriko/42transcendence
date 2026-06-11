<script setup>
import AppButton from './AppButton.vue';
import AppLogo from './AppLogo.vue';
defineEmits(['logout'])

</script>

<template>
  <aside class="w-80 flex-shrink-0 bg-navy-800 border-r border-white/[0.07]
                flex flex-col sticky top-0 h-screen">

    <!-- Лого сверху -->
    <div class="p-6 pb-4">
      <AppLogo />
    </div>

    <!-- Ссылки по центру -->
    <nav class="flex-1 flex flex-col gap-1 px-3 pt-2">
      <RouterLink to="/lobby" class="sidebar-link">Game</RouterLink>
      <RouterLink to="/profile" class="sidebar-link">Profile</RouterLink>
      <RouterLink to="/dashboard" class="sidebar-link">Dashboard</RouterLink>
      <RouterLink to="/chat" class="sidebar-link">Chat</RouterLink>
    </nav>

    <!-- Logout снизу -->
    <div class="p-4 border-t border-white/[0.07]">
      <AppButton variant="ghost" @click="$emit('logout')" class="w-full">
        Logout
      </AppButton>
    </div>
  </aside>
</template>


