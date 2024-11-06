import { defineStore } from "pinia";

export const useStore = defineStore('store', {
    state: () => ({
        currentPiece: {
            id: "",
            properties: {},
            connected_nodes: {},
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
            localidades_data: [],
            exposiciones_data: [], 
        },
    })
})

export const useFilterStore = defineStore('filterStore', {
    state: () => ({
        filters: {
            pieza: [],
            pais: [],
            localidad: [],
            cultura: [],
            exposicion: [],
        }
    })
})