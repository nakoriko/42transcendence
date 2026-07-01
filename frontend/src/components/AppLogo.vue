<template>
  <div class="flex gap--0.5">
  <span v-for="letter in ['P','O','N','G']" :key="letter"
    class="w-10 h-10 rounded-full border border-white/30 inline-flex items-center justify-center text-lg font-light text-white">
    {{ letter }}
  </span>
  </div>
</template>