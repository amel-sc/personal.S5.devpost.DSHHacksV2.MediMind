<script setup>
import HumeurForm from '@/components/HumeurForm.vue';
import { api } from '@/services/api';
import { onMounted, ref } from 'vue';

const humeurs = ref([]);
const humeurCauses = ref([]);
const chargement = ref(false);
const error = ref(null);

async function charger() {
    chargement.value = true
    try {
        const response_humeur = await api.humeur.lister();
        const response_humeurCause = await api.humeurCause.lister();

        humeurs.value = response_humeur.data;
        humeurCauses.value = response_humeurCause.data;

    } catch (e) {
        error.value = e;
        console.error(e);        
    } finally {
        chargement.value = false;
    }
}

onMounted(charger);
</script>
<template>
    <div class="container">
        <h3>Humeur</h3>
        <HumeurForm :humeurs="humeurs" :humeur-causes="humeurCauses" />
    </div>
</template>