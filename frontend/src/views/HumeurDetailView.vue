<script setup>
import { ref } from 'vue';
import { api } from '@/services/api';    
import { onMounted } from 'vue';
import HumeurDetail from '@/components/HumeurDetail.vue';
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
    <div class="container mt-3">
        <RouterLink to="/humeur/list" type="button" class="theme-primary btn-solid btn-styled">
            <i class="bi bi-arrow-left"></i>
            Retour à la liste
        </RouterLink>
        <h3>Humeur {{ humeurJours ? humeurJours.date_creation : '-' }}</h3>
        
        <div v-if="chargement" class="d-flex justify-content-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <div v-else-if="humeurJours">
            <HumeurDetail :humeur-jours="humeurJours" :humeur-jours-causes="humeurJoursCauses" />
        </div>

        <div v-if="erreur" class="alert alert-danger mt-3 mb-3" role="alert">{{ erreur }}</div>
    </div>
</template>