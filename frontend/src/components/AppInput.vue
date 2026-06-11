<script setup>
    defineProps ({
        label: String,
        type: {
            type: String,
            default: 'text',
        },
        placeholder: String,
        autocomplete: String
    })

    const model = defineModel()
</script>

<template>
    <div>
        <!--Name above field-->
        <label class="input-label">
            {{ label }}
        </label>
        <!--Input field-->
        <input
            v-model="model"
            :type="type"
            :placeholder="placeholder"
            :autocomplete="autocomplete"
            class="w-full bg-navy-900 border border-white/[0.07] rounded-xl px-4 py-3
                    text-white placeholder:text-muted/50
                    focus:outline-none focus:border-teal/50 transition"
                    />
           
    </div>
</template>