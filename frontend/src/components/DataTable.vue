<template>
    <div>
      <h1>Piezas</h1>
      
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
            <th>Exposiciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.pieza.id">
            <td><input type="checkbox" v-model="selectedRows" :value="row" /></td>
            <td>{{ row.pieza.id }}</td>
            <td>{{ row.pais }}</td>
            <td>{{ row.loc }}</td>
            <td>{{ row.filiacion_cultural }}</td>
            <td>{{ row.exp }}</td>
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
  
  export default {
    data() {
      return {
        rows: [],
        filteredRows: [],
        selectedRows: [],
        filterText: ""
      };
    },
    methods: {
      async fetchData() {
        try {
          const response = await axios.get('http://localhost:8000/');
          console.log(response)
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
  }
  
  th, td {
    padding: 10px;
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
  </style>
  