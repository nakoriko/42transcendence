/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   chat.js                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/04 12:21:58 by nakoriko          #+#    #+#             */
/*   Updated: 2026/07/04 13:44:27 by nakoriko         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

import { defineStore } from "pinia";
import { send } from '@/services/wsService.js'


export const useChatStore = defineStore('chat', {
    state: () => ({
        messages: {},
        activeContactId: null,
        lastError: null
    }), 

    actions: {
        setActiveContact(contactId) {
            this.activeContactId = contactId
            if(!this.messages[contactId]) {
                this.messages[contactId] = []
            }
            this.lastError = null
        },

        receiveMessage(data) {
            const contactId = data.from_user.id // from whom
            if(!this.messages[contactId]) {
                this.messages[contactId] = []
            }
            this.messages[contactId].push ({
                peerId: contactId,
                content: data.content,
                timeStamp: Date.now(),
                self: false
            })
        },

        sendMessage(toUserId, content) {
            if(!content.trim()) return
            if(!this.messages[toUserId]) {
                this.messages[toUserId] = []
            }
            this.messages[toUserId].push({
                peerId: toUserId, //its not from actually, but which thread it is
                content,
                timeStamp: Date.now(),
                self: true
            })

            send({ type: 'chat_message', to_user_id: toUserId, content })
        },

        receiveError(data) {
            const reasons = {
                user_offline: 'User is offline',
                user_not_found: 'User is not found',
                invalid_message: 'Message cannot be empty'
            }
            this.lastError = reasons[data.reason] || 'Error of message sending'
        }

    }
})