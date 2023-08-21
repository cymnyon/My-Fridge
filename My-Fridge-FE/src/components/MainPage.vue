<template>
  <div class="login-container">
    <app-navbar></app-navbar> <!-- Use the AppNavbar component -->
    <div class="main-page-sections">
      <div>
        <h1 class="headline-text">DISCOVER <br/> YOUR <br/>FRIDGE</h1>
        <p>The most secure place for organizing your notes, writing journals. completing to-do lists with the help of OCR technology and not only.</p>
        <div class="main-page-buttons">
          <button>Let's get started</button>
        </div>
      </div>
      <div>
        <img src="@/assets/phones.png" alt="phones image" style="width: 414px; height: 444px;" />
      </div>
    </div>
  </div>
</template>

<script>
import AppNavbar from './AppNavbar.vue';

export default {
  components: {
    AppNavbar, // Register the AppNavbar component
  },
};
</script>

<style scoped>
/* Import the external CSS file */
@import '@/static/styles.css';

/* Add your component-specific styles here */
</style>