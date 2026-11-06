<script setup>
defineProps({
    humeurJours: {
        type: Object,
        required: true
    },
    humeurJoursCauses: {
        type: Object,
        required: true
    },
})

</script>
<template>
    <p>Votre humeur ce jour : {{ humeurJours.humeur_desce }}</p>
    <p>Votre note ce jour : </p>
    <p>{{ humeurJours.note }}</p>
    <p>Les causes de votre humeur : </p>
    <ul>
        <li v-for="humeurJoursCause in humeurJoursCauses">
            {{ humeurJoursCause.id_humeur_cause }}
        </li>
    </ul>
</template>