<script setup>
import { ref } from 'vue'

// Liste des choix : ajoutez-en autant que vous voulez, ils passeront à la ligne tout seuls
const options = [
  { valeur: 'stress', libelle: 'Stress et examens' },
  { valeur: 'sommeil', libelle: 'Sommeil' },
  { valeur: 'moral', libelle: 'Moral' },
  { valeur: 'solitude', libelle: 'Solitude' },
  { valeur: 'concentration', libelle: 'Concentration' },
  { valeur: 'procrastination', libelle: 'Procrastination' },
  { valeur: 'confiance', libelle: 'Confiance en soi' },
  { valeur: 'argent', libelle: 'Difficultés financières' },
  { valeur: 'orientation', libelle: "Doutes d'orientation" },
]

const choix = ref(null)   // valeur de l'option cochée

function envoyer() {
  console.log('Choix :', choix.value)
}
</script>
<template>
    <form @submit.prevent="envoyer">
        <div class="form-field mb-3">
            <label for="" class="form-label">Votre humeur</label>
            <div class="d-flex flex-wrap column-gap-4 row-gap-2">
                <div v-for="o in options" :key="o.valeur" class="form-field">
                    <input :id="`theme-${o.valeur}`" v-model="choix" class="radio" name="theme" :value="o.valeur" type="radio" required />
                    <label :for="`theme-${o.valeur}`">{{ o.libelle }}</label>
                </div>
            </div>
        </div>

        <button type="submit" class="btn-solid theme-primary" :disabled="!choix">
        Valider
        </button>
    </form>
</template>