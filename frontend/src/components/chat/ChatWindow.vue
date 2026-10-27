<script setup>
    import { computed, ref, watch} from 'vue'
    import { useChatStore } from '@/stores/chat';
    import { usePresence } from '@/composables/usePresence.js';
    import { chatTimeline } from '@/utils/chatTimeline.js';
    import { formatTime } from '@/utils/date.js';
    // import AppInput from '../AppInput.vue';
    // import AppButton from '../AppButton.vue';
    import { ArrowUp, Gamepad2 } from 'lucide-vue-next';
    import AppAvatar from '../AppAvatar.vue';
    import { useRouter } from 'vue-router';


    const props = defineProps({ contact: { type: Object, default: null } })
    const chatStore = useChatStore()
    const { isOnline } = usePresence()
    const router = useRouter()
    const draft = ref('')
    const scrollEl = ref(null)
    const online = computed(() => !!props.contact && isOnline(props.contact))
    const timeline = computed(() => props.contact 
        ? chatTimeline(chatStore.messages[props.contact.id] 
        ?? []) : [])

    function inviteToGame() {
        router.push({ path: '/lobby', query: { opponent: props.contact.id } })
    }

    function handleSend() {
        const text = draft.value.trim()
        if(!text || !online.value) return
        chatStore.sendMessage(props.contact.id, text)
        draft.value = ''
    }

    // keep the newest message in view: on a new message and on switching contact
    watch([() => props.contact?.id, () => timeline.value.length], () => {
        if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight}, { flush: 'post' })



</script>

<template>
    <section class="flex flex-col min-h-0">
        <div v-if="!contact" class="flex-1 flex items-center justify-center text-sm text-muted">
            Choose a contact to start chatting
        </div>

        <template v-else>
            <!-- header -->
            <div class="flex items-center gap-3 pb-4 border-b border-white/[0.07]">
                <AppAvatar :nickname="contact.nickname" :is-online="online" />
                <div class="min-w-0">
                    <div class="text-base text-white truncate">{{ contact.nickname }}</div>
                    <div class="text-xs" :class="online ? 'text-teal' : 'text-muted'">
                        {{ online ? 'Online now' : 'Offline' }}
                    </div>
                </div>
                <button @click="inviteToGame"
                    class="ml-auto p-2 rounded-md text-muted hover:text-white hover:bg-white/[0.04] transition"
                    title="Invite to game" aria-label="Invite to game">
                    <Gamepad2 :size="16" />
                </button>
            </div>
            <!-- messages -->
            <div ref="scrollEl" class="flex-1 min-h-0 overflow-y-auto scroll-thin flex flex-col gap-2 py-4 pr-2">
                <div v-if="!timeline.length" class="m-auto text-xs text-muted">
                    No messages yet. Say hi to {{ contact.nickname }}
                </div>

                <template v-for="(msg, i) in timeline" :key="i">
                    <!-- day divider: line — label — line -->
                    <div v-if="msg.day"
                        class="flex items-center gap-3 my-2 text-[10px] text-muted uppercase tracking-widest
                               before:flex-1 before:h-px before:bg-white/[0.07]
                               after:flex-1 after:h-px after:bg-white/[0.07]">
                        {{ msg.day }}
                    </div>

                    <div :class="msg.self
                            ? 'self-end bg-sage text-navy-900 rounded-[12px_12px_4px_12px]'
                            : 'self-start bg-white/[0.05] text-white rounded-[12px_12px_12px_4px]'"
                        class="max-w-[75%] px-3.5 py-2 text-sm leading-relaxed break-words">
                        {{ msg.content }}
                    </div>

                    <span v-if="msg.showTime"
                        :class="msg.self ? 'self-end' : 'self-start'"
                        class="text-[10px] text-muted tabular-nums px-1.5 -mt-1">
                        {{ formatTime(msg.timeStamp) }}
                    </span>
                </template>
            </div>

            <p v-if="chatStore.lastError" class="text-xs text-coral pb-2">{{ chatStore.lastError }}</p>

            <!-- input -->
            <form @submit.prevent="handleSend"
                class="flex items-center gap-2 pl-4 pr-1.5 py-1.5 rounded-full
                       border border-white/[0.08] bg-white/[0.03] focus-within:border-teal/40 transition">
                <input v-model="draft"
                    :disabled="!online"
                    :placeholder="online ? 'Write a message' : contact.nickname + ' is offline, messages are not delivered'"
                    class="flex-1 min-w-0 bg-transparent text-sm text-white placeholder:text-muted/60
                           outline-none disabled:cursor-not-allowed" />
                <button type="submit" :disabled="!online || !draft.trim()"
                    class="w-8 h-8 rounded-full bg-sage text-navy-900 flex items-center justify-center flex-shrink-0
                           transition hover:bg-sage/80 disabled:opacity-30 disabled:cursor-not-allowed"
                    aria-label="Send">
                    <ArrowUp :size="16" />
                </button>
            </form>
        </template>
    </section>
</template>


<style scoped>
    .chat-window {
        display: flex;
        flex-direction: column;
        height: 100%;
        flex: 1;
    }

    .chat-empty {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.6;
    }

    .chat-messages{
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 12px;
    }

    .chat-message {
        max-width: 60%;
        padding: 8px 12px;
        border-radius: 12px;
        overflow-wrap: break-word;
        word-break: break-word;
    }

    .chat-message.mine{
        align-self: flex-end;
        background: rgba(74, 140, 155, 0.25);
    }

    .chat-message.theirs {
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.08);
    }

    .chat-error {
        color: var(--color-coral);
        padding: 4px 12px;
        font-size: 0.85em;
    }

    .chat-input-row {
        display: flex;
        align-items: center;
        gap: 8px;
        /* padding: 12px; */
    }

    .chat-input {
        flex: 1;
    }
</style>