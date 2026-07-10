/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   presence.js                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/06 19:10:10 by nakoriko          #+#    #+#             */
/*   Updated: 2026/07/10 10:39:28 by nakoriko         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

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