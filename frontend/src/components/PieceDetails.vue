<template>
    <div class="user-details-container">
      <button @click="openModal" class="modern-button">editar pieza</button>
      <FormModal :isVisible="showModal" title="Editar pieza" @close="()=>{showModal = false}" />
      <div class="user-details-card">
        <h1>Info pieza</h1>
        <!-- User Image -->
        <div v-for="(img, index) in piece.imagenes" class="user-image">
          <DeletableImage @imageDeleted="() => piece.imagenes.splice(index)" :imageId="img.filename">pieza imagen</DeletableImage>
        </div>
        
        <!-- User Information -->
        <div class="user-info">
          <template v-for="(val, key) in piece.properties">
            <p>
              <strong>{{ key }}:</strong> {{ val }} 
            </p>
          </template>
            <p v-if="piece.pais"><strong>pais:</strong> {{ piece.pais.name }} </p>
            <p v-if="piece.localidad"><strong>localidad:</strong> {{ piece.localidad.name }} </p>
            <p v-if="piece.cultura"><strong>filiación cultural:</strong> {{ piece.cultura.name }} </p>
            <p v-if="piece.exposicion"><strong>exposicion:</strong> {{ piece.exposicion.name }} </p>
        </div>

        <h1>Info componentes</h1>
        <div v-for="(component, index) in piece.components" class="user-info">
          <h3>componente {{ index+1 }}</h3>
          <div v-for="(img, index) in component.imagenes" class="user-image">
            <DeletableImage @imageDeleted="() => component.imagenes.splice(index)" :imageId="img.filename">pieza imagen</DeletableImage>
          </div>
          <template v-for="(val, key, idx) in component.properties">
            <p><strong>{{ key }}:</strong> {{ val }} </p>
          </template>
          <p v-if="component.ubicacion"><strong>ubicacion:</strong> {{ component.ubicacion.name }} </p>
          <template v-for="(val, key, idx) in component.forma">
            <p><strong>{{ key }}:</strong> {{ val }} </p>
          </template>
          <br><br>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { useStore } from '@/stores/store';
  import DeletableImage from './DeletableImage.vue';
  
  export default {
    data() {
      return {
        piece: {},
        showModal: false,
      };
    },
    components: {
      DeletableImage
    },
    async mounted() {
      const pieceId = this.$route.params.id;  // Get user ID from the route
      try {
        const response = await axios.get(`http://localhost:8000/components/`, {params: {
          piece_id: pieceId,
        }});
        console.log(response);
        let pieceData = response.data[0]
        const properties = pieceData['pieza'];
        delete pieceData['pieza'];
        const connected_nodes = {}
        for (const key of ['pais', 'localidad', 'exposicion', 'cultura']) {
          const val = pieceData[key];
          if (val) {
            connected_nodes[key] = val.name;
          }
        }
        pieceData.connected_nodes = connected_nodes;
        pieceData.properties = properties;
        pieceData.uploadedFiles = [];
        pieceData.previewImages = [];
        let componentsData = response.data[1]
        for (const component of componentsData){
          const cprops = component['componente'];
          delete component['componente'];
          const connected_nodes = {forma: {}}
          for (const key of ['forma', 'ubicacion']) {
          const val = component[key];
            if (val) {
              connected_nodes[key] = val;
            }
          }
          component.connected_nodes = connected_nodes;
          component.properties = cprops;
          component.uploadedFiles = [];
          component.previewImages = [];
        }
        pieceData.components = componentsData;
        
        this.piece = pieceData
        console.log(this.piece);
      } catch (error) {
        console.log(this.$route.params);
        console.error('Error fetching user details:', error);
      }
    },
    methods: {
      // Fetch user details from the backend using an ID
      async fetchDetails() {
      },
      openModal() {
        useStore().$patch({currentPiece: {...this.piece}}); // copies fetched data to form
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;  // Close the modal
      },
    },
  };
  </script>
  
  <style scoped>
  .user-details-container {
    display: flex;
    justify-content: center;
    min-height: 100vh;
    background-color: #f4f4f9;
  }
  
  .user-details-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    width: 600px;
    text-align: center;
  }
  
  .user-image img {
    border-radius: 50%;
    width: 150px;
    height: 150px;
    object-fit: cover;
    margin-bottom: 20px;
    display: inline-flex;
    margin: 0 15pt;
  }
  
  .user-info {
    color: #333;
  }
  
  h2 {
    font-size: 1.5rem;
    margin-bottom: 10px;
  }
  
  p {
    font-size: 1rem;
    margin-bottom: 5px;
  }
  
  .modern-button {
    padding: 12px 24px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease, transform 0.2s ease;
    max-height: 50px;
    margin-top: 15px;
  }
  
  .modern-button:hover {
    background-color: #0056b3;
    transform: scale(1.05);
  }
  </style>
  