<template>
  <div class="login-container">
    <h1>Login</h1>

    <!-- Display error message -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- Login form -->
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">Username</label>
        <input v-model="username" type="text" id="username" placeholder="Enter username" required />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input v-model="password" type="password" id="password" placeholder="Enter password" required />
      </div>

      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: ''
    };
  },
  methods: {
    async login() {
      // Clear previous error messages
      this.errorMessage = '';

      try {
        // Make a POST request to the backend with the login data
        let form = new FormData()
        form.append("username", this.username);
        form.append("password", this.password);
        const response = await axios.post('http://localhost:8000/token', form);

        // Handle successful login (e.g., navigate to dashboard, store token)
        let token = response.data.access_token
        if (token) {
          localStorage.setItem('token', token);  // Save token in localStorage
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          this.$router.push('/dashboard');  // Redirect to dashboard or another protected page
        }
      } catch (error) {
        // Handle login failure
        if (error.response && error.response.status === 401) {
          this.errorMessage = 'Invalid username or password';
        } else {
          this.errorMessage = 'An error occurred. Please try again later.' + error;
        }
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"], input[type="password"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #218838;
}

.error-message {
  color: red;
  margin-bottom: 15px;
}
</style>
