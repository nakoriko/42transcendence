import { defineStore } from "pinia";

export const usePresenceStore = defineStore('presence', {
    state: () =>  ({
        onlineCount: 0,
        online: {}
    }),
    actions: {
        setCount(count) {
            this.onlineCount = count
        },
        setStatus(userId, isOnline) {
            this.online[userId] = isOnline
        }
    }
})