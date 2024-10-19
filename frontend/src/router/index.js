import { createMemoryHistory, createRouter } from 'vue-router';
import axios from 'axios';
import { jwtDecode } from "jwt-decode";
import LoginPage from '../components/LoginPage.vue';
import DataTable from '../components/DataTable.vue';  // Assume you have a Dashboard component

const routes = [
  { path: '/login', name: 'Login', component: LoginPage },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DataTable
  },
  { path: '/:pathMatch(.*)*', name: "nn",
    beforeEnter: (to, from, next) => {
      next('/dashboard');  // Proceed to dashboard
    }
  }  // Redirect any unknown paths to main page
];

const router = createRouter({
    history: createMemoryHistory(),
    routes,
});

// Checks if token is valid, else cleans localstorage
const isAuthenticated = () => {
  const token = localStorage.getItem('token');
  if (!token) return false
  if (jwtDecode(token).exp < Date.now() / 1000) {
    console.log("TOKEN EXPIRED")
    localStorage.clear();
    return false
  }
  return true
}

router.beforeEach(async (to, from) => {
  if (
    !isAuthenticated() &&
    to.name !== 'Login'
  ) {
    // redirect the user to the login page
    return { name: 'Login' }
  }
  else {
    const token = localStorage.getItem('token');
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
})

export default router;
