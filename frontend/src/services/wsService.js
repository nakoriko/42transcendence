/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   wsService.js                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/03 20:56:22 by nakoriko          #+#    #+#             */
/*   Updated: 2026/07/04 13:36:41 by nakoriko         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

import { useChatStore } from "@/stores/chat"

export { connect, disconnect, send}

let socket = null

const messageHandlers = {
    auth_success: () => console.log('WS: authenticated'),
    chat_message: (data) =>  {
        const chatStore = useChatStore()
        chatStore.receiveMessage(data)
    },

    chat_error: (data) =>  {
        const chatStore = useChatStore()
        chatStore.receiveError(data)
        // console.warn('WS: chat error', data),
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