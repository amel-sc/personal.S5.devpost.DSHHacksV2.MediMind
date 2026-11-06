<script setup>
import { ref } from 'vue';
import { api } from '@/services/api';    
import { onMounted } from 'vue';
const props = defineProps({ id: { type: String, required: true } })

const humeurJours = ref(null);
const humeurJoursCauses = ref(null);
const chargement = ref(false);
const erreur = ref(null);

async function charger() {
    chargement.value = true;

    try {
        const response = await api.humeurJours.find(props.id);
        humeurJours.value = response.humeur_jours;
        humeurJoursCauses.value = response.humeur_jours_causes;

    } catch (e) {
        erreur.value = e;
        console.error(e);
    } finally {
        chargement.value = false;
    }
}

onMounted(charger)
</script>
<template>
    <div class="container">
        <h3>Humeur {{ humeurJours ? humeurJours.date_creation : '-' }}</h3>
        
        <div v-if="chargement" class="d-flex justify-content-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <div v-else-if="humeurJours">
            <p>Votre humeur ce jour : {{ humeurJours.humeur_desce }}</p>
            <p>Votre note ce jour : </p>
            <p>{{ humeurJours.note }}</p>
            <p>Les causes de votre humeur : </p>
            <ul>
                <li v-for="humeurJoursCause in humeurJoursCauses">
                    {{ humeurJoursCause.id_humeur_cause }}
                </li>
            </ul>
        </div>

        <div v-if="erreur" class="alert alert-danger mt-3 mb-3" role="alert">{{ erreur }}</div>
    </div>
</template>