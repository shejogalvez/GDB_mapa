import { defineStore } from "pinia";
import axios from 'axios';

export const useStore = defineStore('store', {
    state: () => ({
        currentPiece: {
            id: "",
            properties: {},
            connected_nodes: {},
            uploadedFiles: [],
            previewImages: [],
            components: [{
                id: null,
                connected_nodes: {forma: {}},
                properties: {},
                uploadedFiles: [],
                uploadedInterventions: [],
                previewImages: []
            }],
            // data fetched
            ubicaciones_data: [],
            paises_data: [],
            culturas_data: [], 
            localidades_data: [],
            exposiciones_data: [], 
        },
    }),
    actions: {
        async UpdateFromPieceId(pieceId) {
            const response = await axios.get(`http://localhost:8000/components/`, {params: {
                piece_id: pieceId,
            }});
            let pieceData = response.data[0]
            const properties = pieceData['pieza'];
            let date_properties = ['fecha_ingreso', 'fecha_ultima_modificacion']
            for (const [key, val] of Object.entries(properties)) {
                if (date_properties.includes(key)) {
                    properties[key] = new Date(val);
                }
            }
            delete pieceData['pieza'];
            const connected_nodes = {}
            for (const key of ['pais', 'localidad', 'exposicion', 'cultura']) {
                const val = pieceData[key];
                if (val) {
                    connected_nodes[key] = val.name;
                }
            }
            pieceData.connected_nodes = connected_nodes;
            pieceData.properties = properties;
            pieceData.uploadedFiles = [];
            pieceData.previewImages = [];
            let componentsData = response.data[1]
            for (const component of componentsData){
                const cprops = component['componente'];
                delete component['componente'];
                const connected_nodes = {forma: {}}
                
                for (const [key, val] of Object.entries(cprops)) {
                    if (date_properties.includes(key)) {
                        cprops[key] = new Date(val);
                    }
                }
                for (const key of ['forma', 'ubicacion']) {
                const val = component[key];
                    if (val) {
                    connected_nodes[key] = val;
                    }
                }
                component.connected_nodes = connected_nodes;
                component.properties = cprops;
                component.uploadedFiles = [];
                component.uploadedInterventions = [];
                component.previewImages = [];
            }
            pieceData.components = componentsData;
            
            this.currentPiece = pieceData;
        }
    }
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