<template>
    <v-app :class="fixed">
      
      <v-app-bar :elevation="2">
        <v-app-bar-title>Piezas</v-app-bar-title>
        <template v-slot:append>
          <button @click="openModal" class="modern-button">crear pieza</button>
          
          <v-tooltip text="Exportar vista a excel">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" icon="mdi-download" @click="downloadCsv"></v-btn>
            </template>
          </v-tooltip>
        </template>
      </v-app-bar>
      
      <FormModal :isVisible="showModal" @close="closeModal" />
      
      <!-- Filter Input -->
      <br><br>
      <!-- Data Table -->
      <table >
        <thead>
          <tr>
            <th>Select</th>
            <FilterTH v-for="(val, key) in property_columns" @applyFilter="filterRows" :header_text="val" :property_label="key"></FilterTH>

            <FilterTH @applyFilter="filterRows" header_text="Pais" property_label="name" node_label="pais"></FilterTH>
            <FilterTH @applyFilter="filterRows" header_text="Localidad" property_label="name" node_label="localidad"></FilterTH>
            <FilterTH @applyFilter="filterRows" header_text="Afiliacion Cultural" property_label="name" node_label="cultura"></FilterTH>  
            <FilterTH @applyFilter="filterRows" header_text="exposiciones" property_label="name" node_label="pais"></FilterTH>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredRows" :key="row.pieza.id">
            <td><button class="modern-button" @click="goToDetails(row)"> </button> </td>
            <td v-for="(val, key) in property_columns">{{ row.pieza[key] }}</td>

            <td>{{ row.pais?.name }}</td>
            <td>{{ row.localidad?.name }}</td>
            <td>{{ row.cultura?.name }}</td>
            <td>{{ row.exposicion }}</td>
          </tr>
          <template v-if="filteredRows.length == 0">
            <tr>
              <td colspan="9999" style="height: 250px;">
                    No hay piezas con estos filtros
              </td>
            </tr>
          </template>
        </tbody>
      </table>

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
    </v-app>
  </template>
  
  <script>
  import axios from 'axios';
  import FormModal from './FormModal.vue';
  import FilterTH from './FilterTH.vue';
  import { useStore, useFilterStore } from '@/stores/store';
  
  export default {
    components: {
      FormModal,
      FilterTH,
    },
    data() {
      return {
        rows: [],
        filteredRows: [],
        showModal: false,
        currentPage: 0,
        limitResults: 75,
        totalPages: 50,
        property_columns: {
          id: "Numero de Inventario",
          numero_de_registro_anterior :"Número de registro anterior",
          coleccion :"Coleccion",
          clasificacion :"SURDOC",
          conjunto :"Clasificacion",
          autor :"Conjunto",
          fecha_de_creacion :"Autor",
          contexto_historico :"Fecha de Creación",
          notas_investigacion :"Contexto Historico",
          bibliografia :"Notas de Investigacion",
          avaluo :"Bibliografia",
          procedencia :"Avaluo",
          donante :"Procedencia",
          fecha_ingreso :"Donante",
          fecha_ingreso_text :"Fecha ingreso"
        }
      };
    },
    methods: {

      goToDetails(row) {
        console.log(row);
        this.$router.push({name: `Details`, params: {id:row.id}});  // Navigate to the user details page
      },

      async fetchData() {
        const filters = useFilterStore().$state.filters;
        try {
          const response = await axios.post('http://localhost:8000/pieces/', filters, {params: {
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

      async filterRows() {
        // Filter rows based on filterText input
        const filters = useFilterStore().$state.filters;
        console.log(filters);
        try {
          const response = await axios.post('http://localhost:8000/pieces/', filters, 
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
        console.log(useStore().$state);
        this.showModal = true;  // Open the modal
      },

      closeModal() {
        this.showModal = false;  // Close the modal
      },
      async downloadCsv() {
        const filters = useFilterStore().$state.filters;
        try {
          const response = await axios.post('http://localhost:8000/csv/', filters, {
            responseType: 'blob'
          });
          console.log(response.data);
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'export.xlsx');
          document.body.appendChild(link);
          link.click();
        }
        catch (e){
          console.error(e);
          alert("error exporting file");
        }
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
    margin-right: 10pt;
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
  