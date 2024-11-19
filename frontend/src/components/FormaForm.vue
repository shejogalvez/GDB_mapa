<template>
    <v-container>
        <!-- Shape Selector -->
        <v-select
          v-model="component_forma.forma"
          :items="shapes"
          label="Seleccionar forma"
          outlined
          @update:model-value="resetFields"
        ></v-select>
  
        <!-- Dynamic Fields -->
        <div v-if="component_forma.forma === 'Cilindro'">
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_forma.diametro"
                label="diametro (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_forma.alto"
                label="alto (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
  
        <div v-if="component_forma.forma === 'Plano'">
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_forma.ancho"
                label="ancho (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_forma.largo"
                label="largo (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
  
        <div v-if="component_forma.forma === 'Prisma'">
          <v-row>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="component_forma.alto"
                label="alto (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="component_forma.ancho"
                label="ancho (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="component_forma.largo"
                label="largo (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
  
        
    </v-container>
  </template>
  
  <script>
  import { useStore } from '@/stores/store';

  export default {
    props: {
      component_index: Number
    },
    data() {
      return {
        shapes: ["Cilindro", "Plano", "Prisma"],
        pieceStore: useStore(),
      };
    },
    methods: {
      resetFields() {
        this.pieceStore.$state.currentPiece.components[this.component_index].connected_nodes.forma = {
          diametro: null,
          alto: null,
          ancho: null,
          largo: null,
          forma: this.component_forma.forma,
        };
        console.log(this.pieceStore.$state.currentPiece);
      },
    },
    computed: {
      component_forma() {
        return this.pieceStore.$state.currentPiece.components[this.component_index].connected_nodes.forma;
      }
    }
  };
  </script>
  
  <style scoped>
  .v-container {
    max-width: 100%;
    margin: auto;
  }
  </style>
  