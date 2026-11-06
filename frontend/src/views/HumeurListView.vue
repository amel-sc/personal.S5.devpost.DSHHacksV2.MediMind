<script setup>
import { onMounted, ref } from 'vue';
import { api } from '@/services/api';

const humeurJours = ref([]);
const chargment = ref(false);
const erreur = ref(null)

function charger() {
    try {
        

    } catch (error) {
        
    }
}

onMounted(charger)
</script>

<template>
    <div class="container">
        <h3>Humeur</h3>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th scope="col">Date</th>
                        <th scope="col">Humeur</th>
                        <th scope="col">Cause</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th scope="row">1</th>
                        <td>Mark</td>
                        <td>Otto</td>
                        <td>@mdo</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>