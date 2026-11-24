<script setup>
const config = useRuntimeConfig()
const toast = useToast()
const loading = ref(false)

const state = reactive({
   name: '',
   email: '',
   password: '',
   confirm_password: ''
  })

async function onSubmit() {
  if (state.password !== state.confirm_password) {
    toast.add({ title: 'Password do not match', color: 'error' })
    return
  }
  loading.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/signup`, {
      method: 'POST',
      body: state
    })
    toast.add({ title: 'Account created', color: 'success' })
    await navigateTo('/signin')
  } catch (err) {
    toast.add({
      title: err.data?.error || 'Something went wrong',
      color: 'error'
    })
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
      <UFormField label="Email" name="email">
        <UInput v-model="state.email" class="w-full" />
      </UFormField>
      <UFormField label="Password" name="password">
        <UInput v-model="state.password" type="password" class="w-full" />
      </UFormField>
      <UFormField label="Confirm Password" name="confirm_password">
        <UInput v-model="state.confirm_password" type="password" class="w-full" />
      </UFormField>

      <UButton type="submit" :loading="loading" block>Create account</UButton>
    </UForm>
  </UCard>
</template>
