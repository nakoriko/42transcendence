/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   period.js                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nakoriko <nakoriko@student.42firenze.it    +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/30 11:55:46 by nakoriko          #+#    #+#             */
/*   Updated: 2026/06/30 12:16:11 by nakoriko         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

export const PERIOD_DAYS = { '7d': 7, '30d': 30}

export function filterByPeriod(items, dateField, period) {
    if(period === 'All') return items
    const cutoff = Date.now() - PERIOD_DAYS[period] * (60 * 60 * 24 * 1000)
    return items.filter(item => new Date(item[dateField]).getTime() >= cutoff)

    //dateField takes field which name keeps in dateField argument (good practice for parametrization)
    //new Date() parses ISO date string into a Date object
    //getTime takes time from date (milliseconds from 1970)
    //comparing with filter limit (cutoff)
}