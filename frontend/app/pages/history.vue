<script setup>
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const config = useRuntimeConfig()
const token = useCookie('chatbot_token')
const toast = useToast()
const messages = ref([])
const loading = ref(true)

if (!token.value) {
  await navigateTo('/signin')
}

function toHtml(text) {
  return DOMPurify.sanitize(marked.parse(text))
}

// Runs in the browser only, because DOMPurify needs a browser window
onMounted(async () => {
  try {
    const res = await $fetch(`${config.public.apiBase}/api/history`, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    messages.value = res.messages
  } catch (err) {
    if (err.status === 401) {
      token.value = null
      await navigateTo('/signin')
      return
    }
    toast.add({ title: err.data?.error || 'Something went wrong', color: 'error' })
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-2xl mx-auto mt-6 px-4 pb-10">
    <h1 class="text-xl font-semibold mb-4">Chat history</h1>

    <p v-if="loading" class="text-muted">Loading...</p>
    <p v-else-if="!messages.length" class="text-muted">No messages yet. Start a chat first.</p>

    <div class="space-y-3">
      <div
        v-for="m in messages"
        :key="m.id"
        class="flex"
        :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[80%] rounded-2xl px-4 py-2"
          :class="m.role === 'user' ? 'bg-primary text-white' : 'bg-muted'"
        >
          <div v-if="m.role === 'assistant'" v-html="toHtml(m.content)" />
          <span v-else>{{ m.content }}</span>
          <p class="text-xs opacity-60 mt-1">{{ new Date(m.created_at).toLocaleString() }}</p>
        </div>
      </div>
    </div>
  </div>
</template>