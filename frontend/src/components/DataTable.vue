<template>
    <div>
      <h1>Piezas</h1>

      <button @click="openModal" class="modern-button">crear pieza</button>
      <FormModal :isVisible="showModal" @close="closeModal" />
      
      <!-- Filter Input -->
      <input v-model="filterText" placeholder="Filter by id..." @input="filterRows" />
  
      <!-- Data Table -->
      <table>
        <thead>
          <tr>
            <th>Select</th>
            <th>ID</th>
            <th>Pais</th>
            <th>Localidad</th>
            <th>Afiliacion Cultural</th>
            <th>Fecha de Creacion</th>
            <th>Conjunto</th>
            <th>Exposiciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.pieza.id">
            <td><input type="checkbox" v-model="selectedRows" :value="row" /></td>
            <td>{{ row.pieza.id }}</td>
            <td>{{ row.pais }}</td>
            <td>{{ row.localidad }}</td>
            <td>{{ row.cultura }}</td>
            <td>{{ row.fecha_de_creacion }}</td>
            <td>{{ row.conjunto }}</td>
            <td>{{ row.exposicion }}</td>
          </tr>
        </tbody>
      </table>
  
      <!-- Selected Rows Output -->
      <div v-if="selectedRows.length > 0">
        <h2>Selected Rows:</h2>
        <ul>
          <li v-for="row in selectedRows" :key="row.pieza.id">{{ row.pieza.id }}</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import FormModal from './FormModal.vue';
  
  export default {
    components: {
      FormModal
    },
    data() {
      return {
        rows: [],
        filteredRows: [],
        selectedRows: [],
        filterText: "",
        showModal: true,
      };
    },
    methods: {
      async fetchData() {
        console.log("auth", axios.defaults.headers.common['Authorization']);
        try {
          const response = await axios.get('http://localhost:8000/pieces/');
          this.rows = response.data;
          this.filteredRows = this.rows; // Initialize the filtered rows
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      },
      filterRows() {
        // Filter rows based on filterText input
        const filter = this.filterText.toLowerCase();
        this.filteredRows = this.rows.filter(row => row.id.includes(filter));
        console.log(this.selectedRows)
      },
      openModal() {
        this.showModal = true;  // Open the modal
      },
      closeModal() {
        this.showModal = false;  // Close the modal
      }

    },
    mounted() {
      this.fetchData(); // Fetch data on component mount
    }
  };
  </script>

  <style scoped>
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  th, td {
    padding: 10px 30px;
    max-width: 300px;
    border: 1px solid #ddd;
    text-align: left;
  }
  
  th {
    background-color: #f4f4f4;
  }
  
  input[type="text"] {
    margin-bottom: 10px;
    padding: 5px;
    width: 200px;
  }
  
  input[type="checkbox"] {
    margin-right: 10px;
  }
  
  .main-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: #f9f9f9;
    font-family: 'Arial', sans-serif;
  }
  
  h1 {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 20px;
    color: #333;
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
  }
  
  .modern-button:hover {
    background-color: #0056b3;
    transform: scale(1.05);
  }

  </style>
  