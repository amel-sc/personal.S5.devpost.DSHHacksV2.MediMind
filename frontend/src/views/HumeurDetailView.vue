<script setup>
    const props = defineProps({ id: { type: String, required: true } })
</script>
<template>
    <div class="container">
        <h3>Humeur {{ id }}</h3>
        
    </div>
</template>