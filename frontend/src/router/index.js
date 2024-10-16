import { createMemoryHistory, createRouter } from 'vue-router';
import axios from 'axios';
import LoginPage from '../components/LoginPage.vue';
import DataTable from '../components/DataTable.vue';  // Assume you have a Dashboard component

const routes = [
  { path: '/login', name: 'Login', component: LoginPage },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DataTable,
    beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token');
      console.log(token)
      if (!token) {
        next('/login');  // Redirect to login if not authenticated
      } else {
        next();  // Proceed to dashboard
      }
    }
  },
  { path: '/:pathMatch(.*)*', name: "nn",
    beforeEnter: (to, from, next) => {
        const token = localStorage.getItem('token');
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        if (!token) {
          next('/login');  // Redirect to login if not authenticated
        } else {
          next('/dashboard');  // Proceed to dashboard
        }
    }
  }  // Redirect any unknown paths to login
];

const router = createRouter({
    history: createMemoryHistory(),
    routes,
});
  

export default router;
