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
        width: 380px;
        height: 100%;
        overflow-y: auto;
        /* border-right: 1px solid rgba(255,255,255,0.1); */
    }

    .chat-main {
        flex: 1;
        height: 100%;
        display: flex;
    }

</style>