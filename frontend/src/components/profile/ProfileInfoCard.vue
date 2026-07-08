<script setup>
import ProfileAvatar from '../ProfileAvatar.vue';
import AppInput from '../AppInput.vue';
import AppButton from '../AppButton.vue';
import { ref } from 'vue'
import { apiFetch } from '@/utils/apiFetch.js';
import { Pencil } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user.js';


const userStore =  useUserStore()
const props = defineProps ({ user: Object})
const emit = defineEmits (['updated'])
const errorMsg = ref('')

const isEditing = ref(false)
const editForm = ref ({ nickname: '', email: ''})


//editing
function startEditing() {
    editForm.value.nickname = props.user.nickname
    editForm.value.email = props.user.email
    isEditing.value = true
}

//save changes
async function saveProfile() {
    errorMsg.value = ''
    try {
        const response = await apiFetch('/api/users/profile/', {
            method: 'PATCH',
            body: JSON.stringify({
                nickname: editForm.value.nickname,
                email: editForm.value.email
            })
        })
        if(!response) return
        if(response?.ok) {
            isEditing.value = false
            await userStore.refreshUser()
            emit('updated')
            return
        }
        const data = await response.json()
        errorMsg.value = Object.values(data).flat().join(' ')
    } catch {
        errorMsg.value = 'Something went wrong. Try again'
    }
}


//upload
async function uploadAvatar(file) {
    if(!file) return

    const formData = new FormData()
    formData.append('avatar', file)

    const token = localStorage.getItem('access')
    const response = await fetch('/api/users/avatar/', {
        method: 'PATCH', //updates user tha already exist
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
    })

    if(response.ok) {
        await userStore.refreshUser()
        emit('updated')
    } 
}

</script>

<template>
    <div class="self-start w-full pb-4 ">
        <div class="flex items-center gap-4 sm:gap-8 w-full flex-wrap">
            <ProfileAvatar
            :user="user"
            :canUpload="true"
            class="min-w-0"
            @upload="uploadAvatar" />
            
            <button v-if="!isEditing"
                @click="startEditing"
                class="flex items-center gap-1.5 px-2.5 py-1 text-[11px] 
                    font-light tracking-widest uppercase rounded transition
                    bg-white/[0.04] text-muted hover:text-white flex-shrink-0">
                <Pencil :size="11" />
                Edit
            </button>
        </div>

        <div v-if="isEditing" class="mt-4 flex flex-col gap-3">
            <AppInput v-model="editForm.nickname" label="Nickname" type="text" maxlength="15" />
            <AppInput v-model="editForm.email" label="Email" type="email" />
            <p v-if="errorMsg" class="text-[11px] text-coral"> {{  errorMsg }}</p>
            <div class="flex gap-2 mt-1">
                <AppButton variant="primary" @click="saveProfile">Save</AppButton>
                <AppButton variant="ghost" @click="isEditing = false; errorMsg=''">Cancel</AppButton>
            </div>
        </div>
    </div>
</template>