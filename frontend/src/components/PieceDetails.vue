<template>
    <div class="user-details-container">
      <div class="user-details-card">
        <!-- User Image -->
        <div class="user-image">
          <img :src="user.imageUrl" alt="User Image" />
        </div>
  
        <!-- User Information -->
        <div class="user-info">
          <h2>{{ user.name }}</h2>
          <p><strong>Email:</strong> {{ user.email }}</p>
          <p><strong>Country:</strong> {{ user.country }}</p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    props: {
        id: String,
        pieza: Object,
        exposiciones: Array,
        pais: Object,
        cultura: Object,
        localidad: Object,
        imagen: Object,
    },
    data() {
      return {
        user: {
          name: '',
          email: '',
          country: '',
          imageUrl: '',
        },
        components: []
      };
    },
    mounted() {
      this.fetchDetails();
    },
    methods: {
      // Fetch user details from the backend using an ID
      async fetchDetails() {
        const pieceId = this.id;  // Get user ID from the route
        console.log(this);
        try {
          const response = await axios.get(`http://localhost:8000/components/`, {params: {piece_id: pieceId}});
          this.components = response.data;
        } catch (error) {
            console.log(this.$route.params);
          console.error('Error fetching user details:', error);
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .user-details-container {
    display: flex;
    justify-content: center;
    align-items: center;
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
    width: 300px;
    text-align: center;
  }
  
  .user-image img {
    border-radius: 50%;
    width: 150px;
    height: 150px;
    object-fit: cover;
    margin-bottom: 20px;
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
  