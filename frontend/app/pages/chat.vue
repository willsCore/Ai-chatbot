<script setup>
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const config = useRuntimeConfig()
const token = useCookie('chatbot_token')
const toast = useToast()
const sending = ref(false)
const messages = ref([])
const input = ref('')

if (!token.value) {
  await navigateTo('/signin')
}

function toHtml(text){
    return DOMPurify.sanitize(marked.parse(text))
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
        if (err.status === 401) {
            token.value = null
            await navigateTo('/signin')
            return
        }
        toast.add({ title: err.data?.error || 'Something went wrong', color: 'error' })
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto mt-6 px-4">
    ```vue
<div class="space-y-3 mb-4">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="flex"
        :class="m.role === 'user' ? 'justify-end' : 'justify-start'"
        >
        <div
            class="max-w-[80%] rounded-2xl px-4 py-2"
            :class="m.role === 'user'
            ? 'bg-primary text-white'
            : 'bg-muted'"
        >
            <div v-if="m.role === 'assistant'" v-html="toHtml(m.content)" class="markdown"/>
            <span v-else>{{ m.content }}</span>
        </div>
        </div>
    </div>
```

    <div class="flex gap-2">
      <UInput v-model="input" class="flex-1" placeholder="Type a message" @keydown.enter="send" />
      <UButton :loading="sending" @click="send">Send</UButton>
    </div>
  </div>
</template>


<style scoped>
.markdown > :deep(* + *) { margin-top: 0.75rem; }
.markdown :deep(h1),
.markdown :deep(h2),
.markdown :deep(h3),
.markdown :deep(h4) { font-weight: 600; margin-top: 1.25rem; }
.markdown :deep(h2) { font-size: 1.125rem; }
.markdown :deep(ul) { list-style: disc; padding-left: 1.25rem; }
.markdown :deep(ol) { list-style: decimal; padding-left: 1.25rem; }
.markdown :deep(li + li) { margin-top: 0.25rem; }
.markdown :deep(table) { display: block; overflow-x: auto; border-collapse: collapse; font-size: 0.875rem; }
.markdown :deep(th),
.markdown :deep(td) { border: 1px solid var(--ui-border); padding: 0.375rem 0.625rem; text-align: left; }
.markdown :deep(th) { font-weight: 600; }
.markdown :deep(code) { background: var(--ui-bg-elevated); padding: 0 0.25rem; border-radius: 0.25rem; }
.markdown :deep(pre) { overflow-x: auto; padding: 0.75rem; background: var(--ui-bg-elevated); border-radius: 0.5rem; }
</style>