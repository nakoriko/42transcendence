/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   presence.js                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/06 19:10:10 by nakoriko          #+#    #+#             */
/*   Updated: 2026/07/06 19:12:36 by nakoriko         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

import { defineStore } from "pinia";

export const usePresenceStore = defineStore('presence', {
    state: () =>  ({
        onlineCount: 0
    }),
    actions: {
        setCount(count) {
            this.onlineCount = count
        }
    }
})