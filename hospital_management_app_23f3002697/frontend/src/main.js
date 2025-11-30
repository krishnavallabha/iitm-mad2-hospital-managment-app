import { createApp } from 'vue';
import App from './App.vue';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './styles/global.css';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .catch((err) => console.error('Service worker registration failed', err));
  });
}

const token = localStorage.getItem('serenity_token');
console.error('[INFO] Main.js: App mounting. Token present:', token ? 'YES' : 'NO');
if (token) console.error('[TOKEN] Token value:', token.substring(0, 20) + '...');

createApp(App).mount('#app');

