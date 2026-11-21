import { usePresenceStore } from "@/stores/presence";

export function usePresence() {
    const presenceStore = usePresenceStore()
    const isOnline = (user) => presenceStore.online[user.id] ?? user.is_online
    return { isOnline }
}