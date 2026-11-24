<script setup>
const config = useRuntimeConfig()
const token = useCookie('chatbot_token')
const toast = useToast()
const sending = ref(false)
const messages = ref([])
const input = ref('')

if (!token.value) {
  await navigateTo('/signin')
}

async function send() {
  if (!input.value.trim() || sending.value) return
  const text = input.value
  sending.value = true
  try {
    const res = await $fetch(`${config.public.apiBase}/api/chat`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}` },
      body: { message: text }
    })
    messages.value.push({ role: 'user', content: text })
    messages.value.push({ role: 'assistant', content: res.reply })
    input.value = ''
  } catch (err) {
    toast.add({ title: err.data?.error || 'Something went wrong', color: 'error' })
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto mt-6 px-4">
    <div class="space-y-3 mb-4">
      <div 
        v-for="(m, i) in messages" 
        :key="i"
        class="flex"
        :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
      >
            <div
            class="max-w-[80%] rounded-2xl px-4 py-2"
            :class="m.role === 'user' ? 'bg-primary text-white' : 'bg-muted'"
            >
            {{ m.content }}
            </div>
      </div>
    </div>

    <div class="flex gap-2">
      <UInput v-model="input" class="flex-1" placeholder="Type a message" @keydown.enter="send" />
      <UButton :loading="sending" @click="send">Send</UButton>
    </div>
  </div>
</template>