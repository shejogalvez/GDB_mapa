<template>
    <th>{{header_text}} <v-btn
        @click = "openMenu"
        class="ma-2"
        :color="isFilterApplied ? 'green' : 'blue-lighten-2'"
        :icon= "isOpen ? 'mdi-filter-menu' : 'mdi-filter-menu-outline'"
        variant="text"  
      ></v-btn>
      
      <div v-if="isOpen" class="filter-menu">
        <!-- Select Comparison Option -->
        <label>
            Comparison:
            <select v-model="operation">
                <option value="=">Equals</option>
                <option value="contains">Contains</option>
                <option value="<">Is Less Than</option>
                <option value=">">Is Greater Than</option>
            </select>
        </label>
        
        <!-- Text Input -->
        <label>
            Value:
            <input type="text" v-model="val" />
        </label>
        
        <!-- Apply Filters Button -->
        <v-btn @click="applyFilters">{{isFilterApplied ? 'Remove Filters': 'Apply Filters' }}</v-btn>
      </div></th>
</template>

<script>
export default  {
    props: {
        header_text: {
            type: String,
            required: true
        },
        node_label: {
            type: String,
            required: false,
            default: 'pieza'
        },
        property_label: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            isOpen: false,
            val: '',
            operation: '',
            isFilterApplied: false,
        }
    },
    methods: {
        applyFilters() {
            if (!this.isFilterApplied)
                this.$emit('applyFilter', {
                    node_label: this.node_label,
                    filter: {
                        key: this.property_label,
                        operation: this.operation,
                        val: this.val
                    }
                })
            this.isFilterApplied = !this.isFilterApplied;
            this.isOpen = false;
        },
        openMenu() {
            this.isOpen = !this.isOpen;
        }
    }
}
</script>

<style scoped>
th {
    position: relative;
}

.filter-menu {
    position: absolute;
    width: 250pt;
    height: 150pt;
    display: grid;
    background-color: white;
    z-index: 2;
}
.filter-menu label {
    border-color: black;
    border: 5pt;
}
</style>