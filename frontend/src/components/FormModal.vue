<template>
    <div>
    
        <!-- Modal Form -->
        <div v-if="isVisible" class="modal-overlay">
            <div id="form-container" class="modal">
                <h2>{{ title }}</h2>
                <ConfirmAction 
                    text="Se van a borrar los datos del formulario" 
                    title="Confirmar salida" 
                    :confirmFunction="exitForm"
                >
                    <span class="close">&times;</span>
                </ConfirmAction>
                    <v-form class="form-content" @submit="submitForm">
                        <br>
                        <v-row>
                            <v-text-field :rules="rules" label="numero_de_inventario" v-model="pieceData.properties.id" class="input-field"></v-text-field>
                            <v-text-field label="coleccion" v-model="pieceData.properties.coleccion" class="input-field"></v-text-field>
                        </v-row>
                        
                        <v-row>
                            <v-text-field label="SURDOC" v-model="pieceData.properties.SURDOC" class="input-field" ></v-text-field>
                            <v-text-field label="conjunto" v-model="pieceData.properties.conjunto" class="input-field" ></v-text-field>
                        </v-row>
                        <v-text-field label="clasificacion" v-model="pieceData.properties.clasificacion" class="input-field" ></v-text-field>
                        
                        
                        <v-textarea label="contexto_historico" v-model="pieceData.properties.contexto_historico" class="input-field" ></v-textarea>
                        
                        <v-textarea label="notas_investigacion" v-model="pieceData.properties.notas_investigacion" class="input-field" ></v-textarea>
                        
                        <v-textarea label="bibliografia" v-model="pieceData.properties.bibliografia" class="input-field" ></v-textarea>

                        <v-row>
                            <v-text-field label="avaluo" v-model="pieceData.properties.avaluo" class="input-field" ></v-text-field>
                            <v-text-field label="autor" v-model="pieceData.properties.autor" class="input-field" ></v-text-field>
                        </v-row>

                        <v-text-field label="procedencia" v-model="pieceData.properties.procedencia" class="input-field" ></v-text-field>
                        
                        <v-text-field label="donante" v-model="pieceData.properties.donante" class="input-field" ></v-text-field>
                        
                        <v-date-input label="fecha_ingreso" v-model="pieceData.properties.fecha_ingreso" class="input-field" ></v-date-input>
                        
                        <v-combobox 
                            label="pais" 
                            :items="paises_data?.map(o => o.properties.name)"
                            v-model="pieceData.connected_nodes.pais"
                        ></v-combobox>

                        <v-combobox 
                            label="localidad" 
                            :items="localidades_data?.map(o => o.properties.name)"
                            v-model="pieceData.connected_nodes.localidad"
                        ></v-combobox>
                        
                        <v-combobox 
                            label="cultura" 
                            :items="culturas_data?.map(o => o.properties.name)"
                            v-model="pieceData.connected_nodes.cultura"
                        ></v-combobox>
                        
                        <v-combobox 
                            label="exposición" 
                            :items="exposiciones_data?.map(o => o.properties.name)"
                            v-model="pieceData.connected_nodes.exposicion"
                        ></v-combobox>
                        
                        <!-- Multiple Image Upload -->
                        <label for="imagen"> subir imagen piezas</label>
                        <input type="file" id="imagen" name="imagen" @change="handleComponentFileUpload(pieceData, $event)" multiple></input>

                        <!-- Preview Images -->
                        <div class="image-preview">
                            <div v-for="(image, index) in pieceData.previewImages" :key="index">
                                <img :src="image" alt="Image Preview" class="preview">
                            </div>
                        </div>
                        
                        <h3>Componentes</h3>

                        <div v-for="(component, i) in pieceData.components" :key="i">

                            
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
                            
                            <FormaForm :component_index="i"></FormaForm>

                            <label for="ubicacion">Seleccionar ubicacion:</label>
                            <TreeDropdown
                            :options = "ubicaciones_data"
                            :children_key = "'ubicacion_contiene'"
                            :default="component.connected_nodes.ubicacion"
                            @input="(ubicacion) => component.connected_nodes.ubicacion = ubicacion"
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
                        <div class="buttons-div">
                            <button type="button" @click="agregarComponente">+ componente</button>
                            <button v-if="pieceData.components.length > 1" type="button" style="float: right;" @click="deleteComponent">- componente</button>
                        </div>
                        <br><br>
                        <!-- Submit Button -->
                        <ConfirmAction text="Se van a guardar los datos" title="Confirmar envío de formulario" :confirmFunction="submitForm">
                            <v-btn color="blue">
                                Submit
                            </v-btn>
                        </ConfirmAction>
                    </v-form>
            </div>
    
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import TreeDropdown from './TreeDropdown.vue'
import { VDateInput } from 'vuetify/labs/VDateInput'
import { useStore } from '@/stores/store';
import ConfirmAction from './ConfirmAction.vue';
import FormaForm from './FormaForm.vue';


