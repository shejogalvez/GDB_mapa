<template>
    <div>
    
        <!-- Modal Form -->
        <div v-if="isVisible" class="modal-overlay">
            <div id="form-container" class="modal">
                <h2>Crear Pieza</h2>
                <span class="close" @click="closeModal">&times;</span>
                    <form class="form-content" id="agregar-producto-form" method="put" enctype="multipart/form-data">

                        <label for="numero_de_inventario" class="label"> Número de Inventario:</label>
                        <input type="number" id="numero_de_inventario" v-model="numero_de_inventario" class="input-field" size="10" maxlength="10">
                        <br><br>

                        <label for="coleccion" class="label">Coleccion:</label>
                        <input id="coleccion" v-model="coleccion" class="input-field" size="30">
                        <br><br>

                        <label for="SURDOC" class="label">Código SURDOC:</label>
                        <input id="SURDOC" v-model="SURDOC" class="input-field" size="30">
                        <br><br>
                        
                        <label for="conjunto" class="label">Nombre del Conjunto:</label>
                        <input id="conjunto" v-model="conjunto" class="input-field" size="30">
                        <br><br>
                        
                        <label for="clasificacion" class="label">Clasificacion:</label>
                        <input id="clasificacion" v-model="clasificacion" class="input-field" size="30">
                        <br><br>

                        <label for="contexto_historico" class="label">Contexto Historico:</label>
                        <input id="contexto_historico" v-model="contexto_historico" class="input-field" size="30">
                        <br><br>
                        
                        <label for="notas_investigacion" class="label">notas_investigacion:</label>
                        <input id="notas_investigacion" v-model="notas_investigacion" class="input-field" size="30">
                        <br><br>

                        <label for="bibliografia" class="label">bibliografia:</label>
                        <input id="bibliografia" v-model="bibliografia" class="input-field" size="30">
                        <br><br>
                        
                        <label for="avaluo" class="label">avaluo:</label>
                        <input id="avaluo" v-model="avaluo" class="input-field" size="30">
                        <br><br>

                        <label for="autor" class="label">autor:</label>
                        <input id="autor" v-model="autor" class="input-field" size="30">
                        <br><br>
                        
                        <label for="procedencia" class="label">procedencia:</label>
                        <input id="procedencia" v-model="procedencia" class="input-field" size="30">
                        <br><br>

                        <label for="donante" class="label">donante:</label>
                        <input id="donante" v-model="donante" class="input-field" size="30">
                        <br><br>

                        <label for="fecha_ingreso" class="label">donante:</label>
                        <input type="date" id="fecha_ingreso" v-model="fecha_ingreso" class="input-field" size="30">
                        <br><br>

                        <!-- Multiple Image Upload -->
                        <label for="images">Upload Images:</label>
                        <input type="file" id="images" @change="handleFileUpload" multiple>

                        <!-- Preview Images -->
                        <div class="image-preview">
                            <div v-for="(image, index) in previewImages" :key="index">
                                <img :src="image" alt="Image Preview" class="preview">
                            </div>
                        </div>
                        
                        <h3>Componentes</h3>

                        <div v-for="(component, i) in components" :key="i">

                            <label for="nombre_comun" class="label">Nombre Comun:</label>
                            <input id="nombre_comun" v-model="component.nombre_comun" class="input-field" size="30">
                            <br><br>
                            
                            <label for="nombre_especifico" class="label">Nombre Especifico:</label>
                            <input id="nombre_especifico" v-model="component.nombre_especifico" class="input-field" size="30">
                            <br><br>

                            <label for="materialidad" class="label">materialidad:</label>
                            <input id="materialidad" v-model="component.materialidad" class="input-field" size="30">
                            <br><br>
                            
                            <label for="peso_grs" class="label">avaluo:</label>
                            <input id="peso_grs" v-model="component.peso_grs" class="input-field" size="30">
                            <br><br>

                            <label for="autor" class="label">autor:</label>
                            <input id="autor" v-model="component.autor" class="input-field" size="30">
                            <br><br>
                            
                            <label for="tecnica" class="label">procedencia:</label>
                            <input id="tecnica" v-model="component.tecnica" class="input-field" size="30">
                            <br><br>

                            <label for="descripcion_fisica" class="label">donante:</label>
                            <input  id="descripcion_fisica" v-model="component.descripcion_fisica" class="input-field" size="30">
                            <br><br>

                            <label for="tipologia" class="label">tipologia:</label>
                            <input id="tipologia" v-model="component.tipologia" class="input-field" size="30">
                            <br><br>
                            
                            <label for="funcion" class="label">funcion:</label>
                            <input id="funcion" v-model="component.funcion" class="input-field" size="30">
                            <br><br>

                            <label for="iconografia" class="label">iconografia:</label>
                            <input id="iconografia" v-model="component.iconografia" class="input-field" size="30">
                            <br><br>
                            
                            <label for="estado_genral_de_conservacion" class="label">estado general de conservacion:</label>
                            <select id="estado_genral_de_conservacion" v-model="component.estado_genral_de_conservacion" class="select-field">
                                <option value="" disabled selected>Selecciona una opción</option> <!-- Default option -->
                                <option value="MUY BUENO">MUY BUENO</option>
                                <option value="BUENO">BUENO</option>
                                <option value="REGUKAR">REGUKAR</option>
                                <option value="MALO">MALO</option>
                                <option value="MUY MALO">MUY MALO</option>
                            </select>
                            <br><br>

                            <label for="ubicacion">Seleccionar ubicacion:</label>
                            <TreeDropdown
                            :options = "ubicaciones"
                            :children_key = "'ubicacion_contiene'"
                            v-model="component.selectedUbicacion"
                            >
                            </TreeDropdown>
                            <br><br>

                            <!-- Multiple Image Upload -->
                            <label for="images">Upload Images:</label>
                            <input type="file" id="images" @change="handleFileUpload" multiple>

                            <!-- Preview Images -->
                            <div class="image-preview">
                                <div v-for="(image, index) in previewImages" :key="index">
                                    <img :src="image" alt="Image Preview" class="preview">
                                </div>
                            </div>
                        </div>

                        

                        <!-- Region Selector (shown only if a country is selected) -->
                        <div v-if="false">
                            <label for="region">Select Region:</label>
                            <select id="region">
                                <option value="" disabled>Select a region</option>
                                <option v-for="region in regions" :key="region.name" :value="region.name">{{ region.name }}</option>
                            </select>
                        </div>

                        

                        

                        <!-- Submit Button -->
                        <button @click="submitForm">Submit</button>
                    </form>
                    <span>end</span>
            </div>
    
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import TreeDropdown from './TreeDropdown.vue'

