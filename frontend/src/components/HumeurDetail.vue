<script setup>
defineProps({
    humeurJours: {
        type: [Object, null],
        required: true
    },
    humeurJoursCauses: {
        type: [Array, null],
        required: true
    },
})

</script>
<template>
    <p>Votre humeur ce jour : {{ humeurJours.humeur_desce }}</p>
    <p>Votre note ce jour : </p>
    <p>{{ humeurJours.note }}</p>
    <p>Les causes de votre humeur : </p>
    <p v-if="!humeurJoursCauses">Aucune cause à votre humeur de ce jour</p>
    <ul v-else>
        <li v-for="humeurJoursCause in humeurJoursCauses" :key="humeurJoursCause.id">
            {{ humeurJoursCause.cause_val }}
        </li>
    </ul>
</template>