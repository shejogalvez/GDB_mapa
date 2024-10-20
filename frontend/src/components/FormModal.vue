<template>
    <div>
        <!-- Modal Form -->
        <div v-if="isVisible" class="modal-overlay">
            <div id="form-container" class="modal">
                <form id="agregar-producto-form" method="post"  enctype="multipart/form-data">
                    <label for="tipo_producto" class="label">Tipo de producto:</label>
                    <select id="tipo_producto" name="tipo_producto" class="select-field" onchange="on_select_tipo()">
                        <!-- Opciones para el tipo de producto -->
                        <option value="" disabled selected>Selecciona un tipo de producto</option> <!-- Default option -->
                        <option value="fruta">Frutas</option>
                        <option value="verdura">Verduras</option>
                        <!-- Agrega más opciones según sea necesario -->
                    </select>
                    <br><br>

                    <label class="label">Producto:</label>
                    <p>Productos seleccionados: <span id="selectedValues"></span></p>
                    <div id="producto" name="producto" class="input-field scrollable-div">
                    </div>
                    <br><br>

                    <label for="descripcion" class="label">Descripción:</label>
                    <textarea id="descripcion" name="descripcion" rows="4" cols="50"></textarea>
                    <br><br>
                    
                    <label for="foto_producto" class="label">Foto del producto:</label>
                    <input type="file" id="foto_producto" multiple="multiple" name="foto_producto" class="input-field">
                    <br><br>

                    <label for="region" class="label">Región:</label>
                    <select id="region" name="region" class="select-field">
                        <option v-for="item in []" value={{item.id}}> {{item.nombre}} </option>
                    </select>
                    <br><br>

                    <label for="comuna" class="label">Comuna:</label>
                    <select id="comuna" name="comuna" class="select-field">
                    </select>
                    <br><br>

                    <label for="nombre_productor" class="label">Nombre del productor:</label>
                    <input type="text" id="nombre_productor" name="nombre_productor" class="input-field" size="80" maxlength="80">
                    <br><br>

                    <label for="email_productor" class="label">Email del productor:</label>
                    <input type="email" id="email_productor" name="email_productor" class="input-field" size="30">
                    <br><br>

                    <label for="celular_productor" class="label">Número de celular del productor:</label>
                    <input type="tel" id="celular_productor" name="celular_productor" class="input-field" size="15" placeholder="ej: +56987654321">
                    <br><br>

                    <input type="button" id="submit-producto-btn" value="Agregar producto" class="btn-submit">
                    <span class="close" @click="closeModal">&times;</span>

                <h3>Country/Region and Image Upload Form</h3>

                <!-- Country Selector -->
                <label for="country">Seleccionar ubicacion:</label>
                <select v-model="selectedCountry" id="country" @change="onCountryChange">
                    <option value="" disabled>Select a country</option>
                    <option v-for="country in countries" :key="country.name" :value="country.name + country.label">{{ country.name, country.label }}
                    </option>
                </select>

                <!-- Region Selector (shown only if a country is selected) -->
                <div v-if="selectedCountry">
                    <label for="region">Select Region:</label>
                    <select v-model="selectedRegion" id="region">
                        <option value="" disabled>Select a region</option>
                        <option v-for="region in regions" :key="region.name" :value="region.name">{{ region.name }}</option>
                    </select>
                </div>

                <!-- Multiple Image Upload -->
                <label for="images">Upload Images:</label>
                <input type="file" id="images" @change="handleFileUpload" multiple>

                <!-- Preview Images -->
                <div class="image-preview">
                    <div v-for="(image, index) in previewImages" :key="index">
                        <img :src="image" alt="Image Preview" class="preview">
                    </div>
                </div>

                <!-- Submit Button -->
                <button @click="submitForm">Submit</button>
                </form>
            </div>
    
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    props: {
        isVisible: {
            type: Boolean,
            required: true
        }
    },
    data() {
        return {
            selectedCountry: '',
            selectedRegion: '',
            countries: [
                {
                    name: 'USA',
                    regions: ['California', 'Texas', 'New York', 'Florida']
                },
                {
                    name: 'Canada',
                    regions: ['Ontario', 'Quebec', 'British Columbia', 'Alberta']
                },
                {
                    name: 'Australia',
                    regions: ['New South Wales', 'Victoria', 'Queensland', 'Western Australia']
                }
            ], // List of countries and their regions
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
                this.countries = response.data[0]['value']['ubicacion_contiene']
                console.log(this.countries);    
            }
            catch (error) {
                console.error(error)
            }
        },
        closeModal() {
            this.$emit('close');
        },
        onCountryChange() {
            // Find selected country's regions
            const selectedCountryObj = this.countries.find(country => country.name === this.selectedCountry);
            if (selectedCountryObj) {
                this.regions = selectedCountryObj.ubicacion_contiene;
                this.selectedRegion = ''; // Reset region when country changes
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
            console.log("Selected Country:", this.selectedCountry);
            console.log("Selected Region:", this.selectedRegion);
            console.log("Uploaded Files:", this.uploadedFiles);
        }
    }
};
</script>

<style scoped>

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    width: 400px;
    text-align: center;
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
  border-radius: 12px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0px 15px 30px rgba(0, 0, 0, 0.2);
  position: relative;
  animation: slideUp 0.4s ease;
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
</style>