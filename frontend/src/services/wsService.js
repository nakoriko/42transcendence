/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   wsService.js                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nakoriko <nakoriko@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/03 20:56:22 by nakoriko          #+#    #+#             */
/*   Updated: 2026/07/11 21:18:54 by nakoriko         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

import { useChatStore } from "@/stores/chat"
import { usePresenceStore } from "@/stores/presence"

export { connect, disconnect, send}

let socket = null

const messageHandlers = {
    chat_message: (data) =>  {
        const chatStore = useChatStore()
        chatStore.receiveMessage(data)
    },

    chat_error: (data) =>  {
        const chatStore = useChatStore()
        chatStore.receiveError(data)
        // console.warn('WS: chat error', data),
    },

    online_count: (data) => {
        const presenceStore = usePresenceStore()
        presenceStore.setCount(data.count)
    },
    presence_update: (data) => {
        const presenceStore = usePresenceStore()
        presenceStore.setStatus(data.user_id, data.is_online)
    },
    
    //!!!!!!! NAT: 
    //add for recive friends request in real time. 
    //UNcomment when Sabino will finish on backend
    //in App.vue add aevetnListener as well (onMounted + onUnmounted)
    
    friend_request_received:  () => {
        window.dispatchEvent(new CustomEvent('friends-updated'))
    },
    friend_request_accepted: () => {
        window.dispatchEvent(new CustomEvent('friends-updated'))
    } 

}

function connect(token) {
    if(socket) return // do not open 2nd ws

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws' //protocl type defines dinamycly buy HTTPS or HTTP
    const url = `${protocol}://${window.location.host}/ws/game/`

    socket = new WebSocket(url)

    socket.onopen = () => {
        socket.send(JSON.stringify({type: 'auth', token}))
    }

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data) //trasform str to obj
        const handler = messageHandlers[data.type]
        if(handler)  handler(data)
        else console.warn('WS: unknown type', data.type)
    }

    socket.onclose = () => {
        socket = null
    }

    socket.onerror = (err) => {
        console.error('WS error', err)
    } //for debugging
}


function disconnect() {
    if(!socket) return
    socket.close()
}


function send(payload) {
    if(!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn('WS: cannot send, ws not connected')
        return
    }
    socket.send(JSON.stringify(payload))
}