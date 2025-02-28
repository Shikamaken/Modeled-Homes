// frontend/src/store/store.js
import { configureStore } from '@reduxjs/toolkit';
import hvacReducer from '../reducers/hvacReducer';

const store = configureStore({
  reducer: {
    user: hvacReducer, // ✅ Make sure this key is 'hvac'
  },
});

export default store;