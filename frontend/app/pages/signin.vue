<script setup>
const config = useRuntimeConfig()
const toast = useToast()
const loading = ref(false)
const token = useCookie('chatbot_token', { maxAge: 60 * 60 })

const state = reactive({ name: '',password: ''})

async function onSubmit() {
  loading.value = true
  try {
    const res = await $fetch(`${config.public.apiBase}/api/signin`, {
      method: 'POST',
      body: state
    })
    token.value = res.token
    await navigateTo('/chat')
  } catch (err) {
    toast.add({ title: err.data?.error || 'Something went wrong', color: 'error' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UCard class="max-w-md mx-auto mt-10">
    <UForm :state="state" @submit="onSubmit" class="space-y-4">
      <UFormField label="Name" name="name">
        <UInput v-model="state.name" class="w-full" />
      </UFormField>
      <UFormField label="Password" name="password">
        <UInput v-model="state.password" type="password" class="w-full" />
      </UFormField>
      <UButton type="submit" :loading="loading" block>Login in</UButton>
    </UForm>
  </UCard>
</template>
