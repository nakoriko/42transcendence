import { onMounted, onUnmounted } from 'vue'

export function useResizeObserver(elRef, callback, delay = 200) {
    let timer = null
    const observer = new ResizeObserver(() => {
        clearTimeout(timer)
        timer = setTimeout(callback, delay)        
    })

    onMounted(() => { if (elRef.value) observer.observe(elRef.value) })
    onUnmounted(() => { clearTimeout(timer); observer.disconnect()})
    return observer
}

//callback - function called by trigger (observer)
//timer needs to realize debounce, to avoid unncessary execution of funtion, during size is changing
//so, setTimeout takes function to execute and waits a delay before execute