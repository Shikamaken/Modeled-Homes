// frontend/src/reducers/index.js
import { combineReducers } from '@reduxjs/toolkit';
import hvacReducer from './hvacReducer';

const rootReducer = combineReducers({
  hvac: hvacReducer,
});

export default rootReducer;