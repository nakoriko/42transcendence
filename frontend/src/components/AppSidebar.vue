<script setup>
import AppLogo from './AppLogo.vue';
import { ref, computed } from 'vue'
import {
  User, Gamepad2, BarChart2, MessageSquare, Bell, LogOut, Check, X
} from 'lucide-vue-next'

const props = defineProps ({
  user: {
    type: Object,
    default: () => ({username: 'Player'})
  }, 
  incomingRequests: {
    type: Array,
    default: () =>[]
  },
  hasUnreadMessages: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'full'
  },
  mobileOpen: {
    type: Boolean,
    default: false
  }
})

const showRequests = ref(false)
const emit = defineEmits(['logout', 'accept-request', 'decline-request', 'close-mobile'])
const isOverlay = computed(() => props.mode === 'hidden')

//array for routerLink istead of  all links in template
const navLinks= [
  { to: '/profile', label: 'Profile', icon: User},
  { to: '/lobby', label: 'Game', icon: Gamepad2 },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart2 }, 
  { to: '/chat', label: 'Chat', icon: MessageSquare} ,
]
</script>

<template>
  <Transition name="fade">
    <div
      v-if="isOverlay && mobileOpen"
      class="fixed inset-0 bg-black/50 z-40"
      @click="emit('close-mobile')">
    </div>
  </Transition>

  <Transition name="slide">
    <aside 
      v-if="!isOverlay || mobileOpen"
      class="flex-shrink-0 border-r border-white/[0.07]
                    flex flex-col h-screen transition-[width] duration-200 w-60 2xl:w-80"
      :class="[
        isOverlay ? 'fixed inset-y-0 left-0 z-50 bg-navy-800' : 'sticky top-0 bg-navy-800/30'
      ]">

      
    <!-- Logo gouse to home(/) -->
    <RouterLink to="/" class="p-6 pb-4 flex items-center">
      <AppLogo/>
    </RouterLink>

    <!-- Links from array-->
    <nav class="flex-1 flex flex-col gap-1 px-3 pt-2">
      <RouterLink 
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="relative flex items-center gap-3 py-2.5 px-4 rounded-xl text-sm font-light text-muted transition
            hover:bg-white/[0.04] hover:text-white
            [&.router-link-exact-active]:bg-teal/[0.12] [&.router-link-exact-active]:text-teal"
        >
        <component :is="link.icon" :size="17" aria-hidden="true" />
        <span>{{ link.label }}</span>
        <span
          v-if="link.to === '/chat' && hasUnreadMessages"
            class="bg-coral rounded-full flex-shrink-0 w-2 h-2 ml-auto"
        ></span>
      </RouterLink>
    </nav>

    <!--Devider-->
    <div class="mx-4 my-2 border-t border-white/[0.07]"></div>
    
    <!--Friend income invites-->
    <div class="px-3 pb-2">
      <button
        @click="showRequests = !showRequests"
        class="w-full flex items-center gap-3 py-2.5 px-4 rounded-xl text-sm font-light transition relative"
        :class=" [
          incomingRequests.length
          ? 'text-sand hover:bg-white/[0.04]'
          : 'text-muted hover:bg-white/[0.04] hover:text-white']"
      >
      <Bell :size="17" aria-hidden="true"></Bell>
      <span>Requests</span>
      <span
        v-if="incomingRequests.length"
        class="bg-coral text-white text-[9px] font-semibold
              min-w-[18px] h-[18px] rounded-full flex items-center 
              justify-center px-1 ml-auto">
      {{ incomingRequests.length }}
    </span>
    </button>

    <!--dropdown o list of incoming invites-->
    <Transition name="fade">
      <div
        v-if="showRequests && incomingRequests.length"
        class="mt-1 mx-1 bg-navy-900 border border-white/[0.07] rounded-xl overflow-hidden"
      >
        <div
          v-for="req in incomingRequests"
          :key="req.id"
          class="flex items-center gap-3 px-4 py-2.5 border-b border-white/[0.04]"
        >
          <div class="w-7 h-7 rounded-full bg-teal/20 flex items-center justify-center text-sage text-xs flex-shrink-0">
            {{ req.username?.[0]?.toUpperCase() ?? 'P'}}
          </div>
          <span class="text-xs text-white flex-1 truncate">{{ req.username || 'Unknown' }}</span>
          <button @click="emit('accept-request', req.id)" class="text-sage hover:text-white transition p-1" title="Accept">
            <Check :size="13"></Check>
          </button>
          <button @click="emit('decline-request', req.id)" class="text-muted hover:text-coral transition  p-1" title="Decline">
            <X :size="13"></X>
          </button>
        </div>
      </div>
      </Transition>  
  </div>

  <!--devider-->
  <div class="mx-4 mb-4 border-t border-white/[0.07]"></div>

  <!--USer footer-->
  <div class="px-3 pb-5">
    <div class="group flex items-center gap-3 py-3 rounded-xl
              border border-white/[0.07] hover:bg-white/[0.03] 
              transition cursor-default px-4">
    <!--Avatar with green point-->
    <div class="relative flex-shrink-0">
      <img v-if="user.avatar" :src="user.avatar" alt=""
        class="w-8 h-8 rounded-full object-cover">
      <div v-else class="w-8 h-8 rounded-full bg-teal/20 flex items-center justify-center text-sage text-sm font-light">
        {{ user.nickname?.[0]?.toUpperCase() ?? 'P' }}
      </div>
      <div class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-400 rounded-full border-2 border-navy-800"></div>
    </div>

    <!--NAME-->
    <div class="flex-1 min-w-0">
      <p class="text-white text-xs truncate">{{ user.nickname }}</p>
      <p class="text-muted text-[10px]">Player</p>
    </div>

    <!--Loguot-->
    <button @click="emit('logout')"
            class="p-1 text-muted/40 hover:text-coral transition
            opacity-0 group-hover:opacity-100"
            title="Logout"
    >
      <LogOut :size="15"></LogOut>
    </button>
  </div>
</div>

</aside>
</Transition>
</template>

<style>
  .fade-enter-active, .fade-leave-active {transition: opacity 0.15s, transform 0.15s;}
  .fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px);}

  .slide-enter-active, .slide-leave-active {transition: transform 0.2s ease;}
  .slide-enter-from, .slide-leave-to { transform: translateX(-100%);}
</style>


