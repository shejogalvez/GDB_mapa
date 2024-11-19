<template>
    <div class="custom-select" :tabindex="tabindex" @blur="open = false">
        <div style="align-items: center;">
          <div class="selected" :class="{ open: open }" @click="open = !open">
          {{ selected ? selected.name : "seleccionar ubicacion" }}
          </div>
          <span class="close" v-if="selected" @click="() => {selected = null; open = false; $emit('input', null)}">&times;</span>
        </div>
        <div class="items" :class="{ selectHide: !open }">
            <DropdownItem
                v-for="option of options"
                :item="option"
                :children_key="children_key"
                @input="(item) => {selected = item; open = false; $emit('input', item)}"
            >
            </DropdownItem>
        </div>
    </div>
</template>

<script>
import DropdownItem from './DropdownItem.vue';

export default {
    components:{
        DropdownItem
    },
  props: {
    options: {
      type: Array,
      required: true,
    },
    default: {
      type: Object,
      required: false,
      default: null,
    },
    tabindex: {
      type: Number,
      required: false,
      default: 0,
    },
    children_key: {
      type: String,
      required: false,
      default: 'children',
    },
  },
  data() {
    return {
      selected: this.default
        ? this.default
        : null,
      open: false,
    };
  },
};
</script>

<style>

.custom-select {
  position: relative;
  width: 100%;
  text-align: left;
  outline: none;
  height: 20px;
  line-height: 47px;
}

.custom-select .selected {
  border-radius: 6px;
  border: 1px solid #666666;
  padding-left: 1em;
  cursor: pointer;
  user-select: none;
}

.custom-select .selected.open {
  border: 1px solid #ad8225;
  border-radius: 6px 6px 0px 0px;
}

.custom-select .selected:after {
  position: absolute;
  content: "";
  top: 22px;
  right: 1em;
  width: 0;
  height: 0;
  border-color: #000000;
}

.custom-select .items {
  border-radius: 0px 0px 6px 6px;
  overflow: hidden;
  border-right: 1px solid #ad8225;
  border-left: 1px solid #ad8225;
  border-bottom: 1px solid #ad8225;
  position: absolute;
  left: 0;
  right: 0;
  z-index: 1;
  background-color: #fff;
}

.selectHide {
  display: none;
}

.close {
  background: none;
  border: none;
  font-size: 2rem;
  position: absolute;
  top: 0px;
  right: 15px;
  color: #888;
  cursor: pointer;
}

.close:hover {
  color: #555;
}
</style>