export default {
    props: {
        isVisible: {
            type: Boolean,
            required: true
        }
    },
    components: {
      TreeDropdown
    },
    data() {
        /** @typedef {object} Ubicacion
         * @property {string} id
         * @property {string} label
         * @property {string} name
         * @property {Array<Ubicacion>} ubicacion_contiene
         */

        /** @typedef {object} SubNode 
         * @property {any} id
         * @property {string} id_key
         * @property {string} relation_label
         * @property {string} node_label
         * @property {Object} properties
        */
        return {
            numero_de_inventario: "",
            numero_de_registro_anterior: "",
            coleccion: "",
            SURDOC: "",
            clasificacion: "",
            conjunto: "",
            autor: "",
            fecha_de_creacion: "",
            contexto_historico: "",
            notas_investigacion: "",
            bibliografia: "",
            avaluo: "",
            procedencia: "",
            donante: "",
            fecha_ingreso: "",
            // List of countries and their regions
            /** @type {Array<Ubicacion>} */
            ubicaciones: [],
            components: [
            {
            /** @type {Ubicacion} */
            selectedUbicacion: null,
            id: '',
            propiedades: null,
            forma: null,
            imagenes: []
            }],
            regions: [], // Will be populated based on selected country
            uploadedFiles: [],
            previewImages: []
        };
    },
    mounted() {
        this.fetchUbicaciones();
    },
    methods: {
        async fetchUbicaciones() {
            try {
                const response = await axios.get('http://localhost:8000/nodes/tree/', {params: {
                    labels: 'ubicacion',
                    rel_label: 'ubicacion_contiene'
                }})
                this.ubicaciones = response.data[0]['value']['ubicacion_contiene']
                console.log(this.ubicaciones);    
            }
            catch (error) {
                console.error(error)
            }
        },
        closeModal() {
            this.$emit('close');
        },
        onUbicacionChange() {
            // Find selected country's regions
            const selectedUbicacionObj = this.ubicaciones.find(country => country.name === "TODO");
            if (selectedUbicacionObj) {
                this.selectedUbicacion = selectedUbicacionObj
            } else {
                this.regions = [];
            }
        },
        handleFileUpload(event) {
            this.uploadedFiles = event.target.files;

            // Clear previous previews
            this.previewImages = [];

            // Generate previews for each uploaded image
            for (let i = 0; i < this.uploadedFiles.length; i++) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.previewImages.push(e.target.result);
                };
                reader.readAsDataURL(this.uploadedFiles[i]);
            }
        },
        submitForm() {
            // Form submission logic
            
        }
    }
};
</script>

<style scoped>

.form-content {
    margin: 0 auto;
    overflow-y: auto;
    max-height: 90%;
    position: relative;
}

.image-preview {
    display: flex;
    flex-wrap: wrap;
    margin-top: 10px;
}

.preview {
    width: 100px;
    height: 100px;
    object-fit: cover;
    margin: 5px;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal {
    background: white;
    padding: 30px;
    border-radius: 8px;
    width: 100%;
    max-width: 900px;
    box-shadow: 0px 15px 30px rgba(0, 0, 0, 0.2);
    position: relative;
    animation: slideUp 0.4s ease;
    height: 90%;
}

.close {
  background: none;
  border: none;
  font-size: 2rem;
  position: absolute;
  top: 10px;
  right: 15px;
  color: #888;
  cursor: pointer;
}

.close:hover {
  color: #555;
}

/* Modal Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
  }
  to {
    transform: translateY(0);
  }
}

.scrollable-div {
  height: max-content; /* Adjust the height as needed */
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 5px;
  width: 200px;
}

.label {
    display: block;
    font-weight: bold;
}

.input-field {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    -webkit-box-sizing: border-box; /* Safari/Chrome, other WebKit */
    -moz-box-sizing: border-box;    /* Firefox, other Gecko */
    box-sizing: border-box;         /* Opera/IE 8+ */
}

/* Styles for form elements */
.form-group {
    margin-bottom: 20px;
}

</style>