<script setup>
import { onMounted, ref } from 'vue';
import { api } from '@/services/api';

const humeurJours = ref([]);
const chargement = ref(false);
const erreur = ref(null)

async function charger() {
    chargement.value = true;

    try {
        const response = await api.humeurJours.lister();
        humeurJours.value = response.data;

    } catch (error) {
        erreur = e;
        console.error(e);
    } finally {
        chargement.value = false;
    }
}

onMounted(charger)
</script>

<template>
    <div class="container">
        <h3>Humeur</h3>

        <div v-if="chargement" class="d-flex justify-content-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Chargement…</span>
          </div>
        </div>

        <div v-else-if="humeurJours.length > 0" class="d-flex flex-column gap-3">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Date</th>
                            <th scope="col">Humeur</th>
                        </tr>
                    </thead>
                    <tbody>
                        <RouterLink
                            v-for="humeurJour in humeurJours"
                            :key="humeurJour.id"
                            :to="`/humeur/${humeurJour.id}`"
                            custom
                            v-slot="{ navigate }"
                            >
                            <tr
                                role="link"
                                tabindex="0"
                                @click="navigate"
                                @keydown.enter="navigate"
                                style="cursor: pointer;"
                            >
                                <td>{{ humeurJour.date_creation }}</td>
                                <td>{{ humeurJour.humeur_desce }}</td>
                            </tr>
                        </RouterLink>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-else class="text-center text-secondary py-5">
          <p class="mb-0">Aucun humeur trouvé</p>
        </div>

        <div v-if="erreur" class="alert alert-danger mt-3 mb-3" role="alert">{{ erreur }}</div>
    </div>
</template>