<script setup>

    import { useRoute } from 'vue-router'

    const route = useRoute()
    const matchId = route.query.match_id
    const opponentId = route.query.player2
    //  opsen ws for match
    //listen game invite 
</script>

<template>
    <div class="min-h-screen flex items-center justify-center text-white"> 
        Remote match #{{ matchId  }} vs player {{  opponentId }} - waiting for Sabino's WS logic
    </div>
</template>