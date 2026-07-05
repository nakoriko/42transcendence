<script setup>
    import { computed, ref} from 'vue'
    import { useChatStore } from '@/stores/chat';
    import AppInput from '../AppInput.vue';
    import AppButton from '../AppButton.vue';

    const chatStore = useChatStore()
    const draft = ref('')

    const activeMessages = computed(() => {
        if(!chatStore.activeContactId) return []
        return chatStore.messages[chatStore.activeContactId] || []
    })

    function handleSend() {
        if(!draft.value.trim()) return
        chatStore.sendMessage(chatStore.activeContactId, draft.value)
        draft.value = ''
    }

</script>

<template>
    <div class="chat-window">
        <div v-if="!chatStore.activeContactId" class="chat-empty">Choose a chat</div>
        <template v-else>
            <div class="chat-messages scroll-thin">
                <div v-for="(msg, i) in activeMessages"
                    :key="i"
                    class="chat-message"
                    :class="msg.self ? 'mine' : 'theirs'">
                    {{ msg.content }}</div>
            </div>

            <div v-if="chatStore.lastError" class="chat-error">
                {{  chatStore.lastError }}
            </div>

            <div class="chat-input-row">
                <AppInput v-model="draft"
                    label=""
                    placeholder="Write a message..."
                    @keyup.enter="handleSend"
                    class="flex-1"/>
                <AppButton variant="compact" @click="handleSend">Send</AppButton>
            </div>
        </template>
    </div>
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