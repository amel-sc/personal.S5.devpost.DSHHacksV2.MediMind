<script setup>
import { ref } from 'vue'
import { api } from '@/services/api';

// Liste des choix : ajoutez-en autant que vous voulez, ils passeront à la ligne tout seuls
const props = defineProps({
  humeurs: { type: Array, required: true },
  humeurCauses : { type: Array, required: true }
})

const humeur = ref(null);
const note = ref('');
const humeurCause = ref([]);
const erreur = ref(null)

async function envoyer() {
    try {
        const data = {
            id_humeur: humeur.value,
            note: note.value,
            id_humeur_causes: humeurCause.value
        }

        const response = await api.humeurJours.save(data)
        console.log(response.id_humeur_jours)
    } catch (e) {
        erreur.value = e;
        console.error(e);
    }
}

</script>
<template>
    <div v-if="erreur" class="alert alert-danger mt-3 mb-0" role="alert">{{ erreur }}</div>
    <h4>Ajouter votre humeur d'aujourd'hui</h4>
    <form @submit.prevent="envoyer">
        <div class="form-field mb-3">
            <label for="" class="form-label">Votre humeur</label>
            <div class="d-flex flex-wrap column-gap-4 row-gap-2">
                <div v-for="o in humeurs" :key="o.val" class="form-field">
                    <input :id="`humeur-${o.val}`" v-model="humeur" class="radio" :value="o.val" type="radio" required />
                    <label :for="`humeur-${o.val}`">{{ o.desce }}</label>
                </div>
            </div>
        </div>

        <div class="form-field mb-3">
            <label for="note" class="form-label">Note de votre humeur</label>
            <textarea v-model="note" class="form-control" id="note" rows="4"></textarea>
        </div>

        <div class="form-field mb-3">
            <label for="" class="form-label">Les causes de votre humeur</label>
            <div class="d-flex flex-wrap column-gap-4 row-gap-2">
                <div v-for="o in humeurCauses" :key="o.val" class="form-field">
                    <input :id="`cause-${o.id}`" v-model="humeurCause" class="check" :value="o.id" type="checkbox" />
                    <label :for="`cause-${o.id}`">{{ o.val }}</label>
                </div>
            </div>
        </div>

        <div class="d-grid gap-2">
            <button type="submit" class="btn-solid theme-primary">Valider</button>
        </div>
    </form>
</template>