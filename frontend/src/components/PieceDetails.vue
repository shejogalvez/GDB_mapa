<template>
    <div class="user-details-container">
      <div class="user-details-card">
        <h1>Info pieza</h1>
        <!-- User Image -->
        <div v-for="img in this.piece.imagenes" class="user-image">
          <img :src="img.content" alt="Imagen pieza" />
        </div>
  
        <!-- User Information -->
        <div class="user-info">
          <template>
            <p v-for="(val, key, idx) in this.piece.pieza"><strong>{{ key }}:</strong> {{ val }} </p>
          </template>
            <p><strong>pais:</strong> {{ this.piece.pais?.name }} </p>
            <p><strong>localidad:</strong> {{ this.piece.localidad?.name }} </p>
            <p><strong>filiación cultural:</strong> {{ this.piece.cultura?.name }} </p>
        </div>

        <h1>Info componentes</h1>
        <div v-for="component in this.components" class="user-info">
          <h3>{{ component.id }}</h3>
          <div class="user-image">
            <img v-for="img in component.imagenes" :src="img.content" alt="Imagen componente" />
          </div>
          <template>
            <p v-for="(val, key, idx) in component.component"><strong>{{ key }}:</strong> {{ val }} </p>
          </template>
            <p><strong>ubicacion:</strong> {{ component.ubicacion?.name }} </p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { useStore } from '@/stores/store';
  
  export default {
    data() {
      return {
        components: [],
        piece: {},
      };
    },
    mounted() {
      this.fetchDetails();
    },
    methods: {
      // Fetch user details from the backend using an ID
      async fetchDetails() {
        const pieceId = this.$route.params.id;  // Get user ID from the route
        try {
          const response = await axios.get(`http://localhost:8000/components/`, {params: {
            piece_id: pieceId,
          }});
          console.log(response);
          this.components = response.data[1];
          this.piece = response.data[0];
          for (const img of this.piece.imagenes) {
            this.setImageData(img);
          }
          for (const component of this.components) {
            for (const img of component.imagenes) {
              this.setImageData(img);
            }
          }
          useStore().$state.currentPiece = response.data[0];
          useStore().$state.currentPiece.components = response.data[1];
          console.log(useStore().$state);
          console.log(encodeURIComponent(this.piece.imagenes[0].filename));
        } catch (error) {
          console.log(this.$route.params);
          console.error('Error fetching user details:', error);
        }
      },
      setImageData(img_node) {
        axios.get(`http://localhost:8000/get-image/`, {params: {image_url: img_node.filename}, responseType: 'blob'},)
        .then(async res => {
          const reader = new FileReader();
          reader.onload = (e) => {
            img_node.content = e.target.result;
          };
          reader.readAsDataURL(res.data);
        })
      }
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
  </style>
  