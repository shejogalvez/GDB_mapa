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

      <button type="submit" class="submit-button">Login</button>
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

        // Handle successful login (e.g., navigate to mainpage, store token)
        let token = response.data.access_token
        if (token) {
          localStorage.setItem('token', token);  // Save token in localStorage
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          this.$router.push('/');  // Redirect to mainpage
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

.login-container {
  text-align: center;
}

h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #444;
}

input[type="text"], input[type="password"] {
  width: 90%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  background-color: #f7f7f7;
}

input[type="text"]:focus, input[type="password"]:focus {
  border-color: #007bff;
  background-color: #fff;
}

.submit-button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease, box-shadow 0.2s ease;
}

.submit-button:hover {
  background-color: #0056b3;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
}

.error-message {
  color: red;
  font-size: 0.9rem;
  margin-bottom: 20px;
}
</style>
