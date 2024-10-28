<template>
    <div>
    
        <!-- Modal Form -->
        <div v-if="isVisible" class="modal-overlay">
            <div id="form-container" class="modal">
                <h2>Crear Pieza</h2>
                <span class="close" @click="closeModal">&times;</span>
                    <v-form class="form-content" id="agregar-producto-form" method="put" enctype="multipart/form-data">
                        <br>
                        <v-row>
                            <v-text-field type="text" label="numero_de_inventario" v-model="id" class="input-field" maxlength="5"></v-text-field>
                            <v-text-field label="coleccion" v-model="properties.coleccion" class="input-field"></v-text-field>
                        </v-row>
                        
                        <v-row>
                            <v-text-field label="SURDOC" v-model="properties.SURDOC" class="input-field" ></v-text-field>
                            <v-text-field label="conjunto" v-model="properties.conjunto" class="input-field" ></v-text-field>
                        </v-row>
                        <v-text-field label="clasificacion" v-model="properties.clasificacion" class="input-field" ></v-text-field>
                        
                        
                        <v-textarea label="contexto_historico" v-model="properties.contexto_historico" class="input-field" ></v-textarea>
                        
                        <v-textarea label="notas_investigacion" v-model="properties.notas_investigacion" class="input-field" ></v-textarea>
                        
                        <v-textarea label="bibliografia" v-model="properties.bibliografia" class="input-field" ></v-textarea>

                        <v-row>
                            <v-text-field label="avaluo" v-model="properties.avaluo" class="input-field" ></v-text-field>
                            <v-text-field label="autor" v-model="properties.autor" class="input-field" ></v-text-field>
                        </v-row>

                        <v-text-field label="procedencia" v-model="properties.procedencia" class="input-field" ></v-text-field>
                        
                        <v-text-field label="donante" v-model="properties.donante" class="input-field" ></v-text-field>
                        
                        <v-date-input label="fecha_ingreso" v-model="properties.fecha_ingreso" class="input-field" ></v-date-input>
                        
                        <v-combobox 
                            label="pais" 
                            :items="paises_data.map(o => o.properties.name)"
                            v-model="connected_nodes.pais"
                        ></v-combobox>

                        <v-combobox 
                            label="localidad" 
                            :items="localidades_data.map(o => o.properties.name)"
                            v-model="connected_nodes.localidad"
                        ></v-combobox>
                        
                        <v-combobox 
                            label="cultura" 
                            :items="culturas_data.map(o => o.properties.name)"
                            v-model="connected_nodes.cultura"
                        ></v-combobox>
                        
                        <!-- Multiple Image Upload -->
                        <label for="imagen"> subir imagen piezas</label>
                        <input type="file" id="imagen" name="imagen" @change="handleComponentFileUpload(this, $event)" multiple></input>

                        <!-- Preview Images -->
                        <div class="image-preview">
                            <div v-for="(image, index) in previewImages" :key="index">
                                <img :src="image" alt="Image Preview" class="preview">
                            </div>
                        </div>
                        
                        <h3>Componentes</h3>

                        <div v-for="(component, i) in components" :key="i">

                            
                            <v-text-field label="nombre_comun" v-model="component.properties.nombre_comun" class="input-field" ></v-text-field>
                            
                            <v-text-field label="nombre_especifico" v-model="component.properties.nombre_especifico" class="input-field" ></v-text-field>
                            
                            <v-text-field label="materialidad" v-model="component.properties.materialidad" class="input-field" ></v-text-field>
                                
                            <v-text-field label="peso_grs" v-model="component.properties.peso_grs" class="input-field" ></v-text-field>
                            
                            <v-text-field label="autor" v-model="component.properties.autor" class="input-field" ></v-text-field>
                            
                            <v-text-field label="tecnica" v-model="component.properties.tecnica" class="input-field" ></v-text-field>
                            
                            <v-textarea  label="descripcion_fisica" v-model="component.properties.descripcion_fisica" class="input-field" ></v-textarea>
                            
                            <v-textarea label="tipologia" v-model="component.properties.tipologia" class="input-field" ></v-textarea>
                                
                            <v-text-field label="funcion" v-model="component.properties.funcion" class="input-field" ></v-text-field>
                            
                            <v-textarea label="iconografia" v-model="component.properties.iconografia" class="input-field" ></v-textarea>
                            
                            <v-select 
                            clearable
                            label="estado_genral_de_conservacion" 
                            v-model="component.properties.estado_genral_de_conservacion" 
                            :items="['MUY BUENO', 'BUENO', 'REGULAR', 'MALO', 'MUY MALO']">
                            </v-select>
                            
                            <label for="ubicacion">Seleccionar ubicacion:</label>
                            <TreeDropdown
                            :options = "ubicaciones_data"
                            :children_key = "'ubicacion_contiene'"
                            @input="(ubicacion) => component.connected_nodes.ubicacion = ubicacion?.id"
                            >
                            </TreeDropdown>
                            
                            <!-- Multiple Image Upload -->
                            <br><br>
                            <label :for="`image${i}`"> subir imagen componente {{ i }}</label>  
                            <input type="file" :id="`image${i}`" :name="`image${i}`" @change="handleComponentFileUpload(component, $event)" multiple></input>

                            <!-- Preview Images -->
                            <div class="image-preview">
                                <div v-for="(image, index) in component.previewImages" :key="index">
                                    <img :src="image" alt="Image Preview" class="preview">
                                </div>
                            </div>
                        </div>
                        
                        <button type="button" @click="agregarComponente">+ componente</button>
                        
                        <br><br>
                        <button type="button" @click="submitForm">Submit</button>
                        <!-- Submit Button -->
                    </v-form>
            </div>
    
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import TreeDropdown from './TreeDropdown.vue'
import { VDateInput } from 'vuetify/labs/VDateInput'
import { da } from 'vuetify/locale';


