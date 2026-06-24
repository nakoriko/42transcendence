<script setup>
import ProfileAvatar from '../ProfileAvatar.vue';
import AppInput from '../AppInput.vue';
import AppButton from '../AppButton.vue';
import { ref } from 'vue'
import { apiFetch } from '@/utils/apiFetch.js';
import { Pencil } from 'lucide-vue-next'


const props = defineProps ({ user: Object})
const emit = defineEmits (['updated'])

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
    const response = await apiFetch('/api/users/profile/', {
        method: 'PATCH',
        body: JSON.stringify({
            nickname: editForm.value.nickname,
            email: editForm.value.email
        })
    })
    if(response?.ok) {
        isEditing.value = false
        emit('updated')
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

    if(response.ok) emit('updated')
}

</script>

<template>
    <div class="self-start w-full pb-4 ">

        <div class="flex items-center gap-8 w-full">
            
            <ProfileAvatar
            :user="user"
            :canUpload="true"
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
            <AppInput v-model="editForm.nickname" label="Nickname" type="text" />
            <AppInput v-model="editForm.email" label="Email" type="email" />
            <div class="flex gap-2 mt-1">
                <AppButton variant="primary" @click="saveProfile">Save</AppButton>
                <AppButton variant="ghost" @click="isEditing = false">Cancel</AppButton>
            </div>
        </div>
    </div>
</template>