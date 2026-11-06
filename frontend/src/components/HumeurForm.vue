<script setup>
import { ref } from 'vue'

// Liste des choix : ajoutez-en autant que vous voulez, ils passeront à la ligne tout seuls
const props = defineProps({
  humeurs: { type: Array, required: true },
})

const humeur = ref(null);
const note = ref('');

function envoyer() {
  console.log('Choix :', choix.value)
}
</script>
<template>
    <form @submit.prevent="envoyer">
        <div class="form-field mb-3">
            <label for="" class="form-label">Votre humeur</label>
            <div class="d-flex flex-wrap column-gap-4 row-gap-2">
                <div v-for="o in humeurs" :key="o.valeur" class="form-field">
                    <input :id="`theme-${o.val}`" v-model="humeur" class="radio" name="theme" :value="o.val" type="radio" required />
                    <label :for="`theme-${o.val}`">{{ o.desce }}</label>
                </div>
            </div>
        </div>

        <div class="form-field mb-3">
            <label for="note" class="form-label">Note de votre humeur</label>
            <textarea v-model="note" class="form-control" id="note" rows="4"></textarea>
        </div>

        <button type="submit" class="btn-solid theme-primary">
        Valider
        </button>
    </form>
</template>