export default {
    props: {
        isVisible: {
            type: Boolean,
            required: true
        }
    },
    components: {
      TreeDropdown,
      VDateInput
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
            id: "",
            properties: {
            },
            connected_nodes: {},
            pais: null,
            localidad: null,
            cultura: null,
            exposicion: null,
            uploadedFiles: [],
            previewImages: [],
            components: [{
                /** @type {Ubicacion} */
                selectedUbicacion: null,
                id: null,
                connected_nodes: {},
                properties: {},
                uploadedFiles: [],
                previewImages: []
            }],
            // data fetched
            ubicaciones_data: [],
            paises_data: [],
            culturas_data: [], 
            localidades_data: []
        };
    },
    mounted() {
        this.fetchData();
    },
    methods: {
        async fetchData() {
            try {
                axios.get('http://localhost:8000/nodes/tree/', {params: {
                    labels: 'ubicacion',
                    rel_label: 'ubicacion_contiene'
                }}).then(response => {this.ubicaciones_data = response.data[0]['value']['ubicacion_contiene']; console.log(this.ubicaciones_data);  })
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'pais'
                }}).then(response => {this.paises_data = response.data})
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'localidad'
                }}).then(response => {this.localidades_data = response.data})
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'cultura'
                }}).then(response => {this.culturas_data = response.data})
                  
            }
            catch (error) {
                console.error(error)
            }
        },
        closeModal() {
            this.$emit('close');
        },
        handleFileUpload(event) {
            this.uploadedFiles = event.target.files;
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
        handleComponentFileUpload(component, event) {
            component.uploadedFiles = event.target.files;
            component.previewImages = [];

            for (let i = 0; i < component.uploadedFiles.length; i++) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    component.previewImages.push(e.target.result);
                };
                reader.readAsDataURL(component.uploadedFiles[i]);
            }
            console.log(component.uploadedFiles);
        },
        /**@param {Object} connected_nodes_dict 
         * @returns {SubNode} */
        parseSubnodes(connected_nodes_dict, id_key="name") {
            let result = [];
            for (const [key, val] of Object.entries(connected_nodes_dict)) {
                if (val)
                    result.push({
                        node_id: val,
                        node_label: key,
                        id_key: id_key
                    });
            }
            return result;
        },
        async submitForm() {
            console.log(this );
            const body = JSON.stringify({
                id: this.id,
                properties: this.properties,
                connected_nodes: this.parseSubnodes(this.connected_nodes),
                components: this.components.map(component => ({
                    properties: component.properties,
                    connected_nodes: this.parseSubnodes(component.connected_nodes, "id")
                }))
            });
            console.log(body);
            const data = new FormData();
            data.append('node_create', body);
            //data.append('images', this.uploadedFiles); //no funco
            for (let i=0; i<this.uploadedFiles.length; i++) {
                data.append('images', this.uploadedFiles[i]);
            }
            for (let i=0; i<this.components.length; i++) {
                const component = this.components[i];
                console.log(component);
                for (let j=0; j<component.uploadedFiles.length; j++) {
                    console.log(component.uploadedFiles[j])
                    data.append('component_images', component.uploadedFiles[j], `${i}_${j}_${component.uploadedFiles[j].name}`)
                }
            }
            try {
                const response = await axios.put('http://localhost:8000/add-piece/', data, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                })
                console.log(response);
                this.closeModal();
            }
            catch (e) {
                console.error(e.response.data.detail);
            }
        },
        agregarComponente() {
            this.components.push({
                /** @type {Ubicacion} */
                selectedUbicacion: null,
                id: null,
                connected_nodes: {},
                properties: {},
                uploadedFiles: [],
                previewImages: []
            });
        }
    }
};
</script>

<style scoped>

.form-content {
    overflow-y: auto;
    overflow-x: hidden;
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
    max-width: 950px;
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