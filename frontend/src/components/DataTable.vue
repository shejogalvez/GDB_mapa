<template>
    <div :class="fixed">
      <h1>Piezas</h1>

      <button @click="openModal" class="modern-button">crear pieza</button>
      <FormModal :isVisible="showModal" @close="closeModal" />
      
      <!-- Filter Input -->
      <input v-model="filterText" placeholder="Filter by id..." @input="filterRows" />
  
      <!-- Data Table -->
      <table >
        <thead>
          <tr>
            <th>Select</th>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Numero de Inventario" property_label="id"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Número de registro anterior" property_label="numero_de registro_anterior"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Coleccion" property_label="coleccion"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="SURDOC" property_label="SURDOC"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Clasificacion" property_label="clasificacion"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Conjunto" property_label="conjunto"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Autor" property_label="autor"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Fecha de Creacion" property_label="fecha_de_creacion"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Contexto Historico" property_label="contexto_historico"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Notas de Investigacion" property_label="notas_investigacion"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Pais" property_label="name" node_label="pais"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Localidad" property_label="name" node_label="localidad"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Afiliacion Cultural" property_label="name" node_label="cultura"></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="Fecha de Creacion" property_label=""></FilterTH>
            <FilterTH @applyFilter="(filterobj) => {filterRows(filterobj)}" header_text="exposiciones" property_label="name" node_label="pais"></FilterTH>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.pieza.id">
            <td><button class="modern-button" @click="goToDetails(row)"> </button> </td>
            <td>{{ row.pieza.id }}</td>
            <td>{{ row.pieza["numero_de registro_anterior"] }}</td>
            <td>{{ row.pieza.coleccion }}</td>
            <td>{{ row.pieza.SURDOC }}</td>
            <td>{{ row.pieza.clasificacion }}</td>
            <td>{{ row.pieza.conjunto }}</td>
            <td>{{ row.pieza.autor }}</td>
            <td>{{ row.pieza.fecha_de_creacion }}</td>
            <td>{{ row.pieza.contexto_historico }}</td>
            <td>{{ row.pieza.notas_investigacion }}</td>
            <td>{{ row.pais?.name }}</td>
            <td>{{ row.localidad?.name }}</td>
            <td>{{ row.cultura?.name }}</td>
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

      <!-- page select -->
      <div class="pagination-controls">
        
      <button :disabled="currentPage === 0" @click="changePage(0)">First</button>
      <button :disabled="currentPage === 0" @click="changePage(this.currentPage - 1)">Previous</button>
        
      <button
        v-for="page in pagesArray"
        :key="page"
        @click="changePage(page)"
        :class="{'active': currentPage === page}"
      >
        {{ page+1 }}
      </button>
    
      <button :disabled="currentPage === totalPages" @click="changePage(this.currentPage + 1)">Next</button>
      <button :disabled="currentPage === totalPages" @click="changePage(this.totalPages)">Last</button>
    </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import FormModal from './FormModal.vue';
  import FilterTH from './FilterTH.vue';
  
  export default {
    components: {
      FormModal,
      FilterTH,
    },
    data() {
      return {
        rows: [],
        filteredRows: [],
        selectedRows: [],
        filterText: "",
        filters: {},
        showModal: false,
        currentPage: 0,
        limitResults: 75,
        totalPages: 50,
      };
    },
    methods: {

      goToDetails(row) {
        console.log(row);
        this.$router.push({name: `Details`, params: {...row, id:row.id}});  // Navigate to the user details page
      },

      async fetchData() {
        try {
          const response = await axios.get('http://localhost:8000/pieces/', {params: {
            skip: this.currentPage*this.limitResults,
            limit: this.limitResults
          }});
          this.rows = response.data[0]; 
          this.totalPages = Math.floor(response.data[1]['count'] / this.limitResults)
          //console.log(this.totalPages)
          this.filteredRows = this.rows; // Initialize the filtered rows
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      },

      async changePage(toPage) {
        this.$router.push(`/${toPage}`)
        if (this.filterText) {
          await this.filterRows();
        }
        else {
          await this.fetchData();
        }
      },

      updateFilters(filterobj) {
        const node_label = filterobj.node_label
        if (this.filters[node_label]) {
          this.filters[node_label].push(filterobj.filter)
        }
        else {
          this.filters[node_label] = [filterobj.filter]
        }
      },

      async filterRows(filterobj) {
        // Filter rows based on filterText input
        this.updateFilters(filterobj);
        console.log(this.filters)
        try {
          const response = await axios.post('http://localhost:8000/pieces/', this.filters, 
          {
            params: {
              skip: this.currentPage*this.limitResults,
              limit: this.limitResults
            }
          });
          this.filteredRows = response.data[0]
          this.totalPages = Math.floor(response.data[1]['count'] / this.limitResults)
          console.log(this.totalPages)
        }
        catch (e){
          console.error(e)
        }
        
        //this.filteredRows = this.rows.filter(row => row.pieza.id.includes(filter));
      },

      openModal() {
        this.showModal = true;  // Open the modal
      },

      closeModal() {
        this.showModal = false;  // Close the modal
      }

    },
    computed: {
      pagesArray() {
        let newArr = [];
        for (let i = Math.max(0, this.currentPage - 5); i <= Math.min(this.currentPage + 5, this.totalPages); i++) {
          newArr.push(i);
        }
        return newArr;
      },
      fixed() {
        return this.showModal ? 'fixed' : '';
      }
    }, 
    mounted() {
      //console.log(this.$route.params);
      if (this.$route.params.page) this.currentPage = parseInt(this.$route.params.page);
      this.fetchData(); // Fetch data on component mount
    },
    watch: {
      $route(to, from) {
        this.currentPage = this.$route.params.page
      }
    }
  };
  </script>

  <style scoped>
  .fixed {
    position: fixed;
    overflow-y: auto;
  }

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
    text-overflow: ellipsis;
  }
  
  th {
    background-color: #f4f4f4;
  }
  
  td {
    overflow: hidden;
  }

  input[type="text"] {
    margin-bottom: 10px;
    padding: 5px;
    width: 200px;
  }
  
  input[type="checkbox"] {
    margin-right: 10px;
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

  .pagination-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
}

button {
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #0056b3;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

button.active {
  background-color: #0056b3;
  font-weight: bold;
}
  </style>
  