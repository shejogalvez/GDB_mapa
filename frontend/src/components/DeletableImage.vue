<template>
    <v-card class="image-card" width="200">
      <!-- Image Thumbnail -->
      <v-img
        :src="imageUrl"
        class="clickable-image"
        aspect-ratio="1"
        @click="showFullImage"
      >
        <!-- Delete Icon Overlay -->
            <v-icon
              class="delete-icon"
              color="red"
              @click.stop="deleteImage"
            >
              mdi-trash-can
            </v-icon>
      </v-img>
  
      <!-- Full-Size Image Modal -->
      <v-dialog v-model="isModalOpen" max-width="800">
        <v-card>
          <v-img :src="imageUrl" class="full-size-image" />
        </v-card>
      </v-dialog>
    </v-card>
  </template>
  
  <script>
  import { ref } from "vue";
  import axios from 'axios';
  
  export default {
    name: "ImageComponent",
    emits: ['imageDeleted'],
    props: {
      imageUrl: {
        type: String,
        required: true,
      },
      imageId: {
        type: String,
        required: true,
      },
    },
    setup(props, ctx) {
      const isModalOpen = ref(false);
  
      // Opens the modal to show the full-size image
      const showFullImage = () => {
        isModalOpen.value = true;
      };
  
      // Sends delete request for the image
      const deleteImage = async () => {
        try {
          const response = await axios.delete(`http://localhost:8000/images/`, {params: {filename: props.imageId}});
          // Emit an event to notify parent component about the deletion
          ctx.emit('imageDeleted');
          console.log(response);
        } catch (error) {
          console.error("Error deleting image:", error);
          alert("error eliminando imagen")
        }
      };
  
      return {
        isModalOpen,
        showFullImage,
        deleteImage,
      };
    },
  };
  </script>
  
  <style scoped>
  .image-card {
    position: relative;
  }
  .clickable-image {
    cursor: pointer;
  }
  .delete-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 2;
    cursor: pointer;
    opacity: 30%;
    transition: opacity 0.3s ease;
    transition: transform 0.2s ease;
  }
  .delete-icon:hover {
    opacity: 100%;
    transform: scale(1.5);
  }
  .full-size-image {
    width: 100%;
    height: auto;
  }
  </style>