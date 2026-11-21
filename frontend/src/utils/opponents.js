const group = (user, isOnline) => {
    if (!isOnline(user)) return 2
    return user.is_friend ? 0 : 1
}

export function rankOpponents(users, query, isOnline) {
    const q = query.trim().toLowerCase()
    return users
        .filter(u => u.nickname.toLowerCase().includes(q))
        .sort((a, b) => group(a, isOnline) - group(b, isOnline) || a.nickname.localeCompare(b.nickname))
}