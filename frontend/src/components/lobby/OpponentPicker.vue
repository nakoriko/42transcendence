<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Search, X } from 'lucide-vue-next'
import AppAvatar from '../AppAvatar.vue'
import { usePresence } from '@/composables/usePresence.js'
import { rankOpponents } from '@/utils/opponents.js'
import { calcWinRate, calcTotalMatches } from '@/utils/stats.js'

const props = defineProps({ users: { type: Array, default: () => [] } })
const selectedId = defineModel()

const { isOnline } = usePresence()

const root = ref(null)
const trigger = ref(null)
const searchInput = ref(null)
const list = ref(null)

const open = ref(false)
const query = ref('')
const activeIndex = ref(0)

const selected = computed(() => props.users.find(u => u.id === selectedId.value) ?? null)
const options = computed(() => rankOpponents(props.users, query.value, isOnline))

async function openPopover() {
    open.value = true
    activeIndex.value = 0
    await nextTick()
    searchInput.value?.focus()
}

function close() {
    open.value = false
    query.value = ''
}

function toggle() {
    open.value ? close() : openPopover()
}

function pick(user) {
    selectedId.value = user.id
    close()
}

function move(step) {
    const count = options.value.length
    if (count) activeIndex.value = (activeIndex.value + step + count) % count
}

function pickActive() {
    const user = options.value[activeIndex.value]
    if (!user) return
    pick(user)
    trigger.value?.focus()
}

function closeAndFocus() {
    close()
    trigger.value?.focus()
}

function onOutsideClick(event) {
    if (open.value && !root.value?.contains(event.target)) close()
}

watch(query, () => { activeIndex.value = 0 })

// keeps the row chosen with the arrow keys visible inside the scrolling list
watch(activeIndex, async (index) => {
    await nextTick()
    list.value?.children[index]?.scrollIntoView({ block: 'nearest' })
})

onMounted(() => document.addEventListener('pointerdown', onOutsideClick))
onUnmounted(() => document.removeEventListener('pointerdown', onOutsideClick))
</script>

<template>
    <div ref="root" class="relative w-full">
        <div class="flex justify-center">
            <button ref="trigger" type="button" @click="toggle"
                :aria-expanded="open" aria-haspopup="listbox"
                class="flex flex-col items-center gap-3 max-w-full min-w-0 -m-2 p-2 rounded-xl
                       hover:bg-white/[0.04] focus:outline-none focus-visible:ring-1
                       focus-visible:ring-teal/50 transition">
                <AppAvatar v-if="selected" :nickname="selected.nickname" :is-online="isOnline(selected)" size="lg" />
                <span v-else class="w-16 h-16 rounded-full border border-dashed border-white/30
                                    flex items-center justify-center text-muted flex-shrink-0">?</span>

                <span class="block max-w-full min-w-0">
                    <span class="flex items-center justify-center gap-1.5 text-lg font-light text-muted">
                        <span class="truncate">{{ selected ? selected.nickname : 'Choose opponent' }}</span>
                        <ChevronDown :size="14" :class="{ 'rotate-180': open }"
                            class="text-muted flex-shrink-0 transition" />
                    </span>
                    <span class="block text-xs text-muted">Opponent</span>
                </span>

            </button>

            <button v-if="selected" type="button" @click="selectedId = null" aria-label="Clear opponent"
                class="absolute top-0 right-0 w-11 h-11 rounded-lg flex items-center justify-center
                       text-muted hover:text-white hover:bg-white/[0.04] transition">
                <X :size="16" />
            </button>
        </div>


        <!-- floats above the panel, so opening it does not move the layout -->
        <div v-if="open"
            class="absolute left-0 right-0 top-full mt-2 z-20 p-2 flex flex-col gap-2
                   bg-navy-800 border border-white/[0.07] rounded-xl shadow-xl">
            <div class="relative">
                <Search :size="13" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                <input ref="searchInput" v-model="query" type="text"
                    placeholder="Search players" aria-label="Search players"
                    @keydown.down.prevent="move(1)"
                    @keydown.up.prevent="move(-1)"
                    @keydown.enter.prevent="pickActive"
                    @keydown.esc.prevent="closeAndFocus"
                    @keydown.tab="close"
                    class="w-full bg-navy-900 border border-white/[0.07] rounded-lg pl-8 pr-3 py-2
                           text-sm text-white placeholder:text-muted/50
                           focus:outline-none focus:border-teal/50 transition" />
            </div>

            <div v-if="options.length" ref="list" role="listbox" aria-label="Players"
                class="flex flex-col gap-1 max-h-[260px] overflow-y-auto scroll-thin">
                <button v-for="(u, i) in options" :key="u.id" type="button"
                    role="option" :aria-selected="u.id === selectedId"
                    @click="pick(u)"
                    @mouseenter="activeIndex = i"
                    :class="i === activeIndex ? 'bg-white/[0.06]' : 'bg-white/[0.02]'"
                    class="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-left transition">
                    <AppAvatar :nickname="u.nickname" :is-online="isOnline(u)" size="sm" />
                    <span class="text-sm text-white flex-1 min-w-0 truncate">{{ u.nickname }}</span>
                    <span class="text-[10px] text-muted tabular-nums flex-shrink-0">
                        {{ calcTotalMatches(u.wins, u.losses) }} matches · {{ calcWinRate(u.wins, u.losses) }}%
                    </span>
                </button>
            </div>

            <p v-else class="text-xs text-muted text-center py-6">
                {{ users.length ? 'No players found' : 'No other players yet' }}
            </p>
        </div>
    </div>
</template>