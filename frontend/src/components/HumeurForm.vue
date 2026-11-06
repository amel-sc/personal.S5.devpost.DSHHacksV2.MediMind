<script setup>
import { ref } from 'vue'

// Liste des choix : ajoutez-en autant que vous voulez, ils passeront à la ligne tout seuls
const props = defineProps({
  humeurs: { type: Array, required: true },
  humeurCauses : { type: Array, required: true }
})

const humeur = ref(null);
const note = ref('');
const humeurCause = ref(null);

function envoyer() {
  console.log('Choix :', choix.value)
}
</script>
<template>
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
                    <input :id="`cause-${o.id}`" v-model="humeurCause" class="check" :value="o.id" type="checkbox" required />
                    <label :for="`cause-${o.id}`">{{ o.val }}</label>
                </div>
            </div>
        </div>

        <button type="submit" class="btn-solid theme-primary">
        Valider
        </button>
    </form>
</template>