export default {
    props: {
        isVisible: {
            type: Boolean,
            required: true
        },
        title: {
            type: String,
            default: "Crear Pieza"
        }
    },
    components: {
      TreeDropdown,
      VDateInput,
      ConfirmAction,
      FormaForm,
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
            pieceStore: useStore(),
            componentsToDelete: [],
            confirmSubmit: false,
            rules: [
                value => {
                    if (value) return true
                    return 'Campo no puede estar vacio.'
                },
             ],
             ubicaciones_data: [],
             paises_data: [],
             localidades_data: [],
             culturas_data: [],
             exposiciones_data: [],
        };
    },
    mounted() {
        this.fetchData();
        console.log(this.$data);
    },
    methods: {
        async fetchData() {
            try {
                axios.get('http://localhost:8000/nodes/tree/', {params: {
                    labels: 'ubicacion',
                    rel_label: 'ubicacion_contiene'
                }}).then(response => {this.ubicaciones_data = response.data[0]['value']['ubicacion_contiene']})
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'pais'
                }}).then(response => {this.paises_data = response.data})
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'localidad'
                }}).then(response => {this.localidades_data = response.data})
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'cultura'
                }}).then(response => {this.culturas_data = response.data})
                axios.get('http://localhost:8000/nodes/', {params: {
                    labels: 'exposicion'
                }}).then(response => {this.exposiciones_data = response.data})
                  
            }
            catch (error) {
                console.error(error)
            }
        },
        exitForm() {
            this.pieceStore.$reset();
            this.$emit('close');
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
            //console.log(component.uploadedFiles);
        },
        /**@param {Object} connected_nodes_dict 
         * @returns {SubNode} */
        parseSubnodes(connected_nodes_dict, id_key="name") {
            let result = [];
            for (const [key, val] of Object.entries(connected_nodes_dict)) {
                result.push({
                    node_id: val,
                    node_label: key,
                    id_key: id_key
                });
            }
            return result;
        },
        parseComponentSubnodes(connected_nodes) {
            let result = [];
            if (connected_nodes.forma)
                result.push({properties: connected_nodes.forma, node_label: "forma", method: "MERGE"})
            if (connected_nodes.ubicacion)
                result.push({node_id: connected_nodes.ubicacion.id, node_label: "ubicacion", id_key: "id"})
            return result;
        },
        async submitForm() {
            let pieceData = this.pieceData;
            if (this.rules.some((rule) => rule(pieceData.properties.id) !== true)) return
            console.log(pieceData);
            const body = JSON.stringify({
                id: pieceData.id,
                properties: pieceData.properties,
                connected_nodes: this.parseSubnodes(pieceData.connected_nodes),
                components: pieceData.components.map(component => ({
                    id: component.id, // fix
                    properties: component.properties,
                    connected_nodes: this.parseComponentSubnodes(component.connected_nodes)
                }))
            });
            console.log(body);
            const data = new FormData();
            data.append('node_create', body);
            //data.append('images', this.uploadedFiles); //no funco
            for (let i=0; i<pieceData.uploadedFiles.length; i++) {
                data.append('images', pieceData.uploadedFiles[i]);
            }
            for (let i=0; i<pieceData.components.length; i++) {
                const component = pieceData.components[i];
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
                if (!response.data.status_code){
                    this.exitForm();
                }
                else {
                    alert(response.data.detail);
                }
            }
            catch (e) {
                console.error(e.response.data.detail);
            }
        },
        agregarComponente() {
            this.pieceData.components.push({
                id: null,
                connected_nodes: {forma: {}},
                properties: {},
                uploadedFiles: [],
                previewImages: []
            });
        },
        deleteComponent() {
            this.pieceData.components.pop();
        }
    },
    computed: {
        pieceData() {
            return this.pieceStore.$state.currentPiece
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
    border-radius: 1px;
    margin: 2px;
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
  max-width: 200px;
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