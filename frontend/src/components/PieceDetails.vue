<template>
    <div class="piece-details-container">
      <button @click="openModal" class="modern-button">editar pieza</button>
      <FormModal :isVisible="showModal" title="Editar pieza" @close="()=>{showModal = false}" @success="fetchDetails"/>
      <div class="piece-details-card">
        <h1>Info pieza</h1>
        <!-- User Image -->
        <div v-for="(img, index) in piece.imagenes" class="piece-image">
          <DeletableImage @imageDeleted="removeFromArray(piece.imagenes, index)" :imageId="img.filename" :pieceId="piece.id" :key="index"/>
        </div>
        
        <!-- User Information -->
        <div class="piece-info">
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
        <template v-for="(component, index) in piece.components">
          <h3>componente {{ index+1 }}</h3>
          <div v-for="(img, index) in component.imagenes" class="piece-image">
            <DeletableImage @imageDeleted="removeFromArray(component.imagenes, index)" :imageId="img.filename" :pieceId="piece.id" :key="img.filename"/>
          </div>
          <div class="piece-info">
            <template v-for="(val, key, idx) in component.properties">
              <p><strong>{{ key }}:</strong> {{ val }} </p>
            </template>
            <p v-if="component.ubicacion"><strong>ubicacion:</strong> {{ component.ubicacionpath }} </p>
            <template v-for="(val, key, idx) in component.forma">
              <p><strong>{{ key }}:</strong> {{ val }} </p>
            </template>
          </div>
          <br><br>
        </template>
      </div>
    </div>
  </template>
  
  <script>
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
    mounted() {
      try {
        this.fetchDetails();
        //console.log(this.piece);
      } catch (error) {
        console.log(this.$route.params);
        console.error('Error fetching piece details:', error);
      }
    },
    methods: {
      // Fetch piece details from the backend using an ID
      async fetchDetails() {
        const pieceId = this.$route.params.id;  // Get piece ID from the route
        await useStore().UpdateFromPieceId(pieceId);
        this.piece = useStore().currentPiece;
      },
      openModal() {
        useStore().$patch({currentPiece: {...this.piece}}); // copies fetched data to form
        this.showModal = true;
      },
      closeModal() {
        this.showModal = false;  // Close the modal
      },
      removeFromArray(array, index) {
        array.splice(index, 1);
      },
    },
  };
  </script>
  
  <style scoped>
  .piece-details-container {
    display: flex;
    justify-content: center;
    min-height: 100vh;
    background-color: #f4f4f9;
  }
  
  .piece-details-card {
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
  
  .piece-image img {
    border-radius: 50%;
    width: 150px;
    height: 150px;
    object-fit: cover;
    margin-bottom: 20px;
    display: inline-flex;
    margin: 0 15pt;
  }
  
  .piece-info {
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
  