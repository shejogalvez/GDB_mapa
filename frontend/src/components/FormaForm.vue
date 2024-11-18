<template>
    <v-container>
        <!-- Shape Selector -->
        <v-select
          v-model="component_properties.forma"
          :items="shapes"
          label="Seleccionar forma"
          outlined
          @change="resetFields"
        ></v-select>
  
        <!-- Dynamic Fields -->
        <div v-if="component_properties.forma === 'Cilindro'">
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_properties.diametro"
                label="diametro (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_properties.alto"
                label="alto (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
  
        <div v-if="component_properties.forma === 'Plano'">
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_properties.ancho"
                label="ancho (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="component_properties.largo"
                label="largo (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
  
        <div v-if="component_properties.forma === 'Prisma'">
          <v-row>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="component_properties.alto"
                label="alto (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="component_properties.ancho"
                label="ancho (cm)"
                type="number"
                outlined
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="component_properties.largo"
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
        console.log(this.pieceStore.$state.currentPiece);
        this.component_properties = {
          diametro: null,
          alto: null,
          ancho: null,
          largo: null,
        };
      },
    },
    computed: {
      component_properties() {
        return this.pieceStore.$state.currentPiece.components[this.component_index].properties;
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
  