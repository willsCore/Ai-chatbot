<script setup>

const token = useCookie('chatbot_token')
const config = useRuntimeConfig()

async function signOut() {
  try {
    await $fetch(`${config.public.apiBase}/api/signout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}` }
    })
  } catch {
    // Even if the token already expired, still sign out locally
  }
  token.value = null
  await navigateTo('/signin')
}

useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon', href: '/favicon.ico' }
  ],
  htmlAttrs: {
    lang: 'en'
  }
})

const title = 'AI Chatbot'
const description = 'Chat with Sage, an AI assistant, and review your past conversations.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description
})
</script>

<template>
  <UApp>
    <UHeader>
      <template #left>
        <NuxtLink to="/" class="font-semibold text-lg">AI Chatbot</NuxtLink>
      </template>

      <template #right>
        <template v-if="token">
          <UButton to="/chat" label="Chat" color="neutral" variant="ghost" />
          <UButton to="/history" label="History" color="neutral" variant="ghost" />
          <UButton label="Sign out" color="neutral" variant="subtle" @click="signOut" />
        </template>
        <UColorModeButton />
      </template>
    </UHeader>

    <UMain>
      <NuxtPage />
    </UMain>

  </UApp>
</template>
