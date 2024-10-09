<template>
    <div>
      <h1>Excel-like Data Table</h1>
      
      <!-- Filter Input -->
      <input v-model="filterText" placeholder="Filter by name..." @input="filterRows" />
  
      <!-- Data Table -->
      <table>
        <thead>
          <tr>
            <th>Select</th>
            <th>ID</th>
            <th>Name</th>
            <th>Age</th>
            <th>Job</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in filteredRows" :key="row.id">
            <td><input type="checkbox" v-model="selectedRows" :value="row" /></td>
            <td>{{ row.id }}</td>
            <td>{{ row.name }}</td>
            <td>{{ row.age }}</td>
            <td>{{ row.job }}</td>
          </tr>
        </tbody>
      </table>
  
      <!-- Selected Rows Output -->
      <div v-if="selectedRows.length > 0">
        <h2>Selected Rows:</h2>
        <ul>
          <li v-for="row in selectedRows" :key="row.id">{{ row.name }} ({{ row.job }})</li>
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
          this.rows = response.data;
          this.filteredRows = this.rows; // Initialize the filtered rows
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      },
      filterRows() {
        // Filter rows based on filterText input
        const filter = this.filterText.toLowerCase();
        this.filteredRows = this.rows.filter(row => row.name.toLowerCase().includes(filter));
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
  