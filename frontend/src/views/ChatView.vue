<script setup>
import ChatContactList from '@/components/chat/ChatContactList.vue';
import ChatWindow from '@/components/chat/ChatWindow.vue';
</script>

<template>
    <div class="chat-view">
        <aside class="chat-sidebar">
            <ChatContactList></ChatContactList>
        </aside>
        <section class="chat-main">
            <ChatWindow></ChatWindow>
        </section>
    </div>
</template>

<style scoped>
    .chat-view {
        display: flex;
        height: 100%; 
        gap: 24px;
    }

    .chat-sidebar {
        width: clamp(260px, 30vw, 380px);
        flex-shrink: 0;
        height: 100%;
        overflow-y: auto;
        border-right: 1px solid rgba(255,255,255, 0.07);
        padding-right: 24px;
    }

    .chat-main {
        flex: 1;
        min-width: 0;
        height: 100%;
        display: flex;
    }

    @media (max-width: 767px) {
        .chat-view {
            flex-direction: column;
            gap: 12px;
        }

        .chat-sidebar {
            width: 100%;
            height: 40vh;
            overflow: hidden;
            border-right: none;
            padding-right: 0;
        }

        .chat-main {
            height: auto;
            flex: 1;
            min-height: 0;
        }
    }

</style>